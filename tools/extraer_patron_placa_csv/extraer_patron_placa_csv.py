import csv
from collections import defaultdict


def extraer_patrones():
    """
    Versión simplificada que extrae patrones de placas con valores hardcodeados
    """
    input_csv = 'dataset.csv'  # Archivo CSV de entrada fijo
    output_txt = 'tools\extraer_patron_placa_csv\patrones.txt'  # Archivo de salida fijo

    patrones = set()  # Usamos un set para evitar duplicados

    try:
        print(f"Procesando archivo: {input_csv}")

        # Leer CSV y extraer patrones
        with open(input_csv, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                placa = row.get('placa', '').strip().upper()
                if len(placa) >= 3 and placa[:3].isalpha():
                    patrones.add(placa[:3])

        # Ordenar alfabéticamente
        patrones_ordenados = sorted(patrones)

        # Guardar en archivo
        with open(output_txt, mode='w', encoding='utf-8') as txt_file:
            txt_file.write("\n".join(patrones_ordenados))

        print(f"Se extrajeron {len(patrones_ordenados)} patrones únicos")
        print(f"Resultados guardados en: {output_txt}")

        # Mostrar estadísticas adicionales
        contar_ocurrencias_por_patron(input_csv, patrones_ordenados)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_csv}")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")


def contar_ocurrencias_por_patron(input_csv, patrones):
    """
    Muestra estadísticas de frecuencia de los patrones encontrados
    """
    contador = defaultdict(int)

    try:
        with open(input_csv, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                placa = row.get('placa', '').strip().upper()
                if len(placa) >= 3 and placa[:3].isalpha():
                    patron = placa[:3]
                    if patron in patrones:  # Solo contamos los patrones que encontramos
                        contador[patron] += 1
    except Exception as e:
        print(f"No se pudieron calcular estadísticas: {str(e)}")


if __name__ == "__main__":
    print("Extractor de Patrones de Placas - Versión Simplificada")
    print("======================================================")
    extraer_patrones()
