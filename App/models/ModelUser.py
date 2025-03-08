from .entities.User import User

class ModelUser():
    
    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, password, fullname FROM software2.USER WHERE username = %s"
            cursor.execute(sql, (user.username,))
            row = cursor.fetchone()
            if row is not None:
                if user.check_password(row[2], user.password):
                    authenticated_user = User(row[0], row[1], row[2], row[3])
                    return authenticated_user
                elif (user.password == row[2]):
                    return User(row[0], row[1], row[2], row[3])
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(f"Error al intentar autenticar: {e}")
            raise Exception(e)
        
    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, fullname FROM software2.USER WHERE id = %s"
            cursor.execute(sql, (id,))
            row = cursor.fetchone()
            if row is not None:
                return User(row[0], row[1], row[2])
            else:
                return None
        except Exception as e:
            print(f"Error al intentar autenticar: {e}")
            raise Exception(e)