from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from typing import Optional, List, Dict, Any


class Coche:
    """
    Representa un coche en el sistema de alquiler.
    """
    def __init__(self, id: str, marca: str, modelo: str, matricula: str, categoria_tipo: str, categoria_precio: str,
                año: int, precio_diario: float, kilometraje: float, color: str, combustible: str, cv: int,
                plazas: int, disponible: bool):
        """
        Inicializa una nueva instancia de Coche.

        Parameters
        ----------
        id : str
            Identificador único del coche.
        marca : str
            Marca del coche.
        modelo : str
            Modelo del coche.
        matricula : str
            Matrícula del coche.
        categoria_tipo : str
            Tipo de categoría del coche (e.g., "SUV", "Sedán").
        categoria_precio : str
            Categoría de precio del coche (e.g., "Económico", "Premium").
        año : int
            Año de fabricación del coche.
        precio_diario : float
            Precio del alquiler por día.
        kilometraje : float
            Kilometraje actual del coche.
        color : str
            Color del coche.
        combustible : str
            Tipo de combustible del coche.
        cv : int
            Caballos de vapor del coche.
        plazas : int
            Número de plazas del coche.
        disponible : bool
            Estado de disponibilidad del coche.
        """
        self.id: str = id
        self.marca: str = marca
        self.modelo: str = modelo
        self.matricula: str = matricula
        self.categoria_tipo: str = categoria_tipo
        self.categoria_precio: str = categoria_precio
        self.año: int = año
        self.precio_diario: float = precio_diario
        self.kilometraje: float = kilometraje
        self.color: str = color
        self.combustible: str = combustible
        self.cv: int = cv
        self.plazas: int = plazas
        self.disponible: bool = disponible
        
    @staticmethod
    def obtener_todos(connection:'MySQLConnection') -> List['Coche']:
        """
        Recupera todos los coches de la base de datos.

        Este método ejecuta una consulta SQL para seleccionar todos los registros
        de la tabla 'coches' y los convierte en una lista de instancias
        de la clase Coche.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[Coche]
            Una lista de objetos `Coche`. Retorna una lista vacía si no se
            encuentran coches en la base de datos.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM coches")
                resultados = cursor.fetchall() # Lista de diccionarios
                coches = [Coche(**row) for row in resultados]
            return coches
        except Error as e:
            raise e
    
    @staticmethod
    def obtener_por_matricula(
        connection: 'MySQLConnection',
        matricula: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles de un coche por su matrícula desde la base de datos.

        Busca un coche en la tabla 'coches' que coincida con la matrícula proporcionada
        y devuelve sus datos como un diccionario.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        matricula : str
            La matrícula del coche a buscar.

        Returns
        -------
        Optional[Dict[str, Any]]
            Un diccionario conteniendo los datos del coche si se encuentra.
            Los nombres de las claves del diccionario corresponden a los nombres
            de las columnas en la tabla 'coches'.
            Retorna `None` si no se encuentra ningún coche con la matrícula dada.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la ejecución de la consulta SQL
            (e.g., problema de conexión, error de sintaxis SQL).
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM coches WHERE matricula = %s"
                cursor.execute(query, (matricula,))
                resultado: Optional[Dict[str, Any]] = cursor.fetchone()
                return resultado

        except Error as e:
            raise e



    @staticmethod
    def registrar_coche(
        connection: 'MySQLConnection',
        marca: str,
        modelo: str,
        matricula: str,
        categoria_tipo: str,
        categoria_precio: str,
        año: int,
        precio_diario: float,
        kilometraje: float,
        color: str,
        combustible: str,
        cv: int,
        plazas: int,
        disponible: bool
        ) -> int:
        """
        Registra un nuevo coche en la base de datos tras validar los datos.

        Este método primero valida que los datos proporcionados cumplan con ciertos
        criterios (campos obligatorios, rangos numéricos, tipo booleano).
        Si las validaciones son exitosas, inserta el nuevo coche en la tabla 'coches'.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        marca : str
            Marca del coche.
        modelo : str
            Modelo del coche.
        matricula : str
            Matrícula única del coche.
        categoria_tipo : str
            Tipo de categoría del coche (e.g., "SUV", "Sedán").
        categoria_precio : str
            Categoría de precio del coche (e.g., "Económico", "Premium").
        año : int
            Año de fabricación del coche.
        precio_diario : float
            Precio del alquiler por día. Debe ser mayor que 0.
        kilometraje : float
            Kilometraje actual del coche. No puede ser negativo.
        color : str
            Color del coche.
        combustible : str
            Tipo de combustible del coche.
        cv : int
            Caballos de vapor del coche. Debe ser mayor que 0.
        plazas : int
            Número de plazas del coche. Debe ser mayor o igual a 2.
        disponible : bool
            Estado de disponibilidad inicial del coche.

        Returns
        -------
        int
            El ID del coche recién registrado, generado por la base de datos
            (usualmente el valor de la clave primaria autoincremental).

        Raises
        ------
        ValueError
            Si alguna de las validaciones de los datos de entrada falla,
            o si ocurre un error al interactuar con la base de datos que no sea
            un `mysql.connector.Error` directo (aunque aquí se envuelve).
        TypeError
            Si el campo 'disponible' no es un booleano.
        mysql.connector.Error
            Si ocurre un error específico de la base de datos durante la inserción
            (e.g., violación de constraint UNIQUE para matrícula, error de conexión).
            El método propaga esta excepción.
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
            with connection.cursor() as cursor:
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
                last_id = cursor.lastrowid  # Devuelve el ID generado por MySQL
                return last_id
            
        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al registrar coche en la base de datos: {e}")

                
    
    @staticmethod
    def actualizar_matricula(
        connection: 'MySQLConnection',
        id_coche: int,
        nueva_matricula: str
        ) -> bool:  
        """
        Actualiza la matrícula de un coche existente en la base de datos.

        Este método primero verifica que el coche con `id_coche` exista.
        Luego, comprueba que la `nueva_matricula` no esté ya en uso por otro coche.
        Si ambas verificaciones son exitosas, procede a actualizar la matrícula.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        id_coche : int
            El ID único del coche cuya matrícula se va a actualizar.
        nueva_matricula : str
            La nueva matrícula que se asignará al coche. Se recomienda validar
            su formato y longitud antes de llamar a este método.

        Returns
        -------
        bool
            `True` si la matrícula se actualizó correctamente (es decir, si la
            sentencia UPDATE afectó a una o más filas).

        Raises
        ------
        ValueError
            - Si el `id_coche` no corresponde a un coche existente.
            - Si la `nueva_matricula` ya está registrada para otro coche.
            - Si la actualización no afecta a ninguna fila (inesperado si el coche existe).
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            Se propaga la excepción original de la base de datos.
        """

        
        try:
            with connection.cursor() as cursor:
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

    
    @staticmethod
    def eliminar_coche(connection,id_coche: int) -> bool:
        """
        Elimina un coche de la base de datos basándose en su ID.

        Este método primero intenta eliminar el coche con el ID proporcionado.
        Si la operación de eliminación no afecta a ninguna fila (es decir,
        el coche no existía o ya había sido eliminado), se considera que
        el coche no se encontró y se podría lanzar un error o devolver False
        según la política deseada.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        id_coche : int
            El ID único del coche que se desea eliminar.

        Returns
        -------
        bool
            `True` si el coche se eliminó correctamente (es decir, si la
            sentencia DELETE afectó a una o más filas).

        Raises
        ------
        ValueError
            - Si `id_coche` es inválido (e.g., no positivo).
            - Si la eliminación no afecta a ninguna fila y la política es tratar
            esto como un error de "no encontrado" (como en tu código original).
        mysql.connector.Error
            Si ocurre un error específico de la base de datos durante la eliminación
            (e.g., problemas de conexión, violación de claves foráneas si
            el coche está referenciado en alquileres y no hay CASCADE DELETE).
            La excepción original de `mysql.connector` se propaga.
        """
        
        try:
            with connection.cursor() as cursor:
                # Verificar si el coche existe
                query = ('DELETE FROM coches WHERE id=%s')
                cursor.execute(query,(id_coche,))
                if cursor.rowcount > 0:
                    connection.commit() # Hacer commit SOLO si la eliminación tuvo efecto
                    return True
                else:
                    connection.rollback()
                    raise ValueError(
                        f"No se encontró o no se pudo eliminar el coche con ID {id_coche}. "
                        "Es posible que el ID no exista.")

        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al eliminar el coche: {e}")
            
        
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
    
    
    
    def filtrar_por_modelo(connection, categoria_precio: str, categoria_tipo: str, marca: str, modelo: str) -> list[dict]:
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
    
    