"""
Servicio centralizado para operaciones de GitHub.
Coordina la creación de branches, commits, push y Pull Requests.
"""

import os
import json
import base64
import time
import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())

# Intentar importar PyGithub
try:
    from github import Github, GithubException, InputGitTreeElement
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    logger.warning("⚠️ PyGithub no está instalado. Ejecuta: pip install PyGithub")


class GitHubService:
    """
    Servicio de alto nivel para operaciones de GitHub.
    Encapsula la lógica de branches, commits y PRs.
    """
    
    def __init__(self):
        """Inicializa el servicio con un cliente de GitHub."""
        self.enabled = settings.GITHUB_ENABLED and GITHUB_AVAILABLE
        self.client = None
        self.repo = None
        self._reviewer_client = None
        self._reviewer_repo = None
        
        if self.enabled:
            try:
                self.client = Github(settings.GITHUB_TOKEN)
                self.repo = self.client.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
                logger.info(f"✅ GitHub Service inicializado para {settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            except Exception as e:
                logger.error(f"❌ Error al inicializar GitHub Service: {e}")
                self.enabled = False

    def _get_reviewer_repo(self):
        reviewer_token = getattr(settings, "GITHUB_REVIEWER_TOKEN", "")
        if not reviewer_token:
            return None

        if self._reviewer_repo is not None:
            return self._reviewer_repo

        try:
            self._reviewer_client = Github(reviewer_token)
            self._reviewer_repo = self._reviewer_client.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            logger.info("✅ GitHub Reviewer client inicializado (cuenta distinta)")
            return self._reviewer_repo
        except Exception as e:
            logger.warning(f"⚠️ No se pudo inicializar reviewer client: {e}")
            self._reviewer_client = None
            self._reviewer_repo = None
            return None

    def _sanitize_branch_name(self, branch_name: str) -> str:
        if not branch_name:
            return branch_name

        # Git ref safety: replace common invalid characters and patterns.
        sanitized = branch_name
        sanitized = sanitized.replace("@{", "_")
        sanitized = re.sub(r"[\s\[\]~^:?*\\]+", "_", sanitized)
        sanitized = re.sub(r"/+", "/", sanitized)
        sanitized = sanitized.strip("/.")
        sanitized = sanitized.replace("..", "_")

        # Avoid special suffix that git rejects
        if sanitized.endswith(".lock"):
            sanitized = sanitized[: -len(".lock")] + "_lock"

        return sanitized

    def sanitize_branch_name(self, branch_name: str) -> str:
        return self._sanitize_branch_name(branch_name)
    
    def create_branch_and_commit(
        self,
        branch_name: str,
        files: Dict[str, str],
        commit_message: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Crea un nuevo branch y hace commit de los archivos.
        
        Args:
            branch_name: Nombre del nuevo branch
            files: Diccionario {ruta_archivo: contenido}
            commit_message: Mensaje del commit
            
        Returns:
            Tuple (éxito, sha_del_commit o None)
        """
        if not self.enabled:
            logger.warning("⚠️ GitHub Service no está habilitado")
            return False, None

        original_branch_name = branch_name
        branch_name = self._sanitize_branch_name(branch_name)
        if branch_name != original_branch_name:
            logger.warning(f"⚠️ Nombre de branch inválido ajustado: '{original_branch_name}' -> '{branch_name}'")
        
        try:
            # Obtener el SHA del branch base
            base_branch = self.repo.get_branch(settings.GITHUB_BASE_BRANCH)
            base_sha = base_branch.commit.sha
            
            logger.info(f"📌 Branch base: {settings.GITHUB_BASE_BRANCH} (SHA: {base_sha[:7]})")
            
            # Crear el nuevo branch o obtener el existente
            ref_name = f"refs/heads/{branch_name}"
            branch_exists = False
            parent_sha = base_sha
            
            try:
                self.repo.create_git_ref(ref=ref_name, sha=base_sha)
                logger.info(f"🌿 Branch '{branch_name}' creado")
            except GithubException as e:
                if e.status == 422:
                    data_str = str(getattr(e, "data", ""))
                    # 422 puede ser tanto "ref ya existe" como "ref inválida".
                    if "reference already exists" in data_str.lower():
                        branch_exists = True
                        # Obtener el SHA actual del branch existente para usarlo como parent
                        existing_ref = self.repo.get_git_ref(f"heads/{branch_name}")
                        parent_sha = existing_ref.object.sha
                        logger.info(f"📌 Branch '{branch_name}' ya existe (SHA: {parent_sha[:7]}), agregando commit...")
                    else:
                        logger.error(f"❌ Branch inválido o no aceptado por GitHub: '{branch_name}' (422). Detalles: {getattr(e, 'data', '')}")
                        return False, None
                else:
                    raise
            
            # Crear blobs para cada archivo
            tree_elements = []
            for file_path, content in files.items():
                blob = self.repo.create_git_blob(content, "utf-8")
                tree_elements.append({
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob.sha
                })
                logger.debug(f"📄 Blob creado para: {file_path}")
            
            # Crear el tree usando InputGitTreeElement
            tree_input = []
            for elem in tree_elements:
                tree_input.append(InputGitTreeElement(
                    path=elem["path"],
                    mode=elem["mode"],
                    type=elem["type"],
                    sha=elem["sha"]
                ))
            
            # Usar el tree del parent correcto (branch existente o base)
            parent_tree = self.repo.get_git_tree(parent_sha)
            new_tree = self.repo.create_git_tree(tree_input, parent_tree)
            
            # Crear el commit con el parent correcto
            parent_commit = self.repo.get_git_commit(parent_sha)
            new_commit = self.repo.create_git_commit(
                message=commit_message,
                tree=new_tree,
                parents=[parent_commit]
            )
            
            # Actualizar la referencia del branch
            ref = self.repo.get_git_ref(f"heads/{branch_name}")
            ref.edit(sha=new_commit.sha, force=True)
            
            logger.info(f"✅ Commit creado: {new_commit.sha[:7]} - {commit_message}")
            
            return True, new_commit.sha
            
        except GithubException as e:
            logger.error(f"❌ Error GitHub al crear branch y commit: {e.status} - {e.data}")
            return False, None
        except Exception as e:
            logger.error(f"❌ Error al crear branch y commit: {type(e).__name__}: {e}")
            return False, None
    
    def create_pull_request(
        self,
        branch_name: str,
        title: str,
        body: str
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Crea una Pull Request desde el branch especificado.
        
        Args:
            branch_name: Nombre del branch origen
            title: Título de la PR
            body: Descripción de la PR
            
        Returns:
            Tuple (éxito, número_de_PR o None, url_de_PR o None)
        """
        if not self.enabled:
            logger.warning("⚠️ GitHub Service no está habilitado")
            return False, None, None

        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=settings.GITHUB_BASE_BRANCH
            )
            
            logger.info(f"✅ Pull Request #{pr.number} creada: {pr.html_url}")
            
            return True, pr.number, pr.html_url
            
        except GithubException as e:
            if e.status == 422:
                logger.warning(f"⚠️ Ya existe una PR para el branch '{branch_name}'")
                # Intentar obtener la PR existente
                pulls = self.repo.get_pulls(state='open', head=f"{settings.GITHUB_OWNER}:{branch_name}")
                for pr in pulls:
                    return True, pr.number, pr.html_url
            logger.error(f"❌ Error al crear PR: {e}")
            return False, None, None
        except Exception as e:
            logger.error(f"❌ Error al crear PR: {e}")
            return False, None, None

    def delete_branch(self, branch_name: str) -> bool:
        if not self.enabled:
            return False

        try:
            sanitized = self._sanitize_branch_name(branch_name)
            if sanitized == settings.GITHUB_BASE_BRANCH:
                logger.warning(f"⚠️ Se omitió borrado de branch remoto base: {sanitized}")
                return False
            ref = self.repo.get_git_ref(f"heads/{sanitized}")
            ref.delete()
            logger.info(f"🧹 Branch remoto eliminado: {sanitized}")
            return True
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"⚠️ Branch remoto no encontrado para borrar: {branch_name}")
                return False
            logger.error(f"❌ Error GitHub al borrar branch remoto: {e.status} - {e.data}")
            return False
        except Exception as e:
            logger.error(f"❌ Error al borrar branch remoto: {type(e).__name__}: {e}")
            return False
    
    def approve_pull_request(
        self,
        pr_number: int,
        comment: str,
        use_reviewer_token: bool = False
    ) -> bool:
        """
        Aprueba una Pull Request con un comentario.
        
        Args:
            pr_number: Número de la PR
            comment: Comentario de aprobación
            
        Returns:
            bool: True si se aprobó correctamente
        """
        if not self.enabled:
            logger.warning("⚠️ GitHub Service no está habilitado")
            return False
        
        try:
            reviewer_repo = self._get_reviewer_repo() if use_reviewer_token else None
            target_repo = reviewer_repo or self.repo
            pr = target_repo.get_pull(pr_number)
            
            # Crear review de aprobación
            pr.create_review(
                body=comment,
                event="APPROVE"
            )
            
            logger.info(f"✅ PR #{pr_number} aprobada con comentario")
            
            return True

        except GithubException as e:
            # Caso típico: el mismo usuario/token que creó la PR intenta aprobarla
            if e.status == 422:
                data_str = str(getattr(e, "data", ""))
                if "approve your own pull request" in data_str.lower():
                    logger.warning(
                        f"⚠️ No se puede aprobar la propia PR #{pr_number} (GitHub 422). "
                        "Publicando comentario en lugar de APPROVE."
                    )
                    try:
                        reviewer_repo = self._get_reviewer_repo() if use_reviewer_token else None
                        target_repo = reviewer_repo or self.repo
                        pr = target_repo.get_pull(pr_number)
                        pr.create_review(body=comment, event="COMMENT")
                        logger.info(f"💬 Comentario de revisión publicado en PR #{pr_number}")
                        return True
                    except Exception as e2:
                        logger.warning(f"⚠️ No se pudo publicar review COMMENT en PR #{pr_number}: {e2}")
                        try:
                            reviewer_repo = self._get_reviewer_repo() if use_reviewer_token else None
                            target_repo = reviewer_repo or self.repo
                            pr = target_repo.get_pull(pr_number)
                            pr.create_issue_comment(comment)
                            logger.info(f"💬 Comentario publicado en PR #{pr_number}")
                            return True
                        except Exception as e3:
                            logger.error(f"❌ Error al comentar PR #{pr_number}: {e3}")
                            return False

            logger.error(f"❌ Error GitHub al aprobar PR: {e.status} - {e.data}")
            return False

        except Exception as e:
            logger.error(f"❌ Error al aprobar PR: {e}")
            return False
    
    def add_comment_to_pr(
        self,
        pr_number: int,
        comment: str,
        use_reviewer_token: bool = False
    ) -> bool:
        """
        Añade un comentario a una Pull Request.
        
        Args:
            pr_number: Número de la PR
            comment: Comentario a añadir
            
        Returns:
            bool: True si se añadió correctamente
        """
        if not self.enabled:
            return False
        
        try:
            reviewer_repo = self._get_reviewer_repo() if use_reviewer_token else None
            target_repo = reviewer_repo or self.repo
            pr = target_repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            logger.info(f"💬 Comentario añadido a PR #{pr_number}")
            return True
        except Exception as e:
            logger.error(f"❌ Error al añadir comentario: {e}")
            return False
    
    def merge_pull_request(
        self,
        pr_number: int,
        commit_message: Optional[str] = None,
        merge_method: str = "squash",
        use_reviewer_token: bool = False
    ) -> bool:
        """
        Hace merge de una Pull Request.
        
        Args:
            pr_number: Número de la PR
            commit_message: Mensaje del merge commit (opcional)
            merge_method: Método de merge ('merge', 'squash', 'rebase')
            
        Returns:
            bool: True si se hizo merge correctamente
        """
        if not self.enabled:
            return False
        
        try:
            reviewer_repo = self._get_reviewer_repo() if use_reviewer_token else None
            target_repo = reviewer_repo or self.repo
            pr = target_repo.get_pull(pr_number)

            # GitHub puede tardar en calcular mergeable (None). Reintentar brevemente.
            for _ in range(5):
                if pr.mergeable is not None:
                    break
                time.sleep(1)
                pr = target_repo.get_pull(pr_number)

            if pr.mergeable is not True:
                logger.warning(f"⚠️ PR #{pr_number} no es mergeable")
                logger.info(f"   Estado de la PR:")
                logger.info(f"   - mergeable: {pr.mergeable}")
                logger.info(f"   - mergeable_state: {pr.mergeable_state}")
                logger.info(f"   - state: {pr.state}")
                logger.info(f"   - merged: {pr.merged}")
                
                # Diagnóstico de causas comunes
                if pr.mergeable_state == "dirty":
                    logger.warning(f"   ⚠️ Causa: Conflictos de merge detectados")
                elif pr.mergeable_state == "blocked":
                    logger.warning(f"   ⚠️ Causa: PR bloqueada por branch protection rules o checks requeridos")
                elif pr.mergeable_state == "behind":
                    logger.warning(f"   ⚠️ Causa: Branch está desactualizado respecto a la base")
                elif pr.mergeable_state == "unstable":
                    logger.warning(f"   ⚠️ Causa: Checks de CI/CD fallaron")
                elif pr.mergeable_state == "draft":
                    logger.warning(f"   ⚠️ Causa: PR está en modo draft")
                else:
                    logger.warning(f"   ⚠️ Estado desconocido: {pr.mergeable_state}")
                
                return False
            
            pr.merge(
                commit_message=commit_message,
                merge_method=merge_method
            )
            
            logger.info(f"✅ PR #{pr_number} mergeada con método '{merge_method}'")
            return True

        except GithubException as e:
            # GitHub suele devolver 404 también cuando el token no tiene permisos suficientes.
            if e.status == 404:
                logger.error(
                    "❌ Error al hacer merge (404 Not Found). Suele indicar falta de permisos del token "
                    "(ej: Pull Requests/Contents write) o que la PR no existe/ya no es accesible. "
                    f"Detalles: {e.data}"
                )
                return False

            if e.status == 405:
                logger.error(
                    "❌ Error al hacer merge (405). Puede que el método de merge no esté permitido "
                    f"(merge_method='{merge_method}') o la PR no sea mergeable. Detalles: {e.data}"
                )
                return False

            if e.status == 409:
                logger.error(
                    "❌ Error al hacer merge (409). Normalmente hay conflictos o branch protection bloqueando el merge. "
                    f"Detalles: {e.data}"
                )
                return False

            logger.error(f"❌ Error GitHub al hacer merge: {e.status} - {e.data}")
            return False

        except Exception as e:
            logger.error(f"❌ Error al hacer merge: {type(e).__name__}: {e}")
            return False
    
    def get_pr_files(self, pr_number: int) -> Dict[str, str]:
        """
        Obtiene los archivos modificados en una PR.
        
        Args:
            pr_number: Número de la PR
            
        Returns:
            Dict con {nombre_archivo: contenido}
        """
        if not self.enabled:
            return {}
        
        try:
            pr = self.repo.get_pull(pr_number)
            files = {}
            
            for file in pr.get_files():
                if file.status != "removed":
                    # Obtener contenido del archivo
                    content = self.repo.get_contents(file.filename, ref=pr.head.sha)
                    if hasattr(content, 'decoded_content'):
                        files[file.filename] = content.decoded_content.decode('utf-8')
            
            return files
            
        except Exception as e:
            logger.error(f"❌ Error al obtener archivos de PR: {e}")
            return {}


# Instancia global del servicio
github_service = GitHubService()
