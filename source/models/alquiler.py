
# --- Imports --
from datetime import date
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from typing import Optional, List, Dict, Any
from source.utils import formatear_id, generar_factura_pdf



# --- Clase Alquiler ---
class Alquiler:
    """
    Representa un alquiler de un coche en el sistema.

    Esta clase encapsula la información de un alquiler, incluyendo el coche,
    el usuario, las fechas y el coste. También proporciona métodos para
    gestionar los alquileres.

    Attributes
    ----------
    id_alquiler : int
        Identificador único del alquiler.
    id_coche : int
        Identificador del coche alquilado.
    id_usuario : Optional[int]
        Identificador del usuario que realizó el alquiler. Puede ser None para invitados.
    fecha_inicio : date
        Fecha de inicio del alquiler.
    fecha_fin : date
        Fecha de fin del alquiler.
    coste_total : float
        Coste total calculado para el alquiler.
    activo : bool
        Indica si el alquiler está actualmente activo (True) o ha finalizado (False).
    """
    def __init__(self, id_alquiler: int, id_coche: int, id_usuario: int,
                fecha_inicio: str, fecha_fin: str, coste_total: float,
                activo: bool = True):
        """
        Inicializa un nuevo objeto Alquiler.

        Parameters
        ----------
        id_alquiler : int
            ID único del alquiler.
        id_coche : int
            ID del coche asociado al alquiler.
        id_usuario : Optional[int]
            ID del usuario que realiza el alquiler. `None` si es un invitado.
        fecha_inicio : Union[str, date]
            Fecha de inicio del alquiler. Si es string, debe ser en formato 'YYYY-MM-DD'.
        fecha_fin : Union[str, date]
            Fecha de fin del alquiler. Si es string, debe ser en formato 'YYYY-MM-DD'.
        coste_total : float
            Costo total del alquiler.
        activo : bool, optional
            Estado del alquiler. Por defecto es `True`.

        Raises
        ------
        ValueError
            Si `fecha_inicio` no es anterior a `fecha_fin`.
        """
        
        # Validar que fecha_inicio sea menor que fecha_fin
        if fecha_inicio >= fecha_fin:
            raise ValueError("Error: La fecha de inicio debe ser anterior a la fecha de fin.")

        self.id_alquiler: int = id_alquiler
        self.id_coche: int = id_coche
        self.id_usuario: Optional[int] = id_usuario
        self.fecha_inicio: date = fecha_inicio
        self.fecha_fin: date = fecha_fin
        self.coste_total: float = coste_total
        self.activo: bool = activo

        
    @staticmethod
    def obtener_todos(connection: 'MySQLConnection') -> List[Dict[str, Any]]:
        """
        Obtiene todos los alquileres registrados desde la base de datos, incluyendo la matrícula del coche.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Una conexión activa a la base de datos MySQL.

        Returns
        -------
        List[Dict[str, Any]]
            Una lista de diccionarios, donde cada diccionario representa un alquiler
            e incluye los datos del alquiler y la matrícula del coche asociado.
            Retorna una lista vacía si no hay alquileres.

        Raises
        ------
        mysql.connector.Error
            Si ocurre un error durante la interacción con la base de datos.
            La excepción original de `mysql.connector` se propaga.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:
                query = """
                SELECT 
                    a.id_alquiler, 
                    a.id_coche, 
                    c.matricula,      -- <--- CAMBIO PRINCIPAL: Seleccionamos la matrícula de la tabla coches
                    a.id_usuario, 
                    a.fecha_inicio, 
                    a.fecha_fin, 
                    a.coste_total, 
                    a.activo
                FROM alquileres a INNER JOIN coches c ON a.id_coche = c.id 
                ORDER BY a.fecha_inicio DESC
                """

                cursor.execute(query)
                resultados: List[Dict[str, Any]] = cursor.fetchall()
                return resultados

        except Error as e:
            raise e


    def obtener_por_id(connection, id_alquiler: str) -> dict:
        """
        Obtiene un alquiler por su ID desde la base de datos.

        Parameters
        ----------
        connection : mysql.connector.connection.MySQLConnection
            Conexión activa a la base de datos.
        id_alquiler : str
            El ID del alquiler en formato A001, A002...

        Returns
        -------
        dict
            Un diccionario con los detalles del alquiler.

        Raises
        ------
        ValueError
            Si no se encuentra el alquiler o si hay errores en la consulta.
        Exception
            Si ocurre un error interno en la conexión con la base de datos.
        """
        if not id_alquiler.startswith("A") or not id_alquiler[1:].isdigit():
            raise ValueError("Formato de ID inválido. Debe ser tipo A001.")

        id_numero = int(id_alquiler[1:])  # A001 → 1

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT 
                id_alquiler, id_coche, id_usuario, 
                fecha_inicio, fecha_fin, coste_total, activo
            FROM alquileres
            WHERE id_alquiler = %s
            """
            cursor.execute(query, (id_numero,))
            resultado = cursor.fetchone()

            if not resultado:
                raise ValueError(f"No se encontró ningún alquiler con ID {id_alquiler}")

            return resultado

        except Error as e:
            raise ValueError(f"Error al obtener alquiler: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    @staticmethod
    def alquilar_coche(connection, matricula: str, fecha_inicio: date, fecha_fin: date, email: str = None) -> bytes:
        """
        Registra un nuevo alquiler en la base de datos y devuelve una factura en PDF.

        Parameters
        ----------
        connection : mysql.connection.MySQLConnection
            Conexión activa a la base de datos.
        matricula : str
            Matrícula del coche a alquilar.
        fecha_inicio : date
            Fecha de inicio del alquiler como objeto `date`.
        fecha_fin : date
            Fecha de fin del alquiler como objeto `date`.
        email : str, optional
            Correo electrónico del usuario. Si no se proporciona, se asume un alquiler como invitado.

        Returns
        -------
        bytes
            Bytes del archivo PDF generado como factura del alquiler.

        Raises
        ------
        ValueError
            Si hay errores en fechas, matrícula, correo o inserción en base de datos.
        Exception
            Si ocurre un error interno en la conexión con la base de datos.
        """
        try:
            cursor = connection.cursor(dictionary=True)

            # Verificar si el coche existe y está disponible
            cursor.execute("SELECT * FROM coches WHERE matricula = %s", (matricula,))
            coche = cursor.fetchone()
            if not coche:
                raise ValueError(f"No se encontró ningún coche con la matrícula {matricula}.")
            if not coche['disponible']:
                raise ValueError(f"El coche {coche['marca']} - {coche['modelo']} no está disponible.")

            # Calcular el precio total usando el método ya creado
            componentes_precio = Alquiler.calcular_precio_total(connection, matricula, fecha_inicio, fecha_fin, email)

            precio_total = componentes_precio['precio_total']
            precio_diario = componentes_precio['precio_diario']
            porcentaje_descuento_factura = (1 - componentes_precio["tasa_descuento"]) * 100
            # Registrar el alquiler en la base de datos
            id_usuario = None
            nombre_usuario = "Invitado"

            if email:
                cursor.execute("SELECT id_usuario, nombre FROM usuarios WHERE email = %s", (email,))
                resultado = cursor.fetchone()
                if not resultado:
                    raise ValueError(f"No se encontró el usuario con email: {email}")
                id_usuario = resultado['id_usuario']
                nombre_usuario = resultado['nombre']

            query_insert = """
            INSERT INTO alquileres (
                id_coche, id_usuario, fecha_inicio, fecha_fin, coste_total, activo
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """

            valores_insert = (
                coche['id'], id_usuario, fecha_inicio, fecha_fin,
                precio_total, True
            )

            cursor.execute(query_insert, valores_insert)
            connection.commit()

            id_alquiler_generado = cursor.lastrowid

            # Marcar el coche como no disponible
            cursor.execute("UPDATE coches SET disponible = FALSE WHERE matricula = %s", (matricula,))
            connection.commit()

            # Preparar datos para la factura
            datos_factura = {
                'id_alquiler': formatear_id(id_alquiler_generado, "A"),
                'marca': coche['marca'],
                'modelo': coche['modelo'],
                'matricula': coche['matricula'],
                'fecha_inicio': str(fecha_inicio),
                'fecha_fin': str(fecha_fin),
                'precio_diario': round(precio_diario, 2),                'porcentaje_descuento': round(porcentaje_descuento_factura, 0), 
                'coste_total': round(precio_total, 2),
                'id_usuario': formatear_id(id_usuario, "U") if id_usuario is not None else "INVITADO",
                'nombre_usuario': nombre_usuario
            }

            #  Generar factura usando el método ya definido en la misma clase
            pdf_bytes = generar_factura_pdf(datos_factura)
            return pdf_bytes

        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al registrar el alquiler: {e}")
        finally:
            if cursor:
                cursor.close()
        

    def finalizar_alquiler(connection, id_alquiler: str) -> bool:
        """
        Finaliza un alquiler existente y marca el coche como disponible.

        Este método verifica si el alquiler con el ID proporcionado existe y está activo.
        Si es así, lo marca como inactivo y actualiza el estado del coche asociado.

        Parameters
        ----------
        connection : mysql.connection.MySQLConnection
            Conexión activa a la base de datos.
        id_alquiler : str
            El ID único del alquiler (ej. 'A001').

        Returns
        -------
        bool
            True si el alquiler se finalizó correctamente.

        Raises
        ------
        ValueError
            Si no se pueden cargar los datos o si el alquiler no cumple las condiciones necesarias.
        Exception
            Si ocurre un error interno en la base de datos.
        """
        try:
            cursor = connection.cursor(dictionary=True)

            # Validar formato del ID ('A001' → 1)
            if not id_alquiler.startswith("A") or not id_alquiler[1:].isdigit():
                raise ValueError(f"Formato de ID inválido. Debe ser tipo A001, A002...")

            id_numero = int(id_alquiler[1:])  # A001 → 1

            # Verificar si el alquiler existe y está activo
            cursor.execute("SELECT * FROM alquileres WHERE id_alquiler = %s AND activo = TRUE", (id_numero,))
            alquiler = cursor.fetchone()

            if not alquiler:
                raise ValueError(f"No hay ningún alquiler activo con el ID {id_alquiler}")

            id_coche = alquiler['id_coche']

            # Marcar alquiler como inactivo
            cursor.execute("UPDATE alquileres SET activo = FALSE WHERE id_alquiler = %s", (id_numero,))
            if cursor.rowcount == 0:
                raise ValueError(f"No se pudo marcar como inactivo el alquiler {id_alquiler}")

            # Marcar coche como disponible
            cursor.execute("UPDATE coches SET disponible = TRUE WHERE id = %s", (id_coche,))
            if cursor.rowcount == 0:
                raise ValueError(f"No se pudo marcar como disponible el coche con ID {id_coche}")

            connection.commit()
            return True

        except Error as e:
            connection.rollback()
            raise ValueError(f"Error al finalizar el alquiler: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
        

    @staticmethod
    def calcular_precio_total(connection, matricula: str, fecha_inicio: date, fecha_fin: date, email: str = None) -> float:
        """
        Calcula el precio total del alquiler de un coche basándose en días, precio diario y tipo de usuario.

        Parameters
        ----------
        connection : mysql.connection.MySQLConnection
            Conexión activa a la base de datos.
        matricula : str
            Matrícula del coche que se desea alquilar.
        fecha_inicio : date
            Fecha de inicio del alquiler.
        fecha_fin : date
            Fecha de fin del alquiler.
        email : str, optional
            Correo electrónico del usuario. Si no se proporciona, se asume un usuario normal sin descuento.

        Returns
        -------
        float
            El precio total del alquiler en euros.

        Raises
        ------
        ValueError
            Si hay errores en fechas, matrícula o correo.
        Exception
            Si ocurre un error interno en la base de datos.
        """
        try:
            with connection.cursor(dictionary=True) as cursor:

                # Validar fechas
                if fecha_inicio > fecha_fin:
                    raise ValueError("La fecha de inicio no puede ser mayor a la fecha final.")

                # Buscar el coche por matrícula
                cursor.execute("SELECT id,marca, modelo, precio_diario, disponible FROM coches WHERE matricula = %s", (matricula,))
                coche = cursor.fetchone()
                if not coche:
                    raise ValueError(f"No se encontró ningún coche con la matrícula: {matricula}.")
                if not coche['disponible']:
                    raise ValueError(f"El coche con matrícula {matricula} no está disponible.")

                # Determinar tipo de usuario
                tipo_usuario = 'normal'
                if email:
                    cursor.execute("SELECT tipo FROM usuarios WHERE email = %s", (email,))
                    resultado = cursor.fetchone()
                    if not resultado:
                        raise ValueError(f"No se encontró el correo {email}")
                    tipo_usuario = resultado['tipo'].lower()

                # Definir descuentos
                descuentos = {
                    'cliente': 0.94,
                    'admin': 1.0,
                    'normal': 1.0
                }
                descuento = descuentos.get(tipo_usuario, 1.0)
                # Calcular rango de días
                dias = (fecha_fin - fecha_inicio).days
                if dias <= 0:
                    raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin.")

                
                # Calcular precio total
                precio_diario = float(coche['precio_diario'])
                precio_total = precio_diario * dias * descuento

                return {
                    'precio_diario': precio_diario,
                    'tasa_descuento':descuento,
                    'precio_total':round(precio_total, 2)}

        except Error as e:
            raise ValueError(f"Error al calcular el precio: {e}")

    