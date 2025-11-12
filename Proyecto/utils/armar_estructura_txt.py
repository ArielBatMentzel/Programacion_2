# armar_estructura_txt.py
"""
Genera un archivo de texto con la estructura de carpetas y archivos
de un proyecto, ignorando ciertas carpetas como entornos virtuales
o __pycache__.
"""

import os

# Carpeta raíz que se desea explorar
root_dir = "Proyecto"

# Archivo de salida donde se guardará la estructura
output_file = "estructura.txt"

# Carpetas a ignorar (sin importar su ubicación)
ignore_dirs = {".venv", "venv", "__pycache__"}

with open(output_file, "w", encoding="utf-8") as f:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 🔹 Filtramos las carpetas a ignorar (modifica dirnames in-place)
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        # Nivel de indentación según la profundidad
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        f.write(f"{os.path.basename(dirpath)}/\n")

        subindent = "    " * (level + 1)
        for filename in filenames:
            f.write(f"{subindent}{filename}\n")

print(
    f"✅ Estructura guardada en {output_file} "
    f"(ignorando {', '.join(ignore_dirs)})"
)
