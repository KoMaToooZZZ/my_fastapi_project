from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import text

from app.database import get_db
from app.models.models import CalculatedData as CalculatedDataModel
from app.schemas.schemas import CalculatedData as CalculatedDataSchema, CalculatedDataCreate, CalculatedDataUpdate
from app.crud.crud import crud_calculated_data, crud_measuring_point

router = APIRouter()

# 1. Базовые CRUD операции
@router.get("/calculated-data/", response_model=List[CalculatedDataSchema])
def get_calculated_data(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все расчетные данные"""
    return crud_calculated_data.get_all(db, skip, limit)

@router.get("/calculated-data/{data_id}", response_model=CalculatedDataSchema)
def get_calculated_data_point(data_id: int, db: Session = Depends(get_db)):  # int вместо float
    """Получить конкретные расчетные данные по ID"""
    data = crud_calculated_data.get(db, data_id)
    if not data:
        raise HTTPException(status_code=404, detail="Calculated data not found")
    return data

@router.post("/calculated-data/", response_model=CalculatedDataSchema)
def create_calculated_data(
    data: CalculatedDataCreate,
    db: Session = Depends(get_db)
):
    """Создать новые расчетные данные"""
    # Проверяем существует ли точка измерения
    if not crud_measuring_point.get(db, data.id_point):
        raise HTTPException(status_code=404, detail="Measuring point not found")
    
    return crud_calculated_data.create(db, data)

@router.put("/calculated-data/{data_id}", response_model=CalculatedDataSchema)
def update_calculated_data(
    data_id: int,  # int вместо float
    data_update: CalculatedDataUpdate,
    db: Session = Depends(get_db)
):
    """Обновить расчетные данные"""
    updated = crud_calculated_data.update(db, data_id, data_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Calculated data not found")
    return updated

@router.delete("/calculated-data/{data_id}")
def delete_calculated_data(data_id: int, db: Session = Depends(get_db)):  # int вместо float
    """Удалить расчетные данные"""
    if not crud_calculated_data.delete(db, data_id):
        raise HTTPException(status_code=404, detail="Calculated data not found")
    return {"message": "Calculated data deleted successfully"}

# 2. Специальные операции для данных
@router.get("/calculated-data/point/{point_id}", response_model=List[CalculatedDataSchema])
def get_data_by_point(
    point_id: int,  # int вместо float
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить расчетные данные по ID точки измерения"""
    if not crud_measuring_point.get(db, point_id):
        raise HTTPException(status_code=404, detail="Measuring point not found")
    
    return crud_calculated_data.get_by_point(db, point_id, skip, limit)

@router.get("/calculated-data/date-range", response_model=List[CalculatedDataSchema])
def get_data_by_date_range(
    start_date: str,
    end_date: str,
    point_id: Optional[int] = None,  # int вместо float
    db: Session = Depends(get_db)
):
    """Получить данные за временной период"""
    query = db.query(CalculatedDataModel).filter(
        CalculatedDataModel.data_and_time.between(start_date, end_date)
    )
    
    if point_id:
        query = query.filter(CalculatedDataModel.id_point == point_id)
        if not crud_measuring_point.get(db, point_id):
            raise HTTPException(status_code=404, detail="Measuring point not found")
    
    return query.order_by(CalculatedDataModel.data_and_time).all()

@router.post("/calculated-data/batch", response_model=List[CalculatedDataSchema])
def create_batch_calculated_data(
    data_list: List[CalculatedDataCreate],
    db: Session = Depends(get_db)
):
    """Пакетное добавление расчетных данных"""
    results = []
    for data in data_list:
        # Проверяем точку измерения
        if not crud_measuring_point.get(db, data.id_point):
            raise HTTPException(status_code=404, detail=f"Measuring point {data.id_point} not found")
        
        created = crud_calculated_data.create(db, data)
        results.append(created)
    
    return results

@router.get("/calculated-data/aggregated")
def get_aggregated_data(
    aggregation: str = "daily",  # daily, weekly, monthly
    point_id: Optional[int] = None,  # int вместо float
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить агрегированные данные"""
    # Определяем интервал агрегации
    if aggregation == "daily":
        interval = "DATE(data_and_time)"
    elif aggregation == "weekly":
        interval = "DATE_TRUNC('week', data_and_time)"
    else:  # monthly
        interval = "DATE_TRUNC('month', data_and_time)"
    
    # Строим запрос
    sql = f"""
        SELECT 
            {interval} as period,
            AVG(parametr_ttr) as avg_ttr,
            AVG(parametr_q) as avg_q,
            COUNT(*) as record_count
        FROM "Calculated_data"
        WHERE 1=1
    """
    
    params = {}
    if point_id:
        sql += " AND id_point = :point_id"
        params["point_id"] = point_id
    
    if start_date:
        sql += " AND data_and_time >= :start_date"
        params["start_date"] = start_date
    
    if end_date:
        sql += " AND data_and_time <= :end_date"
        params["end_date"] = end_date
    
    sql += " GROUP BY period ORDER BY period"
    
    result = db.execute(text(sql), params)
    return [dict(row) for row in result]