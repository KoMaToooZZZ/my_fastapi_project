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

# Специфичные схемы для результатов расчета
class VolumeResult(BaseModel):
    volume_index: int
    input_data: GasVolumeInput
    water_content_per_cubic_meter: float
    total_water_mass: float
    base_volume_cubic_meters: float
    base_dew_point_celsius: float

class VolumeDifference(BaseModel):
    water_mass_difference_grams: float
    water_mass_difference_kilograms: float
    direction: str
    percentage_difference: float

class SingleVolumeRequest(BaseModel):
    volumes: List[GasVolumeInput]

class SingleVolumeResponse(BaseModel):
    results: List[VolumeResult]
    difference: Optional[VolumeDifference] = None

class GasMixtureRequest(BaseModel):
    components: List[GasVolumeInput]

class GasMixtureResponse(BaseModel):
    mixture_volume: float
    mixture_water_content: float
    total_water_mass: float
    mixture_dew_point: float

# Схемы для отчетов
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
    input_point_ids: List[int]
    output_point_ids: List[int]
    start_date: str
    end_date: str
    data_interval: str = "hourly"

class InputOutputSummaryResponse(BaseModel):
    input_total_water: float
    output_total_water: float
    difference: float
    input_avg_dew_point: float
    output_avg_dew_point: float