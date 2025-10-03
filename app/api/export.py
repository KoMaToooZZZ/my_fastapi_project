from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any, List
import pandas as pd
import io
import logging

from app.services.humidity_calculations import HumidityCalculator

router = APIRouter()
logger = logging.getLogger(__name__)

class ExportRequest(BaseModel):
    export_type: str  # calculated_data, report, calculator
    parameters: Dict[str, Any]
    format: str = "excel"

@router.post("/export/data")
async def export_data(request: ExportRequest):
    """
    Экспорт данных в различные форматы
    Поддерживает выгрузку результатов расчетов, отчетов и данных калькулятора
    """
    try:
        if request.export_type == "calculator":
            return await export_calculator_data(request.parameters, request.format)
        elif request.export_type == "report":
            return await export_report_data(request.parameters, request.format)
        elif request.export_type == "calculated_data":
            return await export_calculated_data(request.parameters, request.format)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export type")
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

async def export_calculator_data(parameters: Dict[str, Any], format: str = "excel"):
    """Экспорт данных калькулятора"""
    # Создаем пример данных для экспорта (в реальности брать из параметров)
    if parameters.get("calculation_type") == "single_volume":
        data = {
            "Параметр": ["Температура точки росы", "Объем газа", "Влагосодержание", "Общее количество воды"],
            "Значение": [-15.0, 2965.0, 55.2768, 0.16],
            "Единица измерения": ["°C", "тыс. м³", "мг/м³", "т"]
        }
    else:  # gas_mixture
        data = {
            "Компонент": ["Газ 1", "Газ 2", "Смесь"],
            "Температура точки росы (°C)": [-15, 12, -6.03],
            "Объем (тыс. м³/час)": [2695, 562, 3257],
            "Влагосодержание (мг/м³)": [107.45, 357.67, 149.32]
        }
    df = pd.DataFrame(data)
    if format == "excel":
        return create_excel_response(df, "calculator_export.xlsx")
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

async def export_report_data(parameters: Dict[str, Any], format: str = "excel"):
    """Экспорт отчетных данных"""
    # Пример данных отчета "Поиск превышения ТТР по ОСТ"
    report_data = {
        "Точка замера": ["КС-17 (Вход Цех №2)", "ГИС Надым ГП-2", "УЗПД ГИС-12"],
        "Средняя ТТР (°C)": [-10.125, -6.986, 7.189],
        "Порог ОСТ (°C)": [-14.0, -14.0, -14.0],
        "Период превышения": [
            "31.05.2021 00:00 - 03.06.2021 06:15",
            "03.06.2021 09:17 - 03.06.2021 21:34",
            "02.06.2021 18:02 - 02.06.2021 21:11"
        ],
        "Длительность (часы)": [78.25, 12.28, 3.15]
    }
    df = pd.DataFrame(report_data)
    if format == "excel":
        return create_excel_response(df, "ost_exceedance_report.xlsx")
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

async def export_calculated_data(parameters: Dict[str, Any], format: str = "excel"):
    """Экспорт расчетных данных"""
    # Пример данных из модуля расчетов
    calculated_data = {
        "Время": [
            "31.05.2021 00:00", "31.05.2021 01:00", "31.05.2021 02:00",
            "31.05.2021 03:00", "07.06.2021 07:00", "07.06.2021 08:00"
        ],
        "Содержание влаги по ОСТ (т)": [0.1481852, 0.1482154, 0.1461716, 0.1460094, 0.1430151, 0.1451667],
        "Содержание влаги (т)": [0.0760775, 0.0758579, 0.0738977, 0.0738821, 0.0657523, 0.0676737],
        "Разница (т)": [0.0721077, 0.0723575, 0.0722739, 0.0721273, 0.0772628, 0.0774931],
        "В 1 куб. м (мг)": [61.785484, 61.607729, 61.081591, 61.1202, 54.974839, 55.736813]
    }
    df = pd.DataFrame(calculated_data)
    if format == "excel":
        return create_excel_response(df, "calculated_data_export.xlsx")
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

def create_excel_response(dataframe: pd.DataFrame, filename: str) -> Response:
    """Создать Excel файл для ответа"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, sheet_name='Data', index=False)
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/formats")
async def get_export_formats():
    """Получить список поддерживаемых форматов экспорта"""
    return {
        "supported_formats": ["excel"],
        "export_types": [
            {
                "type": "calculator",
                "description": "Данные калькулятора влажности",
                "supported_calculations": ["single_volume", "gas_mixture"]
            },
            {
                "type": "report",
                "description": "Отчетные данные",
                "supported_reports": ["exceeded_ost", "water_intrusion"]
            },
            {
                "type": "calculated_data",
                "description": "Исторические расчетные данные",
                "parameters": ["date_range", "measurement_points"]
            }
        ]
    }