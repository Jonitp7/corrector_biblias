import fitz  # PyMuPDF para extraer información detallada
import re    # Para encontrar números en el texto
import time  # Para simular carga
import unicodedata  # Para normalizar texto

def normalizar_texto(texto):
    """Convierte texto a minúsculas y elimina tildes."""
    texto = texto.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )

def detectar_la_creacion(texto):
    """Detecta 'LA CREACIÓN' con tolerancia a espacios y caracteres raros."""
    pattern = re.compile(r"l\s*a\s*c\s*r\s*e\s*a\s*c\s*i\s*o?\s*n", re.IGNORECASE)
    match = pattern.search(texto)
    if match:
        return match.start()
    return None

def check_bible_books(pdf_path, versiculo_inicio, update_ui=None):
    try:
        if update_ui:
            update_ui("Cargando... Por favor, espere.\n")
        time.sleep(1)  # Simula un pequeño tiempo de carga
        
        doc = fitz.open(pdf_path)
        incidents = []
        number_format = None
        versiculo_format = None
        size_tolerance_chapter = 3  # Tolerancia para tamaño de capítulo
        size_tolerance_verse = 5  # Tolerancia para tamaño de versículo
        found_creation = None  # Guardará la posición más alta de "La Creación"

        # Buscar "La Creación" en la primera página
        page = doc[0]  # Solo analizamos la primera página
        text_info = page.get_text("dict")
        texto_extraido = page.get_text("text")
        texto_normalizado = normalizar_texto(texto_extraido)
        found_creation = detectar_la_creacion(texto_normalizado)
        
        if found_creation is None:
            incidents.append("No se encontró 'LA CREACIÓN' en la primera página.")
        else:
            if update_ui:
                update_ui("\n✅ Detectado 'LA CREACIÓN' en la primera página.\n")
            
        numbers = []
        versiculos = []
        for block in text_info.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    font_size = span["size"]
                    font_name = span["font"]
                    color = span["color"]
                    x_position = span["origin"][0]
                    y_position = span["origin"][1]
                    
                    # Detectar números de capítulo
                    if text.isdigit():
                        numbers.append((text, x_position, y_position, font_size, font_name, color))
                    
                    # Detectar posibles números de versículo
                    if text.isdigit():
                        versiculos.append((text, x_position, y_position, font_size, font_name, color))
        
        if numbers:
            numbers.sort(key=lambda x: -x[3])  # Ordenar por tamaño de fuente descendente
            top_number = numbers[0]  # El número más grande
            number_format = {"size": top_number[3], "font": top_number[4], "color": top_number[5]}
            
            if update_ui:
                update_ui(f"📖 Página 1: Detectado capítulo 1 con formato {number_format}\n")
            
            # Determinar el formato de versículos basándose en los más comunes
            if versiculos:
                versiculos.sort(key=lambda x: x[3])  # Ordenar por tamaño de fuente ascendente
                versiculo_format = {"size": versiculos[0][3], "font": versiculos[0][4], "color": versiculos[0][5]}
                update_ui(f"📖 Formato de referencia de versículo: {versiculo_format}\n")
        
        # Ahora recorremos todo el documento buscando capítulos y versículos con este formato
        if number_format and versiculo_format:
            for page_number in range(len(doc)):
                page = doc[page_number]
                text_info = page.get_text("dict")
                found_numbers = []
                found_verses = []
                
                for block in text_info.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            font_size = span["size"]
                            font_name = span["font"]
                            color = span["color"]
                            x_position = span["origin"][0]
                            y_position = span["origin"][1]

                            # Comparar números de capítulos con tolerancia específica
                            if (text.isdigit() and 
                                abs(font_size - number_format["size"]) <= size_tolerance_chapter and 
                                font_name == number_format["font"] and 
                                color == number_format["color"]):
                                found_numbers.append((text, x_position, y_position))

                            # Comparar números de versículos con tolerancia específica
                            if (text.isdigit() and 
                                abs(font_size - versiculo_format["size"]) <= size_tolerance_verse and 
                                font_name == versiculo_format["font"] and 
                                color == versiculo_format["color"]):
                                found_verses.append((text, x_position, y_position))
                
                # Ordenar versículos en el orden correcto: primero izquierda, luego derecha
                mid_x = page.rect.width / 2
                left_verses = [v for v in found_verses if v[1] < mid_x]
                right_verses = [v for v in found_verses if v[1] >= mid_x]
                left_verses.sort(key=lambda v: v[2])  # Ordenar por Y (de arriba a abajo)
                right_verses.sort(key=lambda v: v[2])  # Ordenar por Y (de arriba a abajo)
                sorted_verses = left_verses + right_verses
                
                if not found_numbers:
                    incidents.append(f"❌ Página {page_number + 1}: No se encontraron números de capítulo con el formato esperado.")
                if not found_verses:
                    incidents.append(f"❌ Página {page_number + 1}: No se encontraron números de versículo con el formato esperado.")
                
                if update_ui:
                    update_ui(f"✔ Página {page_number + 1}: Capítulos detectados {found_numbers}, Versículos detectados {sorted_verses}\n")

        if update_ui:
            update_ui("✅ Proceso completado.\n")

        return incidents

    except Exception as e:
        if update_ui:
            update_ui(f"❌ Error al procesar el PDF: {e}\n")
        return []