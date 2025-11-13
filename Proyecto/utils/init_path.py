"""
“Agregá la carpeta raíz (/app en Render) al path de Python, 
así puede encontrar utils/ y cualquier otro módulo de nivel superior.”
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))