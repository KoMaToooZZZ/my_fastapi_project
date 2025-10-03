from typing import Dict, Any

class UnitsConverter:
    """Конвертер единиц измерения"""
    # Коэффициенты преобразования для объема
    VOLUME_CONVERSIONS = {
        'cubic_meter': 1.0,
        'thousand_cubic_meters': 1000.0,
        'million_cubic_meters': 1000000.0
    }
    # Коэффициенты преобразования для массы воды
    MASS_CONVERSIONS = {
        'gram': 1.0,
        'kilogram': 1000.0,
        'ton': 1000000.0,
        'milligram': 0.001
    }
    @classmethod
    def convert_volume(cls, value: float, from_unit: str, to_unit: str) -> float:
        """Конвертировать объем"""
        if from_unit not in cls.VOLUME_CONVERSIONS or to_unit not in cls.VOLUME_CONVERSIONS:
            raise ValueError(f"Unsupported volume units: {from_unit} -> {to_unit}")
        base_value = value * cls.VOLUME_CONVERSIONS[from_unit]
        return base_value / cls.VOLUME_CONVERSIONS[to_unit]
    @classmethod
    def convert_mass(cls, value: float, from_unit: str, to_unit: str) -> float:
        """Конвертировать массу"""
        if from_unit not in cls.MASS_CONVERSIONS or to_unit not in cls.MASS_CONVERSIONS:
            raise ValueError(f"Unsupported mass units: {from_unit} -> {to_unit}")
        base_value = value * cls.MASS_CONVERSIONS[from_unit]
        return base_value / cls.MASS_CONVERSIONS[to_unit]
    @classmethod
    def convert_dew_point(cls, value: float, from_unit: str, to_unit: str) -> float:
        """Конвертировать температуру (пока только Цельсий поддерживается)"""
        if from_unit != 'celsius' or to_unit != 'celsius':
            raise ValueError("Only Celsius temperature is currently supported")
        return value