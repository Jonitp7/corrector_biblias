from tkinter import *
import check_paginacion  # Importamos la funcionalidad
import check_libros  # Nueva funcionalidad para comprobar libros

# Variable global para el archivo PDF
pdf_file = "biblia_prueba2.pdf"

def update_ui(text):
    """Actualiza la interfaz gráfica con mensajes de estado."""
    result_text.insert(END, text)
    result_text.see(END)
    ventana.update_idletasks()

def mostrar_paginacion():
    """Muestra la pantalla de Comprobación de Paginación."""
    limpiar_pantalla()
    
    Label(ventana, text="Comprobar Paginación", font=("Arial", 16, "bold")).pack(pady=10)

    Label(ventana, text="Seleccione la ubicación del número de paginación:").pack()
    Radiobutton(ventana, text="Arriba Centrado", variable=alignment_var, value="top_center").pack()
    Radiobutton(ventana, text="Arriba Lateral", variable=alignment_var, value="top_lateral").pack()
    Radiobutton(ventana, text="Abajo Centrado", variable=alignment_var, value="bottom_center").pack()
    Radiobutton(ventana, text="Abajo Lateral", variable=alignment_var, value="bottom_lateral").pack()

    Label(ventana, text="¿En qué número empieza la paginación?").pack()
    input_num.pack()
    
    Label(ventana, text="¿La paginación empieza en la primera o segunda página?").pack()
    start_page_option.set("primera")
    Radiobutton(ventana, text="Primera Página", variable=start_page_option, value="primera").pack()
    Radiobutton(ventana, text="Segunda Página", variable=start_page_option, value="segunda").pack()

    btn_start.config(command=comprobar_paginacion, text="Comprobar Paginación")
    btn_start.pack(pady=10)

    # Área de texto con scroll para mostrar resultados
    agregar_area_resultados()

    # Botón de Volver SIEMPRE visible
    agregar_boton_volver()

def comprobar_paginacion():
    """Función para comprobar la paginación."""
    alignment = alignment_var.get()
    start_page_choice = start_page_option.get()
    try:
        start_page = int(input_num.get())  # Convertir a número
    except ValueError:
        result_text.delete(1.0, END)
        result_text.insert(END, "Error: Ingresa un número válido para la paginación inicial.\n")
        return
    
    result_text.delete(1.0, END)  # Limpiar resultados anteriores
    incidents = check_paginacion.check_page_numbers(pdf_file, alignment, start_page, start_page_choice, update_ui)
    
    if incidents:
        result_text.insert(END, "Páginas con incidencias:\n")
        for expected_page, pdf_page, issue in incidents:
            result_text.insert(END, f"Página esperada {expected_page} (PDF: {pdf_page}): {issue}\n")
    else:
        result_text.insert(END, "Todas las páginas tienen numeración correcta.\n")

def mostrar_libros():
    """Muestra la pantalla de Comprobación de Libros."""
    limpiar_pantalla()
    
    Label(ventana, text="Comprobar Libros", font=("Arial", 16, "bold")).pack(pady=10)
    
    Label(ventana, text="¿El capítulo comienza con el número de versículo 1?").pack()
    versiculo_inicio_var.set("si")
    Radiobutton(ventana, text="Sí", variable=versiculo_inicio_var, value="si").pack()
    Radiobutton(ventana, text="No", variable=versiculo_inicio_var, value="no").pack()
    
    btn_check_libros.config(command=comprobar_libros, text="Comprobar Libros")
    btn_check_libros.pack(pady=10)
    
    # Área de texto con scroll para mostrar resultados
    agregar_area_resultados()

    # Botón de Volver SIEMPRE visible
    agregar_boton_volver()

def comprobar_libros():
    """Función para comprobar los libros de la Biblia."""
    versiculo_inicio = versiculo_inicio_var.get()
    result_text.delete(1.0, END)  # Limpiar resultados anteriores
    incidents = check_libros.check_bible_books(pdf_file, versiculo_inicio, update_ui)
    
    """
    if incidents:
        result_text.insert(END, "Libros con incidencias:\n")
        for issue in incidents:
            result_text.insert(END, f"{issue}\n")
    else:
        result_text.insert(END, "Todos los libros están correctos.\n")
    """
def agregar_area_resultados():
    """Agrega la caja de texto con scroll para mostrar resultados."""
    frame_result = Frame(ventana)
    frame_result.pack(pady=10, fill=BOTH, expand=True)

    scrollbar = Scrollbar(frame_result)
    scrollbar.pack(side=RIGHT, fill=Y)

    global result_text
    result_text = Text(frame_result, height=15, width=100, yscrollcommand=scrollbar.set)
    result_text.pack(fill=BOTH, expand=True)

    scrollbar.config(command=result_text.yview)

def agregar_boton_volver():
    """Agrega el botón de volver, asegurando que siempre esté visible."""
    btn_volver = Button(ventana, text="Volver", font=("Arial", 12), command=pantalla_principal)
    btn_volver.pack(side=BOTTOM, fill=X, pady=10)

def limpiar_pantalla():
    """Elimina todos los widgets de la pantalla para mostrar una nueva vista."""
    for widget in ventana.winfo_children():
        widget.pack_forget()

def pantalla_principal():
    """Muestra la pantalla principal con las opciones en rectángulos."""
    limpiar_pantalla()

    Label(ventana, text="Asistente de Corrección", font=("Arial", 18, "bold")).pack(pady=20)

    # Botón de Comprobación de Paginación
    btn_paginacion = Button(ventana, text="Comprobar Paginación", font=("Arial", 12), height=2, width=20, command=mostrar_paginacion)
    btn_paginacion.pack(pady=10)
    
    # Botón de Comprobación de Libros
    btn_libros = Button(ventana, text="Comprobar Libros", font=("Arial", 12), height=2, width=20, command=mostrar_libros)
    btn_libros.pack(pady=10)

# Configuración de la ventana principal
ventana = Tk()
ventana.title("Asistente de Corrección")
ventana.geometry("1200x800")

# Variables globales
alignment_var = StringVar(value="top_center")
start_page_option = StringVar(value="primera")
versiculo_inicio_var = StringVar(value="si")
input_num = Entry(ventana)
btn_start = Button(ventana)
btn_check_libros = Button(ventana)

# Mostrar la pantalla principal al inicio
pantalla_principal()

ventana.mainloop()
