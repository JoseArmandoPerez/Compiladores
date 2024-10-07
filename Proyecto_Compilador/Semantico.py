import hashlib
from prettytable import PrettyTable  # Importa PrettyTable

# Clase para la tabla de hashes
class HashTable:
    def __init__(self):
        self.hashes = {}

    def add_hash(self, name, value, operands=None):
        # Calcular el hash usando SHA256
        hash_value = hashlib.sha256(str(value).encode()).hexdigest()
        # Guardar el hash junto con los operandos
        self.hashes[name] = {
            "hash": hash_value,
            "value": value,
            "operands": operands
        }

    def __str__(self):
        # Usar PrettyTable para formatear la salida
        table = PrettyTable()
        table.field_names = ["Variable", "Hash", "Valor", "Operandos"]
        for name, data in self.hashes.items():
            operands_str = ", ".join(data["operands"]) if data["operands"] else "N/A"
            table.add_row([name, data["hash"], data["value"], operands_str])
        return str(table)

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

    def calculate_hash(self):
        if self.value is not None:
            return hashlib.sha256(str(self.value).encode()).hexdigest()
        return None

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.hash_table = HashTable()  # Inicializa la tabla de hashes

    def add_symbol(self, name, symbol_type, line_declared):
        if name in self.symbols:
            raise Exception(f"Error: '{name}' ya está definido en la línea {self.symbols[name].line_declared}.")
        self.symbols[name] = Symbol(name, symbol_type, line_declared)

    def lookup(self, name):
        return self.symbols.get(name, None)

    def set_value(self, name, value, operands=None):
        symbol = self.lookup(name)
        if not symbol:
            raise Exception(f"Error: '{name}' no está definido.")

        # Solo almacenar el valor si es una declaración inicial
        if symbol.value is None:  # Asegurarse de que solo se almacene el valor en la declaración
            symbol.value = value
            # Almacenar el hash de la variable junto con los operandos
            self.hash_table.add_hash(name, value, operands)

        # Si el valor ya ha sido definido, se puede alterar
        else:
            symbol.value = value  # Actualiza el valor de la variable
            self.hash_table.add_hash(name, value, operands)  # Actualiza el hash

    def add_reference(self, name, line):
        symbol = self.lookup(name)
        if symbol:
            symbol.add_reference(line)
        else:
            raise Exception(f"Error: '{name}' no está definido en la línea {line}.")

    def reset(self):
        self.symbols.clear()  # Limpia la tabla de símbolos
        self.hash_table = HashTable()  # Reinicia la tabla de hashes

    def __str__(self):
        # Usar PrettyTable para formatear la tabla de símbolos
        table = PrettyTable()
        table.field_names = ["Nombre de Variable", "Tipo", "Valor", "Número de Registro (loc)", "Números de Línea"]
        for s in self.symbols.values():
            table.add_row([s.name, s.type, s.value if s.value is not None else 'N/A', hex(id(s)), s.line_declared])
        return str(table)

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

        # Verificación de tipos de datos
        verificar_tipos_datos(var_name, value, line_number)

        # Solo se permite almacenar el valor inicial
        tabla_simbolos.set_value(var_name, value, operands=[str(sent[0]), var_name, value])  # Agregar operandos

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
    elif sent[0] == 'if' or sent[0] == 'do':
        for expr in sent[1:]:  # Asumiendo que todas las expresiones pueden referirse a variables
            procesar_exp(expr, line_number)

def procesar_exp(expr, line_number):
    # Aquí puedes agregar la lógica para procesar expresiones y registrar referencias
    if isinstance(expr, list):
        for elem in expr:
            if isinstance(elem, str):  # Supongamos que es un identificador
                tabla_simbolos.add_reference(elem, line_number)

def verificar_tipos_datos(var_name, value, line_number):
    symbol = tabla_simbolos.lookup(var_name)
    if not symbol:
        raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")

    # Comprobar el tipo de dato
    if symbol.type == 'int':
        if not isinstance(value, int):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un int, se recibió '{value}'.")
    elif symbol.type == 'float':
        if not isinstance(value, (int, float)):  # Permitir tanto int como float
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un float, se recibió '{value}'.")
    elif symbol.type == 'bool':
        # Asegúrate de que el valor booleano sea verdadero o falso
        if isinstance(value, str):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            else:
                raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un bool, se recibió '{value}'.")

        if not isinstance(value, bool):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un bool, se recibió '{value}'.")

def analizar_texto(texto):
    from Sintactico import analizar_sintactico  # Asegúrate de importar tu analizador sintáctico

    # Reiniciar la tabla de símbolos antes de analizar el nuevo texto
    tabla_simbolos.reset()

    arbol = analizar_sintactico(texto)
    if arbol:  # Verifica si se generó un árbol de análisis sintáctico
        try:
            analizar_semantico(arbol)
            print("Tabla de Símbolos:")
            print(tabla_simbolos)
            print("\nTabla de Hashes:")
            print(tabla_simbolos.hash_table)
        except Exception as e:
            print(e)
