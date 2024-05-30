from Lexico import prueba
from Sintactico import analizar_sintactico, formatear_arbol

data = '''
program {
    int a;
}
'''

# Ejecuta el analizador léxico
tokens = prueba(data)
print(tokens)

# Ejecuta el analizador sintáctico
arbol = analizar_sintactico(data)
tree, _ = formatear_arbol(arbol)
for line in tree:
    print(line)
