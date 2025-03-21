import fitz  # PyMuPDF para extraer información detallada
import re    # Para encontrar números en el texto
import time  # Para simular carga
import unicodedata  # Para normalizar texto
import json  # Para manejar los datos de versículos

# Cargar nombres de libros desde el JSON
with open("versiculos_es.json", "r", encoding="utf-8") as f:
    libros_biblia = json.load(f)

def normalizar_texto(texto):
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def detectar_la_creacion(texto):
    pattern = re.compile(r"l\s*a\s*c\s*r\s*e\s*a\s*c\s*i\s*o?\s*n", re.IGNORECASE)
    match = pattern.search(texto)
    if match:
        return match.start()
    return None

def check_bible_books(pdf_path, versiculo_inicio, update_ui=None):
    try:
        if update_ui:
            update_ui("Cargando... Por favor, espere.\n")
        time.sleep(1)

        doc = fitz.open(pdf_path)
        incidents = []
        number_format = None
        versiculo_format = None
        size_tolerance_chapter = 3
        size_tolerance_verse = 0
        found_creation = None
        libro_actual = None
        estructura_libros = {}
        capitulo_actual = None

        # Buscar formatos en la primera página
        page = doc[0]
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
                    x = span["origin"][0]
                    y = span["origin"][1]

                    if text.isdigit():
                        numbers.append((text, x, y, font_size, font_name, color))
                        versiculos.append((text, x, y, font_size, font_name, color))

        if numbers:
            numbers.sort(key=lambda x: -x[3])
            top_number = numbers[0]
            number_format = {"size": top_number[3], "font": top_number[4], "color": top_number[5]}
            if update_ui:
                update_ui(f"📖 Página 1: Detectado capítulo 1 con formato {number_format}\n")

        if versiculos:
            versiculos.sort(key=lambda x: x[3])
            ref = versiculos[0]
            versiculo_format = {"size": ref[3], "font": ref[4], "color": ref[5]}
            if update_ui:
                update_ui(f"📖 Formato de referencia de versículo: {versiculo_format}\n")

        if not (number_format and versiculo_format):
            return ["No se pudieron detectar formatos de capítulo o versículo."]

        for page_number in range(len(doc)):
            page = doc[page_number]
            text_info = page.get_text("dict")
            texto_plano = page.get_text("text")
            texto_normalizado = normalizar_texto(texto_plano)
            all_elements = []

            # Detectar el libro
            libro_encontrado = None
            for nombre_libro in libros_biblia:
                if normalizar_texto(nombre_libro) in texto_normalizado:
                    libro_encontrado = nombre_libro
                    break

            if libro_encontrado:
                if libro_encontrado != libro_actual:
                    if update_ui:
                        update_ui(f"\n🔖 Página {page_number+1}: Nuevo libro detectado → {libro_encontrado}\n")
                    libro_actual = libro_encontrado
                    capitulo_actual = None
                    if libro_actual not in estructura_libros:
                        estructura_libros[libro_actual] = {}

            # Extraer elementos con sus posiciones
            for block in text_info.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        size = span["size"]
                        font = span["font"]
                        color = span["color"]
                        x = span["origin"][0]
                        y = span["origin"][1]
                        if not text.isdigit():
                            continue

                        tipo = None
                        if abs(size - number_format["size"]) <= size_tolerance_chapter and font == number_format["font"] and color == number_format["color"]:
                            tipo = "capitulo"
                        elif abs(size - versiculo_format["size"]) <= size_tolerance_verse and font == versiculo_format["font"] and color == versiculo_format["color"]:
                            tipo = "versiculo"
                        if tipo:
                            all_elements.append((tipo, int(text), x, y))

            # Orden: izquierda a derecha, arriba a abajo
            mid_x = page.rect.width / 2
            all_elements.sort(key=lambda el: (el[2] >= mid_x, el[3]))

            for tipo, numero, x, y in all_elements:
                if tipo == "capitulo":
                    capitulo_actual = numero
                    if libro_actual and capitulo_actual not in estructura_libros[libro_actual]:
                        estructura_libros[libro_actual][capitulo_actual] = []
                elif tipo == "versiculo" and libro_actual and capitulo_actual:
                    if numero not in estructura_libros[libro_actual][capitulo_actual]:
                        estructura_libros[libro_actual][capitulo_actual].append(numero)

        if update_ui:
            update_ui("✅ Proceso completado.\n")
            update_ui("\n📚 Estructura recogida de libros, capítulos y versículos:\n")
            update_ui(json.dumps(estructura_libros, indent=4, ensure_ascii=False))

        return incidents

    except Exception as e:
        if update_ui:
            update_ui(f"❌ Error al procesar el PDF: {e}\n")
        return []
