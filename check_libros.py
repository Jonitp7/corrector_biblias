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

def rgb_to_hex(rgb_int):
    return "#{:06X}".format(rgb_int)

def check_bible_books(pdf_path, versiculo_inicio, update_ui=None):
    try:
        if update_ui:
            update_ui("Cargando... Por favor, espere.\n")
        time.sleep(1)

        doc = fitz.open(pdf_path)
        incidents = []
        number_format = None
        versiculo_format = None
        libro_format = None
        size_tolerance_chapter = 3
        size_tolerance_verse = 2
        size_tolerance_book = 5

        found_creation = None
        libro_actual = None
        estructura_libros = {}
        capitulo_actual = None
        pagina_capitulo = {}

        page = doc[0]
        text_info = page.get_text("dict")
        spans_detectados = []
        for block in text_info["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    texto = span["text"].strip()
                    if normalizar_texto(texto) == "genesis":
                        spans_detectados.append(span)
        if spans_detectados:
            span_genesis = max(spans_detectados, key=lambda s: s["size"])
            libro_format = {
                "text": "Genesis",
                "size": span_genesis["size"],
                "font": span_genesis["font"],
                "color": rgb_to_hex(span_genesis["color"]),
            }

        texto_normalizado = normalizar_texto(page.get_text("text"))
        found_creation = detectar_la_creacion(texto_normalizado)

        if found_creation is None:
            incidents.append("No se encontró 'LA CREACIÓN' en la primera página.")
        else:
            if update_ui:
                update_ui("✅ Detectado 'LA CREACIÓN' en la primera página.\n")

        numbers, versiculos = [], []
        for block in text_info.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    size = span["size"]
                    font = span["font"]
                    color = span["color"]
                    x = span["origin"][0]
                    y = span["origin"][1]
                    if text.isdigit():
                        numbers.append((text, x, y, size, font, color))
                        versiculos.append((text, x, y, size, font, color))

        if numbers:
            numbers.sort(key=lambda x: -x[3])
            top_number = numbers[0]
            number_format = {"size": top_number[3], "font": top_number[4], "color": rgb_to_hex(top_number[5])}
            if update_ui:
                update_ui(f"📖 Página 1: Detectado capítulo 1 con formato {number_format}\n")

        if numbers and versiculos:
            cap_x, cap_y = top_number[1], top_number[2]
            cap_size = top_number[3]

            candidato = None
            min_distancia = float("inf")

            for v in versiculos:
                numero = int(v[0])
                v_x, v_y = v[1], v[2]
                v_size = v[3]

                if (versiculo_inicio == "si" and numero != 1) or (versiculo_inicio == "no" and numero != 2):
                    continue
                if v_size >= cap_size * 0.9:
                    continue
                if v_x <= cap_x:
                    continue

                distancia = abs(v_y - cap_y)
                if distancia < min_distancia:
                    min_distancia = distancia
                    candidato = v

            if candidato:
                versiculo_format = {
                    "size": candidato[3],
                    "font": candidato[4],
                    "color": rgb_to_hex(candidato[5])
                }
                if update_ui:
                    update_ui(f"📖 Formato de referencia de versículo: {versiculo_format} (extraído del número {candidato[0]})\n")
            else:
                if update_ui:
                    update_ui("⚠ No se pudo determinar el formato de versículo de referencia.\n")

        if not (number_format and versiculo_format and libro_format):
            return ["No se pudieron detectar los formatos necesarios."]

        for page_number in range(len(doc)):
            page = doc[page_number]
            text_info = page.get_text("dict")
            texto_plano = page.get_text("text")
            texto_normalizado = normalizar_texto(texto_plano)
            all_elements = []

            libro_encontrado = None
            for block in text_info["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if (
                            abs(span["size"] - libro_format["size"]) < size_tolerance_book and
                            span["font"] == libro_format["font"] and
                            rgb_to_hex(span["color"]) == libro_format["color"]
                        ):
                            span_text = normalizar_texto(span["text"].strip())
                            for nombre_libro in libros_biblia:
                                if normalizar_texto(nombre_libro) == span_text:
                                    libro_encontrado = nombre_libro
                                    break
                    if libro_encontrado:
                        break
                if libro_encontrado:
                    break

            if libro_encontrado:
                if libro_encontrado != libro_actual:
                    if update_ui:
                        update_ui(f"\n🔖 Página {page_number + 1}: Nuevo libro detectado → {libro_encontrado}\n")
                    libro_actual = libro_encontrado
                    capitulo_actual = None
                    if libro_actual not in estructura_libros:
                        estructura_libros[libro_actual] = {}

            for block in text_info.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        size = span["size"]
                        font = span["font"]
                        color = rgb_to_hex(span["color"])
                        x, y = span["origin"]
                        if not text.isdigit():
                            continue
                        tipo = None
                        if abs(size - number_format["size"]) <= size_tolerance_chapter and font == number_format["font"] and color == number_format["color"]:
                            tipo = "capitulo"
                        elif abs(size - versiculo_format["size"]) <= size_tolerance_verse and font == versiculo_format["font"] and color == versiculo_format["color"]:
                            tipo = "versiculo"
                        if tipo:
                            all_elements.append((tipo, int(text), x, y, page_number + 1))

            mid_x = page.rect.width / 2
            all_elements.sort(key=lambda el: (el[2] >= mid_x, el[3]))

            for tipo, numero, x, y, pag in all_elements:
                if tipo == "capitulo":
                    capitulo_actual = numero
                    pagina_capitulo[(libro_actual, capitulo_actual)] = pag
                    if capitulo_actual not in estructura_libros[libro_actual]:
                        estructura_libros[libro_actual][capitulo_actual] = []
                elif tipo == "versiculo" and libro_actual and capitulo_actual:
                    if numero not in estructura_libros[libro_actual][capitulo_actual]:
                        estructura_libros[libro_actual][capitulo_actual].append(numero)

        if update_ui:
            update_ui("\n🔎 Comparando estructura extraída con JSON de referencia...\n")

        libros_detectados = set(estructura_libros.keys())
        libros_referencia = set(libros_biblia.keys())

        for libro, caps_reales in estructura_libros.items():
            if libro not in libros_biblia:
                incidents.append(f"📕 Libro inesperado: {libro}")
                continue
            caps_esperados = libros_biblia[libro]

            for cap, vers_reales in caps_reales.items():
                cap_str = str(cap)
                pagina = pagina_capitulo.get((libro, cap), "?")

                if cap_str not in caps_esperados:
                    incidents.append(f"📘 Capítulo inesperado: {libro} {cap} (página {pagina})")
                    continue

                total_versiculos = caps_esperados[cap_str]
                if isinstance(total_versiculos, int):
                    vers_esperados = list(range(1, total_versiculos + 1))
                else:
                    vers_esperados = total_versiculos

                if versiculo_inicio == "no":
                    vers_esperados = [v for v in vers_esperados if v != 1]

                faltan = sorted(set(vers_esperados) - set(vers_reales))
                sobran = sorted(set(vers_reales) - set(vers_esperados))
                desordenados = vers_reales != sorted(vers_reales)

                if faltan:
                    incidents.append(f"❗ Faltan versículos en {libro} {cap} (página {pagina}): {faltan}")
                if sobran:
                    incidents.append(f"❗ Sobran versículos en {libro} {cap} (página {pagina}): {sobran}")
                if desordenados:
                    incidents.append(f"⚠ Versículos desordenados en {libro} {cap} (página {pagina})")

        for libro in libros_biblia:
            if libro not in estructura_libros:
                incidents.append(f"📗 Falta el libro: {libro}")

        if update_ui:
            update_ui("✅ Comparación completada.\n")
            for i in incidents:
                update_ui(f"{i}\n")

        return incidents

    except Exception as e:
        if update_ui:
            update_ui(f"❌ Error al procesar el PDF: {e}\n")
        return []
