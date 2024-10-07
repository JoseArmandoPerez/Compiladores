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

        # Actualiza el valor de la variable
        symbol.value = value  
        # Almacenar el hash de la variable junto con los operandos
        self.hash_table.add_hash(name, value, operands)

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
        value = procesar_expresion(sent[2])  # Evaluar la expresión

        # Verificación de tipos de datos
        verificar_tipos_datos(var_name, value, line_number)

        # Almacenar el valor de la variable
        tabla_simbolos.set_value(var_name, value, operands=[str(sent[0]), var_name, str(value)])

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


def procesar_expresion(expr):
    if isinstance(expr, list):
        # Asegúrate de que la expresión es una lista de operandos y operadores
        operadores = []
        operandos = []

        for elemento in expr:
            if elemento in ['+', '-', '*', '/']:
                operadores.append(elemento)
            else:
                # Evaluar y agregar el operando
                operandos.append(procesar_operando(elemento))

        # Realizar la evaluación de los operandos y operadores
        resultado = operandos[0]

        for i in range(len(operadores)):
            if operadores[i] == '+':
                resultado += operandos[i + 1]
            elif operadores[i] == '-':
                resultado -= operandos[i + 1]
            elif operadores[i] == '*':
                resultado *= operandos[i + 1]
            elif operadores[i] == '/':
                if operandos[i + 1] == 0:
                    raise Exception("Error: División por cero.")
                resultado /= operandos[i + 1]

        return resultado  # Asegúrate de devolver solo el resultado final

    # Si es un valor literal (int, float, bool)
    return expr


def procesar_operando(operand):
    # Procesa el operando: puede ser un identificador o un literal
    if isinstance(operand, str):  # Si es una variable
        return procesar_identificador(operand)  # Devuelve el valor actual de la variable
    return operand  # Retorna el valor literal directamente

def procesar_identificador(var_name):
    # Supongamos que aquí se realiza la búsqueda en la tabla de símbolos
    simbolo = tabla_simbolos.lookup(var_name)
    if simbolo:
        return simbolo.value  # Retorna el valor asociado a la variable
    raise Exception(f"Error: '{var_name}' no está definido.")

def verificar_tipos_datos(var_name, value, line_number):
    symbol = tabla_simbolos.lookup(var_name)
    if not symbol:
        raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")

    # Comprobar el tipo de dato
    if symbol.type == 'int':
        if not isinstance(value, (int, float)):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un int, se recibió '{value}'.")
    elif symbol.type == 'float':
        if not isinstance(value, (int, float)):  # Permitir tanto int como float
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un float, se recibió '{value}'.")
    elif symbol.type == 'bool':
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
            print(tabla_simbolos)  # Imprimir la tabla de símbolos
            print("Tabla de Hashes:")
            print(tabla_simbolos.hash_table)  # Imprimir la tabla de hashes
        except Exception as e:
            print(str(e))

# Aquí llamas a analizar_texto con el código a analizar
# Ejemplo: analizar_texto("programa { ... }")
