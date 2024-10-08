import ply.lex as lex

# resultado del análisis
resultado_lexema = []

reservada = (
    'INCLUDE',
    'USING',
    'NAMESPACE',
    'STD',
    'COUT',
    'CIN',
    'GET',
    'CADENA',
    'RETURN',
    'VOID',
    'INT',
    'FLOAT',
    'BOOL',
    'ENDL',
    'PROGRAM',
    'WRITE',
    'READ',
    'DO',
    'BREAK',
    'IF',
    'ELSE',   # Agrega ELSE como palabra reservada
    'WHILE',
    'FOR',
)
tokens = reservada + (
    'IDENTIFICADOR',
    'ENTERO',
    'FLOTANTE',
    'ASIGNAR',
    'SUMA',
    'RESTA',
    'MULT',
    'DIV',
    'POTENCIA',
    'MODULO',
    'MINUSMINUS',
    'PLUSPLUS',
    'SI',
    'SINO',
    'MIENTRAS',
    'PARA',
    'AND',
    'OR',
    'NOT',
    'MENORQUE',
    'MENORIGUAL',
    'MAYORQUE',
    'MAYORIGUAL',
    'IGUAL',
    'DISTINTO',
    'NUMERAL',
    'PARIZQ',
    'PARDER',
    'CORIZQ',
    'CORDER',
    'LLAIZQ',
    'LLADER',
    'PUNTOCOMA',
    'COMA',
    'COMDOB',
    'MAYORDER',
    'MAYORIZQ',
    'FI',     # Agrega FI como un token
)

# Reglas de Expresiones Regulares para tokens de Contexto simple
t_SUMA = r'\+'
t_RESTA = r'-'
t_MINUSMINUS = r'\-\-'
t_MULT = r'\*'
t_DIV = r'/'
t_MODULO = r'\%'
t_POTENCIA = r'(\*{2}|\^)'
t_ASIGNAR = r'='
t_AND = r'\&\&'
t_OR = r'\|{2}'
t_NOT = r'\!'
t_MENORQUE = r'<'
t_MAYORQUE = r'>'
t_PUNTOCOMA = r';'
t_COMA = r','
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_CORIZQ = r'\['
t_CORDER = r'\]'
t_LLAIZQ = r'{'
t_LLADER = r'}'
t_COMDOB = r'\"'

def t_INCLUDE(t):
    r'include'
    return t

def t_USING(t):
    r'using'
    return t

def t_NAMESPACE(t):
    r'namespace'
    return t

def t_STD(t):
    r'std'
    return t

def t_COUT(t):
    r'cout'
    return t

def t_CIN(t):
    r'cin'
    return t

def t_GET(t):
    r'get'
    return t

def t_ENDL(t):
    r'endl'
    return t

def t_SINO(t):
    r'else'
    return t

def t_SI(t):
    r'if'
    return t

def t_RETURN(t):
    r'return'
    return t

def t_VOID(t):
    r'void'
    return t

def t_INT(t):
    r'int'
    return t

def t_FLOAT(t):
    r'float'
    return t

def t_BOOL(t):
    r'bool'
    return t

def t_PROGRAM(t):
    r'program'
    return t

def t_WRITE(t):
    r'write'
    return t

def t_READ(t):
    r'read'
    return t

def t_DO(t):
    r'do'
    return t

def t_BREAK(t):
    r'break'
    return t

def t_MIENTRAS(t):
    r'while'
    return t

def t_PARA(t):
    r'for'
    return t

def t_FLOTANTE(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFICADOR(t):
    r'\w+(_\d\w)*'
    return t

def t_CADENA(t):
    r'\"?(\w+ \ *\w*\d* \ *)\"?'
    return t

def t_NUMERAL(t):
    r'\#'
    return t

def t_PLUSPLUS(t):
    r'\+\+'
    return t

def t_MENORIGUAL(t):
    r'<='
    return t

def t_MAYORIGUAL(t):
    r'>='
    return t

def t_IGUAL(t):
    r'=='
    return t

def t_MAYORDER(t):
    r'<<'
    return t

def t_MAYORIZQ(t):
    r'>>'
    return t

def t_DISTINTO(t):
    r'!='
    return t

def t_FI(t):
    r'fi'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comments(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

def t_comments_ONELine(t):
    r'\/\/(.)*\n'
    t.lexer.lineno += 1

t_ignore = ' \t'

def t_error(t):
    global resultado_lexema
    estado = "** Token no válido en la Línea {:4} Valor {:16} Posición {:4}".format(
        str(t.lineno), str(t.value), str(t.lexpos)
    )
    resultado_lexema.append(estado)
    t.lexer.skip(1)

# Prueba de ingreso
def prueba(data):
    global resultado_lexema

    analizador = lex.lex()
    analizador.input(data)

    resultado_lexema.clear()
    while True:
        tok = analizador.token()
        if not tok:
            break
        estado = "Línea {:4} Tipo {:16} Valor {:16} Posición {:4}".format(
            str(tok.lineno), str(tok.type), str(tok.value), str(tok.lexpos)
        )
        resultado_lexema.append(estado)
    return resultado_lexema

# Instanciamos el analizador léxico
analizador = lex.lex()

if __name__ == '__main__':
    while True:
        data = input("Ingrese un programa: ")
        prueba(data)
        print(resultado_lexema)
