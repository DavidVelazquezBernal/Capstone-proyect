"""
Servicio centralizado para operaciones de Azure DevOps.
Coordina todas las interacciones con Azure DevOps desde los agentes.
Encapsula la lógica de negocio y reduce duplicación de código.
"""

import os
import json
from typing import Optional, Dict, Any, Tuple
from models.state import AgentState
from models.schemas import AzureDevOpsMetadata
from tools.azure_devops_integration import AzureDevOpsClient, estimate_story_points, estimate_effort_hours
from tools.file_utils import detectar_lenguaje_y_extension, extraer_nombre_archivo, limpiar_codigo_markdown
from config.settings import settings
from config.prompt_templates import PromptTemplates
from utils.logger import setup_logger

logger = setup_logger(__name__, level=settings.get_log_level())


class AzureDevOpsService:
    """
    Servicio de alto nivel para operaciones de Azure DevOps.
    Encapsula la lógica de negocio y coordinación de work items.
    """
    
    def __init__(self):
        """Inicializa el servicio con un cliente de Azure DevOps."""
        self.client = AzureDevOpsClient() if settings.AZURE_DEVOPS_ENABLED else None
        self.enabled = settings.AZURE_DEVOPS_ENABLED
    
    def is_enabled(self) -> bool:
        """Verifica si Azure DevOps está habilitado y configurado."""
        return self.enabled and self.client is not None
    
    # ==================== PRODUCT OWNER ====================
    
    def create_pbi_from_requirements(self, requisitos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un PBI en Azure DevOps a partir de requisitos formales.
        Verifica si ya existe uno similar antes de crear.
        
        Args:
            requisitos: Diccionario con requisitos formales del Product Owner
            
        Returns:
            Diccionario con metadatos del PBI creado o None si falla
        """
        if not self.is_enabled():
            return None
        
        try:
            # Probar conexión primero
            if not self.client.test_connection():
                logger.warning("⚠️ No se pudo conectar con Azure DevOps")
                return None
            
            # Estimar story points
            story_points = estimate_story_points(requisitos)
            logger.info(f"📊 Story Points estimados: {story_points}")
            
            # Verificar si ya existe un PBI similar
            objetivo = requisitos.get('objetivo_funcional', '')
            logger.info(f"🔍 Verificando si existe PBI con título similar...")
            
            existing_pbis = self.client.search_work_items(
                title_contains=objetivo[:50],
                work_item_type="Product Backlog Item",
                tags=["AI-Generated"],
                max_results=5
            )
            
            pbi = None
            if existing_pbis:
                for existing_pbi in existing_pbis:
                    existing_title = existing_pbi['fields'].get('System.Title', '')
                    if objetivo[:50] in existing_title:
                        logger.warning(f"⚠️ Ya existe un PBI similar: #{existing_pbi['id']} - {existing_title}")
                        logger.info(f"🔗 {existing_pbi['_links']['html']['href']}")
                        logger.info(f"♻️ Reutilizando PBI existente")
                        pbi = existing_pbi
                        break
            
            # Si no existe, crear uno nuevo
            if not pbi:
                logger.info("✨ No se encontró PBI existente, creando nuevo...")
                
                # Preparar descripción HTML enriquecida
                description = self._format_pbi_description(requisitos)
                acceptance_criteria = self._format_acceptance_criteria(requisitos)
                
                # Detectar lenguaje para tags
                lenguaje = requisitos.get('lenguaje_version', 'Unknown').split()[0]
                
                # Crear PBI en Azure DevOps
                pbi = self.client.create_pbi(
                    title=f"[AI-Generated] {objetivo[:80]}",
                    description=description,
                    acceptance_criteria=acceptance_criteria,
                    story_points=story_points,
                    tags=["AI-Generated", "Multiagente", lenguaje],
                    priority=2
                )
            
            if pbi:
                logger.info(f"✅ PBI #{pbi['id']} en Azure DevOps")
                logger.info(f"🔗 {pbi['_links']['html']['href']}")
                
                # Crear objeto AzureDevOpsMetadata
                return AzureDevOpsMetadata(
                    work_item_id=pbi['id'],
                    work_item_url=pbi['_links']['html']['href'],
                    work_item_type='Product Backlog Item',
                    area_path=self.client.area_path or None,
                    iteration_path=self.client.iteration_path or None,
                    story_points=story_points
                )
            else:
                logger.warning("⚠️ No se pudo crear el PBI en Azure DevOps")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Error al crear PBI: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return None
    
    def _format_pbi_description(self, requisitos: Dict[str, Any]) -> str:
        """Formatea la descripción del PBI en HTML."""
        return f"""
        <h3>Objetivo Funcional</h3>
        <p>{requisitos.get('objetivo_funcional', 'N/A')}</p>
        
        <h3>Especificaciones Técnicas</h3>
        <ul>
            <li><strong>Lenguaje:</strong> {requisitos.get('lenguaje_version', 'N/A')}</li>
            <li><strong>Función/Clase:</strong> <code>{requisitos.get('nombre_funcion', 'N/A')}</code></li>
        </ul>
        
        <h3>Entradas Esperadas</h3>
        <p>{requisitos.get('entradas_esperadas', 'N/A')}</p>
        
        <h3>Salidas Esperadas</h3>
        <p>{requisitos.get('salidas_esperadas', 'N/A')}</p>
        
        <hr/>
        <p><em>🤖 Generado automáticamente por el sistema multiagente de desarrollo ágil</em></p>
        """
    
    def _format_acceptance_criteria(self, requisitos: Dict[str, Any]) -> str:
        """Formatea los criterios de aceptación en HTML."""
        return f"""
        <h4>Criterios de Aceptación</h4>
        <ul>
            <li>✅ El código debe implementar: {requisitos.get('objetivo_funcional', 'N/A')}</li>
            <li>✅ Las entradas deben cumplir: {requisitos.get('entradas_esperadas', 'N/A')}</li>
            <li>✅ Las salidas deben cumplir: {requisitos.get('salidas_esperadas', 'N/A')}</li>
            <li>✅ Todos los tests unitarios deben pasar</li>
            <li>✅ El código debe pasar el análisis de SonarQube sin issues bloqueantes</li>
        </ul>
        """
    
    # ==================== DESARROLLADOR ====================
    
    def create_implementation_tasks(
        self, 
        state: AgentState, 
        lenguaje: str
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Crea las Tasks de Implementación y Testing asociadas al PBI.
        Verifica si ya existen antes de crear nuevas.
        
        Args:
            state: Estado compartido del workflow
            lenguaje: Lenguaje de programación detectado
            
        Returns:
            Tupla (implementation_task_id, testing_task_id)
        """
        if not self.is_enabled() or not state.get('azure_pbi_id'):
            return None, None
        
        try:
            pbi_id = state['azure_pbi_id']
            
            # Verificar si ya existen Tasks asociadas
            logger.info(f"🔍 Verificando tasks existentes para el PBI #{pbi_id}...")
            existing_children = self.client.get_child_work_items(pbi_id)
            
            # Filtrar por tipo Task y tag AI-Generated
            existing_tasks = [
                child for child in existing_children 
                if child['fields'].get('System.WorkItemType') == 'Task' and
                   'AI-Generated' in child['fields'].get('System.Tags', '')
            ]
            
            if existing_tasks:
                logger.warning(f"⚠️ Ya existen {len(existing_tasks)} Task(s) AI-Generated asociadas al PBI #{pbi_id}")
                impl_id = None
                test_id = None
                
                for task in existing_tasks:
                    task_title = task['fields'].get('System.Title', '')
                    task_id = task['id']
                    logger.info(f"   📋 Task #{task_id}: {task_title}")
                    
                    if 'Implementar' in task_title or 'Implementation' in task_title:
                        impl_id = task_id
                    elif 'test' in task_title.lower():
                        test_id = task_id
                
                if impl_id and test_id:
                    logger.info("♻️ Reutilizando Tasks existentes")
                    return impl_id, test_id
            
            # No existen tasks, crear nuevas
            logger.info("✨ No se encontraron Tasks existentes, creando nuevas...")
            
            # Parsear requisitos formales
            requisitos = json.loads(state.get('requisitos_formales', '{}'))
            objetivo = requisitos.get('objetivo_funcional', 'Implementar funcionalidad')
            nombre_funcion = requisitos.get('nombre_funcion', 'función')
            lenguaje_req = requisitos.get('lenguaje_version', lenguaje)
            
            # TASK 1: Implementación
            task_impl = self.client.create_task(
                title=f"[AI-Generated] Implementar {nombre_funcion}",
                description=f"""
                <h3>Objetivo</h3>
                <p>{objetivo}</p>
                
                <h3>Especificaciones Técnicas</h3>
                <ul>
                    <li><strong>Lenguaje:</strong> {lenguaje_req}</li>
                    <li><strong>Función/Clase:</strong> <code>{nombre_funcion}</code></li>
                </ul>
                
                <h3>Tareas</h3>
                <ul>
                    <li>✅ Código generado automáticamente por IA</li>
                    <li>⏳ Revisar implementación</li>
                    <li>⏳ Validar lógica de negocio</li>
                    <li>⏳ Verificar manejo de errores</li>
                </ul>
                
                <hr/>
                <p><em>🤖 Task creada automáticamente por el sistema multiagente</em></p>
                """,
                parent_id=pbi_id,
                remaining_work=estimate_effort_hours("implementation"),
                tags=["AI-Generated", "Implementation", lenguaje, "Auto-Created"]
            )
            
            # TASK 2: Testing
            task_test = self.client.create_task(
                title=f"[AI-Generated] Crear unit tests para {nombre_funcion}",
                description=f"""
                <h3>Objetivo</h3>
                <p>Crear suite completa de unit tests para validar la implementación de {nombre_funcion}</p>
                
                <h3>Especificaciones de Testing</h3>
                <ul>
                    <li><strong>Framework:</strong> {"vitest" if lenguaje.lower() == "typescript" else "pytest"}</li>
                    <li><strong>Cobertura objetivo:</strong> &gt;80%</li>
                </ul>
                
                <h3>Casos de Prueba Requeridos</h3>
                <ul>
                    <li>⏳ Tests para flujo normal (happy path)</li>
                    <li>⏳ Tests para casos límite (edge cases)</li>
                    <li>⏳ Tests para manejo de errores</li>
                </ul>
                
                <hr/>
                <p><em>🤖 Task creada automáticamente por el sistema multiagente</em></p>
                """,
                parent_id=pbi_id,
                remaining_work=estimate_effort_hours("testing"),
                tags=["AI-Generated", "Testing", "Unit-Tests", lenguaje, "Auto-Created"]
            )
            
            impl_id = task_impl['id'] if task_impl else None
            test_id = task_test['id'] if task_test else None
            
            if impl_id:
                logger.info(f"✅ Task de Implementación creada: #{impl_id}")
            if test_id:
                logger.info(f"✅ Task de Testing creada: #{test_id}")
            
            if impl_id and test_id:
                logger.info(f"🎯 2 Tasks creadas y asociadas al PBI #{pbi_id}")
            
            return impl_id, test_id
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron crear Tasks: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return None, None
    
    # ==================== ANALIZADOR SONARQUBE ====================
    
    def update_implementation_task_to_in_progress(self, task_id: int) -> bool:
        """
        Actualiza el estado de la Task de Implementación a "In Progress".
        
        Args:
            task_id: ID de la Task de Implementación
            
        Returns:
            True si se actualizó correctamente
        """
        if not self.is_enabled() or not task_id:
            return False
        
        try:
            logger.info(f"🔄 Actualizando Task de Implementación #{task_id} a 'In Progress'...")
            
            result = self.client.update_work_item(
                work_item_id=task_id,
                fields={"System.State": "In Progress"}
            )
            
            if result:
                logger.info(f"✅ Task #{task_id} actualizada a 'In Progress'")
                return True
            else:
                logger.warning(f"⚠️ No se pudo actualizar el estado de la Task #{task_id}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Error al actualizar Task: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def add_sonarqube_approval_comment(self, task_id: int, report_file: str) -> bool:
        """
        Agrega comentario de aprobación de SonarQube a la Task de Implementación.
        
        Args:
            task_id: ID de la Task de Implementación
            report_file: Nombre del archivo de reporte
            
        Returns:
            True si se agregó el comentario
        """
        if not self.is_enabled() or not task_id:
            return False
        
        try:
            comment = f"""✅ Análisis de SonarQube completado exitosamente

El código ha pasado el análisis de calidad sin issues bloqueantes.

📊 Reporte guardado: {report_file}
🎯 Estado: Aprobado para continuar con testing"""
            
            success = self.client.add_comment(task_id, comment)
            if success:
                logger.info(f"📝 Comentario de aprobación agregado a Task #{task_id}")
            return success
            
        except Exception as e:
            logger.warning(f"⚠️ Error al agregar comentario: {e}")
            return False
    
    def add_sonarqube_issues_comment(
        self, 
        task_id: int, 
        report_file: str, 
        instructions_file: str,
        attempt: int,
        max_attempts: int
    ) -> bool:
        """
        Agrega comentario con issues de SonarQube a la Task de Implementación.
        
        Args:
            task_id: ID de la Task de Implementación
            report_file: Nombre del archivo de reporte
            instructions_file: Nombre del archivo de instrucciones
            attempt: Intento actual
            max_attempts: Intentos máximos
            
        Returns:
            True si se agregó el comentario
        """
        if not self.is_enabled() or not task_id:
            return False
        
        try:
            comment = f"""⚠️ Issues de calidad detectados por SonarQube (Intento {attempt}/{max_attempts})

El código requiere correcciones antes de continuar.

📊 Reporte: {report_file}
📝 Instrucciones: {instructions_file}

El código será corregido automáticamente por el Desarrollador."""
            
            success = self.client.add_comment(task_id, comment)
            if success:
                logger.info(f"📝 Comentario de issues agregado a Task #{task_id}")
            return success
            
        except Exception as e:
            logger.warning(f"⚠️ Error al agregar comentario: {e}")
            return False
    
    # ==================== EJECUTOR PRUEBAS ====================
    
    def update_testing_task_to_in_progress(self, task_id: int) -> bool:
        """
        Actualiza el estado de la Task de Testing a "In Progress".
        
        Args:
            task_id: ID de la Task de Testing
            
        Returns:
            True si se actualizó correctamente
        """
        if not self.is_enabled() or not task_id:
            return False
        
        try:
            logger.info(f"🔄 Actualizando Task de Testing #{task_id} a 'In Progress'...")
            
            result = self.client.update_work_item(
                work_item_id=task_id,
                fields={"System.State": "In Progress"}
            )
            
            if result:
                logger.info(f"✅ Task #{task_id} actualizada a 'In Progress'")
                return True
            else:
                logger.warning(f"⚠️ No se pudo actualizar el estado de la Task #{task_id}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Error al actualizar Task: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def attach_tests_and_add_success_comment(
        self,
        state: AgentState,
        test_file_path: str,
        total_tests: int
    ) -> bool:
        """
        Adjunta tests al PBI y Task de Testing, y agrega comentario de éxito.
        
        Args:
            state: Estado compartido
            test_file_path: Ruta del archivo de tests
            total_tests: Número total de tests que pasaron
            
        Returns:
            True si se completó correctamente
        """
        if not self.is_enabled():
            return False
        
        pbi_id = state.get('azure_pbi_id')
        task_id = state.get('azure_testing_task_id')
        
        if not pbi_id or not task_id:
            return False
        
        try:
            # Validar archivo
            if not os.path.exists(test_file_path):
                logger.warning(f"⚠️ Archivo de tests no encontrado: {test_file_path}")
                return False
            
            file_name = os.path.basename(test_file_path)
            file_size = os.path.getsize(test_file_path)
            attempt = state['attempt_count']
            sq_attempt = state['sonarqube_attempt_count']
            
            print()  # Línea en blanco
            logger.info("=" * 60)
            logger.info("📎 ADJUNTANDO TESTS UNITARIOS A AZURE DEVOPS")
            logger.info("-" * 60)
            logger.info(f"📄 Archivo: {file_name}")
            logger.info(f"📊 Tamaño: {file_size} bytes")
            logger.info(f"🎯 PBI: #{pbi_id}")
            logger.info(f"🧪 Task Testing: #{task_id}")
            
            # Adjuntar al PBI
            success_pbi = self.client.attach_file(
                work_item_id=pbi_id,
                file_path=test_file_path,
                comment=f"✅ Tests unitarios generados (req{attempt}_sq{sq_attempt}) - Todos los tests pasaron"
            )
            
            if success_pbi:
                logger.info(f"✅ Tests adjuntados al PBI #{pbi_id}")
            
            # Adjuntar a Task
            success_task = self.client.attach_file(
                work_item_id=task_id,
                file_path=test_file_path,
                comment=f"✅ Suite de tests unitarios completa - {file_size} bytes"
            )
            
            if success_task:
                logger.info(f"✅ Tests adjuntados a Task #{task_id}")
            
            if success_pbi and success_task:
                logger.info("🎉 Tests unitarios adjuntados exitosamente a ambos work items")
                
                # Agregar comentario de éxito
                comment = f"""✅ Tests unitarios ejecutados exitosamente

Todos los tests han pasado correctamente.

📊 Resultados:
  • Total de tests: {total_tests}
  • Estado: PASSED ✅

📎 Tests adjuntados al work item"""
                
                self.client.add_comment(task_id, comment)
                logger.info(f"📝 Comentario de éxito agregado a Task #{task_id}")
            
            logger.info("=" * 60)
            
            return success_pbi and success_task
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron adjuntar tests: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def add_test_failure_comment(
        self,
        task_id: int,
        total: int,
        passed: int,
        failed: int,
        attempt: int,
        max_attempts: int,
        report_file: str
    ) -> bool:
        """
        Agrega comentario cuando los tests fallan.
        
        Args:
            task_id: ID de la Task de Testing
            total: Total de tests
            passed: Tests que pasaron
            failed: Tests que fallaron
            attempt: Intento actual
            max_attempts: Intentos máximos
            report_file: Nombre del archivo de reporte
            
        Returns:
            True si se agregó el comentario
        """
        if not self.is_enabled() or not task_id:
            return False
        
        try:
            comment = f"""❌ Tests fallidos (Intento {attempt}/{max_attempts})

Los tests no han pasado y requieren corrección del código.

📊 Estadísticas:
  • Total: {total}
  • Pasados: {passed}
  • Fallidos: {failed}

📁 Reporte: {report_file}

El código será corregido automáticamente por el Desarrollador."""
            
            success = self.client.add_comment(task_id, comment)
            if success:
                logger.info(f"📝 Comentario de fallo agregado a Task #{task_id}")
            return success
            
        except Exception as e:
            logger.warning(f"⚠️ Error al agregar comentario: {e}")
            return False
    
    # ==================== STAKEHOLDER ====================
    
    def attach_final_code_to_work_items(self, state: AgentState) -> bool:
        """
        Adjunta el código final al PBI y Task de Implementación.
        
        Args:
            state: Estado compartido
            
        Returns:
            True si se adjuntó correctamente a ambos work items
        """
        if not self.is_enabled():
            return False
        
        pbi_id = state.get('azure_pbi_id')
        task_id = state.get('azure_implementation_task_id')
        
        if not pbi_id or not task_id:
            return False
        
        try:
            # Detectar lenguaje y construir path
            lenguaje, extension, patron_limpieza = detectar_lenguaje_y_extension(
                state.get('requisitos_formales', '')
            )
            
            # Extraer nombre descriptivo del archivo
            nombre_base = extraer_nombre_archivo(state.get('requisitos_formales', ''))
            nombre_archivo = f"{nombre_base}{extension}"
            codigo_path = os.path.join(settings.OUTPUT_DIR, nombre_archivo)
            
            # Si el archivo no existe, crearlo desde el estado
            if not os.path.exists(codigo_path):
                codigo_generado = state.get('codigo_generado', '')
                if codigo_generado:
                    codigo_limpio = limpiar_codigo_markdown(codigo_generado)
                    with open(codigo_path, 'w', encoding='utf-8') as f:
                        f.write(codigo_limpio)
                    logger.info(f"📝 Archivo {nombre_archivo} creado para adjuntar")
                else:
                    logger.warning(f"⚠️ No hay código generado para crear {nombre_archivo}")
                    return False
            
            file_size = os.path.getsize(codigo_path)
            
            print()  # Línea en blanco
            logger.info("=" * 60)
            logger.info("📎 ADJUNTANDO CÓDIGO FINAL A AZURE DEVOPS")
            logger.info("-" * 60)
            logger.info(f"📄 Archivo: {nombre_archivo}")
            logger.info(f"📊 Tamaño: {file_size} bytes")
            logger.info(f"🎯 PBI: #{pbi_id}")
            logger.info(f"⚙️ Task Implementación: #{task_id}")
            
            # Adjuntar al PBI
            success_pbi = self.client.attach_file(
                work_item_id=pbi_id,
                file_path=codigo_path,
                comment="✅ Código final validado por el Stakeholder - Listo para producción"
            )
            
            if success_pbi:
                logger.info(f"✅ Código final adjuntado al PBI #{pbi_id}")
            
            # Adjuntar a Task
            success_task = self.client.attach_file(
                work_item_id=task_id,
                file_path=codigo_path,
                comment=f"✅ Implementación completa y validada - {file_size} bytes"
            )
            
            if success_task:
                logger.info(f"✅ Código final adjuntado a Task #{task_id}")
            
            if success_pbi and success_task:
                logger.info("🎉 Código final adjuntado exitosamente a ambos work items")
            
            logger.info("=" * 60)
            
            return success_pbi and success_task
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo adjuntar código final: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def update_all_work_items_to_done(self, state: AgentState) -> bool:
        """
        Actualiza todos los work items (PBI y Tasks) a estado "Done".
        
        Args:
            state: Estado compartido
            
        Returns:
            True si se actualizaron todos correctamente
        """
        if not self.is_enabled():
            return False
        
        pbi_id = state.get('azure_pbi_id')
        impl_task_id = state.get('azure_implementation_task_id')
        test_task_id = state.get('azure_testing_task_id')
        
        if not pbi_id:
            return False
        
        try:
            print()  # Línea en blanco
            logger.info("=" * 60)
            logger.info("🎯 ACTUALIZANDO WORK ITEMS A 'DONE'")
            logger.info("-" * 60)
            
            success = True
            
            # Actualizar Task de Implementación
            if impl_task_id:
                logger.info(f"🔄 Actualizando Task de Implementación #{impl_task_id} a 'Done'...")
                result = self.client.update_work_item(
                    work_item_id=impl_task_id,
                    fields={"System.State": "Done"}
                )
                if result:
                    logger.info(f"✅ Task de Implementación #{impl_task_id} marcada como 'Done'")
                    self.client.add_comment(
                        impl_task_id,
                        "✅ Implementación completada y validada por el Stakeholder. Código listo para producción."
                    )
                else:
                    logger.warning(f"⚠️ No se pudo actualizar Task #{impl_task_id}")
                    success = False
            
            # Actualizar Task de Testing
            if test_task_id:
                logger.info(f"🔄 Actualizando Task de Testing #{test_task_id} a 'Done'...")
                result = self.client.update_work_item(
                    work_item_id=test_task_id,
                    fields={"System.State": "Done"}
                )
                if result:
                    logger.info(f"✅ Task de Testing #{test_task_id} marcada como 'Done'")
                    self.client.add_comment(
                        test_task_id,
                        "✅ Todos los tests pasaron exitosamente. Testing completado."
                    )
                else:
                    logger.warning(f"⚠️ No se pudo actualizar Task #{test_task_id}")
                    success = False
            
            # Actualizar PBI
            logger.info(f"🔄 Actualizando PBI #{pbi_id} a 'Done'...")
            result = self.client.update_work_item(
                work_item_id=pbi_id,
                fields={"System.State": "Done"}
            )
            if result:
                logger.info(f"✅ PBI #{pbi_id} marcado como 'Done'")
                
                # Agregar comentario final con resumen
                summary_comment = f"""🎉 Proyecto completado exitosamente

El código ha sido:
✅ Implementado y generado automáticamente
✅ Aprobado por análisis de SonarQube
✅ Validado con tests unitarios
✅ Aprobado por el Stakeholder

📊 Estado final: DONE
🚀 Listo para producción"""
                
                self.client.add_comment(pbi_id, summary_comment)
                logger.info(f"📝 Comentario de cierre agregado al PBI #{pbi_id}")
            else:
                logger.warning(f"⚠️ No se pudo actualizar PBI #{pbi_id}")
                success = False
            
            logger.info("-" * 60)
            if success:
                logger.info("🎉 Todos los work items actualizados a 'Done'")
            logger.info("=" * 60)
            
            return success
            
        except Exception as e:
            logger.warning(f"⚠️ Error al actualizar work items a Done: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False
    
    def generate_and_add_release_note(self, state: AgentState) -> bool:
        """
        Genera un Release Note usando LLM y lo agrega como comentario al PBI.
        
        Args:
            state: Estado compartido del workflow con toda la información del proyecto
            
        Returns:
            True si se agregó exitosamente
        """
        if not self.is_enabled():
            return False
        
        pbi_id = state.get('azure_pbi_id')
        if not pbi_id:
            return False
        
        try:
            from llm.gemini_client import call_gemini
            from config.prompts import Prompts
            import json
            import time
            
            logger.info("=" * 60)
            logger.info("📝 GENERANDO RELEASE NOTE")
            logger.info("-" * 60)
            
            # Preparar métricas para el template
            requisitos = json.loads(state.get('requisitos_formales', '{}'))
            
            story_points = requisitos.get('azure_devops', {}).get('story_points', 'N/A')
            total_attempts = state.get('attempt_count', 1)
            debug_attempts = state.get('debug_attempt_count', 0)
            sonarqube_attempts = state.get('sonarqube_attempt_count', 0)
            test_suites = len(state.get('tests_unitarios_generados', '').split('describe')) - 1 if state.get('tests_unitarios_generados') else 0
            
            logger.info("🤖 Generando Release Note con LLM...")
            logger.debug("🔗 Usando ChatPromptTemplate de LangChain")
            start_time = time.time()
            
            # Usar ChatPromptTemplate para generar el Release Note
            prompt_formateado = PromptTemplates.format_release_note_generator(
                requisitos_formales=state.get('requisitos_formales', 'N/A'),
                codigo_generado=state.get('codigo_generado', 'N/A'),
                story_points=str(story_points),
                total_attempts=total_attempts,
                debug_attempts=debug_attempts,
                sonarqube_attempts=sonarqube_attempts,
                test_suites=test_suites,
                estado_final="VALIDADO por Stakeholder"
            )
            
            # Llamar al LLM con el prompt formateado
            release_note = call_gemini(prompt_formateado, "")
            
            duration = time.time() - start_time
            logger.info(f"⏱️  Release Note generado en {duration:.2f}s")
            
            # Estrategia 1: Actualizar el campo Custom.ReleaseNote del PBI
            logger.info(f"📤 Actualizando campo ReleaseNote del PBI #{pbi_id}...")
            
            # Actualizar el PBI con el Release Note en el campo personalizado
            try:
                update_result = self.client.update_work_item(
                    work_item_id=pbi_id,
                    fields={"Custom.ReleaseNote": release_note}
                )
                if update_result:
                    logger.info(f"✅ Release Note agregado al campo Custom.ReleaseNote del PBI #{pbi_id}")
                    success_release_field = True
                else:
                    logger.warning(f"⚠️ No se pudo actualizar el campo Custom.ReleaseNote")
                    success_release_field = False
            except Exception as field_error:
                logger.warning(f"⚠️ Error al actualizar Custom.ReleaseNote: {field_error}")
                success_release_field = False
            
                # Considerar éxito solo si el campo personalizado fue actualizado
                if success_release_field:
                    logger.info("=" * 60)
                    return True
                else:
                    logger.warning(f"⚠️ No se pudo agregar el Release Note al PBI #{pbi_id}")
                    logger.warning("   Puede ser un problema de permisos en Azure DevOps")
                    try:
                        logger.info("💾 Guardando Release Note localmente como respaldo...")
                        from tools.file_utils import guardar_fichero_texto
                        filename = f"release_note_pbi_{pbi_id}.html"
                        guardar_fichero_texto(filename, release_note, directorio=settings.OUTPUT_DIR)
                        logger.info(f"✅ Release Note guardado en: output/{filename}")
                    except Exception as save_error:
                        logger.warning(f"⚠️ No se pudo guardar localmente: {save_error}")
                        return False
        except Exception as e:
            logger.warning(f"⚠️ Error inesperado en el proceso de Release Note: {e}")
            logger.debug(f"Stack trace: {e}", exc_info=True)
            return False


# ==================== INSTANCIA GLOBAL ====================

# Singleton para uso en los agentes
azure_service = AzureDevOpsService()
