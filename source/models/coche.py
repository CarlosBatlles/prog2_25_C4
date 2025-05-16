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
                cursor.execute("SELECT 1 FROM coches WHERE id = %s",(id_coche,))
                if cursor.fetchone() is None:
                    raise ValueError(f"El coche con ID {id_coche} no existe")
                
                # Verificar si la nueva matricula ya esta en uso
                cursor.execute("SELECT 1 FROM coches WHERE matricula = %s AND id != %s",(nueva_matricula,id_coche))
                if cursor.fetchone() is not None:
                    raise ValueError(f"La matricula {nueva_matricula} ya está registrada")
                
                query = ("UPDATE coches SET matricula=%s WHERE id = %s")
                valores = (nueva_matricula,id_coche)
                
                cursor.execute(query, valores)
                
                if cursor.rowcount > 0:
                    connection.commit()
                    return True
                else:
                    connection.rollback()
                    raise ValueError(f"No se ha podido actualizar la matricula del coche con id: {id_coche}")
            
        except Error as e:
            connection.rollback()
            raise e

    
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
        if not id_coche.startswith("UID") or not id_coche[3:].isdigit():
            raise ValueError("Formato de ID inválido. Debe ser tipo A001.")

        id_numero = int(id_coche[3:])
        
        try:
            with connection.cursor() as cursor:
                # Verificar si el coche existe
                query = ('DELETE FROM coches WHERE id=%s')
                cursor.execute(query,(id_numero,))
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
    def cargar_coches_disponibles(connection: 'MySQLConnection') -> List[Dict[str, Any]]:
        """
        Obtiene una lista de todos los coches marcados como disponibles en la base de datos.

        Ejecuta una consulta SQL para seleccionar todos los coches de la tabla 'coches'
        donde el campo 'disponible' es TRUE.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[Dict[str, Any]]
            Una lista de diccionarios, donde cada diccionario representa un coche
            disponible y contiene todos sus campos. Retorna una lista vacía
            si no se encuentran coches disponibles.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos
            (e.g., error de conexión, error de sintaxis SQL).
            La excepción original de `mysql.connector` se propaga.
        """

        try:
            with connection.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM coches WHERE disponible = TRUE"
                cursor.execute(query)
                resultados: List[Dict[str, Any]] = cursor.fetchall()
                
                return resultados

        except Error as e:
            raise e
    
    @staticmethod
    def obtener_categorias_precio(connection: 'MySQLConnection') -> List[str]: 
        """
        Obtiene una lista única y ordenada de las categorías de precio de los coches disponibles.

        Ejecuta una consulta SQL para seleccionar los valores distintos de la columna
        'categoria_precio' de la tabla 'coches', filtrando solo por aquellos
        coches que están marcados como 'disponible'. Las categorías se devuelven
        ordenadas alfabéticamente.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[str]
            Una lista de strings, donde cada string es una categoría de precio única.
            Retorna una lista vacía si no se encuentran categorías o coches disponibles.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos
            (e.g., error de conexión, error de sintaxis SQL).
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT DISTINCT categoria_precio 
                    FROM coches 
                    WHERE disponible = TRUE 
                    ORDER BY categoria_precio ASC
                    """
                cursor.execute(query)
                categorias: List[str] = [row[0] for row in cursor.fetchall()]
            
            return categorias
        
        except Error as e:
            raise e
                
    
    @staticmethod
    def obtener_categorias_tipo(
        connection: 'MySQLConnection',
        categoria_precio: str
        ) -> List[str]: 
        """
        Obtiene una lista única y ordenada de tipos de categoría para una categoría de precio dada.

        Filtra los coches disponibles por la `categoria_precio` especificada y
        luego recupera los valores distintos de 'categoria_tipo' para esos coches.
        Los tipos de categoría se devuelven ordenados alfabéticamente.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        categoria_precio : str
            La categoría de precio específica por la cual filtrar los coches
            (e.g., "Económico", "Premium").

        Returns
        -------
        List[str]
            Una lista de strings, donde cada string es un tipo de categoría único
            (e.g., "SUV", "Sedán") para la `categoria_precio` dada.
            Retorna una lista vacía si no se encuentran tipos de categoría para
            la combinación dada o si no hay coches disponibles que coincidan.

        Raises
        ------
        ValueError
            Si `categoria_precio` es inválida (e.g., vacía).
            En la versión original, también si no se encontraban resultados.
            En esta versión, se devuelve lista vacía si no hay resultados,
            a menos que se decida mantener el lanzamiento de error.
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT DISTINCT categoria_tipo 
                    FROM coches 
                    WHERE disponible = TRUE AND categoria_precio = %s
                    ORDER BY categoria_tipo ASC
                """
                cursor.execute(query, (categoria_precio,))
                
            resultados: List[str] = [row[0] for row in cursor.fetchall()]

            if not resultados:
                raise ValueError("No hay categorías de tipo disponibles.")
            return resultados
        
        except Error as e:
            raise e
    
    
    @staticmethod
    def obtener_marcas(
        connection: 'MySQLConnection',
        categoria_precio: str,
        categoria_tipo: str
        ) -> List[str]:
        """
        Obtiene una lista única y ordenada de marcas de coches disponibles
        para una combinación específica de categoría de precio y tipo de categoría.

        Filtra los coches disponibles por la `categoria_precio` y `categoria_tipo`
        especificadas, y luego recupera los valores distintos de 'marca' para
        esos coches. Las marcas se devuelven ordenadas alfabéticamente.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        categoria_precio : str
            La categoría de precio específica por la cual filtrar (e.g., "Económico").
        categoria_tipo : str
            El tipo de categoría específico por el cual filtrar (e.g., "SUV").

        Returns
        -------
        List[str]
            Una lista de strings, donde cada string es una marca única
            (e.g., "Toyota", "Ford") para la combinación de filtros dada.
            Retorna una lista vacía si no se encuentran marcas que coincidan
            con los criterios.

        Raises
        ------
        ValueError
            Si `categoria_precio` o `categoria_tipo` son inválidas (e.g., vacías).
            En la versión original, también si no se encontraban resultados.
            En esta versión, se devuelve lista vacía si no hay resultados.
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT DISTINCT marca 
                    FROM coches 
                    WHERE disponible = TRUE 
                        AND categoria_precio = %s 
                        AND categoria_tipo = %s
                    ORDER BY marca ASC
                """
                # Los parámetros deben pasarse como una tupla
                cursor.execute(query, (categoria_precio, categoria_tipo))

            marcas: List[str] = [row[0] for row in cursor.fetchall()]

            if not marcas:
                raise ValueError("No hay marcas disponibles con esos filtros.")
            return marcas
        except Error as e:
            raise e
    
    
    
    @staticmethod
    def obtener_modelos(
        connection: 'MySQLConnection',
        categoria_precio: str,
        categoria_tipo: str,
        marca: str
        ) -> List[str]:
        """
        Obtiene una lista única y ordenada de modelos de coches disponibles
        para una combinación específica de categoría de precio, tipo de categoría y marca.

        Filtra los coches disponibles por `categoria_precio`, `categoria_tipo` y `marca`
        especificadas, y luego recupera los valores distintos de 'modelo' para
        esos coches. Los modelos se devuelven ordenados alfabéticamente.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        categoria_precio : str
            La categoría de precio específica por la cual filtrar (e.g., "Económico").
        categoria_tipo : str
            El tipo de categoría específico por el cual filtrar (e.g., "SUV").
        marca : str
            La marca específica del coche por la cual filtrar (e.g., "Toyota").

        Returns
        -------
        List[str]
            Una lista de strings, donde cada string es un modelo único
            (e.g., "Corolla", "RAV4") para la combinación de filtros dada.
            Retorna una lista vacía si no se encuentran modelos que coincidan
            con los criterios.

        Raises
        ------
        ValueError
            Si `categoria_precio`, `categoria_tipo` o `marca` son inválidas (e.g., vacías).
            En la versión original, también si no se encontraban resultados.
            En esta versión, se devuelve lista vacía si no hay resultados.
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT DISTINCT modelo 
                    FROM coches 
                    WHERE disponible = TRUE 
                        AND categoria_precio = %s 
                        AND categoria_tipo = %s 
                        AND marca = %s
                    ORDER BY modelo ASC
                """
                cursor.execute(query, (categoria_precio, categoria_tipo, marca))
                
                modelos: List[str] = [row[0] for row in cursor.fetchall()]

            if not modelos:
                raise ValueError("No hay modelos disponibles con esos filtros.")
            return modelos
        except Error as e:
            raise e
    
    
    @staticmethod
    def filtrar_por_modelo(
        connection: 'MySQLConnection',
        categoria_precio: str,
        categoria_tipo: str,
        marca: str,
        modelo: str
        ) -> List[Dict[str, Any]]:
        """
        Obtiene una lista de coches disponibles que coinciden con todos los criterios especificados.

        Filtra los coches de la tabla 'coches' que están marcados como 'disponible'
        y que además coinciden con la `categoria_precio`, `categoria_tipo`, `marca`
        y `modelo` proporcionados.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.
        categoria_precio : str
            La categoría de precio del coche a filtrar.
        categoria_tipo : str
            El tipo de categoría del coche a filtrar.
        marca : str
            La marca del coche a filtrar.
        modelo : str
            El modelo específico del coche a filtrar.

        Returns
        -------
        List[Dict[str, Any]]
            Una lista de diccionarios, donde cada diccionario representa un coche
            que coincide con todos los criterios de filtrado. Contiene todos
            los campos del coche. Retorna una lista vacía si no se encuentran
            coches que coincidan.

        Raises
        ------
        ValueError
            Si alguno de los parámetros de filtro (`categoria_precio`,
            `categoria_tipo`, `marca`, `modelo`) es inválido (e.g., vacío).
            En la versión original, también si no se encontraban resultados.
            En esta versión, se devuelve lista vacía si no hay resultados.
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """

        try:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT * 
                    FROM coches 
                    WHERE disponible = TRUE 
                        AND categoria_precio = %s 
                        AND categoria_tipo = %s 
                        AND marca = %s 
                        AND modelo = %s
                    ORDER BY id ASC -- Opcional: añadir un orden para consistencia
                """
                # Los parámetros deben pasarse como una tupla
                params = (categoria_precio, categoria_tipo, marca, modelo)
                cursor.execute(query, params)
                
                # cursor.fetchall() con dictionary=True devuelve List[Dict[str, Any]]
                resultados: List[Dict[str, Any]] = cursor.fetchall()

            if not resultados:
                raise ValueError("No se encontraron coches con estos filtros.")
            return resultados
        except Error as e:
            raise e
    
    
    @staticmethod
    def mostrar_categorias_tipo(connection: 'MySQLConnection') -> List[str]:
        """
        Obtiene una lista única y ordenada de los tipos de categoría de los coches disponibles.

        Consulta la base de datos para recuperar los valores distintos de la columna
        'categoria_tipo' de la tabla 'coches', considerando solo aquellos coches
        que están marcados como 'disponible'. Las categorías se devuelven
        ordenadas alfabéticamente.

        El nombre "mostrar_" sugiere una acción de UI, pero el método devuelve datos.
        Considerar renombrar a "obtener_categorias_tipo" si es más preciso para su uso.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[str]
            Una lista de strings, donde cada string es un tipo de categoría único
            (e.g., "SUV", "Sedán"). Retorna una lista vacía si no se encuentran
            categorías o coches disponibles.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT DISTINCT categoria_tipo 
                    FROM coches 
                    WHERE disponible = TRUE 
                    ORDER BY categoria_tipo ASC
                """
                cursor.execute(query)
                
                # cursor.fetchall() devolverá una lista de diccionarios,
                # ej: [{'categoria_tipo': 'Compacto'}, {'categoria_tipo': 'SUV'}, ...]
                # La comprensión de listas extrae el valor asociado a la clave 'categoria_tipo'.
                categorias_tipo: List[str] = [row['categoria_tipo'] for row in cursor.fetchall()]
                
            if not categorias_tipo:
                raise ValueError("No hay categorías de tipo disponibles en la base de datos.")
            return categorias_tipo

        except Error as e:
            raise e
    
    
    @staticmethod
    def mostrar_categorias_precio(connection: 'MySQLConnection') -> List[str]:
        """
        Obtiene una lista única y ordenada de las categorías de precio de los coches disponibles.

        Consulta la base de datos para recuperar los valores distintos de la columna
        'categoria_precio' de la tabla 'coches', considerando solo aquellos coches
        que están marcados como 'disponible'. Las categorías se devuelven
        ordenadas alfabéticamente.

        El nombre "mostrar_" sugiere una acción de UI, pero el método devuelve datos.
        Considerar renombrar a "obtener_categorias_precio" si es más preciso para su uso.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[str]
            Una lista de strings, donde cada string es una categoría de precio única
            (e.g., "Económico", "Premium"). Retorna una lista vacía si no se encuentran
            categorías o coches disponibles.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                    SELECT DISTINCT categoria_precio 
                    FROM coches 
                    WHERE disponible = TRUE 
                    ORDER BY categoria_precio ASC
                """
                cursor.execute(query)
                categorias_precio: List[str] = [row['categoria_precio'] for row in cursor.fetchall()]
                
            if not categorias_precio:
                raise ValueError("No hay categorías de precio disponibles en la base de datos.")
            return categorias_precio
        
        except Error as e:
            raise e