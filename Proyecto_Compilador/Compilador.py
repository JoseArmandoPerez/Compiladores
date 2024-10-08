import ast
import sys
import io
import tkinter as tk
from tkinter import ttk, filedialog
import re
import Lexico
from tabulate import tabulate
import Sintactico
import Sintactico2
from Semantico import analizar_texto
from Semantico import tabla_simbolos
import Arbol

# Clase personalizada para redirigir stdout y stderr
class RedirectText(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.config(state='normal')
        if "Error" in message or "error" in message:  # Verifica si el mensaje contiene "Error"
            self.text_widget.insert('end', message, 'error')  # Aplica el estilo 'error'
        else:
            self.text_widget.insert('end', message)
        self.text_widget.see('end')
        self.text_widget.config(state='disabled')

    def flush(self):
        pass


# Función para redirigir stdout y stderr a la pestaña de errores
def setup_output_redirection():
    redirect_text = RedirectText(error_text)
    sys.stdout = redirect_text  # Redirige stdout a error_text
    sys.stderr = redirect_text  # Redirige stderr a error_text



# Definir las palabras clave y operadores
keywords = {"int", "float", "double", "char", "string", "bool", "print", "main", "for", "while", "true", "if", "void", "while", "do", "switch", "case"}
operators = {";", ")", "(", "{", "}", "+", "-", "*", "/", "%", "=", "==", "!=", ">", "<", ">=", "<=", "&&", "||", "!", "++", "--", "+=", "-=", "=", "/=", "%="}

# Función para resaltar las palabras clave y operadores
def highlight(event=None):
    text = text_entry.get("1.0", "end-1c")
    text_entry.tag_remove("keyword", "1.0", "end")
    text_entry.tag_remove("operator", "1.0", "end")
    
    for word in text.split():
        if word in keywords:
            start = "1.0"
            while True:
                pos = text_entry.search(word, start, stopindex="end")
                if not pos:
                    break
                end = f"{pos}+{len(word)}c"
                text_entry.tag_add("keyword", pos, end)
                start = end
        elif any(char in operators for char in word):
            start = "1.0"
            while True:
                for char in word:
                    if char in operators:
                        pos = text_entry.search(char, start, stopindex="end")
                        end = f"{pos}+1c"
                        text_entry.tag_add("operator", pos, end)
                        start = end
                start = f"{start}+1c"
                pos = text_entry.search(word, start, stopindex="end")
                if not pos:
                    break
                start = pos
    
    for match in re.finditer(r'\belse\b', text):
        start = "1.0 +{}c".format(match.start())
        end = "1.0 +{}c".format(match.end())
        text_entry.tag_add("red_keyword", start, end)
    
    for match in re.finditer(r'\bcase\s+(\d+)\b', text):
        start = f"1.0 +{match.start(1)}c"
        end = f"1.0 +{match.end(1)}c"
        text_entry.tag_add("purple_number", start, end)
        
# Actualizar números de línea
    update_line_numbers()

def update_line_numbers():
    line_count = int(text_entry.index('end-1c').split('.')[0])  # Contar líneas
    line_numbers = '\n'.join(str(i) for i in range(1, line_count + 1))  # Crear texto de números de línea
    line_number_canvas.delete('all')  # Limpiar el canvas
    line_number_canvas.create_text(5, 5, anchor='nw', text=line_numbers, font=('Courier', 10), fill='gray')  # Insertar números de línea

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "r") as file:
            text = file.read()
            text_entry.delete("1.0", "end")
            text_entry.insert("1.0", text)
            highlight()

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        with open(file_path, "w") as file:
            text = text_entry.get("1.0", "end-1c")
            file.write(text)

def save_as_file():
    file_path = filedialog.asksaveasfilename()
    if file_path:
        with open(file_path, "w") as file:
            text = text_entry.get("1.0", "end-1c")
            file.write(text)

def analyze_lexical():
    text = text_entry.get("1.0", "end-1c")
    lexical_result = Lexico.prueba(text)
    
    table = [["Linea", "Tipo", "Valor", "Posicion"]]
    for item in lexical_result:
        parts = item.split()
        table.append([parts[1], parts[3], parts[5], parts[7]])
    
    table_text = tabulate(table, headers="firstrow", tablefmt="plain")
    
    result_text_lexical.config(state="normal")
    result_text_lexical.delete("1.0", "end")
    result_text_lexical.insert("1.0", table_text)
    result_text_lexical.config(state="disabled")

'''
def analyze_syntactic():
    text = text_entry.get("1.0", "end-1c")
    result = Sintactico.parser.parse(text, lexer=Lexico.analizador)
    
    if result:
        tree, _ = Sintactico.formatear_arbol(result)
        tree_text = "\n".join(tree)
    else:
        tree_text = "Errores en el análisis sintáctico."

    result_text_syntax.config(state="normal")
    result_text_syntax.delete("1.0", "end")
    result_text_syntax.insert("1.0", tree_text)
    result_text_syntax.config(state="disabled")
'''

def analyze_syntactic():
    text = text_entry.get("1.0", "end-1c")
    result = Sintactico.parser.parse(text, lexer=Lexico.analizador)
    
    if result:
        tree = Sintactico2.formatear_arbol(result)
        #tree_text = "\n".join(tree)
        tree_text = tree
    else:
        tree_text = "Errores en el análisis sintáctico."

    result_text_syntax.config(state="normal")
    result_text_syntax.delete("1.0", "end")
    result_text_syntax.insert("1.0", tree_text)
    result_text_syntax.config(state="disabled")

def analyze_semantic():
    # Obtener el texto del widget de entrada
    text = text_entry.get("1.0", "end-1c")

    # Limpiar las áreas de errores y resultados semánticos antes de realizar el análisis
    error_text.config(state="normal")
    error_text.delete("1.0", "end")
    error_text.config(state="disabled")

    result_text_semantic.config(state="normal")
    result_text_semantic.delete("1.0", "end")
    result_text_semantic.config(state="disabled")

    # Crear instancias de RedirectText para capturar stdout y stderr
    redirect_stdout = RedirectText(error_text)
    redirect_stderr = RedirectText(error_text)

    # Guardar las referencias originales de stdout y stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        # Redirigir stdout y stderr
        sys.stdout = redirect_stdout
        sys.stderr = redirect_stderr

        print("Iniciando análisis semántico...")

        # Llama a la función analizar_texto y maneja el retorno de tablas
        tabla_simbolos, tabla_hashes = analizar_texto(text)

        # Mostrar el mensaje de éxito si no hay errores
        result_text_semantic.config(state="normal")
        result_text_semantic.insert("1.0", "Análisis semántico completado sin errores.\n\n")
        result_text_semantic.insert("end", "Tabla de Símbolos:\n")
        result_text_semantic.insert("end", str(tabla_simbolos) + "\n\n")
        result_text_semantic.insert("end", "Tabla de Hashes:\n")
        result_text_semantic.insert("end", str(tabla_hashes))
        result_text_semantic.config(state="disabled")

    except Exception as e:
        # Mostrar cualquier error que ocurra en el análisis semántico
        error_text.config(state="normal")
        error_text.insert("end", f"{str(e)}\n")
        error_text.config(state="disabled")

    finally:
        # Restaurar stdout y stderr a sus valores originales
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def generate_intermediate_code():
    # Placeholder para generación de código intermedio
    intermediate_code = "Código intermedio generado: No implementado aún."
    
    result_text_intermediate_code.config(state="normal")
    result_text_intermediate_code.delete("1.0", "end")
    result_text_intermediate_code.insert("1.0", intermediate_code)
    result_text_intermediate_code.config(state="disabled")

def generar_arbol_anotado():
    #Aqui esta lo necesario para generar el arbol.
    text = text_entry.get("1.0", "end-1c")
    result = Sintactico2.parser.parse(text, lexer=Lexico.analizador)
    
    if result:
        tree = Sintactico2.formatear_arbol(result)
        #print('Este es el arbol que voy a enviar:',tree)
        #print('Este es el tipo de arbol:',type(tree))  # Verifica el tipo del árbol en general
        #Arbol.generar_arbol(tree)

        # Convierte tree de str a tupla
        try:
            tree_tupla = ast.literal_eval(tree)  # Convierte la cadena a una tupla
        except Exception as e:
            print(f"Error al convertir a tupla: {e}")
            return
        
        #print('Voy a enviar un arbol de tipo: ',type(tree_tupla))
        #print("Arbol que voy a enviar: ",tree_tupla)
        Arbol.visualizar_arbol(tree_tupla, tabla_simbolos)

        # Obtener la tabla de símbolos directamente
        symbols_table_str = str(tabla_simbolos)  # Convertir a string
        print('Tabla de Simbolos despues de Arbol:', symbols_table_str)
        
        # Mostrar la tabla de símbolos en el widget de resultados semánticos
        result_text_semantic.config(state="normal")
        result_text_semantic.delete("1.0", "end")
        result_text_semantic.insert("1.0", symbols_table_str)
        result_text_semantic.config(state="disabled")

def analyze_both():
    analyze_lexical()
    analyze_syntactic()

root = tk.Tk()
root.title("Editor de Código")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Archivo", menu=file_menu)
file_menu.add_command(label="Abrir", command=open_file)
file_menu.add_command(label="Guardar", command=save_file)
file_menu.add_command(label="Guardar como", command=save_as_file)

compile_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Compilar", menu=compile_menu)
compile_menu.add_command(label="Analizar léxico", command=analyze_lexical)
compile_menu.add_command(label="Analizar sintáctico", command=analyze_syntactic)
compile_menu.add_command(label="Analizar semántico", command=analyze_semantic)
compile_menu.add_command(label="Generar código intermedio", command=generate_intermediate_code)
compile_menu.add_command(label="Analizar ambos", command=analyze_both)
compile_menu.add_command(label="Generar Arbol Semantico", command=generar_arbol_anotado)

left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="both", expand=True)

right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True)

text_frame = tk.Frame(left_frame)
text_frame.pack(side="left", fill="both", expand=True)

line_number_canvas = tk.Canvas(text_frame, width=30, bg='white', highlightthickness=0)
line_number_canvas.pack(side="left", fill="y")

text_entry = tk.Text(left_frame, wrap="word", width=60, height=20)
text_entry.pack(side="left", expand=True, fill="both")

text_entry.tag_config("keyword", foreground="blue")
text_entry.tag_config("red_keyword", foreground="red")
text_entry.tag_config("operator", foreground="red")
text_entry.tag_config("purple_number", foreground="purple")

text_entry.bind("<KeyRelease>", highlight)

top_right_frame = tk.Frame(right_frame)
top_right_frame.pack(side="top", fill="both", expand=True)

bottom_right_frame = tk.Frame(right_frame)
bottom_right_frame.pack(side="bottom", fill="both", expand=True)

analyzer_notebook = ttk.Notebook(top_right_frame)

lexical_tab = ttk.Frame(analyzer_notebook)
analyzer_notebook.add(lexical_tab, text="Analizador Léxico")

syntax_tab = ttk.Frame(analyzer_notebook)
analyzer_notebook.add(syntax_tab, text="Analizador Sintáctico")

semantic_tab = ttk.Frame(analyzer_notebook)
analyzer_notebook.add(semantic_tab, text="Análisis Semántico")

intermediate_code_tab = ttk.Frame(analyzer_notebook)
analyzer_notebook.add(intermediate_code_tab, text="Código Intermedio")

analyzer_notebook.pack(expand=True, fill="both")

result_text_lexical = tk.Text(lexical_tab, state="disabled")
result_text_lexical.pack(expand=True, fill="both")

result_text_syntax = tk.Text(syntax_tab, state="disabled")
result_text_syntax.pack(expand=True, fill="both")

result_text_semantic = tk.Text(semantic_tab, state="disabled")
result_text_semantic.pack(expand=True, fill="both")

result_text_intermediate_code = tk.Text(intermediate_code_tab, state="disabled")
result_text_intermediate_code.pack(expand=True, fill="both")

error_notebook = ttk.Notebook(bottom_right_frame)

error_tab = ttk.Frame(error_notebook)
error_notebook.add(error_tab, text="Errores")

result_tab = ttk.Frame(error_notebook)
error_notebook.add(result_tab, text="Resultado")

error_notebook.pack(expand=True, fill="both")

error_text = tk.Text(error_tab)
error_text.pack(expand=True, fill="both")

result_text = tk.Text(result_tab, state="disabled")
result_text.pack(expand=True, fill="both")

error_text.tag_config('error', foreground='red')  # Configurar el tag para el estilo de error en rojo
setup_output_redirection()

highlight()

root.mainloop()
