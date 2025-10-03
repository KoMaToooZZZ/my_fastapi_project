from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

# Схемы для MeasuringPoint
class MeasuringPointBase(BaseModel):
    name_point: str
    measurement_type: Optional[str] = "informational"
    route_name: Optional[str] = None
    description: Optional[str] = None
    id_parametr_ttr: Optional[float] = None
    id_parametr_q: Optional[float] = None
    id_parent_point: Optional[int] = None
    is_active: Optional[bool] = True

class MeasuringPointCreate(MeasuringPointBase):
    pass  # id_point будет генерироваться автоматически

class MeasuringPointUpdate(BaseModel):
    name_point: Optional[str] = None
    measurement_type: Optional[str] = None
    route_name: Optional[str] = None
    description: Optional[str] = None
    id_parametr_ttr: Optional[float] = None
    id_parametr_q: Optional[float] = None
    id_parent_point: Optional[int] = None
    is_active: Optional[bool] = None

class MeasuringPoint(MeasuringPointBase):
    id_point: int
    
    class Config:
        from_attributes = True

# Схемы для CalculatedData
class CalculatedDataBase(BaseModel):
    data_and_time: datetime
    parametr_ttr: Optional[float] = None
    parametr_q: Optional[float] = None
    parametr_q_H2O: Optional[float] = None
    parametr_q_H2O_porog: Optional[float] = None
    parametr_other: Optional[float] = None
    id_point: int

class CalculatedDataCreate(CalculatedDataBase):
    pass  # id_data будет генерироваться автоматически

class CalculatedDataUpdate(BaseModel):
    data_and_time: Optional[datetime] = None
    parametr_ttr: Optional[float] = None
    parametr_q: Optional[float] = None
    parametr_q_H2O: Optional[float] = None
    parametr_q_H2O_porog: Optional[float] = None
    parametr_other: Optional[float] = None
    id_point: Optional[int] = None

class CalculatedData(CalculatedDataBase):
    id_data: int
    
    class Config:
        from_attributes = True

# Схемы для калькулятора влажности
class GasVolumeInput(BaseModel):
    gas_volume: float
    volume_unit: str = "thousand_cubic_meters"
    dew_point: float
    dew_point_unit: str = "celsius"

class SingleVolumeRequest(BaseModel):
    volumes: List[GasVolumeInput]

class SingleVolumeResponse(BaseModel):
    results: List[dict]
    difference: Optional[dict] = None

class GasMixtureRequest(BaseModel):
    components: List[GasVolumeInput]

class GasMixtureResponse(BaseModel):
    mixture_volume: float
    mixture_water_content: float
    total_water_mass: float
    mixture_dew_point: float

# Схемы для отчетов
class ExceededOstRequest(BaseModel):
    start_date: str
    end_date: str
    exceedance_threshold: float = 3.0
    duration_threshold: int = 2
    measurement_point_ids: List[float]
    season: str = "summer"

class ExceededOstResponse(BaseModel):
    point_name: str
    average_dew_point: float
    ost_threshold: float
    exceedance_period: str
    duration_hours: float

class WaterIntrusionRequest(BaseModel):
    start_date: str
    end_date: str
    duration: str = "last_month"

class ExportRequest(BaseModel):
    export_type: str  # calculated_data, report, calculator
    parameters: Dict[str, Any]
    format: str = "excel"

# Схемы для аналитики
class InputOutputSummaryRequest(BaseModel):
    input_point_ids: List[float]
    output_point_ids: List[float]
    start_date: str
    end_date: str
    data_interval: str = "hourly"

class InputOutputSummaryResponse(BaseModel):
    input_total_water: float
    output_total_water: float
    difference: float
    input_avg_dew_point: float
    output_avg_dew_point: float