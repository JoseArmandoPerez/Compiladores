import hashlib
from prettytable import PrettyTable  # Importa PrettyTable

# Clase para la tabla de hashes
import hashlib
from prettytable import PrettyTable  # Importa PrettyTable

# Clase para la tabla de hashes
class HashTable:
    def __init__(self):
        self.hashes = {}

    def add_hash(self, name, value, operands=None):
        # Calcular el hash usando SHA256
        hash_value = hashlib.sha256(str(value).encode()).hexdigest()
        
        # Si la variable ya existe en la tabla, agregamos a la lista (encadenamiento)
        if name in self.hashes:
            self.hashes[name].append({
                "hash": hash_value,
                "value": value,
                "operands": operands
            })
        else:
            # Si no existe, creamos una nueva lista para manejar las colisiones
            self.hashes[name] = [{
                "hash": hash_value,
                "value": value,
                "operands": operands
            }]

    def __str__(self):
        # Usar PrettyTable para formatear la salida
        table = PrettyTable()
        table.field_names = ["Variable", "Hash", "Valor", "Operandos"]
        
        for name, data_list in self.hashes.items():
            for data in data_list:
                operands_str = ", ".join(data["operands"]) if data["operands"] else "N/A"
                table.add_row([name, data["hash"], data["value"], operands_str])
        
        return str(table)

# Clases para la tabla de símbolos
class Symbol:
    def __init__(self, name, symbol_type, line_declared):
        self.name = name
        self.type = symbol_type
        self.value = None  # Almacena el valor en la declaración o asignación
        self.line_declared = line_declared
        self.references = []  # Lista de líneas donde se hace referencia

    def add_reference(self, line):
        if line not in self.references:
            self.references.append(line)  # Agrega la línea a las referencias

# Modificar la clase SymbolTable para que muestre las referencias
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.hash_table = HashTable()

    def add_symbol(self, name, symbol_type, line_declared):
        if name in self.symbols:
            raise Exception(f"Error: La variable '{name}' ya fue declarada en la línea {self.symbols[name].line_declared + 1} y no se puede redeclarar en la línea {line_declared + 1}.")
        else:
            self.symbols[name] = Symbol(name, symbol_type, line_declared)

    def lookup(self, var_name, line_number=None):
        if var_name in self.symbols:
            return self.symbols[var_name]
        else:
            if line_number is not None:
                raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")
            else:
                raise Exception(f"Error: '{var_name}' no está definido.")

    def lookup2(self, name):
        return self.symbols.get(name, None)

    def set_value(self, name, value, operands=None):
        symbol = self.lookup(name, None)
        if not symbol:
            raise Exception(f"Error: '{name}' no está definido.")

        # Actualiza el valor de la variable
        symbol.value = value  
        # Almacena el hash de la variable junto con los operandos
        self.hash_table.add_hash(name, value, operands)

    def add_reference(self, name, line):
        symbol = self.lookup(name, line)
        if symbol:
            symbol.add_reference(line)

    def reset(self):
        self.symbols.clear()
        self.hash_table = HashTable()

    # Mostrar referencias en la tabla de símbolos
    def __str__(self):
        table = PrettyTable()
        table.field_names = ["Nombre de Variable", "Tipo", "Valor", "Declarado en Línea", "Referencias"]
        for s in self.symbols.values():
            referencias_str = ", ".join(map(str, s.references)) if s.references else "N/A"
            table.add_row([s.name, s.type, s.value if s.value is not None else 'N/A', s.line_declared, referencias_str])
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


def verificar_variable_decl(var_name, line_number):
    if var_name not in tabla_simbolos.symbols:
        raise Exception(f"Error: La variable '{var_name}' se usa antes de ser declarada en la línea {line_number}.")

def procesar_sent(sent, line_number):
    if sent[0] == 'decl':
        procesar_decl(sent, line_number)
    elif sent[0] == 'assign':
        var_name = sent[1]
        
        # Verificar si la variable está siendo declarada antes de la asignación
        verificar_variable_decl(var_name, line_number)

        value = procesar_expresion(sent[2], line_number)  # Evaluar la expresión

        # Verificación de tipos de datos
        verificar_tipos_datos(var_name, value, line_number)

        # Almacenar el valor de la variable
        tabla_simbolos.set_value(var_name, value, operands=[str(sent[0]), var_name, str(value)])

        # Agregar referencia a la variable, que es la línea actual donde se asigna
        tabla_simbolos.add_reference(var_name, line_number)

    elif sent[0] == 'write':
        var_name = sent[1]
        symbol = tabla_simbolos.lookup(var_name, line_number)
        if not symbol:
            raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")

        # Agregar referencia a la variable
        tabla_simbolos.add_reference(var_name, line_number)

        print(f"Escribiendo valor de {var_name}: {symbol.value}")  # Imprimir valor


def procesar_expresion(expr, line_number=None):
    if isinstance(expr, list):
        # Asegúrate de que la expresión es una lista de operandos y operadores
        operadores = []
        operandos = []

        for elemento in expr:
            if elemento in ['+', '-', '*', '/']:
                operadores.append(elemento)
            else:
                # Evaluar y agregar el operando
                operandos.append(procesar_operando(elemento, line_number))

        # Realizar la evaluación de los operandos y operadores
        resultado = operandos[0]

        for i in range(len(operadores)):
            # Asegúrate de que los operandos sean del tipo correcto antes de operar
            if not isinstance(operandos[i + 1], (int, float)):
                raise Exception(f"Error: Operando inválido '{operandos[i + 1]}' en la operación '{operadores[i]}'.")
            
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
    if expr == 'true':
        return True
    elif expr == 'false':
        return False
    return expr

def procesar_operando(operand, line_number):
    # Procesa el operando: puede ser un identificador o un literal
    if isinstance(operand, str):  # Si es una variable
        return procesar_identificador(operand, line_number)  # Devuelve el valor actual de la variable
    return operand  # Retorna el valor literal directamente

def procesar_identificador(var_name, line_number):
    # Verificar que la variable está declarada antes de su uso
    simbolo = tabla_simbolos.lookup(var_name, line_number)
    if not simbolo:
        raise Exception(f"Error: Variable '{var_name}' no declarada en línea {line_number}.")
    
    # Agregar referencia a la variable
    tabla_simbolos.add_reference(var_name, line_number)

    return simbolo.value  # Retorna el valor actual de la variable

def verificar_tipos_datos(var_name, value, line_number):
    symbol = tabla_simbolos.lookup(var_name, line_number)
    if not symbol:
        raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")
    
    # Verificación del tipo de dato y el valor asignado
    if symbol.type == 'int':
        if isinstance(value, bool):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' es int, pero se asignó un valor booleano '{value}'.")
        elif isinstance(value, float):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' es int, pero se asignó un número real '{value}'.")
        elif not isinstance(value, int):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un int, se recibió '{value}'.")
    
    elif symbol.type == 'float':
        if not isinstance(value, (int, float)):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un float, se recibió '{value}'.")
    
    elif symbol.type == 'bool':
        if not isinstance(value, bool):
            raise Exception(f"Error de tipo en línea {line_number}: '{var_name}' debe ser un bool, se recibió '{value}'.")




def analizar_texto(texto):
    from Sintactico import analizar_sintactico  # Asegúrate de importar tu analizador sintáctico

    # Reiniciar la tabla de símbolos antes de analizar el nuevo texto
    tabla_simbolos.reset()

    # Ejecuta el análisis sintáctico
    arbol = analizar_sintactico(texto)

    if arbol:  # Verifica si se generó un árbol de análisis sintáctico
        try:
            analizar_semantico(arbol)  # Realiza el análisis semántico

            # En lugar de imprimir, retorna las tablas para que se manejen en la interfaz
            return tabla_simbolos, tabla_simbolos.hash_table

        except Exception as e:
            # En lugar de imprimir el error, lanzamos la excepción para que se maneje externamente
            raise Exception(f"Error semántico: {str(e)}")
    else:
        raise Exception("Error sintáctico: No se pudo generar el árbol de análisis sintáctico.")


