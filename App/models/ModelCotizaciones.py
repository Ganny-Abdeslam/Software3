from .entities.Cotizaciones import Cotizaciones

class ModelCotizaciones():

    @classmethod
    def traerCotizacion(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT c.id, idUser, fecha, informacion, fullname FROM software2.cotizacion c INNER JOIN software2.user us on (us.id = idUser) WHERE idUser = %s"
            cursor.execute(sql, (id,))
            rows = cursor.fetchall()
            if rows is not None:
                cotizaciones = [
                    {
                        "id": row[0],
                        "idUser": row[1],
                        "fecha": row[2],
                        "informacion": row[3],
                        "fullname": row[4]
                    } for row in rows
                ]
                return cotizaciones
            else:
                return None
        except Exception as e:
            print(f"Error al intentar autenticar: {e}")
            raise Exception(e)