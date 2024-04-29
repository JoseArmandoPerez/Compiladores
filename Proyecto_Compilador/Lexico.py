import re

# Definir las palabras clave y operadores
keywords = {"int", "float", "double", "char", "string", "bool", "print", "main", "for", "while", "true", "if", "else", "void", "while", "do", "switch", "case"}
operators = {";", ")", "(", "{", "}", "+", "-", "*", "/", "%", "=", "==", "!=", ">", "<", ">=", "<=", "&&", "||", "!", "++", "--", "+=", "-=", "=", "/=", "%="}

def tokenize(text):
    tokens = []
    current_word = ""
    for char in text:
        if char.isspace() or char in operators:
            if current_word:
                if current_word in keywords:
                    tokens.append(("PALABRA RESERVADA", current_word))
                elif current_word.isdigit():
                    tokens.append(("ENTERO", current_word))
                elif re.match(r'^\d+\.\d+$', current_word):
                    tokens.append(("FLOAT", current_word))
                elif re.match(r'^\d+\.\d+[eE][+-]?\d+$', current_word):
                    tokens.append(("DOUBLE", current_word))
                elif re.match(r'^\[[^\]]+\]$', current_word):
                    tokens.append(("VECTOR", current_word))
                elif re.match(r'^\[[^\]]+\]\[[^\]]+\]$', current_word):
                    tokens.append(("MATRIZ", current_word))
                else:
                    tokens.append(("IDENTIFICADOR", current_word))
                current_word = ""
            if char in operators:
                tokens.append(("CARACTER", char))
        else:
            current_word += char
    
    # Verificar si queda una palabra al final del texto
    if current_word:
        # Utilizar una expresión regular para buscar "case" seguido de uno o más dígitos
        match = re.match(r'\bcase\s+\d+\b', current_word)
        if match:
            tokens.append(("PALABRA RESERVADA", match.group(0)))  # Agregar "case" y el número como palabra reservada
        elif current_word in keywords:
            tokens.append(("PALABRA RESERVADA", current_word))
        elif current_word.isdigit():
            tokens.append(("ENTERO", current_word))  # Agregar el número como un entero si es un dígito
        elif re.match(r'^\d+\.\d+$', current_word):
            tokens.append(("FLOAT", current_word))  # Agregar el número como un float si tiene un punto decimal
        elif re.match(r'^\d+\.\d+[eE][+-]?\d+$', current_word):
            tokens.append(("DOUBLE", current_word))  # Agregar el número como un double si tiene notación científica
        elif re.match(r'^\[[^\]]+\]$', current_word):
            tokens.append(("VECTOR", current_word))  # Agregar como vector si está entre corchetes
        elif re.match(r'^\[[^\]]+\]\[[^\]]+\]$', current_word):
            tokens.append(("MATRIZ", current_word))  # Agregar como matriz si está entre dos pares de corchetes
        else:
            tokens.append(("IDENTIFICADOR", current_word))

    # Buscar la combinación "if else" y tratarla como una palabra reservada
    text = " ".join([token[1] for token in tokens])
    for match in re.finditer(r'\bif\s+else\b', text):
        start = match.start()
        end = match.end()
        tokens.append(("PALABRA RESERVADA", text[start:end]))

    return tokens
