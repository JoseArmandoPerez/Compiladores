import ply.yacc as yacc
from Lexico import tokens

# Definición de reglas gramaticales
def p_programa(p):
    '''programa : PROGRAM LLAIZQ lista_decl lista_sent LLADER'''  # program {}
    p[0] = ('programa', p[3], *p[4])  # Usar * para expandir lista_sent

def p_lista_decl(p):
    '''lista_decl : lista_decl decl
                  | decl
                  | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_decl(p):
    '''decl : tipo lista_id PUNTOCOMA'''
    p[0] = ('decl', p[1], p[2])  # Retener la lista de identificadores

def p_tipo(p):
    '''tipo : INT
            | FLOAT
            | BOOL'''
    p[0] = p[1]

def p_lista_id(p):
    '''lista_id : lista_id COMA IDENTIFICADOR
                | IDENTIFICADOR'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_lista_sent(p):
    '''lista_sent : lista_sent sent
                  | sent
                  | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_sent(p):
    '''sent : sent_if
            | sent_while
            | sent_do
            | sent_read
            | sent_write
            | sent_assign
            | sent_cout
            | sent_cin
            | BREAK PUNTOCOMA
            | decl'''
    p[0] = p[1]

def p_sent_if(p):
    '''sent_if : SI PARIZQ exp_bool PARDER bloque SINO bloque
               | SI PARIZQ exp_bool PARDER bloque FI
               | SI PARIZQ exp_bool PARDER bloque'''
    if len(p) == 8:
        p[0] = ('if', p[3], ('bloque', p[5]), ('bloque', p[7]))  # Cambiar la estructura aquí
    else:
        p[0] = ('if', p[3], ('bloque', p[5]))

def p_sent_while(p):
    '''sent_while : MIENTRAS PARIZQ exp_bool PARDER bloque'''
    p[0] = ('while', p[3], ('bloque', p[5]))

def p_sent_do(p):
    '''sent_do : DO bloque MIENTRAS PARIZQ exp_bool PARDER PUNTOCOMA'''
    p[0] = ('do_while', ('bloque', p[2]), p[5])

def p_sent_read(p):
    '''sent_read : READ PARIZQ IDENTIFICADOR PARDER PUNTOCOMA'''
    p[0] = ('read', p[3])

def p_sent_write(p):
    '''sent_write : WRITE PARIZQ exp PARDER PUNTOCOMA'''
    p[0] = ('write', p[3])

def p_sent_assign(p):
    '''sent_assign : IDENTIFICADOR ASIGNAR exp PUNTOCOMA'''
    p[0] = ('assign', p[1], p[3])

def p_sent_cin(p):
    '''sent_cin : CIN PUNTOCOMA IDENTIFICADOR PUNTOCOMA'''
    p[0] = ('cin', p[3])

def p_sent_cout(p):
    '''sent_cout : COUT PARIZQ exp PARDER PUNTOCOMA'''
    p[0] = ('cout', p[3]) 

def p_bloque(p):
    '''bloque : LLAIZQ lista_sent LLADER'''
    p[0] = p[2]  # Cambiar para que solo retorne la lista de sentencias

def p_exp_bool(p):
    '''exp_bool : exp_bool OR exp_bool
                | exp_bool AND exp_bool
                | NOT exp_bool
                | exp_rel'''
    if len(p) == 4:
        p[0] = ('or', p[1], p[3]) if p[2] == '||' else ('and', p[1], p[3])
    elif len(p) == 3:
        p[0] = ('not', p[2])
    else:
        p[0] = p[1]

def p_exp_rel(p):
    '''exp_rel : exp MENORQUE exp
               | exp MAYORQUE exp
               | exp MENORIGUAL exp
               | exp MAYORIGUAL exp
               | exp IGUAL exp
               | exp DISTINTO exp'''
    p[0] = (p[2], p[1], p[3])

def p_exp(p):
    '''exp : exp SUMA exp
           | exp RESTA exp
           | exp MULT exp
           | exp DIV exp
           | exp POTENCIA exp
           | exp MODULO exp
           | factor'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_factor(p):
    '''factor : ENTERO
              | FLOTANTE
              | IDENTIFICADOR
              | CADENA
              | PARIZQ exp PARDER'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at EOF")

# Construir el analizador sintáctico
parser = yacc.yacc()

# Función para analizar sintácticamente una entrada
def analizar_sintactico(data):
    return parser.parse(data)


def formatear_arbol(arbol):
    """Función para dar formato al árbol sintáctico como cadena."""
    if isinstance(arbol, tuple):
        # Si el nodo es 'decl', tratamos de formatearlo sin corchetes adicionales
        if arbol[0] == 'decl':
            resultado = f"('{arbol[0]}', '{arbol[1]}', {formatear_arbol(arbol[2])})"
        else:
            # Convertir el nodo actual en una cadena
            resultado = f"('{arbol[0]}'"
            # Procesar cada hijo
            for hijo in arbol[1:]:
                resultado += f", {formatear_arbol(hijo)}"
            resultado += ")"
        return resultado
    elif isinstance(arbol, list):
        # Procesar cada elemento de la lista
        return "[" + ", ".join(formatear_arbol(elemento) for elemento in arbol) + "]"
    else:
        # Mantener los números como enteros o flotantes
        if isinstance(arbol, (int, float)):
            return str(arbol)  # Convertir solo a string para la salida
        return f"'{arbol}'"  # Retornar el valor simple (string)





if __name__ == '__main__':
    data = '''
program { 
int x, y, z, suma;  
float a, b, c; 
suma = 45; 
x = 23;  
y = 2 + 3 - 1; 
z = y + 7; 
y = y + 1; 
a = 24.0 + 4 - 1 / 3 * 2 + 34 - 1; 
x = (5 - 3) * (8 / 2); 
y = 5 + 3 - 2 * 4 / 7 - 9; 
z = 8 / 2 + 15 * 4; 
y = 14.54; 
if (2 > 3) {
  y = a + b; 
} 
else {
        y = 9;
}
while (a < 2){ 
        y = y - 1; 
 }
 do {
        y = y + 1; 
    } while (y < 10); 
write (x);
read (y);   
}
    '''
    arbol = analizar_sintactico(data)
    tree, _ = formatear_arbol(arbol)
    for line in tree:
        print(line)
