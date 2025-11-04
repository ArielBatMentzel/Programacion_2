import os

# Carpeta raíz que quieres explorar
root_dir = "Proyecto"
# Archivo donde se guardará la estructura
output_file = "estructura.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Calcula el nivel de indentación según la profundidad
        level = dirpath.replace(root_dir, "").count(os.sep)
        indent = "    " * level
        f.write(f"{indent}{os.path.basename(dirpath)}/\n")
        subindent = "    " * (level + 1)
        for filename in filenames:
            f.write(f"{subindent}{filename}\n")

print(f"Estructura guardada en {output_file}")
