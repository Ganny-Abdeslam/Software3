class Articulo:
    def __init__(self, codigo, nombre, presentaciones, categoria, lote, fecha_vencimiento, extras=None):
        self.codigo = codigo
        self.nombre = nombre
        self.presentaciones = presentaciones
        self.categoria = categoria
        self.lote = lote
        self.fecha_vencimiento = fecha_vencimiento
        self.extras = extras if extras else {}  # Atributos adicionales

    def to_mongo(self):
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "presentaciones": self.presentaciones,
            "categoria": self.categoria,
            "lote": self.lote,
            "fecha_vencimiento": self.fecha_vencimiento,
            **self.extras  # Se agregan atributos extra según la categoría
        }

    @staticmethod
    def from_mongo(data):
        return Articulo(
            codigo=data["codigo"],
            nombre=data["nombre"],
            presentaciones=data["presentaciones"],
            categoria=data["categoria"],
            extras={k: v for k, v in data.items() if k not in ["codigo", "nombre", "presentaciones", "categoria"]}
        )
