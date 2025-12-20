"""Sistema de auditoría de correos procesados para MatrixMAE.

Dependencias:
    - polars: Para manejo eficiente de DataFrames
    - xlsxwriter: Para exportación a Excel (instalar con: pip install xlsxwriter)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import polars as pl


class EmailAuditor:
    """
    Auditor de correos procesados con exportación a Parquet y Excel.
    
    Registra metadata completa de cada correo procesado para debugging
    y análisis de falsos negativos/positivos.
    """
    
    def __init__(self, ruta_salida: str):
        """
        Inicializa el auditor.
        
        Args:
            ruta_salida: Carpeta donde se guardarán los archivos de auditoría
        """
        self.ruta_salida = Path(ruta_salida)
        self.registros: List[Dict] = []
        
        # Timestamp para archivos
        self.timestamp = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
        
        # Rutas de archivos
        self.archivo_parquet = self.ruta_salida / f"auditoria_correos_{self.timestamp}.parquet"
        self.archivo_excel = self.ruta_salida / f"auditoria_correos_{self.timestamp}.xlsx"
    
    def registrar_correo(self, 
                        entry_id: str,
                        received_time: datetime,
                        subject: str,
                        sender: str,
                        cumple_fecha: bool,
                        cumple_frases: bool,
                        tiene_adjuntos: bool,
                        num_adjuntos: int = 0,
                        adjuntos_nombres: Optional[List[str]] = None,
                        adjuntos_descargados: int = 0,
                        estado_final: str = "PROCESADO",
                        motivo_rechazo: str = "",
                        fase_proceso: str = "FILTRADO"):
        """
        Registra la metadata de un correo procesado.
        
        Args:
            entry_id: ID único del correo
            received_time: Fecha de recepción
            subject: Asunto del correo
            sender: Remitente
            cumple_fecha: Si está en el rango de fechas
            cumple_frases: Si coincide con las frases
            tiene_adjuntos: Si tiene adjuntos
            num_adjuntos: Cantidad de adjuntos
            adjuntos_nombres: Lista de nombres de adjuntos
            adjuntos_descargados: Cantidad descargada
            estado_final: PROCESADO | RECHAZADO | ERROR
            motivo_rechazo: Razón del rechazo
            fase_proceso: FILTRADO | DESCARGA
        """
        
        # Serializar lista de adjuntos a JSON string
        adjuntos_json = json.dumps(adjuntos_nombres or [], ensure_ascii=False)
        
        registro = {
            'entry_id': entry_id,
            'received_time': received_time,
            'subject': subject,
            'sender': sender,
            'cumple_fecha': cumple_fecha,
            'cumple_frases': cumple_frases,
            'tiene_adjuntos': tiene_adjuntos,
            'num_adjuntos': num_adjuntos,
            'adjuntos_nombres': adjuntos_json,
            'adjuntos_descargados': adjuntos_descargados,
            'estado_final': estado_final,
            'motivo_rechazo': motivo_rechazo,
            'fase_proceso': fase_proceso
        }
        
        self.registros.append(registro)
    
    def actualizar_descarga(self, 
                           entry_id: str, 
                           adjuntos_descargados: int,
                           estado_final: str = "PROCESADO",
                           motivo_rechazo: str = ""):
        """
        Actualiza el registro de un correo después de intentar descargar adjuntos.
        
        Args:
            entry_id: ID del correo a actualizar
            adjuntos_descargados: Cantidad de adjuntos descargados
            estado_final: Estado final actualizado
            motivo_rechazo: Motivo si no se descargó nada
        """
        for registro in self.registros:
            if registro['entry_id'] == entry_id:
                registro['adjuntos_descargados'] = adjuntos_descargados
                registro['estado_final'] = estado_final
                registro['fase_proceso'] = "DESCARGA"
                if motivo_rechazo:
                    registro['motivo_rechazo'] = motivo_rechazo
                break
    
    def exportar_a_parquet(self) -> str:
        """
        Exporta registros a archivo Parquet.
        
        Returns:
            str: Ruta del archivo Parquet generado
        """
        if not self.registros:
            return ""
        
        # Crear DataFrame con Polars
        df = pl.DataFrame(self.registros)
        
        # Escribir a Parquet
        df.write_parquet(str(self.archivo_parquet))
        
        return str(self.archivo_parquet)
    
    def exportar_a_excel(self) -> str:
        """
        Exporta registros a archivo Excel usando xlsxwriter.
        
        Returns:
            str: Ruta del archivo Excel generado
        """
        if not self.registros:
            return ""
        
        # Crear DataFrame con Polars
        df = pl.DataFrame(self.registros)
        
        # Escribir a Excel usando xlsxwriter engine
        df.write_excel(
            workbook=str(self.archivo_excel),
            worksheet="Auditoria",
            autofit=True
        )
        
        return str(self.archivo_excel)
    
    def exportar_todo(self) -> Dict[str, str]:
        """
        Exporta a Parquet y Excel.
        
        Returns:
            dict: Rutas de archivos generados
        """
        parquet_path = self.exportar_a_parquet()
        excel_path = self.exportar_a_excel()
        
        return {
            'parquet': parquet_path,
            'excel': excel_path
        }
    
    def get_estadisticas(self) -> Dict:
        """
        Calcula estadísticas de la auditoría.
        
        Returns:
            dict: Estadísticas de los correos auditados
        """
        if not self.registros:
            return {
                'total_correos': 0,
                'rechazados': 0,
                'procesados': 0,
                'con_adjuntos': 0,
                'adjuntos_descargados': 0,
                'tasa_exito': 0.0
            }
        
        df = pl.DataFrame(self.registros)
        
        total_correos = len(df)
        rechazados = len(df.filter(pl.col('estado_final') == 'RECHAZADO'))
        procesados = len(df.filter(pl.col('estado_final') == 'PROCESADO'))
        con_adjuntos = len(df.filter(pl.col('tiene_adjuntos') == True))
        adjuntos_descargados = df['adjuntos_descargados'].sum()
        
        # Calcular tasa de éxito (correos con adjuntos que fueron descargados)
        correos_con_descargas = len(df.filter(pl.col('adjuntos_descargados') > 0))
        tasa_exito = (correos_con_descargas / con_adjuntos * 100) if con_adjuntos > 0 else 0.0
        
        return {
            'total_correos': total_correos,
            'rechazados': rechazados,
            'procesados': procesados,
            'con_adjuntos': con_adjuntos,
            'adjuntos_descargados': adjuntos_descargados,
            'tasa_exito': tasa_exito
        }
    
    def get_correos_problematicos(self) -> pl.DataFrame:
        """
        Identifica correos problemáticos (con adjuntos pero no descargados).
        
        Returns:
            pl.DataFrame: DataFrame con correos problemáticos
        """
        if not self.registros:
            return pl.DataFrame()
        
        df = pl.DataFrame(self.registros)
        
        # Filtrar: tiene adjuntos PERO no se descargó ninguno
        problematicos = df.filter(
            (pl.col('tiene_adjuntos') == True) & 
            (pl.col('adjuntos_descargados') == 0)
        )
        
        return problematicos
    
    def get_motivos_rechazo(self) -> Dict[str, int]:
        """
        Cuenta correos por motivo de rechazo.
        
        Returns:
            dict: Motivos de rechazo con contadores
        """
        if not self.registros:
            return {}
        
        df = pl.DataFrame(self.registros)
        
        # Filtrar solo rechazados con motivo
        rechazados = df.filter(
            (pl.col('motivo_rechazo') != "") & 
            (pl.col('motivo_rechazo').is_not_null())
        )
        
        if len(rechazados) == 0:
            return {}
        
        # Contar por motivo
        conteo = rechazados.group_by('motivo_rechazo').agg(
            pl.count().alias('cantidad')
        )
        
        # Convertir a dict
        return dict(zip(conteo['motivo_rechazo'].to_list(), 
                       conteo['cantidad'].to_list()))
    
    def __len__(self) -> int:
        """Retorna cantidad de correos registrados"""
        return len(self.registros)
    
    def __repr__(self) -> str:
        return f"EmailAuditor(registros={len(self.registros)}, ruta={self.ruta_salida})"


# Exportar
__all__ = ['EmailAuditor']