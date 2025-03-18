import fitz  # PyMuPDF para extraer información detallada
import re    # Para encontrar números en el texto
import time  # Para simular carga

def check_page_numbers(pdf_path, alignment="top_center", start_page=1, start_page_option="primera", update_ui=None):
    try:
        if update_ui:
            update_ui("Cargando... Por favor, espere.\n")
        time.sleep(1)  # Simula un pequeño tiempo de carga
        
        doc = fitz.open(pdf_path)
        incidents = []
        pagination_style = None  # Almacenar fuente, tamaño y color del número de paginación
        
        # Definir desde qué página empieza la numeración
        start_page_index = 0 if start_page_option == "primera" else 1
        
        # Detectar la fuente, tamaño y color del primer número de paginación basado en la entrada del usuario
        first_page = doc[start_page_index]
        text_info = first_page.get_text("dict")
        detected_number = None
        
        numbers_with_position = []
        for block in text_info["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    font_size = span["size"]  # Tamaño de fuente
                    font_name = span["font"]  # Nombre de la fuente
                    color = span["color"]  # Color del texto
                    x_position = span["origin"][0]  # Posición horizontal
                    y_position = span["origin"][1]  # Posición vertical
                    
                    text_cleaned = re.search(r'\d+', text)  # Buscar el primer número en el texto
                    if text_cleaned and int(text_cleaned.group()) == start_page:
                        numbers_with_position.append((int(text_cleaned.group()), y_position, x_position, font_size, font_name, color))
        
        # Seleccionar el número según la posición indicada
        if numbers_with_position:
            if "top" in alignment:
                numbers_with_position.sort(key=lambda x: x[1])  # Más arriba en la página
            else:
                numbers_with_position.sort(key=lambda x: -x[1])  # Más abajo en la página
            
            top_number = numbers_with_position[0]
            pagination_style = {
                "size": top_number[3],
                "font": top_number[4],
                "color": top_number[5],
                "position": alignment
            }
        else:
            if update_ui:
                update_ui("No se pudo detectar el formato del número de paginación en la primera página de numeración.\n")
            return []
        
        for page_number in range(start_page_index, len(doc)):
            if update_ui:
                update_ui(f"Procesando página {page_number + 1} de {len(doc)}...\n")
            expected_page_number = start_page + (page_number - start_page_index)  # Ajustar número esperado según inicio
            pdf_page_number = page_number + 1  # Página real del PDF
            page = doc[page_number]
            text_info = page.get_text("dict")
            numbers_with_position = []
            
            # Extraer números con su información de fuente, tamaño y color
            for block in text_info["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        y_position = span["origin"][1]  # Posición vertical del número
                        x_position = span["origin"][0]  # Posición horizontal del número
                        font_size = span["size"]  # Tamaño de fuente
                        font_name = span["font"]  # Nombre de la fuente
                        color = span["color"]  # Color del texto
                        
                        text_cleaned = re.search(r'\d+', text)  # Buscar el primer número en el texto
                        if text_cleaned:
                            number = int(text_cleaned.group())
                            if font_size == pagination_style["size"] and font_name == pagination_style["font"] and color == pagination_style["color"]:
                                numbers_with_position.append((number, y_position, x_position))
            
            if "top" in alignment:
                numbers_with_position.sort(key=lambda x: x[1])  # Más arriba
            else:
                numbers_with_position.sort(key=lambda x: -x[1])  # Más abajo
            
            if numbers_with_position:
                top_number = numbers_with_position[0]  # Número con la posición deseada
                if top_number[0] != expected_page_number:
                    incidents.append((expected_page_number, pdf_page_number, f"Número incorrecto: {top_number[0]}"))
            else:
                incidents.append((expected_page_number, pdf_page_number, "Sin número o formato incorrecto"))
            
            if update_ui:
                update_ui(f"Página esperada {expected_page_number} (PDF: {pdf_page_number}) - Números encontrados: {[(num, y, x) for num, y, x in numbers_with_position]}\n")
        
        if update_ui:
            update_ui("Proceso completado.\n")
        return incidents
    except Exception as e:
        if update_ui:
            update_ui(f"Error al procesar el PDF: {e}\n")
        return []