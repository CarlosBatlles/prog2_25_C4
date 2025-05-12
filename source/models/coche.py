
from mysql.connector import Error

class Coche:
    def __init__(self, id: str, marca: str, modelo: str, matricula: str, categoria_tipo: str, categoria_precio: str,
                año: int, precio_diario: float, kilometraje: float, color: str, combustible: str, cv: int,
                plazas: int, disponible: bool):
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.matricula = matricula
        self.categoria_tipo = categoria_tipo
        self.categoria_precio = categoria_precio
        self.año = año
        self.precio_diario = precio_diario
        self.kilometraje = kilometraje
        self.color = color
        self.combustible = combustible
        self.cv = cv
        self.plazas = plazas
        self.disponible = disponible
        
        
    @staticmethod
    def obtener_todos(connection):
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM coches")
        resultados = cursor.fetchall()
        
        return [Coche(**row)for row in resultados]

    @staticmethod
    def registrar_coche(connection,marca: str, modelo: str, matricula: str, categoria_tipo: str, categoria_precio: str,
                        año: int, precio_diario: float, kilometraje: float, color: str, combustible: str, cv: int,
                        plazas: int, disponible: bool) -> bool:
        """
        Registra un nuevo coche en el sistema.

        Este método realiza validaciones y añade el coche al archivo CSV correspondiente.
        """
        # Validaciones de campos obligatorios
        if not all([marca, modelo, matricula, categoria_tipo, categoria_precio]):
            raise ValueError("Todos los campos de texto (marca, modelo, matricula, categoria_tipo, categoria_precio) deben tener un valor.")

        if precio_diario <= 0:
            raise ValueError("El precio diario debe ser mayor que 0.")
        if kilometraje < 0:
            raise ValueError("El kilometraje no puede ser negativo.")
        if cv <= 0:
            raise ValueError("La potencia del coche debe ser mayor que 0.")
        if plazas < 2:
            raise ValueError("Las plazas del coche deben ser mayores o iguales a 2.")
        if not isinstance(disponible, bool):
            raise TypeError("El campo 'disponible' debe ser True o False.")

        
        try:
            cursor = connection.cursor()
            query = """
            INSERT INTO coches (
                marca, modelo, matricula, categoria_tipo, categoria_precio, año, 
                precio_diario, kilometraje, color, combustible, cv, plazas, disponible
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                marca, modelo, matricula, categoria_tipo, categoria_precio,
                año, precio_diario, kilometraje, color, combustible, cv, plazas, disponible
            )
            cursor.execute(query, valores)
            connection.commit()
            return cursor.lastrowid  # Devuelve el ID generado por MySQL
            
        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al registrar coche en la base de datos: {e}")
        finally:
            if cursor:
                cursor.close()
                
        
    @staticmethod
    def actualizar_matricula(connection,id_coche: int, nueva_matricula: str) -> bool:
        """
        Actualiza la matrícula de un coche existente en el sistema.

        Este método verifica si el ID del coche existe y si la nueva matrícula no está duplicada 
        antes de realizar la actualización en el archivo CSV correspondiente.

        Parameters
        ----------
        connection: mysql.connector.connection.MySQLConnection
            Conexion activa a la base de datos
        id_coche : int
            El ID único del coche cuya matrícula se desea actualizar.
        nueva_matricula : str
            La nueva matrícula que se asignará al coche.

        Returns
        -------
        bool
            True si la matrícula se actualizó correctamente.

        Raises
        ------
        ValueError
            Si el ID del coche no está registrado o si la nueva matrícula ya está en uso.
        Exception
            Si ocurre un error al guardar los cambios en el archivo CSV.
        """
        
        try:
            cursor = connection.cursor()
            
            # Verificar si el coche existe
            cursor.execute("SELECT COUNT(*) FROM coches WHERE id = %s",(id_coche))
            if not cursor.fetchone()[0]:
                raise ValueError(f"El coche con ID {id_coche} no existe")
            
            # Verificar si la nueva matricula ya esta en uso
            cursor.execute("SELECT COUNT(*) FROM coches WHERE matricula = %s",(nueva_matricula))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"La matricula {nueva_matricula} ya está registrada")
            
            query = ("UPDATE coches SET matricula=%s WHERE id = %s")
            valores = (nueva_matricula,id_coche)
            
            cursor.execute(query, valores)
            connection.commit()
            
            if cursor.rowcount > 0:
                return True
            else:
                raise ValueError(f"No se ha podido actualizar la matricula del coche con id: {id_coche}")
            
        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al actualizar la matricula: {e}")
        finally:
            if cursor:
                cursor.close()
    
    
    @staticmethod
    def eliminar_coche(connection, empresa, id_coche: int) -> bool:
        """
        Elimina un coche del sistema basándose en su ID.

        Este método verifica si el coche con el ID proporcionado existe en el sistema 
        y lo elimina del archivo CSV correspondiente.

        Parameters
        ----------
        empresa : Empresa
            Instancia de la clase Empresa para cargar/guardar datos.
        id_coche : str
            El ID único del coche que se desea eliminar.

        Returns
        -------
        bool
            True si el coche se eliminó correctamente.

        Raises
        ------
        ValueError
            Si el coche con el ID proporcionado no está registrado o si ocurre un error al guardar los cambios.

        Notes
        -----
        - Antes de eliminar el coche, se verifica que el ID exista en el sistema.
        - El método utiliza el archivo CSV como fuente de datos, por lo que los cambios son persistentes.
        """
        
        try:
            cursor = connection.cursor()
            
            # Verificar si el coche existe
            cursor.execute("SELECT COUNT(*) FROM coches WHERE id = %s",(id_coche))
            if not cursor.fetchone()[0]:
                raise ValueError(f"El coche con ID {id_coche} no existe")
            
            query = ('DELETE FROM coches WHERE id=%s')
            cursor.execute(query,(id_coche))
            connection.commit()
            
            if cursor.rowcount > 0:
                return True
            else:
                raise ValueError(f"No se ha podido eliminar el coche con id: {id_coche}")
        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al eliminar el coche: {e}")
        finally:
            if cursor:
                cursor.close()
            
        
    @staticmethod
    def cargar_coches_disponibles(connection) -> list:
        """
        Carga todos los coches disponibles desde la base de datos.
        """
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM coches WHERE disponible = TRUE"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Error as e:
            raise ValueError(f"Error al cargar coches disponibles: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            
    
    @staticmethod
    def obtener_categorias_precio(connection) -> list:
        """
        Devuelve una lista única de categorías de precio disponibles.
        """
        try:
            cursor = connection.cursor()
            query = "SELECT DISTINCT categoria_precio FROM coches WHERE disponible = TRUE ORDER BY categoria_precio"
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]
        except Error as e:
            raise ValueError(f"Error al obtener categorías de precio: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
                
                
    @staticmethod
    def obtener_categorias_tipo(connection, categoria_precio: str) -> list:
        """
        Devuelve una lista de categorías de tipo únicas para una categoría de precio específica.
        """
        try:
            cursor = connection.cursor()
            query = """
            SELECT DISTINCT categoria_tipo 
            FROM coches 
            WHERE disponible = TRUE AND categoria_precio = %s
            ORDER BY categoria_tipo
            """
            cursor.execute(query, (categoria_precio,))
            resultados = [row[0] for row in cursor.fetchall()]
            if not resultados:
                raise ValueError("No hay categorías de tipo disponibles.")
            return resultados
        except Error as e:
            raise ValueError(f"Error al obtener categorías de tipo: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    @staticmethod
    def obtener_marcas(connection, categoria_precio: str, categoria_tipo: str) -> list:
        """
        Devuelve una lista de marcas únicas para una combinación de categoría de precio y tipo.
        """
        try:
            cursor = connection.cursor()
            query = """
            SELECT DISTINCT marca 
            FROM coches 
            WHERE disponible = TRUE 
            AND categoria_precio = %s 
            AND categoria_tipo = %s
            ORDER BY marca
            """
            cursor.execute(query, (categoria_precio, categoria_tipo))
            resultados = [row[0] for row in cursor.fetchall()]
            if not resultados:
                raise ValueError("No hay marcas disponibles con esos filtros.")
            return resultados
        except Error as e:
            raise ValueError(f"Error al obtener marcas: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    @staticmethod
    def obtener_modelos(connection, categoria_precio: str, categoria_tipo: str, marca: str) -> list:
        """
        Devuelve una lista de modelos únicos para una marca, categoría de precio y tipo específicos.
        """
        try:
            cursor = connection.cursor()
            query = """
            SELECT DISTINCT modelo 
            FROM coches 
            WHERE disponible = TRUE 
            AND categoria_precio = %s 
            AND categoria_tipo = %s 
            AND marca = %s
            ORDER BY modelo
            """
            cursor.execute(query, (categoria_precio, categoria_tipo, marca))
            resultados = [row[0] for row in cursor.fetchall()]
            if not resultados:
                raise ValueError("No hay modelos disponibles con esos filtros.")
            return resultados
        except Error as e:
            raise ValueError(f"Error al obtener modelos: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    @staticmethod
    def filtrar_por_modelo(connection, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str) -> list:
        """
        Devuelve los coches disponibles que coinciden con todos los criterios:
        categoría de precio, categoría de tipo, marca y modelo.
        """
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT * FROM coches 
            WHERE disponible = TRUE 
            AND categoria_precio = %s 
            AND categoria_tipo = %s 
            AND marca = %s 
            AND modelo = %s
            """
            cursor.execute(query, (categoria_precio, categoria_tipo, marca, modelo))
            resultados = cursor.fetchall()
            if not resultados:
                raise ValueError("No se encontraron coches con estos filtros.")
            return resultados
        except Error as e:
            raise ValueError(f"Error al filtrar por modelo: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    @staticmethod
    def mostrar_categorias_tipo(connection) -> list:
        """
        Muestra las categorías de tipo de los coches disponibles en el sistema.

        Este método consulta la base de datos y devuelve una lista 
        de las categorías de tipo únicas disponibles.

        Parameters
        ----------
        connection : mysql.connection.MySQLConnection
            Conexión activa a la base de datos.

        Returns
        -------
        list
            Una lista de las categorías de tipo únicas de los coches.

        Raises
        ------
        ValueError
            Si no se pueden obtener las categorías de tipo desde la base de datos.
        """
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT DISTINCT categoria_tipo FROM coches WHERE disponible = TRUE ORDER BY categoria_tipo"
            cursor.execute(query)
            resultados = cursor.fetchall()

            if not resultados:
                raise ValueError("No hay categorías de tipo disponibles en la base de datos.")

            return [row['categoria_tipo'] for row in resultados]

        except Error as e:
            raise ValueError(f"Error al obtener las categorías de tipo: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    
    @staticmethod
    def mostrar_categorias_precio(connection) -> list:
        """
        Muestra las categorías de precio de los coches disponibles en el sistema.

        Este método consulta la base de datos y devuelve una lista 
        de las categorías de precio únicas disponibles.

        Parameters
        ----------
        connection : mysql.connection.MySQLConnection
            Conexión activa a la base de datos.

        Returns
        -------
        list
            Una lista de las categorías de precio únicas de los coches.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos o si no hay categorías disponibles.
        """
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT DISTINCT categoria_precio FROM coches WHERE disponible = TRUE ORDER BY categoria_precio"
            cursor.execute(query)
            resultados = cursor.fetchall()

            if not resultados:
                raise ValueError("No hay categorías de precio disponibles en la base de datos.")

            return [row['categoria_precio'] for row in resultados]

        except Error as e:
            raise ValueError(f"Error al obtener las categorías de precio: {e}")

        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    