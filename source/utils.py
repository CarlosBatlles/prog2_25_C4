# source/utils.py

import hashlib
import re
from fpdf import FPDF
import os
from datetime import datetime


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

        # --- Encabezado: Logo (opcional) y Título ---
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "Logo.png")
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=10, y=8, w=40) # Ajustar x, y, w según necesidad
        except Exception as e:
            raise Exception(f"Error al cargar el logo: {e}")

        # Título
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, txt="Factura de Alquiler", ln=0, align="C") 
        pdf.ln(20) # Salto de línea después del título y logo

        # --- Información General de la Factura ---
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 7, txt=f"ID Alquilerde: {alquiler.get('id_alquiler', 'N/A')}", ln=True, align="R")
        pdf.cell(0, 7, txt=f"Fecha de Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
        pdf.ln(10) # Espacio
        
        # --- Detalles del Cliente ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, txt="Datos del Cliente:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 6, txt=f"  Nombre: {alquiler.get('nombre_usuario', 'Invitado')}", ln=True)
        id_usuario_factura = alquiler.get('id_usuario')
        if id_usuario_factura and id_usuario_factura not in ["INVITADO", "N/A"]: 
            pdf.cell(0, 6, txt=f"  ID Cliente: {id_usuario_factura}", ln=True)
        pdf.ln(8)

        # --- Tabla de Detalles del Alquiler ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, txt="Conceptos Facturados:", ln=True)
        
        # Definir anchos de columna
        col_desc_width = 130
        col_valor_width = 50
        line_height = 8

        # Cabecera de la tabla
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(230, 230, 230) 
        pdf.cell(col_desc_width, line_height, "Descripción", border=1, fill=True, align="C")
        pdf.cell(col_valor_width, line_height, "Importe", border=1, fill=True, align="C", ln=True)

        # Filas de la tabla
        pdf.set_font("Arial", size=10)
        
        # Preparar datos para mostrar en la tabla
        items_factura = [
            (f"Alquiler Vehículo: {alquiler.get('marca', '')} {alquiler.get('modelo', '')} (Matrícula: {alquiler.get('matricula', 'N/A')})", ""), # Usar ""
            (f"  Periodo: Desde {datetime.strptime(alquiler.get('fecha_inicio', '1900-01-01'), '%Y-%m-%d').strftime('%d/%m/%Y')} hasta {datetime.strptime(alquiler.get('fecha_fin', '1900-01-01'), '%Y-%m-%d').strftime('%d/%m/%Y')}", ""), # Usar "" y .get() para fechas
            ("  Precio Base Diario:", f"{alquiler.get('precio_diario', 0.0):.2f} EUR"),
            ("  Descuento Aplicado:", f"{alquiler.get('porcentaje_descuento', 0.0):.0f}%"),
        ]


        for descripcion, valor_str in items_factura:
            pdf.set_font("Arial", "", 10)
            if descripcion.startswith("Alquiler Vehículo:") or descripcion.startswith("  Periodo:"):
                pdf.set_font("Arial", "I", 10)
                
            pdf.cell(col_desc_width, line_height, descripcion, border=1)
            
            if valor_str and "EUR" in valor_str or "%" in valor_str:
                pdf.cell(col_valor_width, line_height, valor_str, border=1, align="R", ln=True)
            else: 
                pdf.cell(col_valor_width, line_height, valor_str, border=1, align="L", ln=True) 
            

        # --- Total General ---
        pdf.ln(5) # Espacio antes del total
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(200, 220, 255) 
        pdf.cell(col_desc_width, line_height + 2, "TOTAL FACTURA (EUR)", border=1, fill=True, align="R")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(col_valor_width, line_height + 2, f"{alquiler.get('coste_total', 0.0):.2f}", border=1, fill=True, align="R", ln=True)
        pdf.ln(15)

        # --- Mensaje Final ---
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(0, 0, 0) 
        pdf.multi_cell(0, 5, txt="Gracias por elegir nuestros servicios. Para cualquier consulta, no dude en contactarnos.", align="C")

        # --- Pie de página ---
        pdf_bytes = pdf.output(dest='S')
        if isinstance(pdf_bytes, str): 
            return pdf_bytes.encode('latin-1')
        return pdf_bytes
    
    except Exception as e:
        raise Exception(f"Error al generar la factura en PDF: {e}")