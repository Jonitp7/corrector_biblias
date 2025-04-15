import fitz  # PyMuPDF para extraer información detallada
import re    # Para encontrar números en el texto
import time  # Para simular carga

def int_to_rgb(color_int):
    r = (color_int >> 16) & 255
    g = (color_int >> 8) & 255
    b = color_int & 255
    return (r, g, b)

def color_similar(c1, c2, tolerance=10):
    r1, g1, b1 = int_to_rgb(c1)
    r2, g2, b2 = int_to_rgb(c2)
    return all(abs(a - b) <= tolerance for a, b in zip((r1, g1, b1), (r2, g2, b2)))

def check_page_numbers(pdf_path, alignment="top_center", start_page=1, start_page_option="primera", update_ui=None):
    try:
        if update_ui:
            update_ui("Cargando... Por favor, espere.\n")
        time.sleep(1)
        
        doc = fitz.open(pdf_path)
        incidents = []
        pagination_style = None
        
        start_page_index = 0 if start_page_option == "primera" else 1
        first_page = doc[start_page_index]
        text_info = first_page.get_text("dict")
        numbers_with_position = []

        for block in text_info["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    font_size = span["size"]
                    font_name = span["font"]
                    color = span["color"]
                    x_position = span["origin"][0]
                    y_position = span["origin"][1]

                    text_cleaned = re.search(r'\d+', text)
                    if text_cleaned and int(text_cleaned.group()) == start_page:
                        numbers_with_position.append((int(text_cleaned.group()), y_position, x_position, font_size, font_name, color))
        
        if numbers_with_position:
            if "top" in alignment:
                numbers_with_position.sort(key=lambda x: x[1])
            else:
                numbers_with_position.sort(key=lambda x: -x[1])
            
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
            expected_page_number = start_page + (page_number - start_page_index)
            pdf_page_number = page_number + 1
            page = doc[page_number]
            text_info = page.get_text("dict")
            numbers_with_position = []

            for block in text_info["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        y_position = span["origin"][1]
                        x_position = span["origin"][0]
                        font_size = span["size"]
                        font_name = span["font"]
                        color = span["color"]

                        text_cleaned = re.search(r'\d+', text)
                        if text_cleaned:
                            number = int(text_cleaned.group())
                            size_tolerance = 4
                            if (
                                abs(font_size - pagination_style["size"]) <= size_tolerance and
                                font_name == pagination_style["font"] and
                                color_similar(color, pagination_style["color"])
                            ):
                                numbers_with_position.append((number, y_position, x_position))

            if "top" in alignment:
                numbers_with_position.sort(key=lambda x: x[1])
            else:
                numbers_with_position.sort(key=lambda x: -x[1])

            if numbers_with_position:
                top_number = numbers_with_position[0]
                if top_number[0] != expected_page_number:
                    incidents.append((expected_page_number, pdf_page_number, f"Número incorrecto: {top_number[0]}"))
            else:
                incidents.append((expected_page_number, pdf_page_number, "Sin número o formato incorrecto"))

            if update_ui:
                update_ui(f"Página esperada {expected_page_number} (PDF: {pdf_page_number}) - Números encontrados: {[(num, round(y, 2), round(x, 2)) for num, y, x in numbers_with_position]}\n")

        if update_ui:
            update_ui("Proceso completado.\n")
        return incidents

    except Exception as e:
        if update_ui:
            update_ui(f"Error al procesar el PDF: {e}\n")
        return []
