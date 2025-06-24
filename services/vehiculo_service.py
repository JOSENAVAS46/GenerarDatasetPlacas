import requests
import re
from bs4 import BeautifulSoup
from models.vehiculo_model import Vehiculo


class VehiculoService:
    # Expresiones regulares para validar placas
    PLACA_AUTO_REGEX = re.compile(
        r'^[A-Za-z]{3}-?(\d{3}|\d{4})$')  # ABC123 o ABC0123
    PLACA_MOTO_REGEX = re.compile(r'^[A-Za-z]{2}\d{3}[A-Za-z]$')    # JK563Y

    @classmethod
    def normalizar_placa(cls, placa):
        """
        Normaliza la placa a mayúsculas y ajusta el formato para autos (agrega 0 si es necesario)
        Retorna None si el formato no es válido
        """
        # Convertir a mayúsculas y eliminar guiones
        placa = placa.upper().replace('-', '')

        # Verificar si es placa de auto
        if cls.PLACA_AUTO_REGEX.match(placa):
            if len(placa) == 6:  # Formato ABC123
                letras = placa[:3]
                numeros = placa[3:]
                # Agregar cero al inicio si son 3 dígitos
                if len(numeros) == 3:
                    numeros = '0' + numeros
                return letras + numeros  # Retorna ABC0123
            return placa  # Ya está en formato correcto

        # Verificar si es placa de moto
        elif cls.PLACA_MOTO_REGEX.match(placa):
            return placa  # JK563Y

        return None

    @staticmethod
    def obtener_informacion_vehiculo(placa):
        """
        Obtiene información de un vehículo por su placa
        Primero normaliza la placa y luego realiza la consulta
        """
        # Normalizar la placa primero
        placa_normalizada = VehiculoService.normalizar_placa(placa)

        if not placa_normalizada:
            raise ValueError(
                f"Formato de placa inválido: {placa}. Formatos aceptados: ABC123, ABC0123 o JK563Y")

        url = f"https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_grid_citaciones.jsp?ps_tipo_identificacion=PLA&ps_identificacion={placa_normalizada}&ps_placa="

        try:
            respuesta = requests.get(url, timeout=10)
            respuesta.raise_for_status()  # Lanza excepción para códigos 4XX/5XX

            soup = BeautifulSoup(respuesta.content, 'html.parser')
            tabla = soup.find(
                'table', {'border': '0', 'cellspacing': '1', 'cellpadding': '2'})

            if not tabla:
                return None

            filas = tabla.find_all('tr')
            info_vehiculo = {}

            for fila in filas:
                titulos = fila.find_all('td', class_='titulo')
                detalles = fila.find_all('td', class_='detalle_formulario')

                if len(titulos) == len(detalles):
                    for titulo, detalle in zip(titulos, detalles):
                        clave = titulo.get_text(
                            strip=True).replace(':', '').strip()
                        valor = detalle.get_text(strip=True)
                        info_vehiculo[clave] = valor

            return Vehiculo(
                placa=placa_normalizada,
                marca=info_vehiculo.get("Marca"),
                color=info_vehiculo.get("Color"),
                anio_matricula=info_vehiculo.get("Año de Matrícula"),
                modelo=info_vehiculo.get("Modelo"),
                clase=info_vehiculo.get("Clase"),
                fecha_matricula=info_vehiculo.get("Fecha de Matrícula"),
                anio=info_vehiculo.get("Año"),
                servicio=info_vehiculo.get("Servicio"),
                fecha_caducidad=info_vehiculo.get("Fecha de Caducidad"),
                polarizado=info_vehiculo.get(
                    "Polarizado", "No existe registro de polarizado")
            )

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error al consultar el servicio ANT: {str(e)}")
