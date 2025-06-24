class Vehiculo:
    def __init__(self, placa, marca, color, anio_matricula, modelo, clase, fecha_matricula, anio, servicio, fecha_caducidad, polarizado):
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.color = color
        self.anio_matricula = anio_matricula
        self.clase = clase
        self.fecha_matricula = fecha_matricula
        self.servicio = servicio
        self.fecha_caducidad = fecha_caducidad
        self.polarizado = polarizado

    def mostrar_informacion(self):
        print(f"Placa: {self.placa}")
        print(f"Marca: {self.marca}")
        print(f"Modelo: {self.modelo}")
        print(f"Año: {self.anio}")
        print(f"Color: {self.color}")
        print(f"Clase: {self.clase}")
        print(f"Servicio: {self.servicio}")
        print(f"Año de Matrícula: {self.anio_matricula}")
        print(f"Fecha de Matrícula: {self.fecha_matricula}")
        print(f"Fecha de Caducidad: {self.fecha_caducidad}")
        print(f"Polarizado: {self.polarizado}")

    def to_dict(self):
        return {
            "placa": self.placa,
            "marca": self.marca,
            "color": self.color,
            "anio_matricula": self.anio_matricula,
            "modelo": self.modelo,
            "clase": self.clase,
            "fecha_matricula": self.fecha_matricula,
            "anio": self.anio,
            "servicio": self.servicio,
            "fecha_caducidad": self.fecha_caducidad,
            "polarizado": self.polarizado
        }
