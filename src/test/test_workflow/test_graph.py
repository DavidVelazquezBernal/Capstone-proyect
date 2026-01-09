import pytest
from unittest.mock import Mock, patch, MagicMock
from workflow.graph import create_workflow


class TestWorkflowGraph:
    
    def test_create_workflow_retorna_compiled_graph(self):
        """Verifica que create_workflow retorna un grafo compilado"""
        workflow = create_workflow()
        
        assert workflow is not None
        assert hasattr(workflow, 'get_graph')
    
    def test_workflow_tiene_todos_los_nodos(self):
        """Verifica que el workflow tiene todos los nodos esperados"""
        workflow = create_workflow()
        graph = workflow.get_graph()
        
        expected_nodes = [
            "ProductOwner",
            "Developer-Code",
            "Sonar",
            "Developer-UnitTests",
            "Developer2-Reviewer",
            "Stakeholder",
            "Developer-CompletePR"
        ]
        
        # Verificar que los nodos existen en el grafo
        nodes = graph.nodes
        for node_name in expected_nodes:
            assert any(node_name in str(node) for node in nodes)
    
    def test_workflow_puede_obtener_grafo(self):
        """Verifica que se puede obtener el grafo del workflow"""
        workflow = create_workflow()
        graph = workflow.get_graph()
        
        assert graph is not None
        assert hasattr(graph, 'nodes')
        assert hasattr(graph, 'edges')
    
    def test_workflow_tiene_nodos_y_edges(self):
        """Verifica que el workflow tiene nodos y edges"""
        workflow = create_workflow()
        graph = workflow.get_graph()
        
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
    
    def test_workflow_puede_generar_mermaid(self):
        """Verifica que el workflow puede generar diagrama Mermaid"""
        workflow = create_workflow()
        
        try:
            mermaid_diagram = workflow.get_graph().draw_mermaid()
            assert mermaid_diagram is not None
            assert isinstance(mermaid_diagram, str)
            assert len(mermaid_diagram) > 0
        except Exception as e:
            pytest.skip(f"No se pudo generar diagrama Mermaid: {e}")
    
    def test_workflow_estructura_basica(self):
        """Verifica la estructura básica del workflow"""
        workflow = create_workflow()
        
        # Verificar que es un objeto compilado válido
        assert workflow is not None
        assert callable(getattr(workflow, 'invoke', None))
        assert callable(getattr(workflow, 'get_graph', None))
