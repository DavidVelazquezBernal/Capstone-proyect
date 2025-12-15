"""
Servicio centralizado para operaciones de GitHub.
Coordina la creación de branches, commits, push y Pull Requests.
"""

import os
import json
import base64
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
        
        if self.enabled:
            try:
                self.client = Github(settings.GITHUB_TOKEN)
                self.repo = self.client.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
                logger.info(f"✅ GitHub Service inicializado para {settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            except Exception as e:
                logger.error(f"❌ Error al inicializar GitHub Service: {e}")
                self.enabled = False
    
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
                if e.status == 422:  # Branch ya existe
                    branch_exists = True
                    # Obtener el SHA actual del branch existente para usarlo como parent
                    existing_ref = self.repo.get_git_ref(f"heads/{branch_name}")
                    parent_sha = existing_ref.object.sha
                    logger.info(f"📌 Branch '{branch_name}' ya existe (SHA: {parent_sha[:7]}), agregando commit...")
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
    
    def approve_pull_request(
        self,
        pr_number: int,
        comment: str
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
            pr = self.repo.get_pull(pr_number)
            
            # Crear review de aprobación
            pr.create_review(
                body=comment,
                event="APPROVE"
            )
            
            logger.info(f"✅ PR #{pr_number} aprobada con comentario")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al aprobar PR: {e}")
            return False
    
    def add_comment_to_pr(
        self,
        pr_number: int,
        comment: str
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
            pr = self.repo.get_pull(pr_number)
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
        merge_method: str = "squash"
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
            pr = self.repo.get_pull(pr_number)
            
            if not pr.mergeable:
                logger.warning(f"⚠️ PR #{pr_number} no es mergeable")
                return False
            
            pr.merge(
                commit_message=commit_message,
                merge_method=merge_method
            )
            
            logger.info(f"✅ PR #{pr_number} mergeada con método '{merge_method}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al hacer merge: {e}")
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
