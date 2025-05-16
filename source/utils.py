# source/utils.py

import hashlib
import re
from fpdf import FPDF
import os
from datetime import datetime
from data import Logo


def hash_contraseña(contraseña: str) -> str:
    """
    Genera un hash SHA-256 de la contraseña proporcionada.

    Parameters
    ----------
    contraseña : str
        La contraseña que se desea hashear.

    Returns
    -------
    str
        Un hash SHA-256 de la contraseña en formato hexadecimal.

    Notes
    -----
    Este método utiliza la biblioteca hashlib para generar un hash seguro de la contraseña.
    El resultado es una cadena hexadecimal de 64 caracteres.
    """
    return hashlib.sha256(contraseña.encode()).hexdigest()


def es_email_valido(email: str) -> bool:
    """
    Verifica si un correo electrónico es válido utilizando una expresión regular.

    Parameters
    ----------
    email : str
        El correo electrónico que se desea validar.

    Returns
    -------
    bool
        True si el correo electrónico es válido, False en caso contrario.

    Notes
    -----
    Esta función utiliza una expresión regular para validar el formato del correo electrónico.
    El patrón utilizado sigue las reglas estándar para correos electrónicos válidos.
    """
    patron = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(patron, email) is not None


def formatear_id(id_registro: int, prefijo: str) -> str:
    """
    Convierte un ID numérico en un formato amigable con prefijo.
    
    Ejemplos:
        formatear_id(1, 'UID') → 'UID001'
        formatear_id(10, 'U')   → 'U010'
        formatear_id(7, 'A')    → 'A007'
    """
    return f"{prefijo}{id_registro:03d}"


def generar_factura_pdf(alquiler: dict) -> bytes:
    """
    Genera una factura en formato PDF para un alquiler específico.

    Parameters
    ----------
    alquiler : dict
        Diccionario con los siguientes campos:
        - id_alquiler (str): ID único del alquiler.
        - marca (str): Marca del coche.
        - modelo (str): Modelo del coche.
        - matricula (str): Matrícula del coche.
        - fecha_inicio (str): Fecha de inicio ('YYYY-MM-DD').
        - fecha_fin (str): Fecha de fin ('YYYY-MM-DD').
        - coste_total (float): Costo total del alquiler.
        - nombre_usuario (str, optional): Nombre del cliente.

    Returns
    -------
    bytes
        El archivo PDF generado como bytes.

    Raises
    ------
    ValueError
        Si faltan datos obligatorios.
    Exception
        Si ocurre un error durante la generación del PDF.
    """
    # Validaciones básicas
    campos_obligatorios = ['id_alquiler', 'marca', 'modelo', 'matricula', 'fecha_inicio', 'fecha_fin', 'coste_total']
    for campo in campos_obligatorios:
        if campo not in alquiler:
            raise ValueError(f"Falta el campo '{campo}' en el diccionario de alquiler.")

    try:
        pdf = FPDF()
        pdf.add_page()

        # Intentar cargar el logo
        try:
            logo_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "..","data","Logo.png")
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=10, y=10, w=50)
        except Exception as e:
            raise Exception(f"Error al cargar el logo: {e}")

        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 20, txt="Factura de Alquiler", ln=True, align="C")
        pdf.ln(10)

        # Fecha de emisión
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=f"Fecha de Emisión: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="C")
        pdf.ln(10)

        # Tabla de detalles
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 12)

        ancho_tabla = 150
        posicion_x = (pdf.w - ancho_tabla) / 2

        pdf.set_x(posicion_x)
        pdf.cell(50, 10, "Campo", border=1, fill=True)
        pdf.cell(100, 10, "Valor", border=1, fill=True, ln=True)

        pdf.set_font("Arial", size=12)

        # Datos del alquiler sin caracteres UTF-8 problemáticos
        datos_factura = [
            ("ID de Alquiler", alquiler['id_alquiler']),
            ("Marca", alquiler['marca']),
            ("Modelo", alquiler['modelo']),
            ("Matrícula", alquiler['matricula']),
            ("Fecha Inicio", datetime.strptime(alquiler['fecha_inicio'], "%Y-%m-%d").strftime("%d/%m/%Y")),
            ("Fecha Fin", datetime.strptime(alquiler['fecha_fin'], "%Y-%m-%d").strftime("%d/%m/%Y")),
            ("Precio Diario", f"{alquiler.get('precio_diario', 'N/A')}"),
            ("Descuento", f"{alquiler.get('descuento', 0) * 100:.0f}%"),
            ("Total", f"{alquiler['coste_total']:.2f} EUR"),
            ("Cliente", alquiler.get('nombre_usuario', 'Invitado')),
        ]

        for campo, valor in datos_factura:
            pdf.set_x(posicion_x)
            pdf.cell(50, 10, str(campo), border=1)
            pdf.cell(100, 10, str(valor), border=1, ln=True)

        # Precio total destacado
        pdf.ln(10)
        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, txt=f"Precio Total: {alquiler['coste_total']:.2f} EUR", ln=True, align="R")

        # Mensaje final
        pdf.ln(10)
        pdf.set_font("Arial", "I", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, txt="Gracias por elegirnos. ¡Esperamos verte pronto!", ln=True, align="C")

        # Devolver el PDF como bytes usando codificación segura
        return pdf.output(dest='S').encode('latin1')

    except Exception as e:
        raise Exception(f"Error al generar la factura en PDF: {e}")