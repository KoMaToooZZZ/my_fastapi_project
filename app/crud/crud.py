from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import MeasuringPoint, CalculatedData
from app.schemas.schemas import MeasuringPointCreate, MeasuringPointUpdate, CalculatedDataCreate, CalculatedDataUpdate

class CRUDMeasuringPoint:
    def get(self, db: Session, id_point: int) -> Optional[MeasuringPoint]:
        return db.query(MeasuringPoint).filter(MeasuringPoint.id_point == id_point).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[MeasuringPoint]:
        return db.query(MeasuringPoint).offset(skip).limit(limit).all()
    
    def get_by_parent(self, db: Session, parent_id: int) -> List[MeasuringPoint]:
        return db.query(MeasuringPoint).filter(MeasuringPoint.id_parent_point == parent_id).all()
    
    def create(self, db: Session, measuring_point: MeasuringPointCreate) -> MeasuringPoint:
        db_measuring_point = MeasuringPoint(**measuring_point.dict())
        db.add(db_measuring_point)
        db.commit()
        db.refresh(db_measuring_point)
        return db_measuring_point
    
    def update(self, db: Session, id_point: int, measuring_point: MeasuringPointUpdate) -> Optional[MeasuringPoint]:
        db_measuring_point = self.get(db, id_point)
        if db_measuring_point:
            update_data = measuring_point.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_measuring_point, field, value)
            db.commit()
            db.refresh(db_measuring_point)
        return db_measuring_point
    
    def delete(self, db: Session, id_point: int) -> bool:
        db_measuring_point = self.get(db, id_point)
        if db_measuring_point:
            db.delete(db_measuring_point)
            db.commit()
            return True
        return False

class CRUDCalculatedData:
    def get(self, db: Session, id_data: int) -> Optional[CalculatedData]:
        return db.query(CalculatedData).filter(CalculatedData.id_data == id_data).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[CalculatedData]:
        return db.query(CalculatedData).offset(skip).limit(limit).all()
    
    def get_by_point(self, db: Session, id_point: int, skip: int = 0, limit: int = 100) -> List[CalculatedData]:
        return db.query(CalculatedData).filter(CalculatedData.id_point == id_point).offset(skip).limit(limit).all()
    
    def create(self, db: Session, calculated_data: CalculatedDataCreate) -> CalculatedData:
        db_calculated_data = CalculatedData(**calculated_data.dict())
        db.add(db_calculated_data)
        db.commit()
        db.refresh(db_calculated_data)
        return db_calculated_data
    
    def update(self, db: Session, id_data: int, calculated_data: CalculatedDataUpdate) -> Optional[CalculatedData]:
        db_calculated_data = self.get(db, id_data)
        if db_calculated_data:
            update_data = calculated_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_calculated_data, field, value)
            db.commit()
            db.refresh(db_calculated_data)
        return db_calculated_data
    
    def delete(self, db: Session, id_data: int) -> bool:
        db_calculated_data = self.get(db, id_data)
        if db_calculated_data:
            db.delete(db_calculated_data)
            db.commit()
            return True
        return False

# Создаем экземпляры CRUD классов
crud_measuring_point = CRUDMeasuringPoint()
crud_calculated_data = CRUDCalculatedData()