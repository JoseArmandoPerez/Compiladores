import ply.yacc as yacc
from Lexico import tokens

# Definición de reglas gramaticales
def p_programa(p):
    '''programa : PROGRAM LLAIZQ lista_decl lista_sent LLADER''' # program {}
    p[0] = ('programa', p[3], p[4])

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
    p[0] = ('decl', p[1], p[2])

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
            | BREAK PUNTOCOMA
            | decl'''
    p[0] = p[1]

def p_sent_if(p):
    '''sent_if : SI PARIZQ exp_bool PARDER bloque SINO bloque
               | SI PARIZQ exp_bool PARDER bloque FI
               | SI PARIZQ exp_bool PARDER bloque'''
    if len(p) == 8:
        p[0] = ('if_else', p[3], p[5], p[7])
    else:
        p[0] = ('if', p[3], p[5])

def p_sent_while(p):
    '''sent_while : MIENTRAS PARIZQ exp_bool PARDER bloque'''
    p[0] = ('while', p[3], p[5])

def p_sent_do(p):
    '''sent_do : DO bloque MIENTRAS PARIZQ exp_bool PARDER PUNTOCOMA'''
    p[0] = ('do_while', p[2], p[5])

def p_sent_read(p):
    '''sent_read : READ PARIZQ IDENTIFICADOR PARDER PUNTOCOMA'''
    p[0] = ('read', p[3])

def p_sent_write(p):
    '''sent_write : WRITE PARIZQ exp PARDER PUNTOCOMA'''
    p[0] = ('write', p[3])

def p_sent_assign(p):
    '''sent_assign : IDENTIFICADOR ASIGNAR exp PUNTOCOMA'''
    p[0] = ('assign', p[1], p[3])

def p_bloque(p):
    '''bloque : LLAIZQ lista_sent LLADER'''
    p[0] = ('bloque', p[2])

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

# Función para formatear el árbol de análisis
def formatear_arbol(arbol, nivel=0, order=1):
    if isinstance(arbol, tuple):
        resultado = [" " * nivel + f"{order}. {arbol[0]}"]
        sub_orders = []
        for hijo in arbol[1:]:
            sub_orders.append(order)
            sub_tree, order = formatear_arbol(hijo, nivel + 2, order + 1)
            resultado.extend(sub_tree)
        resultado.extend([f"  {' ' * nivel}{'  '.join([str(o) for o in sub_orders])}"])
        return resultado, order
    else:
        return [" " * nivel + str(arbol)], order

if __name__ == '__main__':
    data = '''
    program {
        int x, y;
        float a, b;
        bool c;
        c = false;
        x=5; 
        y=4; 
        a=0.0;
        b=3.0;
        do {
            if(x<y && y>=0) {
                c=true;
            } else {
                x=x-2;
                a=a*x+b;
                y=y-1;
            }
        } while(c == true);
        write (a);
        a=a+1.0;
        x=a-y;
    }
    '''
    arbol = analizar_sintactico(data)
    tree, _ = formatear_arbol(arbol)
    for line in tree:
        print(line)
