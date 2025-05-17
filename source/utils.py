
# --- Imports ---
import hashlib
import re
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union # Añadido Optional y Union
from fpdf import FPDF


# --------------------------------------------------------------------------
# SECCIÓN 1: FUNCIONES DE SEGURIDAD Y VALIDACIÓN
# --------------------------------------------------------------------------


def hash_contraseña(contraseña: str) -> str:
    """
    Genera un hash SHA-256 de la contraseña proporcionada.

    Utiliza la codificación UTF-8 para la contraseña antes de hashearla
    y devuelve el hash como una cadena hexadecimal.

    Parameters
    ----------
    contraseña : str
        La contraseña en texto plano que se desea hashear.

    Returns
    -------
    str
        El hash SHA-256 de la contraseña, representado como una cadena
        hexadecimal de 64 caracteres.

    Examples
    --------
    hash_contraseña("miClaveSegura123")
    '...' # (el hash correspondiente)

    return hashlib.sha256(contraseña.encode()).hexdigest()
    """
    # Genera un hash SHA-256 de la contraseña
    return hashlib.sha256(contraseña.encode()).hexdigest()

def es_email_valido(email: Optional[str]) -> bool:
    """
    Verifica si una cadena de texto tiene el formato de un correo electrónico válido.

    Utiliza una expresión regular para comprobar si el formato del email
    cumple con los patrones comunes de direcciones de correo electrónico.

    Parameters
    ----------
    email : Optional[str]
        El correo electrónico que se desea validar. Puede ser `None`.

    Returns
    -------
    bool
        `True` si el `email` es una cadena no vacía y coincide con el patrón
        de email válido, `False` en caso contrario (incluyendo si `email` es `None`
        o una cadena vacía).

    Examples
    --------
    >>> es_email_valido("usuario@ejemplo.com")
    True
    >>> es_email_valido("usuario.ejemplo.com")
    False
    >>> es_email_valido(None)
    False
    >>> es_email_valido("")
    False

    Notes
    -----
    - El patrón de expresión regular utilizado es una aproximación común y cubre
    la mayoría de los casos, pero la validación completa de emails según RFC
    es extremadamente compleja.
    - Esta función no verifica si el dominio del email existe o si el buzón está activo.
    """
    patron: str = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.fullmatch(patron, email): # fullmatch para asegurar que todo el string coincida
        return True
    return False


# --------------------------------------------------------------------------
# SECCIÓN 3: FUNCIONES DE FORMATEO
# --------------------------------------------------------------------------


def formatear_id(id_registro: Optional[Union[int, str]], prefijo: str) -> str:
    """
    Convierte un ID numérico o string numérico en un formato con prefijo y padding de ceros.

    Asegura que la parte numérica del ID tenga al menos 3 dígitos,
    añadiendo ceros a la izquierda si es necesario.

    Parameters
    ----------
    id_registro : Optional[Union[int, str]]
        El ID numérico o string que representa un número.
        Si es `None`, se devuelve un valor por defecto "N/A" o similar.
    prefijo : str
        El prefijo a añadir al ID formateado (e.g., "UID", "A", "U").

    Returns
    -------
    str
        El ID formateado como una cadena de texto (e.g., "UID001", "A007").
        Devuelve `f"{prefijo}N/A"` si `id_registro` es `None`.
    
    Ejemplos:
        formatear_id(1, 'UID') → 'UID001'
        formatear_id(10, 'U')   → 'U010'
        formatear_id(7, 'A')    → 'A007'
    """
    return f"{prefijo}{id_registro:03d}"


# --------------------------------------------------------------------------
# SECCIÓN 4: GENERACIÓN DE DOCUMENTOS
# --------------------------------------------------------------------------


def generar_factura_pdf(alquiler: dict) -> bytes:
    """
    Genera una factura en formato PDF para un alquiler específico.

    Utiliza la librería FPDF para construir el documento PDF con los detalles
    proporcionados del alquiler.

    Parameters
    ----------
    alquiler_info : Dict[str, Any]
        Diccionario con los datos del alquiler. Se esperan las siguientes claves:
        - 'id_alquiler' (str): ID formateado del alquiler (e.g., "A001").
        - 'marca' (str): Marca del coche.
        - 'modelo' (str): Modelo del coche.
        - 'matricula' (str): Matrícula del coche.
        - 'fecha_inicio' (str): Fecha de inicio del alquiler en formato 'YYYY-MM-DD'.
        - 'fecha_fin' (str): Fecha de fin del alquiler en formato 'YYYY-MM-DD'.
        - 'precio_diario' (float): Precio diario del coche.
        - 'porcentaje_descuento' (float): Porcentaje de descuento aplicado (e.g., 6.0 para 6%).
        - 'coste_total' (float): Costo total final del alquiler.
        - 'nombre_usuario' (str, optional): Nombre del cliente. Por defecto "Invitado".
        - 'id_usuario' (str, optional): ID formateado del usuario.

    Returns
    -------
    bytes
        El contenido del archivo PDF generado como una secuencia de bytes.

    Raises
    ------
    ValueError
        Si faltan campos obligatorios en `alquiler_info` o si las fechas
        son inválidas.
    Exception
        Si ocurre cualquier otro error durante la generación del PDF.
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
        pdf.cell(0, 7, txt=f"ID Alquiler: {alquiler.get('id_alquiler', 'N/A')}", ln=True, align="R")
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
            (f"Alquiler Vehículo: {alquiler.get('marca', '')} {alquiler.get('modelo', '')} (Matrícula: {alquiler.get('matricula', 'N/A')})", ""),
            (f"  Periodo: Desde {datetime.strptime(alquiler.get('fecha_inicio', '1900-01-01'), '%Y-%m-%d').strftime('%d/%m/%Y')} hasta {datetime.strptime(alquiler.get('fecha_fin', '1900-01-01'), '%Y-%m-%d').strftime('%d/%m/%Y')}", ""), 
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