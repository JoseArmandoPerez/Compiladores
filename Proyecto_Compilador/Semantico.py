class Symbol:
    def __init__(self, name, symbol_type, line_declared):
        self.name = name
        self.type = symbol_type
        self.value = None  # Almacenará el valor directo solo en la declaración
        self.line_declared = line_declared
        self.references = []  # Lista de líneas donde se hace referencia
        self.location = hex(id(self))  # Simulación de dirección de memoria

    def add_reference(self, line):
        if line not in self.references:
            self.references.append(line)  # Agrega la línea a las referencias

class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def _hash(self, name):
        return hash(name) % 100  # Ejemplo de tamaño de tabla de 100

    def add_symbol(self, name, symbol_type, line_declared):
        index = self._hash(name)
        if index not in self.symbols:
            self.symbols[index] = []

        # Verificar si el símbolo ya existe en la lista de ese índice
        for symbol in self.symbols[index]:
            if symbol.name == name:
                raise Exception(f"Error: El símbolo '{name}' ya está definido en la línea {symbol.line_declared}.")

        # Agregar el nuevo símbolo
        self.symbols[index].append(Symbol(name, symbol_type, line_declared))

    def lookup(self, name):
        index = self._hash(name)
        if index in self.symbols:
            for symbol in self.symbols[index]:
                if symbol.name == name:
                    return symbol
        return None

    def set_value(self, name, value, line_number):
        symbol = self.lookup(name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{name}' no está definido en la línea {line_number}. No se puede asignar el valor.")

        # Verificación de tipo
        if isinstance(value, bool) and symbol.type != 'bool':
            raise Exception(f"Error de tipo: La asignación de '{name}' con valor '{value}' no coincide con su tipo declarado '{symbol.type}' en la línea {symbol.line_declared}.")
        elif isinstance(value, int) and symbol.type not in ['int', 'float']:
            raise Exception(f"Error de tipo: La asignación de '{name}' con valor '{value}' no coincide con su tipo declarado '{symbol.type}' en la línea {symbol.line_declared}.")
        elif isinstance(value, float) and symbol.type != 'float':
            raise Exception(f"Error de tipo: La asignación de '{name}' con valor '{value}' no coincide con su tipo declarado '{symbol.type}' en la línea {symbol.line_declared}.")
        elif isinstance(value, str) and symbol.type == 'int':
            raise Exception(f"Error de tipo: Se intentó asignar un string '{value}' a la variable '{name}', que se declaró como tipo 'int' en la línea {symbol.line_declared}.")
        
        # Solo almacenar el valor si es una declaración inicial
        if symbol.value is None:  # Asegurarse de que solo se almacene el valor en la declaración
            symbol.value = value

    def add_reference(self, name, line):
        symbol = self.lookup(name)
        if symbol:
            symbol.add_reference(line)
        else:
            raise Exception(f"Error: El símbolo '{name}' no está definido en la línea {line}. No se puede agregar la referencia.")

    def __str__(self):
        # Cabecera de la tabla
        header = f"{'Nombre de Variable':<20} {'Tipo':<10} {'Valor':<10} {'Número de Registro (loc)':<25} {'Número de Línea':<15} {'Referencias':<30}"
        lines = [header]

        # Agregar los símbolos en formato tabular
        for bucket in self.symbols.values():
            for s in bucket:
                line = f"{s.name:<20} {s.type:<10} {s.value:<10} {s.location:<25} {s.line_declared:<15} {str(s.references):<30}"
                lines.append(line)
        
        return '\n'.join(lines)

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

        # Verificación de tipo
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{var_name}' no está definido antes de la asignación en la línea {line_number}.")
        
        # Comprobar si el valor es un literal o una variable
        if isinstance(value, str):
            if value.isnumeric():  # Si es un número, convertirlo a int
                value = int(value)
            else:
                # Comprobando si el valor es una variable
                referenced_symbol = tabla_simbolos.lookup(value)
                if referenced_symbol:
                    value = referenced_symbol.value
                else:
                    # Si no es una variable, se lanza una excepción mencionando el nombre de la variable
                    raise Exception(f"Error: El símbolo '{value}' no está definido en la línea {line_number}. No se puede asignar.")

        # Solo se permite almacenar el valor inicial
        tabla_simbolos.set_value(var_name, value, line_number)  # Asignar valor directo

        # Agregar referencia a la variable, que es la línea actual donde se asigna
        tabla_simbolos.add_reference(var_name, line_number)

    elif sent[0] == 'write':
        var_name = sent[1]
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{var_name}' no está definido en la línea {line_number}. No se puede escribir su valor.")

        # Agregar referencia a la variable
        tabla_simbolos.add_reference(var_name, line_number)

        print(f"Escribiendo valor de {var_name}: {symbol.value}")  # Imprimir valor

    if sent[0] == 'decl':
        procesar_decl(sent, line_number)
    elif sent[0] == 'assign':
        var_name = sent[1]
        value = sent[2]  # Suponiendo que el valor está en sent[2]

        # Verificación de tipo
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{var_name}' no está definido antes de la asignación en la línea {line_number}.")
        
        # Aquí ajustamos para manejar correctamente valores literales y variables
        if isinstance(value, str) and not value.isdigit():  # Verifica que no sea un literal numérico
            referenced_symbol = tabla_simbolos.lookup(value)
            if referenced_symbol:
                value = referenced_symbol.value
            else:
                raise Exception(f"Error: El símbolo '{value}' no está definido en la línea {line_number}. No se puede asignar.")
        
        # Solo se permite almacenar el valor inicial
        tabla_simbolos.set_value(var_name, value, line_number)  # Asignar valor directo

        # Agregar referencia a la variable, que es la línea actual donde se asigna
        tabla_simbolos.add_reference(var_name, line_number)

    elif sent[0] == 'write':
        var_name = sent[1]
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{var_name}' no está definido en la línea {line_number}. No se puede escribir su valor.")

        # Agregar referencia a la variable
        tabla_simbolos.add_reference(var_name, line_number)

        print(f"Escribiendo valor de {var_name}: {symbol.value}")  # Imprimir valor

    elif sent[0] == 'if' or sent[0] == 'do':
        for expr in sent[1:]:  # Asumiendo que todas las expresiones pueden referirse a variables
            procesar_exp(expr, line_number)
    if sent[0] == 'decl':
        procesar_decl(sent, line_number)
    elif sent[0] == 'assign':
        var_name = sent[1]
        value = sent[2]  # Suponiendo que el valor está en sent[2]

        # Verificación de tipo
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{var_name}' no está definido antes de la asignación en la línea {line_number}.")
        
        if isinstance(value, str):
            # Comprobando si el valor es una variable o un literal
            referenced_symbol = tabla_simbolos.lookup(value)
            if referenced_symbol:
                value = referenced_symbol.value
            else:
                raise Exception(f"Error: El símbolo '{value}' no está definido en la línea {line_number}. No se puede asignar.")

        # Solo se permite almacenar el valor inicial
        tabla_simbolos.set_value(var_name, value, line_number)  # Asignar valor directo

        # Agregar referencia a la variable, que es la línea actual donde se asigna
        tabla_simbolos.add_reference(var_name, line_number)

    elif sent[0] == 'write':
        var_name = sent[1]
        symbol = tabla_simbolos.lookup(var_name)
        if not symbol:
            raise Exception(f"Error: El símbolo '{var_name}' no está definido en la línea {line_number}. No se puede escribir su valor.")

        # Agregar referencia a la variable
        tabla_simbolos.add_reference(var_name, line_number)

        print(f"Escribiendo valor de {var_name}: {symbol.value}")  # Imprimir valor

    elif sent[0] == 'if' or sent[0] == 'do':
        for expr in sent[1:]:  # Asumiendo que todas las expresiones pueden referirse a variables
            procesar_exp(expr, line_number)

def procesar_exp(expr, line_number):
    # Aquí puedes agregar la lógica para procesar expresiones y registrar referencias
    if isinstance(expr, list):
        for elem in expr:
            if isinstance(elem, str):  # Supongamos que es un identificador
                tabla_simbolos.add_reference(elem, line_number)

def evaluar_expresion(expr):
    # Lógica para evaluar expresiones constantes
    if isinstance(expr, (int, float, bool)):
        return expr  # Retorna el valor literal
    elif isinstance(expr, str):
        symbol = tabla_simbolos.lookup(expr)
        if symbol:
            return symbol.value
        else:
            raise Exception(f"Error: La variable '{expr}' no está definida. No se puede evaluar la expresión.")

    # Para expresiones más complejas, como aritméticas
    if isinstance(expr, list) and len(expr) == 3:  # Suponiendo una expresión binaria
        left = evaluar_expresion(expr[0])
        operator = expr[1]
        right = evaluar_expresion(expr[2])
        
        if operator == '+':
            return left + right
        elif operator == '-':
            return left - right
        elif operator == '*':
            return left * right
        elif operator == '/':
            if right == 0:
                raise Exception("Error: División por cero.")
            return left / right
        else:
            raise Exception(f"Error: Operador '{operator}' no reconocido.")

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
        print("Error: No se pudo generar el árbol de análisis sintáctico.")

# Ejemplo de uso
if __name__ == '__main__':
    text = '''
    program {
        int a, b;          // Declaraciones correctas
        float c;          // Declaración correcta
        a = 10;           // Asignación correcta
        b = "5";          // Error: tipo de dato incorrecto, se esperaba un int
        c = a + b;        // Error: inferencia de tipos, b no se puede usar aquí
        d = 3.14;         // Error: 'd' no está declarado antes de su uso
        e = a + 1;        // Error: 'e' no está declarado antes de su uso

        // Evaluación de expresiones aritméticas
        resultado = a * (b + c); // Error: b tiene un tipo de dato incorrecto
        write(resultado);         // Debe imprimir el resultado de la expresión 
    }
    '''
    analizar_texto(text)
