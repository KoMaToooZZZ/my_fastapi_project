from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base

class MeasuringPoint(Base):
    __tablename__ = "Measuring_point"
    
    # ТОЛЬКО ТЕ СТОЛБЦЫ, КОТОРЫЕ ЕСТЬ В РЕАЛЬНОЙ ТАБЛИЦЕ
    id_point = Column(Integer, primary_key=True, index=True)
    name_point = Column(String(100))
    id_parametr_ttr = Column(Float)
    id_parametr_q = Column(Float)
    id_parent_point = Column(Integer, ForeignKey("Measuring_point.id_point"))
    
    # Связь для иерархии
    parent = relationship("MeasuringPoint", remote_side=[id_point], backref="children")
    
    # Связь с расчетными данными
    calculated_data = relationship("CalculatedData", back_populates="measuring_point")

class CalculatedData(Base):
    __tablename__ = "Calculated_data"
    
    id_data = Column(Integer, primary_key=True, index=True)
    data_and_time = Column(DateTime)
    parametr_ttr = Column(Float)
    parametr_q = Column(Float)
    parametr_q_H2O = Column(Float)
    parametr_q_H2O_porog = Column(Float)
    id_point = Column(Integer, ForeignKey("Measuring_point.id_point"))
    
    # Связь с точкой измерения
    measuring_point = relationship("MeasuringPoint", back_populates="calculated_data")