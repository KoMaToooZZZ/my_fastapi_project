from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text

from app.database import get_db
from app.models.models import MeasuringPoint as MeasuringPointModel, CalculatedData as CalculatedDataModel
from app.schemas.schemas import MeasuringPoint as MeasuringPointSchema, MeasuringPointCreate, MeasuringPointUpdate, CalculatedData as CalculatedDataSchema
from app.crud.crud import crud_measuring_point, crud_calculated_data

router = APIRouter()

# Базовые CRUD операции
@router.get("/measuring-points/", response_model=List[MeasuringPointSchema])
def get_measuring_points(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить список всех точек измерений с пагинацией"""
    return crud_measuring_point.get_all(db, skip=skip, limit=limit)

@router.get("/measuring-points/{point_id}", response_model=MeasuringPointSchema)
def get_measuring_point(point_id: int, db: Session = Depends(get_db)):
    """Получить детальную информацию о точке измерения по ID"""
    point = crud_measuring_point.get(db, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Measuring point not found")
    return point

@router.post("/measuring-points/", response_model=MeasuringPointSchema)
def create_measuring_point(
    point: MeasuringPointCreate,
    db: Session = Depends(get_db)
):
    """Создать новую точку измерения"""
    # Проверяем нет ли точки с таким ID
    if crud_measuring_point.get(db, point.id_point):
        raise HTTPException(status_code=400, detail="Point with this ID already exists")
    return crud_measuring_point.create(db, point)

@router.put("/measuring-points/{point_id}", response_model=MeasuringPointSchema)
def update_measuring_point(
    point_id: int,
    point_update: MeasuringPointUpdate,
    db: Session = Depends(get_db)
):
    """Обновить информацию о точке измерения"""
    updated = crud_measuring_point.update(db, point_id, point_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Measuring point not found")
    return updated

@router.delete("/measuring-points/{point_id}")
def delete_measuring_point(point_id: int, db: Session = Depends(get_db)):
    """Удалить точку измерения"""
    if not crud_measuring_point.delete(db, point_id):
        raise HTTPException(status_code=404, detail="Measuring point not found")
    return {"message": "Measuring point deleted successfully"}

# Специальные операции для точек
@router.get("/measuring-points/{point_id}/calculated-data", response_model=List[CalculatedDataSchema])
def get_point_calculated_data(
    point_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить все расчетные данные для конкретной точки"""
    # Проверяем существует ли точка
    if not crud_measuring_point.get(db, point_id):
        raise HTTPException(status_code=404, detail="Measuring point not found")
    
    return crud_calculated_data.get_by_point(db, point_id, skip, limit)

@router.get("/measuring-points/tree")
def get_measuring_points_tree(db: Session = Depends(get_db)):
    """Получить иерархию точек измерений (родитель-потомок)"""
    points = crud_measuring_point.get_all(db)
    
    # Строим дерево
    tree = []
    
    for point in points:
        if point.id_parent_point is None:
            tree.append({
                "point": MeasuringPointSchema.from_orm(point),
                "children": [
                    MeasuringPointSchema.from_orm(child) for child in points 
                    if child.id_parent_point == point.id_point
                ]
            })
    
    return tree

@router.get("/measuring-points/search", response_model=List[MeasuringPointSchema])
def search_measuring_points(
    query: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Поиск точек измерений по названию"""
    points = db.query(MeasuringPointModel).filter(
        MeasuringPointModel.name_point.ilike(f"%{query}%")
    ).offset(skip).limit(limit).all()
    return points

@router.get("/measuring-points/{point_id}/statistics")
def get_point_statistics(point_id: int, db: Session = Depends(get_db)):
    """Получить статистику по точке измерения"""
    point = crud_measuring_point.get(db, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Measuring point not found")
    
    # Статистика по расчетным данным
    data_stats = db.execute(text("""
        SELECT 
            COUNT(*) as total_records,
            AVG(parametr_ttr) as avg_ttr,
            AVG(parametr_q) as avg_q,
            AVG(parametr_q_H2O) as avg_q_H2O,
            AVG(parametr_q_H2O_porog) as avg_q_H2O_porog,
            MIN(data_and_time) as first_record,
            MAX(data_and_time) as last_record
        FROM "Calculated_data" 
        WHERE id_point = :point_id
    """), {"point_id": point_id}).first()
    
    return {
        "point_info": MeasuringPointSchema.from_orm(point),
        "statistics": {
            "total_records": data_stats[0],
            "average_ttr": float(data_stats[1]) if data_stats[1] else 0,
            "average_q": float(data_stats[2]) if data_stats[2] else 0,
            "average_q_H2O": float(data_stats[3]) if data_stats[3] else 0,
            "average_q_H2O_porog": float(data_stats[4]) if data_stats[4] else 0,
            "first_record": data_stats[5],
            "last_record": data_stats[6]
        }
    }