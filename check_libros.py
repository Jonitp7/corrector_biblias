import fitz  # PyMuPDF para extraer información detallada
import re    # Para encontrar números en el texto
import time  # Para simular carga
import unicodedata  # Para normalizar texto

def normalizar_texto(texto):
    """Convierte texto a minúsculas y elimina tildes."""
    texto = texto.lower()  # Convertir a minúsculas
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )

def check_bible_books(pdf_path, versiculo_inicio, update_ui=None):
    try:
        if update_ui:
            update_ui("Cargando... Por favor, espere.\n")
        time.sleep(1)  # Simula un pequeño tiempo de carga
        
        doc = fitz.open(pdf_path)
        incidents = []
        number_format = None
        size_tolerance = 3  # Margen de tolerancia para el tamaño de fuente
        
        for page_number in range(len(doc)):
            page = doc[page_number]
            text_info = page.get_text("dict")
            found_creation = None  # Inicializamos en cada página
            numbers = []
            
            for block in text_info.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        font_size = span["size"]
                        font_name = span["font"]
                        color = span["color"]
                        x_position = span["origin"][0]
                        y_position = span["origin"][1]
                        
                        # Normalizar texto para comparar correctamente "La Creación"
                        if normalizar_texto(text) == "la creacion":
                            found_creation = y_position
                        
                        # Verificar si encontramos un "1" debajo de "La Creación"
                        if text == "1" and found_creation is not None and y_position > found_creation:
                            numbers.append((text, y_position, font_size, font_name, color))
            
            if numbers:
                numbers.sort(key=lambda x: -x[2])  # Ordenar por tamaño de fuente descendente
                top_number = numbers[0]  # El número más grande
                number_format = {"size": top_number[2], "font": top_number[3], "color": top_number[4]}
                
                if update_ui:
                    update_ui(f"Página {page_number + 1}: Detectado '1' con formato {number_format}\n")
                
                break  # Solo necesitamos el formato del primer número encontrado
        
        if number_format is None:
            incidents.append("No se encontró el número 1 debajo de 'La Creación' en ninguna página.")
        else:
            if update_ui:
                update_ui("Buscando números con el mismo formato en todo el documento...\n")
            
            for page_number in range(len(doc)):
                page = doc[page_number]
                text_info = page.get_text("dict")
                found_numbers = []
                
                for block in text_info.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            font_size = span["size"]
                            font_name = span["font"]
                            color = span["color"]
                            y_position = span["origin"][1]
                            
                            # Aplicar tolerancia en comparación del tamaño de fuente
                            if (text.isdigit() and 
                                abs(font_size - number_format["size"]) <= size_tolerance and 
                                font_name == number_format["font"] and 
                                color == number_format["color"]):
                                found_numbers.append((text, y_position))
                
                if not found_numbers:
                    incidents.append(f"Página {page_number + 1}: No se encontraron números con el formato esperado.")
                else:
                    found_numbers.sort(key=lambda x: x[1])  # Ordenar por posición vertical
                    if update_ui:
                        update_ui(f"Página {page_number + 1}: Números detectados {found_numbers}\n")
        
        if update_ui:
            update_ui("Proceso completado.\n")
        
        return incidents

    except Exception as e:
        if update_ui:
            update_ui(f"Error al procesar el PDF: {e}\n")
        return []
