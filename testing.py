import fitz  # PyMuPDF para leer PDFs
import re
import unicodedata

def normalizar_texto(texto):
    """Convierte texto a minúsculas y elimina tildes."""
    texto = texto.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )

def extraer_la_creacion(pdf_path):
    """Extrae y analiza 'LA CREACIÓN' de la primera página del PDF."""
    try:
        doc = fitz.open(pdf_path)
        primera_pagina = doc[0]  # Accede a la primera página
        texto = primera_pagina.get_text("text")  # Extrae texto plano
        
        print("\n=== CONTENIDO COMPLETO DE LA PRIMERA PÁGINA ===\n")
        print(texto)  # Ver el texto completo para revisar anomalías

        # Ver texto carácter por carácter con su posición
        print("\n=== ANÁLISIS DE TEXTO CARÁCTER POR CARÁCTER ===")
        for i, char in enumerate(texto):
            print(f"Pos {i}: {repr(char)}")

        # Normalizar y eliminar espacios extraños
        texto_normalizado = normalizar_texto(texto)
        texto_normalizado = re.sub(r'\s+', ' ', texto_normalizado)  # Sustituir múltiples espacios por uno solo

        print("\n=== TEXTO NORMALIZADO ===\n")
        print(texto_normalizado)

        # Expresión regular para buscar "LA CREACIÓN" con tolerancia a espacios y caracteres raros
        pattern = re.compile(r"l\s*a\s*c\s*r\s*e\s*a\s*c\s*i\s*o?\s*n", re.IGNORECASE)

        match = pattern.search(texto_normalizado)

        if match:
            la_creacion = "la creacion"
            print(f"\n✅ Detectado: {la_creacion} en posición {match.start()}")
            return la_creacion
        else:
            print("\n❌ No se encontró 'LA CREACIÓN' en la primera página.")
            return None

    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")
        return None

# Uso de la función
pdf_path = "biblia_prueba2.pdf"  # Cambia esto por el nombre de tu archivo PDF
extraer_la_creacion(pdf_path)
