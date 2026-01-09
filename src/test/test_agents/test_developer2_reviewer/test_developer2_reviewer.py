import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from models.state import AgentState
from agents.developer2_reviewer import developer2_reviewer_node


class TestDeveloper2ReviewerNode:
    
    def test_reviewer_omite_revision_cuando_github_deshabilitado(self, mock_state, mock_file_utils, mock_settings):
        result = developer2_reviewer_node(mock_state)
        
        assert result['codigo_revisado'] is True
        assert 'omitida' in result['revision_comentario'].lower()
    
    def test_reviewer_omite_revision_sin_pr(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        result = developer2_reviewer_node(mock_state)
        
        assert result['codigo_revisado'] is True
        assert 'No hay PR' in result['revision_comentario']
    
    def test_reviewer_aprueba_codigo_calidad_aceptable(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['codigo_generado'] = 'def suma(a, b): return a + b'
        mock_state['tests_unitarios_generados'] = 'def test_suma(): assert suma(1, 2) == 3'
        
        with patch('agents.developer2_reviewer.call_gemini') as mock_gemini:
            mock_gemini.return_value = json.dumps({
                "aprobado": True,
                "puntuacion": 9,
                "aspectos_positivos": ["Código limpio", "Buena cobertura"],
                "aspectos_mejorar": [],
                "comentario_revision": "Excelente implementación"
            })
            
            with patch('agents.developer2_reviewer.github_service') as mock_github:
                mock_github.approve_pull_request.return_value = True
                
                result = developer2_reviewer_node(mock_state)
                
                assert result['codigo_revisado'] is True
                assert result['revision_puntuacion'] == 9
                assert result['pr_aprobada'] is True
                mock_github.approve_pull_request.assert_called_once()
    
    def test_reviewer_rechaza_codigo_baja_calidad(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['codigo_generado'] = 'def test(): pass'
        
        with patch('agents.developer2_reviewer.call_gemini') as mock_gemini:
            mock_gemini.return_value = json.dumps({
                "aprobado": False,
                "puntuacion": 4,
                "aspectos_positivos": ["Sintaxis correcta"],
                "aspectos_mejorar": ["Falta documentación", "No hay validación"],
                "comentario_revision": "Requiere mejoras"
            })
            
            with patch('agents.developer2_reviewer.github_service') as mock_github:
                result = developer2_reviewer_node(mock_state)
                
                assert result['codigo_revisado'] is False
                assert result['revision_puntuacion'] == 4
                assert result['pr_aprobada'] is False
                mock_github.add_comment_to_pr.assert_called_once()
    
    def test_reviewer_incrementa_contador_en_rechazo(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['revisor_attempt_count'] = 0
        
        with patch('agents.developer2_reviewer.call_gemini') as mock_gemini:
            mock_gemini.return_value = json.dumps({
                "aprobado": False,
                "puntuacion": 5,
                "aspectos_positivos": [],
                "aspectos_mejorar": ["Mejorar"],
                "comentario_revision": "Requiere cambios"
            })
            
            with patch('agents.developer2_reviewer.github_service'):
                result = developer2_reviewer_node(mock_state)
                
                assert result['revisor_attempt_count'] == 1
    
    def test_reviewer_maneja_error_parsing_json(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        
        with patch('agents.developer2_reviewer.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'Respuesta no JSON'
            
            with patch('agents.developer2_reviewer.github_service') as mock_github:
                mock_github.approve_pull_request.return_value = True
                
                result = developer2_reviewer_node(mock_state)
                
                assert result['codigo_revisado'] is True
                assert result['revision_puntuacion'] == 7
    
    def test_reviewer_limpia_markdown_de_respuesta(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        
        with patch('agents.developer2_reviewer.call_gemini') as mock_gemini:
            mock_gemini.return_value = '''```json
{
    "aprobado": true,
    "puntuacion": 8,
    "aspectos_positivos": ["Bien"],
    "aspectos_mejorar": [],
    "comentario_revision": "OK"
}
```'''
            
            with patch('agents.developer2_reviewer.github_service') as mock_github:
                mock_github.approve_pull_request.return_value = True
                
                result = developer2_reviewer_node(mock_state)
                
                assert result['codigo_revisado'] is True
                assert result['revision_puntuacion'] == 8
    
    def test_reviewer_guarda_archivo_resultado(self, mock_state, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'GITHUB_ENABLED', True)
        
        mock_state['github_pr_number'] = 123
        mock_state['attempt_count'] = 2
        
        with patch('agents.developer2_reviewer.call_gemini') as mock_gemini:
            mock_gemini.return_value = json.dumps({
                "aprobado": True,
                "puntuacion": 8,
                "aspectos_positivos": [],
                "aspectos_mejorar": [],
                "comentario_revision": "OK"
            })
            
            with patch('agents.developer2_reviewer.guardar_fichero_texto') as mock_guardar:
                with patch('agents.developer2_reviewer.github_service') as mock_github:
                    mock_github.approve_pull_request.return_value = True
                    
                    developer2_reviewer_node(mock_state)
                    
                    mock_guardar.assert_called()
                    filename = mock_guardar.call_args[0][0]
                    assert 'req2' in filename
                    assert 'APROBADO' in filename
