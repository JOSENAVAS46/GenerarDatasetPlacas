import csv
import random
import string
import time
import requests
from services.vehiculo_service import VehiculoService

PROVINCIAS = {
    'Azuay': 'A',
    'Bolívar': 'B',
    'Cañar': 'U',
    'Carchi': 'C',
    'Cotopaxi': 'X',
    'Chimborazo': 'H',
    'El Oro': 'O',
    'Esmeraldas': 'E',
    'Galápagos': 'W',
    'Guayas': 'G',
    'Imbabura': 'I',
    'Loja': 'L',
    'Los Ríos': 'R',
    'Manabí': 'M',
    'Morona': 'V',
    'Napo': 'N',
    'Pastaza': 'S',
    'Pichincha': 'P',
    'Santa Elena': 'Y',
    'Santo Domingo': 'J',
    'Sucumbíos': 'K',
    'Tungurahua': 'T',
    'Zamora': 'Z'
}


class GeneradorConsultorPlacas:
    def __init__(self, archivo_dataset='dataset.csv'):
        self.archivo_dataset = archivo_dataset
        self.placas_existentes = self._cargar_placas_existentes()
        self.patron_valido_actual = None
        self.ultimo_numero = 0
        self.max_variaciones = 10  # Máximo de variaciones numéricas por patrón válido

    def _cargar_placas_existentes(self):
        """Carga las placas existentes del dataset para evitar duplicados"""
        try:
            with open(self.archivo_dataset, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return {row['placa'] for row in reader}
        except FileNotFoundError:
            return set()

    def generar_placa_auto(self, provincia=None, base=None):
        """
        Genera una placa de auto válida para Ecuador (LLL1234)
        - Si se proporciona base: usa las letras de base y genera nuevos números
        - Si no: genera nueva combinación completa
        """
        if base and len(base) >= 3:
            # Generar variación numérica de un patrón válido
            letras = base[:3]
            nuevo_numero = self.ultimo_numero + 1
            self.ultimo_numero = nuevo_numero
            return f"{letras}{nuevo_numero:04d}"
        else:
            # Generar nueva placa desde cero
            if not provincia:
                provincia, letra_provincia = random.choice(
                    list(PROVINCIAS.items()))
            else:
                letra_provincia = PROVINCIAS.get(
                    provincia, random.choice(list(PROVINCIAS.values())))

            letras_extra = ''.join(random.choices(string.ascii_uppercase, k=2))
            numeros = f"{random.randint(0, 9999):04d}"
            return f"{letra_provincia}{letras_extra}{numeros}"

    def guardar_vehiculo(self, vehiculo):
        """Guarda un vehículo en el dataset CSV"""
        fieldnames = [
            'placa', 'marca', 'modelo', 'anio', 'color',
            'clase', 'fecha_matricula', 'anio_matricula', 'servicio',
            'fecha_caducidad', 'polarizado'
        ]

        file_exists = False
        try:
            with open(self.archivo_dataset, mode='r', newline='', encoding='utf-8') as file:
                file_exists = True
        except FileNotFoundError:
            pass

        with open(self.archivo_dataset, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(vehiculo.to_dict())

        self.placas_existentes.add(vehiculo.placa)

    def procesar_placas(self, cantidad, provincia=None, delay=2):
        placas_procesadas = 0
        placas_guardadas = 0
        variaciones_generadas = 0

        while placas_guardadas < cantidad:
            # Generar placa según el contexto actual
            if self.patron_valido_actual and variaciones_generadas < self.max_variaciones:
                placa = self.generar_placa_auto(
                    provincia, self.patron_valido_actual)
                variaciones_generadas += 1
            else:
                placa = self.generar_placa_auto(provincia)
                self.patron_valido_actual = None
                variaciones_generadas = 0

            if placa in self.placas_existentes:
                print(f"Placa {placa} ya existe, saltando...")
                continue

            try:
                print(f"Consultando placa: {placa}")
                vehiculo = VehiculoService.obtener_informacion_vehiculo(placa)

                if vehiculo:
                    self.guardar_vehiculo(vehiculo)
                    placas_guardadas += 1

                    # Si es una nueva combinación válida, guardar el patrón
                    if variaciones_generadas == 0:
                        self.patron_valido_actual = placa[:3]
                        self.ultimo_numero = int(placa[3:7])
                        print(
                            f"¡Nuevo patrón válido encontrado! {self.patron_valido_actual}****")

                    print(f"Guardada {placa} ({placas_guardadas}/{cantidad})")
                else:
                    print(f"No se encontró información para {placa}")

            except Exception as e:
                print(f"Error al consultar {placa}: {str(e)}")
                # Si hay error con un patrón, lo descartamos
                self.patron_valido_actual = None

            time.sleep(delay)
            placas_procesadas += 1

            if placas_procesadas > cantidad * 50 and placas_guardadas == 0:
                print("Demasiados intentos fallidos. Deteniendo...")
                break

        print(
            f"Proceso completado. Placas guardadas: {placas_guardadas}/{cantidad}")

    def procesar_placas_desde_archivo(self, archivo_placas, delay=2):
        """
        Procesa un listado de placas desde un archivo de texto
        :param archivo_placas: Ruta del archivo con las placas (una por línea)
        :param delay: Tiempo de espera entre consultas (en segundos)
        """
        try:
            with open(archivo_placas, mode='r', encoding='utf-8') as file:
                placas_a_buscar = [line.strip()
                                   for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Error: Archivo {archivo_placas} no encontrado")
            return

        if not placas_a_buscar:
            print("El archivo no contiene placas válidas")
            return

        print(f"\nIniciando búsqueda de {len(placas_a_buscar)} placas...")
        placas_encontradas = 0

        for placa in placas_a_buscar:
            # Validar formato básico de placa (3 letras + 3-4 números)
            if not (len(placa) in [6, 7] and placa[:3].isalpha() and placa[3:].isdigit()):
                print(f"Placa {placa} no tiene formato válido, saltando...")
                continue

            placa = placa.upper()  # Normalizar a mayúsculas

            if placa in self.placas_existentes:
                print(f"Placa {placa} ya existe en el dataset, saltando...")
                continue

            try:
                print(f"\nConsultando placa: {placa}")
                vehiculo = VehiculoService.obtener_informacion_vehiculo(placa)

                if vehiculo:
                    self.guardar_vehiculo(vehiculo)
                    placas_encontradas += 1
                    print(
                        f"¡Encontrada y guardada! Total: {placas_encontradas}")
                else:
                    print(f"No se encontró información para {placa}")

            except Exception as e:
                print(f"Error al consultar {placa}: {str(e)}")

            time.sleep(delay)

        print(
            f"\nProceso completado. Placas encontradas: {placas_encontradas}/{len(placas_a_buscar)}")

    def procesar_placas_desde_patron(self, patron, cantidad, delay=2):
        """
        Genera y consulta placas basadas en un patrón de 3 letras
        :param patron: Las 3 letras iniciales de las placas (ej: 'ABC')
        :param cantidad: Cantidad de placas a generar y consultar
        :param delay: Tiempo de espera entre consultas (en segundos)
        """
        if len(patron) != 3 or not patron.isalpha():
            print("Error: El patrón debe contener exactamente 3 letras")
            return

        patron = patron.upper()
        print(f"\nGenerando {cantidad} placas con patrón {patron}****")
        placas_encontradas = 0

        # Comenzar desde un número aleatorio para evitar secuencias predecibles
        numero_inicial = random.randint(0, 9999)

        for i in range(cantidad):
            # Generar número secuencial o aleatorio
            # Asegurar que sea de 4 dígitos
            numero = (numero_inicial + i) % 10000
            placa = f"{patron}{numero:04d}"

            if placa in self.placas_existentes:
                print(f"Placa {placa} ya existe, saltando...")
                continue

            try:
                print(f"\nConsultando placa: {placa}")
                vehiculo = VehiculoService.obtener_informacion_vehiculo(placa)

                if vehiculo:
                    self.guardar_vehiculo(vehiculo)
                    placas_encontradas += 1
                    print(
                        f"¡Encontrada y guardada! Total: {placas_encontradas}/{cantidad}")
                else:
                    print(f"No se encontró información para {placa}")

            except Exception as e:
                print(f"Error al consultar {placa}: {str(e)}")

            time.sleep(delay)

        print(
            f"\nProceso completado. Placas encontradas: {placas_encontradas}/{cantidad}")

    def procesar_patrones_desde_archivo(self, archivo_patrones, cantidad_por_patron, delay=2):
        """
        Procesa múltiples patrones desde un archivo y genera variaciones numéricas para cada uno
        :param archivo_patrones: Ruta del archivo con los patrones (uno por línea)
        :param cantidad_por_patron: Cantidad de placas a generar por cada patrón
        :param delay: Tiempo de espera entre consultas (en segundos)
        """
        try:
            with open(archivo_patrones, mode='r', encoding='utf-8') as file:
                patrones = [line.strip().upper()
                            for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Error: Archivo {archivo_patrones} no encontrado")
            return

        if not patrones:
            print("El archivo no contiene patrones válidos")
            return

        print(
            f"\nIniciando búsqueda para {len(patrones)} patrones ({cantidad_por_patron} cada uno)...")
        total_encontradas = 0

        for i, patron in enumerate(patrones, 1):
            if len(patron) != 3 or not patron.isalpha():
                print(f"\nPatrón {patron} no válido, saltando...")
                continue

            print(f"\n[{i}/{len(patrones)}] Procesando patrón: {patron}")
            encontradas = self.procesar_placas_desde_patron_silencioso(
                patron, cantidad_por_patron, delay)
            total_encontradas += encontradas

        print(
            f"\nProceso completado. Total de placas encontradas: {total_encontradas}")

    def procesar_placas_desde_patron_silencioso(self, patron, cantidad, delay=2):
        """
        Versión silenciosa de procesar_placas_desde_patron para uso interno
        Devuelve el número de placas encontradas
        """
        if len(patron) != 3 or not patron.isalpha():
            return 0

        patron = patron.upper()
        placas_encontradas = 0
        numero_inicial = random.randint(0, 9999)

        for i in range(cantidad):
            numero = (numero_inicial + i) % 10000
            placa = f"{patron}{numero:04d}"

            if placa in self.placas_existentes:
                continue

            try:
                vehiculo = VehiculoService.obtener_informacion_vehiculo(placa)
                if vehiculo:
                    self.guardar_vehiculo(vehiculo)
                    placas_encontradas += 1
            except Exception as e:
                print(f"Error al consultar {placa}: {str(e)}")

            time.sleep(delay)

        return placas_encontradas


if __name__ == "__main__":
    consultor = GeneradorConsultorPlacas()

    print("Sistema de Consulta de Placas Vehiculares")
    print("========================================")
    print("1. Generar y consultar placas aleatorias")
    print("2. Consultar placas desde archivo")
    print("3. Generar desde patrón de 3 letras")
    print("4. Procesar múltiples patrones desde archivo")

    try:
        opcion = int(input("\nSeleccione una opción: "))

        if opcion == 1:
            print("\nProvincias disponibles:")
            for i, (provincia, letra) in enumerate(PROVINCIAS.items(), 1):
                print(f"{i}. {provincia} ({letra})")
            print("0. Aleatoria")

            opcion_prov = int(
                input("\nSeleccione provincia (0 para aleatoria): "))
            provincia = None

            if 0 < opcion_prov <= len(PROVINCIAS):
                provincia = list(PROVINCIAS.keys())[opcion_prov-1]
                print(
                    f"Generando placas para {provincia} ({PROVINCIAS[provincia]})")

            cantidad = int(
                input("Ingrese la cantidad de placas a consultar: "))
            if cantidad > 0:
                consultor.procesar_placas(cantidad, provincia)
            else:
                print("La cantidad debe ser mayor a 0")

        elif opcion == 2:
            archivo = input("Ingrese la ruta del archivo con las placas: ")
            consultor.procesar_placas_desde_archivo(archivo)

        elif opcion == 3:
            patron = input(
                "Ingrese las 3 letras del patrón (ej: ABC): ").strip().upper()
            cantidad = int(input("Ingrese la cantidad de placas a generar: "))
            if cantidad > 0:
                consultor.procesar_placas_desde_patron(patron, cantidad)
            else:
                print("La cantidad debe ser mayor a 0")
        elif opcion == 4:
            archivo = input(
                "Ingrese la ruta del archivo con los patrones (o Enter para 'patrones.txt'): ").strip()
            if not archivo:
                archivo = 'tools\extraer_patron_placa_csv\patrones.txt'

            cantidad = int(
                input("Ingrese la cantidad de placas a generar por patrón: "))
            if cantidad > 0:
                consultor.procesar_patrones_desde_archivo(archivo, cantidad)
            else:
                print("La cantidad debe ser mayor a 0")
        else:
            print("Opción no válida")

    except ValueError:
        print("Por favor ingrese un número válido")
