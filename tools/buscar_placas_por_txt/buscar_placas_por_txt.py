import sys
import os
from pathlib import Path
import csv
from time import sleep

# Configuración de paths - IMPORTANTE
current_dir = Path(__file__).parent.absolute()  # Directorio del script actual
# Subir dos niveles a la raíz del proyecto
project_root = current_dir.parent.parent

# Añadir el directorio raíz al path de Python
sys.path.insert(0, str(project_root))


def agregar_placas_desde_txt():
    # Archivos fijos (hardcoded)
    # Archivo con las placas a agregar (una por línea)
    archivo_placas_txt = 'tools/buscar_placas_por_txt/placas.txt'
    archivo_csv = 'dataset.csv'  # Archivo CSV principal
    archivo_backup = 'tools/buscar_placas_por_txt/dataset_backup.csv'  # Backup por seguridad

    print(
        f"\nIniciando proceso para agregar placas desde {archivo_placas_txt}")
    print("=============================================")

    # 1. Verificar que existan los archivos necesarios
    if not os.path.exists(archivo_placas_txt):
        print(f"Error: No se encontró el archivo {archivo_placas_txt}")
        return

    if not os.path.exists(archivo_csv):
        print(f"Error: No se encontró el archivo CSV principal {archivo_csv}")
        return

    # 2. Crear backup del CSV original
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as orig, \
                open(archivo_backup, 'w', encoding='utf-8') as backup:
            backup.write(orig.read())
        print(f"Backup creado: {archivo_backup}")
    except Exception as e:
        print(f"Error al crear backup: {str(e)}")
        return

    # 3. Leer las placas existentes para evitar duplicados
    placas_existentes = set()
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            placas_existentes = {row['placa'].strip().upper()
                                 for row in reader if 'placa' in row}
        print(
            f"CSV actual contiene {len(placas_existentes)} placas registradas")
    except Exception as e:
        print(f"Error al leer el CSV: {str(e)}")
        return

    # 4. Leer las nuevas placas del archivo txt
    try:
        with open(archivo_placas_txt, 'r', encoding='utf-8') as f:
            nuevas_placas = {line.strip().upper()
                             for line in f if line.strip()}

        print(f"Se encontraron {len(nuevas_placas)} placas en el archivo .txt")

        # Filtrar placas que ya existen
        placas_a_agregar = [
            p for p in nuevas_placas if p not in placas_existentes]

        if not placas_a_agregar:
            print("Todas las placas ya existen en el CSV. No hay nada que agregar.")
            return

        print(f"{len(placas_a_agregar)} placas nuevas para agregar")
    except Exception as e:
        print(f"Error al leer el archivo .txt: {str(e)}")
        return

    # 5. Configurar el servicio de consulta
    from services.vehiculo_service import VehiculoService
    # 6. Procesar cada placa nueva
    exitosas = 0
    fieldnames = [
        'placa', 'marca', 'modelo', 'anio', 'color',
        'clase', 'fecha_matricula', 'anio_matricula', 'servicio',
        'fecha_caducidad', 'polarizado'
    ]

    print("\nIniciando consultas...")
    for i, placa in enumerate(placas_a_agregar, 1):
        try:
            print(f"{i}/{len(placas_a_agregar)} Consultando: {placa}",
                  end=' ', flush=True)

            vehiculo = VehiculoService.obtener_informacion_vehiculo(placa)
            sleep(2)  # Espera para no saturar el servicio

            if vehiculo:
                # Modo 'append' para agregar al final del archivo
                file_exists = os.path.isfile(archivo_csv)
                with open(archivo_csv, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(vehiculo.to_dict())

                print("✓ Agregada")
                exitosas += 1
            else:
                print("✗ No encontrada")

        except Exception as e:
            print(f"✗ Error: {str(e)}")

    # 7. Resumen final
    print("\nResumen:")
    print(f"- Placas procesadas: {len(placas_a_agregar)}")
    print(f"- Placas agregadas exitosamente: {exitosas}")
    print(f"- Placas no encontradas: {len(placas_a_agregar) - exitosas}")


if __name__ == "__main__":
    print("Agregador de Placas desde archivo .txt")
    print("=====================================")
    agregar_placas_desde_txt()
