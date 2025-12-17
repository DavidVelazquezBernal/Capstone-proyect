"""
Script para corregir la indentación en testing.py
"""

def fix_testing_indentation():
    file_path = r"c:\ACADEMIA\IIA\Capstone proyect v2\src\agents\testing.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Encontrar la línea donde empieza el with agent_execution_context en testing_node
    # y asegurar que todo el código dentro esté correctamente indentado
    
    in_testing_node = False
    in_with_block = False
    base_indent = 0
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Detectar inicio de testing_node
        if 'def testing_node(state: AgentState)' in line:
            in_testing_node = True
            fixed_lines.append(line)
            continue
        
        # Detectar inicio del with block en testing_node
        if in_testing_node and 'with agent_execution_context("🧪 TESTING", logger):' in line:
            in_with_block = True
            base_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Si estamos dentro del with block de testing_node
        if in_with_block:
            # Detectar el final del with block (return state sin indentar extra)
            if line.strip() == 'return state' and len(line) - len(line.lstrip()) == base_indent + 4:
                # Este es el return final dentro del with
                fixed_lines.append(line)
                in_with_block = False
                in_testing_node = False
                continue
            
            # Asegurar que las líneas dentro del with tengan al menos base_indent + 4 espacios
            if line.strip():  # Si la línea no está vacía
                current_indent = len(line) - len(line.lstrip())
                if current_indent < base_indent + 4:
                    # Necesita más indentación
                    extra_indent = (base_indent + 4) - current_indent
                    line = ' ' * extra_indent + line
        
        fixed_lines.append(line)
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Indentación corregida en {file_path}")

if __name__ == "__main__":
    fix_testing_indentation()
