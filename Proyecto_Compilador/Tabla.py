import hashlib
from prettytable import PrettyTable  # Importa PrettyTable

errores_semanticos=[]

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
       # if line not in self.references:
            self.references.append(line)  # Agrega la línea a las referencias

# Modificar la clase SymbolTable para que muestre las referencias
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.hash_table = HashTable()

    def add_symbol(self, name, symbol_type, line_declared):
        if name in self.symbols:
            errores_semanticos.append(f"Error: La variable '{name}' ya fue declarada en la línea {self.symbols[name].line_declared + 1} y no se puede redeclarar en la línea {line_declared + 1}.")
            #raise Exception(f"Error: La variable '{name}' ya fue declarada en la línea {self.symbols[name].line_declared + 1} y no se puede redeclarar en la línea {line_declared + 1}.")
        else:
            self.symbols[name] = Symbol(name, symbol_type, line_declared)
        #print(tabla_simbolos)

    def lookup(self, var_name, line_number=None):
        if var_name in self.symbols:
            return self.symbols[var_name]
        else:
            if line_number is not None:
                errores_semanticos.append(f"Error: '{var_name}' no está definido en la línea {line_number}.")
                #raise Exception(f"Error: '{var_name}' no está definido en la línea {line_number}.")
            else:
                errores_semanticos.append(f"Error: '{var_name}' no está definido.")
                #raise Exception(f"Error: '{var_name}' no está definido.")

    def lookup2(self, name):
        return self.symbols.get(name, None)

    def set_value(self, name, value, operands=None):
        symbol = self.lookup(name, None)
        if symbol:
            # Actualiza el valor de la variable
            symbol.value = value  
            # Almacena el hash de la variable junto con los operandos
            self.hash_table.add_hash(name, value, operands)
            #print(tabla_simbolos)
        else:
            errores_semanticos.append(f"Error: '{name}' no está definido.")
            #raise Exception(f"Error: '{name}' no está definido.")
            #symbol.value = 'Na'
            #self.hash_table.add_hash(name, None, operands)

    def add_reference(self, name, line):
        symbol = self.lookup(name, line)
        if symbol:
            symbol.add_reference(line)
        #print(tabla_simbolos)

    def reset(self):
        self.symbols.clear()
        self.hash_table = HashTable()

    # Mostrar referencias en la tabla de símbolos
    def __str__(self):
        table = PrettyTable()
        table.field_names = ["Nombre de Variable", "Tipo", "Valor", "DeclLínea", "Referencias"]

        # Limitar el ancho de las columnas
        table.max_width["Nombre de Variable"] = 15
        table.max_width["Tipo"] = 8
        table.max_width["Valor"] = 10
        table.max_width["Decl Línea"] = 15
        table.max_width["Referencias"] = 40 # Mantener ancho amplio para evitar truncamiento
        
        for s in self.symbols.values():
            referencias_str = ", ".join(map(str, s.references)) if s.references else 'N/A'
            table.add_row([
                s.name[:15],  # Limitar el nombre de la variable a 15 caracteres
                s.type,
                s.value if s.value is not None else 'N/A',
                s.line_declared,
                referencias_str  # Mostrar todas las referencias sin truncar
            ])
        
        return str(table)
# Inicializa la tabla de símbolos
tabla_simbolos = SymbolTable()


