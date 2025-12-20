"""Utilidades para manejo seguro de fechas en MatrixMAE."""

from datetime import datetime, time


def normalize_to_naive(dt: datetime) -> datetime:
    """
    Convierte un datetime a naive (sin zona horaria).
    
    Args:
        dt: datetime que puede ser aware o naive
        
    Returns:
        datetime naive (sin tzinfo)
    """
    if dt is None:
        return None
    
    # Si ya es naive, retornar tal cual
    if dt.tzinfo is None:
        return dt
    
    # Si es aware, convertir a naive eliminando tzinfo
    # Nota: esto preserva la fecha/hora local sin convertir
    return dt.replace(tzinfo=None)


def get_day_start(dt: datetime) -> datetime:
    """
    Obtiene el inicio del día (00:00:00.000000) para una fecha.
    
    Args:
        dt: datetime de referencia
        
    Returns:
        datetime al inicio del día (naive)
    """
    dt_naive = normalize_to_naive(dt)
    return datetime.combine(dt_naive.date(), time.min)


def get_day_end(dt: datetime) -> datetime:
    """
    Obtiene el fin del día (23:59:59.999999) para una fecha.
    
    Args:
        dt: datetime de referencia
        
    Returns:
        datetime al final del día (naive)
    """
    dt_naive = normalize_to_naive(dt)
    return datetime.combine(dt_naive.date(), time.max)


def compare_dates(dt1: datetime, dt2: datetime) -> int:
    """
    Compara dos fechas de forma segura (maneja naive y aware).
    
    Args:
        dt1: primera fecha
        dt2: segunda fecha
        
    Returns:
        -1 si dt1 < dt2
         0 si dt1 == dt2
         1 si dt1 > dt2
    """
    # Normalizar ambas a naive
    dt1_naive = normalize_to_naive(dt1)
    dt2_naive = normalize_to_naive(dt2)
    
    if dt1_naive < dt2_naive:
        return -1
    elif dt1_naive > dt2_naive:
        return 1
    else:
        return 0


def validate_date_range(fecha_inicio: datetime, fecha_fin: datetime) -> tuple[bool, str]:
    """
    Valida un rango de fechas de forma segura.
    
    Args:
        fecha_inicio: fecha inicial
        fecha_fin: fecha final
        
    Returns:
        (bool, str): (es_valido, mensaje_error)
    """
    if not fecha_inicio or not fecha_fin:
        return False, "Debe seleccionar fechas de inicio y fin"
    
    # Normalizar para comparación segura
    inicio_naive = normalize_to_naive(fecha_inicio)
    fin_naive = normalize_to_naive(fecha_fin)
    
    if inicio_naive > fin_naive:
        return False, "La fecha de inicio no puede ser posterior a la fecha fin"
    
    return True, ""


def is_date_in_range(fecha: datetime, fecha_inicio: datetime, fecha_fin: datetime) -> bool:
    """
    Verifica si una fecha está dentro de un rango (inclusive).
    
    Args:
        fecha: fecha a verificar
        fecha_inicio: inicio del rango
        fecha_fin: fin del rango
        
    Returns:
        bool: True si está en el rango
    """
    # Normalizar todas las fechas
    fecha_naive = normalize_to_naive(fecha)
    inicio_naive = normalize_to_naive(fecha_inicio)
    fin_naive = normalize_to_naive(fecha_fin)
    
    return inicio_naive <= fecha_naive <= fin_naive