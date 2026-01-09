import pytest
from unittest.mock import Mock, patch, MagicMock
from models.state import AgentState
from agents.stakeholder import stakeholder_node


class TestStakeholderNode:
    
    def test_stakeholder_valida_codigo_exitosamente(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO: El código cumple con los requisitos'
            
            result = stakeholder_node(mock_state)
            
            assert result['validado'] is True
    
    def test_stakeholder_rechaza_codigo_con_feedback(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'RECHAZADO\nMotivo: Falta validación de entrada'
            with patch('agents.stakeholder.guardar_fichero_texto'):
                result = stakeholder_node(mock_state)
                
                assert result['validado'] is False
                assert 'Falta validación' in result['feedback_stakeholder']
    
    def test_stakeholder_falla_al_exceder_intentos(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 4
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.guardar_fichero_texto'):
            result = stakeholder_node(mock_state)
            
            assert result['validado'] is False
    
    def test_stakeholder_guarda_archivo_validado(self, mock_state, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO: Perfecto'
            with patch('agents.stakeholder.guardar_fichero_texto') as mock_guardar:
                stakeholder_node(mock_state)
                
                mock_guardar.assert_called()
                filename = mock_guardar.call_args[0][0]
                assert 'VALIDADO' in filename
                assert 'intento_1' in filename
    
    def test_stakeholder_guarda_archivo_rechazado(self, mock_state, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'OUTPUT_DIR', '/tmp/test')
        
        mock_state['attempt_count'] = 2
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'RECHAZADO\nMotivo: Necesita mejoras'
            with patch('agents.stakeholder.guardar_fichero_texto') as mock_guardar:
                stakeholder_node(mock_state)
                
                mock_guardar.assert_called()
                filename = mock_guardar.call_args[0][0]
                assert 'RECHAZADO' in filename
                assert 'intento_2' in filename
    
    def test_stakeholder_usa_prompt_template(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO'
            with patch('agents.stakeholder.PromptTemplates.format_stakeholder') as mock_template:
                mock_template.return_value = "Formatted prompt"
                with patch('agents.stakeholder.guardar_fichero_texto'):
                    stakeholder_node(mock_state)
                    
                    mock_template.assert_called_once()
                    assert mock_template.call_args[1]['requisitos_formales'] == mock_state['requisitos_formales']
                    assert mock_template.call_args[1]['codigo_generado'] == mock_state['codigo_generado']
    
    def test_stakeholder_actualiza_azure_a_done_en_validacion(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO'
            with patch('agents.stakeholder.guardar_fichero_texto'):
                with patch('agents.stakeholder.azure_service') as mock_azure:
                    stakeholder_node(mock_state)
                    
                    mock_azure.update_all_work_items_to_done.assert_called_once()
    
    def test_stakeholder_genera_release_note_en_validacion(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        mock_state['azure_pbi_id'] = 123
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO'
            with patch('agents.stakeholder.guardar_fichero_texto'):
                with patch('agents.stakeholder.azure_service') as mock_azure:
                    stakeholder_node(mock_state)
                    
                    mock_azure.generate_and_add_release_note.assert_called_once()
    
    def test_stakeholder_no_actualiza_azure_en_rechazo(self, mock_state, mock_file_utils, monkeypatch):
        from config.settings import settings
        monkeypatch.setattr(settings, 'AZURE_DEVOPS_ENABLED', True)
        
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'RECHAZADO\nMotivo: Problemas'
            with patch('agents.stakeholder.guardar_fichero_texto'):
                with patch('agents.stakeholder.azure_service') as mock_azure:
                    stakeholder_node(mock_state)
                    
                    mock_azure.update_all_work_items_to_done.assert_not_called()
                    mock_azure.generate_and_add_release_note.assert_not_called()
    
    def test_stakeholder_extrae_feedback_con_regex(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = '''RECHAZADO
Motivo: El código no maneja excepciones correctamente.
Además, falta documentación.'''
            with patch('agents.stakeholder.guardar_fichero_texto'):
                result = stakeholder_node(mock_state)
                
                assert result['validado'] is False
                assert 'no maneja excepciones' in result['feedback_stakeholder']
    
    def test_stakeholder_valida_en_primer_intento(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 1
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO: Excelente implementación'
            with patch('agents.stakeholder.guardar_fichero_texto'):
                result = stakeholder_node(mock_state)
                
                assert result['validado'] is True
                assert result['attempt_count'] == 1
    
    def test_stakeholder_valida_en_ultimo_intento(self, mock_state, mock_file_utils, mock_settings):
        mock_state['attempt_count'] = 3
        mock_state['max_attempts'] = 3
        
        with patch('agents.stakeholder.call_gemini') as mock_gemini:
            mock_gemini.return_value = 'VALIDADO: Cumple requisitos'
            with patch('agents.stakeholder.guardar_fichero_texto'):
                result = stakeholder_node(mock_state)
                
                assert result['validado'] is True
                assert result['attempt_count'] == 3
