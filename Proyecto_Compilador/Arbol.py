import tkinter as tk
from tkinter import ttk

errores = []  # Vector global para almacenar los errores
linea = 1

def evaluar_expresion(arbol, tabla_simbolos):
    global linea  # Asegurarse de que la variable global se usa correctamente
    if isinstance(arbol, tuple):
        operador = arbol[0]
        try:
            operando1 = evaluar_expresion(arbol[1], tabla_simbolos)
            operando2 = evaluar_expresion(arbol[2], tabla_simbolos)

            if operando1 is None or operando2 is None:
                errores.append(f"Error: Uno de los operandos es None. Operando1: {operando1}, Operando2: {operando2}. Operador: {operador}. En la linea: {linea}")
                return None

            if operador == '+':
                return operando1 + operando2
            elif operador == '-':
                return operando1 - operando2
            elif operador == '*':
                return operando1 * operando2
            elif operador == '/':
                if operando2 == 0:
                    errores.append(f"Error: Intento de división por cero. Linea: {linea}")
                    return None
                return operando1 / operando2
            elif operador == '^':
                return operando1 ** operando2
            elif operador == '%':
                return operando1 % operando2
            elif operador == '<':
                return operando1 < operando2
            elif operador == '>':
                return operando1 > operando2
            elif operador == '<=':
                return operando1 <= operando2
            elif operador == '>=':
                return operando1 >= operando2
            elif operador == '==':
                return operando1 == operando2
            elif operador == '!=':
                return operando1 != operando2
            else:
                errores.append(f"Error: Operador no reconocido {operador}. En la Linea: {linea}")
                return None
        except Exception as e:
            errores.append(f"Linea: {linea} Error evaluando la expresión {arbol}: {str(e)}.")
            return None
    else:
        # Manejo de valores atómicos (números y variables)
        if isinstance(arbol, (int, float)):
            return arbol
        elif isinstance(arbol, str):
            simbolo = tabla_simbolos.lookup2(arbol)
            if simbolo is not None:
                tabla_simbolos.add_reference(simbolo.name, linea)
                return simbolo.value
            else:
                errores.append(f"Error: Símbolo no encontrado en la tabla: {arbol}. En la linea: {linea}")
                return None
        else:
            errores.append(f"Error: Tipo de dato no reconocido: {type(arbol)} para el valor {arbol}. En la linea: {linea}")
            return None


def crear_arbol_sintactico(tree, arbol, tabla_simbolos, padre=""):
    global linea
    if isinstance(arbol, tuple):
        nodo_texto = arbol[0]
        if nodo_texto == "assign":
            linea += 1
            #print(f'L: {linea}: Encontro asignacion: {arbol[0]} -> {arbol[1]}= {arbol[2]}')

            var_nombre = arbol[1]
            valor = evaluar_expresion(arbol[2], tabla_simbolos)

            # Obtener el tipo de la variable desde la tabla de símbolos
            simbolo = tabla_simbolos.lookup2(var_nombre)
            if simbolo:
                tipo = simbolo.type
                # Si el tipo es 'int' y el valor es flotante, redondeamos
                if tipo == 'int' and isinstance(valor, float):
                    valor = round(valor)
            else:
                errores.append(f"Error: Simbolo no Encontrado: {var_nombre}. En la linea: {linea}")


            # Si hubo error en la evaluación, el valor será None, pero continuamos
            if valor is not None:
                tabla_simbolos.set_value(var_nombre, valor)  # Actualizamos el valor en la tabla correcta
                texto_nodo = f"{var_nombre} = {valor}"
                tabla_simbolos.add_reference(var_nombre, linea)
            else:
                texto_nodo = f"{var_nombre} = None (Error)"

        elif nodo_texto == "decl":
            linea += 1
            tipo = arbol[1]
            variables = arbol[2]
            #print(f'L: {linea}: Encontro declaracion: {arbol[0]} -> {arbol[1]} {arbol[2]}')
            for var in variables:
                if tabla_simbolos.lookup2(var):
                    errores.append(f"Error: Variable ya declarada: {var} En la Linea: {linea}")
                else:
                    tabla_simbolos.add_symbol(var, tipo, linea)  # Agregamos el símbolo en la tabla correcta
            texto_nodo = f"decl {tipo}: {', '.join(variables)}"

        elif nodo_texto == "if_else":
            linea += 1
            #print(f'L: {linea}: Encontro condicional if_else: {arbol[0]} ({arbol[1]}) bloaque 1: {arbol[2]} bloque 2: {arbol[3]} ')
            condicion = arbol[1]
            bloque_if = arbol[2]
            bloque_else = arbol[3]
            resultado_condicion = evaluar_expresion(condicion, tabla_simbolos)
            texto_nodo = f"if_else {resultado_condicion}"
            item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))

            # Agregar referencia de las variables usadas en la condición
            for var in condicion:
                if isinstance(var, str):
                    if tabla_simbolos.lookup2(var):
                        tabla_simbolos.add_reference(var, linea)

            for instruccion in bloque_if[1]:
                crear_arbol_sintactico(tree, instruccion, tabla_simbolos, item)


            for instruccion in bloque_else[1]:
                crear_arbol_sintactico(tree, instruccion, tabla_simbolos, item)
            

            return

        elif nodo_texto == "if":
            linea += 1
            #print(f'L: {linea}: Encontro condicional if: {arbol[0]} ({arbol[1]}) bloaque 1: {arbol[2]}')
            condicion = arbol[1]
            bloque = arbol[2]
            resultado_condicion = evaluar_expresion(condicion, tabla_simbolos)
            texto_nodo = f"if {resultado_condicion}"
            item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))

            # Agregar la condición como hijo
            tree.insert(item, 'end', text=str(condicion), values=("", ""))

            # Agregar el bloque
            for instruccion in bloque[1]:
                crear_arbol_sintactico(tree, instruccion, tabla_simbolos, item)
            
            return
        
        elif nodo_texto == "while":
            linea += 1
            #print(f'L: {linea}: Encontro ciclo: {arbol[0]} Condicion: {arbol[1]} bloque 1: {arbol[2]} ')
            condicion = arbol[1]
            bloque = arbol[2]
            resultado_condicion = evaluar_expresion(condicion, tabla_simbolos)
            texto_nodo = f"while {resultado_condicion}"
            item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))

            # Agregar referencia de las variables usadas en la condición
            for var in condicion:
                if isinstance(var, str):
                    if tabla_simbolos.lookup2(var):
                        tabla_simbolos.add_reference(var, linea)
            
            for instruccion in bloque[1]:
                crear_arbol_sintactico(tree, instruccion, tabla_simbolos, item)
            return
        
        elif nodo_texto == "do_while":
            linea += 1
            #print(f'L: {linea}: Encontro ciclo: {arbol[0]} bloque 1: {arbol[1]} condicion: {arbol[2]} ')
            bloque = arbol[1]
            condicion = arbol[2]
            resultado_condicion = evaluar_expresion(condicion, tabla_simbolos)
            texto_nodo = f"do_while {resultado_condicion}"
            item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))

            for instruccion in bloque[1]:
                crear_arbol_sintactico(tree, instruccion, tabla_simbolos, item)
            return
        
        elif nodo_texto == "write":
            linea += 1
            texto_nodo = f"write {arbol[1]}"
            item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))
        elif nodo_texto == "read":
            linea += 1
            texto_nodo = f"read {arbol[1]}"
            item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))
        else:
            #linea += 1
            texto_nodo = nodo_texto

        item = tree.insert(padre, 'end', text=texto_nodo, values=("", ""))
        for hijo in arbol[1:]:
            crear_arbol_sintactico(tree, hijo, tabla_simbolos, item)
    elif isinstance(arbol, list):
        for sub_arbol in arbol:
            crear_arbol_sintactico(tree, sub_arbol, tabla_simbolos, padre)
    else:
        if isinstance(arbol, str):
            tipo_valor = tabla_simbolos.lookup2(arbol)
            tipo = tipo_valor.type if tipo_valor else 'none'
            valor = tipo_valor.value if tipo_valor else 'none'
            texto_nodo = f"{arbol}"
            tree.insert(padre, 'end', text=texto_nodo, values=(tipo, valor))
        else:
            tree.insert(padre, 'end', text=str(arbol), values=("num", arbol))



# Función para mostrar la tabla de símbolos
def mostrar_tabla_simbolos(tabla_simbolos):
    # Crear ventana para la tabla de símbolos
    ventana_tabla = tk.Toplevel()
    ventana_tabla.title("Tabla de Símbolos")

    tree_frame = tk.Frame(ventana_tabla)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    columnas = ('Nombre', 'Tipo', 'Valor', 'Línea Declarada', 'Referencias')
    tree = ttk.Treeview(tree_frame, columns=columnas)
    tree.heading("#0", text="")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Tipo", text="Tipo")
    tree.heading("Valor", text="Valor")
    tree.heading("Línea Declarada", text="Línea Declarada")
    tree.heading("Referencias", text="Referencias")
    tree.column("#0", width=0)
    tree.column("Nombre", width=150)
    tree.column("Tipo", width=100)
    tree.column("Valor", width=100)
    tree.column("Línea Declarada", width=120)
    tree.column("Referencias", width=200)
    tree.pack(fill=tk.BOTH, expand=True)

    # Agregar los símbolos a la tabla
    for s in tabla_simbolos.symbols.values():
        referencias_str = ', '.join(map(str, s.references)) if s.references else 'N/A'
        tree.insert("", 'end', text="", values=(s.name, s.type, s.value if s.value is not None else 'N/A', s.line_declared, referencias_str))


# Función para visualizar el árbol
def visualizar_arbol(arbol, tabla_s):
    tabla_s.reset()
    global linea
    linea = 1
    # Crear ventana principal
    ventana = tk.Tk()
    ventana.title("Árbol Sintáctico Expandible")
    ventana.geometry("530x600")  # Ajustar el tamaño inicial de la ventana
    #ventana.attributes('-fullscreen', True)

    # Crear un Frame con un scrollbar
    main_frame = tk.Frame(ventana)
    main_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(main_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Vincular el desplazamiento del ratón al canvas
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    tree_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=tree_frame, anchor="nw")

    # Crear el árbol de vista con columnas adicionales
    columnas = ('Tipo', 'Valor')
    tree = ttk.Treeview(tree_frame, columns=columnas)
    tree.heading("#0", text="Expresión")
    tree.heading("Tipo", text="Tipo")
    tree.heading("Valor", text="Valor")
    tree.column("#0", width=300, anchor='w')
    tree.column("Tipo", width=100, anchor='center')
    tree.column("Valor", width=100, anchor='center')
    tree.pack(fill=tk.BOTH, expand=True)

    # Asegurarse de que el Treeview ocupe el alto completo
    def ajustar_alto(event):
        height = ventana.winfo_height() - 100  # Espacio para el botón
        tree.config(height=height)

    ventana.bind("<Configure>", ajustar_alto)

    # Tabla de símbolos auxiliar
    # from Semantico import tabla_simbolos
    # tabla_simbolos = TablaSimbolos()

    # Generar el árbol sintáctico
    crear_arbol_sintactico(tree, arbol, tabla_s)

    # Expandir todos los nodos automáticamente
    def expandir_nodos(item=""):
        for child in tree.get_children(item):
            tree.item(child, open=True)  # Expandir nodo
            expandir_nodos(child)  # Recursión para expandir los hijos

    expandir_nodos()  # Llamar para expandir todos los nodos

    # Botón para mostrar la tabla de símbolos
    btn_mostrar_tabla = tk.Button(ventana, text="Mostrar Tabla de Símbolos", command=lambda: mostrar_tabla_simbolos(tabla_s))
    btn_mostrar_tabla.pack(pady=10)

    # Ajustar el tamaño del árbol a la ventana
    tree_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    if errores:
        print("Errores encontrados durante la ejecución:")
        for error in errores:
            print(error)

    ventana.mainloop()

    



'''
# Ejemplo de uso
codigo_fuente = """
program { 
    int a,c;
    a = 10 + 5;
    c = a * 2;
    if (a>0){
        a = a-1;
        c = c+a;
    }
}
"""
'''


# Ejemplo de uso con la nueva gramática y correcciones:
# arbol_de_ejemplo =
''' 
('programa',
   ('decl', 'int', ['a', 'c']),
   ('assign', 'a', ('+', 10, 5)),
   ('assign', 'c', ('*', 'a', 2)),
   ('if_else', ('>', 'a', 0), ('bloque', [
       ('assign', 'a', ('+', 'a', 1)),
       ('assign', 'c', ('-', 'c', 'a'))
   ]),         ('bloque', [
       ('assign', 'a', ('-', 'a', 1)),
       ('assign', 'c', ('+', 'c', 'a'))
   ])),
   ('switch', 'a', 
       ('case', 1, ('assign', 'c', 10)),
       ('case', 2, ('assign', 'c', 20)),
       ('case', 3, ('assign', 'c', 30))
   ),
   ('for', ('decl', 'int', ['i']), 
       ('assign', 'i', 0),
       ('bloque', [
           ('assign', 'a', ('+', 'a', 'i')),
           ('assign', 'i', ('+', 'i', 1))
       ])
   )
)
'''
'''
#Arbol Funcional
arbol_de_ejemplo = ('programa',
    ('decl', 'int', ['a', 'c']),
    ('assign', 'a', ('+', 10, 5)),
    ('assign', 'c', ('*', 'a', 2)),
    ('if', ('>', 'a', 0), ('bloque', [
        ('assign', 'a', ('-', 'a', 1)),
        ('assign', 'c', ('+', 'c', 'a'))
    ]))
)
'''

'''
Arbol No Funcional
arbol_de_ejemplo = ('programa', 
    (('decl', 'int', ('a', 'c'))), 
    (('assign', 'a', ('+', 10, 5)), 
     ('assign', 'c', ('*', 'a', 2)), 
     ('if', ('>', 'a', 0), ('bloque', (
         ('assign', 'a', ('-', 'a', 1)), 
         ('assign', 'c', ('+', 'c', 'a'))
    )))
))

'''
'''
arbol_de_ejemplo = ('programa', 
  [('decl', 'int', ['a', 'c'])], 
  ('assign', 'a', ('+', '10', '5')), 
  ('assign', 'c', ('*', 'a', '2')), 
  ('if', ('>', 'a', '0'), ('bloque', [
      ('assign', 'a', ('-', 'a', '1')), 
      ('assign', 'c', ('+', 'c', 'a'))]
   ))
)
'''

'''
arbol_de_ejemplo = ('programa', 
                    [('decl', 'int', ['a', 'c'])], 
                    ('assign', 'a', ('+', '10', '5')), 
                    ('assign', 'c', ('*', 'a', '2')), 
                    ('decl', 'float', ['x', 'y']), 
                    ('assign', 'x', '0.1'), 
                    ('assign', 'y', ('+', 'x', '1.2')), 
                    ('decl', 'float', ['w']), 
                    ('assign', 'w', ('/', 'a', '3')), 
                    ('decl', 'float', ['t']), 
                    ('assign', 't', ('*', 'c', 'y')))
'''
'''                    
arbol_de_ejemplo = ('programa', 
                    [('decl', 'int', ['a', 'c'])], 
                    ('assign', 'a', ('+', 10, 5)), 
                    ('assign', 'c', ('*', 'a', 2)), 
                    ('decl', 'float', ['x', 'y']), 
                    ('assign', 'x', 0.1), 
                    ('assign', 'y', ('+', 'x', 1.2)), 
                    ('decl', 'float', ['w']), 
                    ('assign', 'w', ('/', 'a', 3)), 
                    ('decl', 'float', ['t']), 
                    ('assign', 't', ('*', 'c', 'y')))
'''
'''
arbol_de_ejemplo = ('programa', 
                    [('decl', 'int', ['x', 'y', 'z', 'suma']), 
                     ('decl', 'float', ['a', 'b', 'c'])], 
                     ('assign', 'suma', 45), ('assign', 'x', 23), 
                     ('assign', 'y', ('+', 2, ('-', 3, 1))), 
                     ('assign', 'z', ('+', 'y', 7)), 
                     ('assign', 'y', ('+', 'y', 1)), 
                     ('assign', 'a', ('+', 24.0, ('-', 4, ('/', 1, ('*', 3, ('+', 2, ('-', 34, 1))))))), 
                     ('assign', 'x', ('*', ('-', 5, 3), ('/', 8, 2))), 
                     ('assign', 'y', ('+', 5, ('-', 3, ('*', 2, ('/', 4, ('-', 7, 9)))))), 
                     ('assign', 'z', ('/', 8, ('+', 2, ('*', 15, 4)))), 
                     ('assign', 'y', 14.54), 
                     ('if', ('>', 2, 3), ('bloque', [('assign', 'y', ('+', 'a', 'b'))]), ('bloque', [('assign', 'y', 9)])), ('while', ('<', 'a', 2), ('bloque', [('assign', 'y', ('-', 'y', 1))])), ('do_while', ('bloque', [('assign', 'y', ('+', 'y', 1))]), ('<', 'y', 10)), 
                     ('write', 'x'), 
                     ('read', 'y'))
'''
'''
arbol_de_ejemplo = ('programa', 
                    [('decl', 'int', ['x', 'y', 'z', 'suma']), 
                     ('decl', 'float', ['a', 'b', 'c'])], 
                     ('assign', 'suma', 45), 
                     ('assign', 'x', 23), 
                     ('assign', 'y', ('+', 2, ('-', 3, 1))), 
                     ('assign', 'z', ('+', 'y', 7)), 
                     ('assign', 'y', ('+', 'y', 1)), 
                     ('assign', 'a', ('+', 24.0, ('-', 4, ('/', 1, ('*', 3, ('+', 2, ('-', 34, 1))))))), 
                     ('assign', 'x', ('*', ('-', 5, 3), ('/', 8, 2))), 
                     ('assign', 'y', ('+', 5, ('-', 3, ('*', 2, ('/', 4, ('-', 7, 9)))))), 
                     ('assign', 'z', ('/', 8, ('+', 2, ('*', 15, 4)))), 
                     ('assign', 'y', 14.54), 
                     ('if', ('<', 2, 3), ('bloque', [('assign', 'b', 10), ('assign', 'y', ('+', 'a', 'b'))]), ('bloque', [('assign', 'y', 9)])), ('while', ('<', 'a', 2), ('bloque', [('assign', 'y', ('-', 'y', 1))])), ('do_while', ('bloque', [('assign', 'y', ('+', 'y', 1))]), ('<', 'y', 10)), 
                     ('write', 'x'), 
                     ('read', 'y'))
'''

#arbol_de_ejemplo = ('programa', [('decl', 'int', ['x', 'y', 'z', 'suma']), ('decl', 'float', ['a', 'b', 'c'])], ('assign', 'suma', 45), ('assign', 'x', 23), ('assign', 'y', ('+', 2, ('-', 3, 1))), ('assign', 'z', ('+', 'y', 7)), ('assign', 'y', ('+', 'y', 1)), ('assign', 'a', ('+', 24.0, ('-', 4, ('/', 1, ('*', 3, ('+', 2, ('-', 34, 1))))))), ('assign', 'x', ('*', ('-', 5, 3), ('/', 8, 2))), ('assign', 'y', ('+', 5, ('-', 3, ('*', 2, ('/', 4, ('-', 7, 9)))))), ('assign', 'z', ('/', 8, ('+', 2, ('*', 15, 4)))), ('assign', 'y', 14.54), ('if', ('<', 2, 3), ('bloque', [('assign', 'b', 10), ('assign', 'y', ('+', 'a', 'b'))]), ('bloque', [('assign', 'y', 9)])), ('while', ('<', 'a', 2), ('bloque', [('assign', 'y', ('-', 'y', 1))])), ('do_while', ('bloque', [('assign', 'y', ('+', 'y', 1))]), ('<', 'y', 10)), ('write', 'x'), ('read', 'y'))
#print('Tipo de Funcional: ',type(arbol_de_ejemplo))
#visualizar_arbol(arbol_de_ejemplo)

'''
def generar_arbol(arbol):
    arbol_apl = arbol
    print('Arbol a Analizar y Desglozar:',arbol_apl)
    visualizar_arbol(arbol_apl)
    '''
