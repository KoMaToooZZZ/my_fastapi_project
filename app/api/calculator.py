from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.services.humidity_calculations import HumidityCalculator
from app.utils.units_converter import UnitsConverter
from app.schemas.schemas import (
    GasVolumeInput,
    SingleVolumeRequest,
    SingleVolumeResponse,
    VolumeResult,
    VolumeDifference,
    GasMixtureRequest,
    GasMixtureResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/calculator/single-volume", response_model=SingleVolumeResponse)
async def calculate_single_volume(request: SingleVolumeRequest):
    """
    Расчет влагосодержания для одного/двух объемов газа
    Соответствует п. 6.3.1 ТЗ
    """
    if len(request.volumes) == 0:
        raise HTTPException(status_code=400, detail="At least one volume required")
    if len(request.volumes) > 2:
        raise HTTPException(status_code=400, detail="Maximum 2 volumes supported")
    
    results = []
    total_water_masses = []
    
    try:
        for i, volume in enumerate(request.volumes):
            # Конвертируем объем в базовые единицы (куб. м)
            base_volume = UnitsConverter.convert_volume(
                volume.gas_volume,
                volume.volume_unit,
                'cubic_meter'
            )
            # Конвертируем температуру
            base_dew_point = UnitsConverter.convert_dew_point(
                volume.dew_point,
                volume.dew_point_unit,
                'celsius'
            )
            # Расчет влагосодержания
            humidity_content = HumidityCalculator.calculate_humidity_content(base_dew_point)
            # Расчет общего количества воды
            water_mass_grams = HumidityCalculator.calculate_water_mass(humidity_content, base_volume)
            
            # Создаем объект результата
            result = VolumeResult(
                volume_index=i + 1,
                input_data=volume,
                water_content_per_cubic_meter=round(humidity_content, 6),
                total_water_mass=round(water_mass_grams, 6),
                base_volume_cubic_meters=base_volume,
                base_dew_point_celsius=base_dew_point
            )
            results.append(result)
            total_water_masses.append(water_mass_grams)
        
        # Расчет разницы если два объема
        difference = None
        if len(total_water_masses) == 2:
            mass_difference = total_water_masses[1] - total_water_masses[0]
            difference = VolumeDifference(
                water_mass_difference_grams=abs(mass_difference),
                water_mass_difference_kilograms=abs(mass_difference) / 1000,
                direction="increase" if mass_difference > 0 else "decrease",
                percentage_difference=abs(mass_difference) / total_water_masses[0] * 100 if total_water_masses[0] > 0 else 0
            )
        
        return SingleVolumeResponse(results=results, difference=difference)
        
    except Exception as e:
        logger.error(f"Error in single volume calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")

@router.post("/calculator/gas-mixture", response_model=GasMixtureResponse)
async def calculate_gas_mixture(request: GasMixtureRequest):
    """
    Расчет параметров смеси газов
    Соответствует п. 6.3.2 ТЗ
    """
    if len(request.components) == 0:
        raise HTTPException(status_code=400, detail="At least one component required")
    
    try:
        total_volume = 0
        weighted_humidity_sum = 0
        
        for component in request.components:
            # Конвертируем объем в базовые единицы
            base_volume = UnitsConverter.convert_volume(
                component.gas_volume,
                component.volume_unit,
                'cubic_meter'
            )
            # Конвертируем температуру
            base_dew_point = UnitsConverter.convert_dew_point(
                component.dew_point,
                component.dew_point_unit,
                'celsius'
            )
            # Расчет влагосодержания для каждого компонента
            humidity_content = HumidityCalculator.calculate_humidity_content(base_dew_point)
            total_volume += base_volume
            weighted_humidity_sum += humidity_content * base_volume
        
        # Расчет параметров смеси
        mixture_water_content = weighted_humidity_sum / total_volume if total_volume > 0 else 0
        total_water_mass_grams = mixture_water_content * total_volume
        mixture_dew_point = HumidityCalculator.calculate_mixture_dew_point(mixture_water_content)
        
        # Конвертируем общий объем обратно в тыс. куб. м для отображения
        display_volume = UnitsConverter.convert_volume(total_volume, 'cubic_meter', 'thousand_cubic_meters')
        
        return GasMixtureResponse(
            mixture_volume=round(display_volume, 2),
            mixture_water_content=round(mixture_water_content, 6),
            total_water_mass=round(total_water_mass_grams / 1000000, 6),  # в тоннах
            mixture_dew_point=round(mixture_dew_point, 2)
        )
        
    except Exception as e:
        logger.error(f"Error in gas mixture calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")