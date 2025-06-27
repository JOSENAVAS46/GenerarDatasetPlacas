import csv
import os
from typing import List


def extraer_y_guardar_colores(archivo_csv: str, archivo_salida: str = 'colores.txt') -> None:
    """
    Extrae los colores únicos de vehículos y los guarda en un archivo de texto.

    Args:
        archivo_csv (str): Ruta al archivo CSV con datos de vehículos
        archivo_salida (str): Ruta del archivo de salida (por defecto 'colores.txt')

    Raises:
        FileNotFoundError: Si no encuentra el archivo CSV
        ValueError: Si el CSV no tiene la columna 'color'
        Exception: Para otros errores durante el procesamiento
    """
    colores = set()

    try:
        # Paso 1: Leer y procesar el archivo CSV
        with open(archivo_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=',')

            if 'color' not in reader.fieldnames:
                raise ValueError(
                    "El archivo CSV no contiene la columna 'color'")

            for row in reader:
                color = row['color'].strip().upper()
                if color:
                    colores.add(color)

        # Paso 2: Ordenar los colores alfabéticamente
        colores_ordenados = sorted(colores)

        # Paso 3: Guardar en el archivo de salida
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            for i, color in enumerate(colores_ordenados, 1):
                f.write(f"{color}\n")

        print(
            f"¡Proceso completado! Se encontraron {len(colores_ordenados)} colores únicos.")
        print(f"Resultados guardados en: {os.path.abspath(archivo_salida)}")

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: No se encontró el archivo {os.path.abspath(archivo_csv)}")
    except Exception as e:
        raise Exception(f"Error durante el procesamiento: {str(e)}")


if __name__ == "__main__":
    # Configuración de rutas según tu estructura de proyecto
    # Sube 3 niveles desde tools/extraer_colores
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    archivo_entrada = os.path.join(base_dir, 'dataset.csv')
    archivo_salida = os.path.join(os.path.dirname(__file__), 'colores.txt')

    # Ejecutar el proceso
    try:
        extraer_y_guardar_colores(archivo_entrada, archivo_salida)
    except Exception as e:
        print(str(e))
