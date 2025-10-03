from typing import Dict, List, Optional
from datetime import datetime
from app.services.humidity_calculations import HumidityCalculator

class OSTService:
    """Сервис для работы с ОСТ (Отраслевой стандарт) значениями"""
    
    @staticmethod
    def check_dew_point_exceedance(
        actual_dew_point: float, 
        season: str = "summer", 
        threshold_offset: float = 0.0
    ) -> Dict[str, any]:
        """
        Проверка превышения ТТР над ОСТ значением
        
        Args:
            actual_dew_point: Фактическая температура точки росы
            season: Сезон (summer/winter)
            threshold_offset: Дополнительное смещение порога
            
        Returns:
            Словарь с результатами проверки
        """
        ost_threshold = HumidityCalculator.get_ost_threshold(season)
        exceedance = actual_dew_point - (ost_threshold + threshold_offset)
        is_exceeded = exceedance > 0
        
        return {
            "actual_dew_point": actual_dew_point,
            "ost_threshold": ost_threshold,
            "threshold_offset": threshold_offset,
            "effective_threshold": ost_threshold + threshold_offset,
            "exceedance": exceedance,
            "is_exceeded": is_exceeded,
            "season": season
        }
    
    @staticmethod
    def calculate_ost_comparison(
        actual_water_content: float,
        actual_volume: float,
        season: str = "summer"
    ) -> Dict[str, any]:
        """
        Сравнение фактических данных с ОСТ значениями
        
        Args:
            actual_water_content: Фактическое влагосодержание
            actual_volume: Фактический объем газа
            season: Сезон
            
        Returns:
            Словарь с результатами сравнения
        """
        # Расчет по ОСТ
        ost_dew_point = HumidityCalculator.get_ost_threshold(season)
        ost_water_content = HumidityCalculator.calculate_humidity_content(ost_dew_point)
        ost_total_water = HumidityCalculator.calculate_water_mass(ost_water_content, actual_volume)
        
        # Фактические значения
        actual_total_water = HumidityCalculator.calculate_water_mass(actual_water_content, actual_volume)
        
        # Разница
        water_difference = actual_total_water - ost_total_water
        percentage_difference = (water_difference / ost_total_water * 100) if ost_total_water > 0 else 0
        
        return {
            "season": season,
            "ost_dew_point": ost_dew_point,
            "ost_water_content": ost_water_content,
            "ost_total_water": ost_total_water,
            "actual_water_content": actual_water_content,
            "actual_total_water": actual_total_water,
            "water_difference": water_difference,
            "percentage_difference": percentage_difference,
            "is_within_limits": water_difference <= 0
        }