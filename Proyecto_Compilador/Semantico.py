# Clases para la tabla de símbolos
class Symbol:
    def __init__(self, name, symbol_type, line_declared):
        self.name = name
        self.type = symbol_type
        self.value = None  # Almacenará el valor directo solo en la declaración
        self.line_declared = line_declared
        self.references = []  # Lista de líneas donde se hace referencia

    def add_reference(self, line):
        if line not in self.references:
            self.references.append(line)  # Agrega la línea a las referencias

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def add_symbol(self, name, symbol_type, line_declared):
        if name in self.symbols:
            raise Exception(f"Error: '{name}' ya está definido en la línea {self.symbols[name].line_declared}.")
        self.symbols[name] = Symbol(name, symbol_type, line_declared)

    def lookup(self, name):
        return self.symbols.get(name, None)

    def set_value(self, name, value):
        symbol = self.lookup(name)
        if not symbol:
            raise Exception(f"Error: '{name}' no está definido.")
        
        # Solo almacenar el valor si es una declaración inicial
        if symbol.value is None:  # Asegurarse de que solo se almacene el valor en la declaración
            symbol.value = value

    def add_reference(self, name, line):
        symbol = self.lookup(name)
        if symbol:
            symbol.add_reference(line)
        else:
            raise Exception(f"Error: '{name}' no está definido en la línea {line}.")

    def __str__(self):
        return '\n'.join([f"{s.name}: {s.type}, Valor: {s.value}, Declarada en: {s.line_declared}, Referencias: {s.references}"
                          for s in self.symbols.values()])

# Inicializa la tabla de símbolos
tabla_simbolos = SymbolTable()

# Funciones para recorrer el árbol de análisis
def analizar_semantico(arbol):
    if arbol[0] == 'programa':
        line_number = 1  # Inicia el conteo de líneas
        for decl in arbol[1]:
            procesar_decl(decl, line_number)
            line_number += 1  # Incrementar el número de línea después de cada declaración
        for sent in arbol[2]:
            procesar_sent(sent, line_number)
            line_number += 1  # Incrementar el número de línea después de cada sentencia

def procesar_decl(decl, line_number):
    tipo = decl[1]  # Tipo de dato
    for id in decl[2]:  # Lista de identificadores
        tabla_simbolos.add_symbol(id, tipo, line_number)  # Agregar línea de declaración

def procesar_sent(sent, line_number):
    if sent[0] == 'decl':
        procesar_decl(sent, line_number)
    elif sent[0] == 'assign':
        var_name = sent[1]
        value = sent[2]  # Suponiendo que el valor está en sent[2]

        # Solo se permite almacenar el valor inicial
        tabla_simbolos.set_value(var_name, value)  # Asignar valor directo

        # Agregar referencia a la variable, que es la línea actual donde se asigna
        tabla_simbolos.add_reference(var_name, line_number)

    elif sent[0] == 'write':
        var_name = sent[1]
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")

        # Agregar referencia a la variable
        tabla_simbolos.add_reference(var_name, line_number)

        print(f"Escribiendo valor de {var_name}: {symbol.value}")  # Imprimir valor

    # Procesar otros tipos de sentencias según sea necesario
    # Asegúrate de registrar las referencias en cada parte donde se usa la variable
    elif sent[0] == 'if' or sent[0] == 'do':
        for expr in sent[1:]:  # Asumiendo que todas las expresiones pueden referirse a variables
            procesar_exp(expr, line_number)

def procesar_exp(expr, line_number):
    # Aquí puedes agregar la lógica para procesar expresiones y registrar referencias
    if isinstance(expr, list):
        for elem in expr:
            if isinstance(elem, str):  # Supongamos que es un identificador
                tabla_simbolos.add_reference(elem, line_number)

def analizar_texto(texto):
    from Sintactico import analizar_sintactico  # Asegúrate de importar tu analizador sintáctico

    arbol = analizar_sintactico(texto)
    if arbol:  # Verifica si se generó un árbol de análisis sintáctico
        try:
            analizar_semantico(arbol)
            print("Tabla de Símbolos:")
            print(tabla_simbolos)
        except Exception as e:
            print(f"Error semántico: {e}")
    else:
        print("No se pudo generar el árbol de análisis sintáctico.")

# Ejemplo de uso
if __name__ == '__main__':
    text = '''
    program {
        int x, y;    
        float a, b;
        bool c;
        c = false;  // Línea 4
        x = 5;      // Línea 5
        y = 4;      // Línea 6
        a = 0.0;    // Línea 7
        b = 3.0;    // Línea 8
        do {        // Línea 9
            if(x < y && y >= 0) { // Línea 10
                c = true;       // Línea 11
            } else {
                x = x - 2;     // Línea 13
                a = a * x + b; // Línea 14
                y = y - 1;     // Línea 15
            }
        } while(c == true); // Línea 16
        write(a);           // Línea 17
        a = a + 1.0;       // Línea 18
        x = a - y;         // Línea 19
    }
    '''
    
    analizar_texto(text)

# Al final de Semantico.py
def obtener_tabla_simbolos():
    return str(tabla_simbolos)
