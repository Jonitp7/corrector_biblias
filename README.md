# Asistente de Corrección de Biblias

Este proyecto es una herramienta interactiva construida con Python que permite verificar automáticamente la estructura de Biblias en formato PDF. El asistente comprueba errores de paginación, libros, capítulos y versículos utilizando reglas de formato definidas en el archivo `versiculos_es.json`.

## Estructura del Proyecto

### 1. `main.py`
Este archivo es el punto de entrada principal del programa. Se encarga de arrancar la interfaz gráfica llamando a las funciones definidas en `gui.py`.

### 2. `gui.py`
Contiene la interfaz gráfica creada con Tkinter. Permite al usuario:
- Seleccionar si desea comprobar la paginación o la estructura de libros.
- Elegir opciones como la posición de los números de página y si los capítulos comienzan con el versículo 1.
- Ver los resultados y errores encontrados en un área de texto con scroll.

### 3. `check_paginacion.py`
Encargado de verificar la numeración de páginas en el PDF. Este módulo:
- Detecta el estilo del número de paginación (fuente, tamaño, color) en la primera o segunda página.
- Recorre todas las páginas y verifica si la numeración es continua y si sigue el mismo estilo.
- Informa si faltan, sobran o están mal posicionados los números de página.

### 4. `check_libros.py`
Este módulo se encarga de verificar la estructura completa de la Biblia. Se analiza:
- La detección correcta del nombre de cada libro mediante formato.
- El formato del número de capítulo y versículo.
- El orden visual correcto de lectura (mitad izquierda arriba-abajo, luego mitad derecha).
- Que cada capítulo contenga los versículos esperados, según el archivo `versiculos_es.json`.
- Se informa si hay versículos faltantes, sobrantes o desordenados.
- También detecta títulos clave como "LA CREACIÓN".

## Salida por consola (Tkinter)

Toda la información y el resultado de las comprobaciones se muestra en un área de texto con scroll en la interfaz gráfica. A continuación se explican los diferentes tipos de mensajes que pueden aparecer:

### Mensajes informativos

Estos indican avances normales del proceso, por ejemplo:

```
✅ Detectado 'LA CREACIÓN' en la primera página.
📖 Página 1: Detectado capítulo 1 con formato {'size': 20.5, 'font': 'Times-Bold', 'color': '#000000'}
📖 Formato de referencia de versículo: {'size': 10.0, 'font': 'Times-Roman', 'color': '#000000'}
🔖 Página 10: Nuevo libro detectado → Éxodo
🔎 Comparando estructura extraída con JSON de referencia...
✅ Comparación completada.
```

### Mensajes de advertencia o errores detectados

El sistema reporta errores estructurales como:

```
❗ Faltan versículos en Génesis 2 (página 5): [15, 16]
❗ Sobran versículos en Levítico 3 (página 120): [23]
⚠ Versículos desordenados en Éxodo 1 (página 12)
📘 Capítulo inesperado: Job 43 (página 210)
📗 Falta el libro: Apocalipsis
```

### Errores técnicos

Si ocurre un fallo en el procesamiento del PDF:

```
❌ Error al procesar el PDF: no se puede abrir el archivo...
```

## Requisitos
- Python 3.x
- Bibliotecas: `PyMuPDF`, `tkinter`, `re`, `unicodedata`, `json`

## Uso
1. Ejecuta `main.py`.
2. Usa la interfaz gráfica para elegir una de las funciones de validación.
3. Observa los resultados detallados en pantalla.

## Autor
Desarrollado por Jonitp7. Este proyecto forma parte de una solución automatizada para control de calidad en producción de Biblias.

---
