# source/utils.py

def formatear_id(id_registro: int, prefijo: str) -> str:
    """
    Convierte un ID numérico en un formato amigable con prefijo.
    
    Ejemplos:
        formatear_id(1, 'UID') → 'UID001'
        formatear_id(10, 'U')   → 'U010'
        formatear_id(7, 'A')    → 'A007'
    """
    return f"{prefijo}{id_registro:03d}"