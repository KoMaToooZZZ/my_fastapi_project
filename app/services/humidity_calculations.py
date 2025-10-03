import math
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class HumidityCalculator:
    """Класс для расчетов влажности по формулам из ТЗ"""
    # Константы из ТЗ (п. 6.2.2)
    A0 = 1.5435
    A1 = 0.07374
    A2 = -0.000307
    B0 = -3.1716
    B1 = 0.05355
    B2 = -0.000201
    P_ATM = 1.033
    P = 40
    # Таблица для определения ТТР смеси (упрощенная версия из Приложения Г)
    DEW_POINT_TABLE = {
        0.030: -23.1, 0.035: -21.1, 0.040: -19.4, 0.045: -17.9,
        0.050: -16.5, 0.060: -14.1, 0.070: -12.0, 0.080: -9.9,
        0.090: -8.4,  0.100: -7.0,  0.150: -1.2,  0.200: 3.1,
        0.250: 6.5,   0.300: 9.3,   0.350: 11.8,  0.400: 13.8,
        0.450: 15.7,  0.500: 17.7,  0.600: 20.8,  0.700: 23.4,
        0.800: 25.9,  0.900: 28.0,  1.000: 29.8
    }
    @classmethod
    def calculate_humidity_content(cls, dew_point: float) -> float:
        """
        Расчет влагосодержания по температуре точки росы
        Формула из п. 6.2.2 ТЗ
        w = [Exp(A0 + A1*T + A2*T²) * P_атм / P] + Exp(B0 + B1*T + B2*T²)
        """
        try:
            part1 = (math.exp(cls.A0 + cls.A1 * dew_point + cls.A2 * dew_point**2) * cls.P_ATM) / cls.P
            part2 = math.exp(cls.B0 + cls.B1 * dew_point + cls.B2 * dew_point**2)
            result = part1 + part2
            logger.debug(f"Humidity calculation: T={dew_point}, result={result}")
            return result
        except (OverflowError, ValueError) as e:
            logger.error(f"Error in humidity calculation: {e}")
            return 0.0
    @classmethod
    def calculate_water_mass(cls, humidity_content: float, gas_volume: float) -> float:
        """
        Расчет количества воды в объеме газа
        Формула из п. 6.2.2 ТЗ: W = w * V
        """
        return humidity_content * gas_volume
    @classmethod
    def calculate_mixture_dew_point(cls, mixture_humidity: float) -> float:
        """
        Расчет ТТР смеси газов по таблице из Приложения Г
        Использует метод интерполяции из п. 6.2.2 и 6.3.2 ТЗ
        """
        if mixture_humidity <= 0:
            return -50.0  # Минимальное значение
        # Находим ближайшие значения в таблице
        sorted_humidities = sorted(cls.DEW_POINT_TABLE.keys())
        if mixture_humidity <= sorted_humidities[0]:
            return cls.DEW_POINT_TABLE[sorted_humidities[0]]
        if mixture_humidity >= sorted_humidities[-1]:
            return cls.DEW_POINT_TABLE[sorted_humidities[-1]]
        # Находим ближайшие значения для интерполяции
        lower_humidity = None
        upper_humidity = None
        for i in range(len(sorted_humidities) - 1):
            if sorted_humidities[i] <= mixture_humidity <= sorted_humidities[i + 1]:
                lower_humidity = sorted_humidities[i]
                upper_humidity = sorted_humidities[i + 1]
                break
        if lower_humidity is None or upper_humidity is None:
            return cls.DEW_POINT_TABLE[sorted_humidities[0]]
        # Линейная интерполяция
        lower_dew_point = cls.DEW_POINT_TABLE[lower_humidity]
        upper_dew_point = cls.DEW_POINT_TABLE[upper_humidity]
        # Интерполяция: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
        interpolated_dew_point = lower_dew_point + (mixture_humidity - lower_humidity) * \
                               (upper_dew_point - lower_dew_point) / (upper_humidity - lower_humidity)
        return round(interpolated_dew_point, 2)
    @classmethod
    def get_ost_threshold(cls, season: str = "summer") -> float:
        """Получить пороговое значение ТТР по ОСТ"""
        return -14.0 if season.lower() == "summer" else -20.0
    @classmethod
    def calculate_ost_water_content(cls, season: str = "summer") -> float:
        """Расчет влагосодержания по ОСТ значениям"""
        ost_threshold = cls.get_ost_threshold(season)
        return cls.calculate_humidity_content(ost_threshold)