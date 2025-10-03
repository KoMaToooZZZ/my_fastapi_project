from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import datetime
import sys
import fastapi

from app.database import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Проверка здоровья приложения и базы данных"""
    try:
        # Проверяем подключение к БД
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }

@router.get("/version")
def get_version():
    """Получить версию API"""
    return {
        "api_version": "1.0.0",
        "python_version": sys.version,
        "fastapi_version": fastapi.__version__
    }

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    """Метрики для мониторинга (Prometheus format)"""
    # Количество точек
    points_count = db.execute(text('SELECT COUNT(*) FROM "Measuring_point"')).scalar()
    # Количество данных
    data_count = db.execute(text('SELECT COUNT(*) FROM "Calculated_data"')).scalar()
    # Последняя запись
    last_record = db.execute(text('SELECT MAX(data_and_time) FROM "Calculated_data"')).scalar()
    return {
        "points_total": points_count,
        "data_total": data_count,
        "last_record_time": last_record.isoformat() if last_record else None,
        "uptime": "TODO"  # Можно добавить время работы
    }

@router.get("/config")
def get_config():
    """Получить конфигурацию API (без sensitive data)"""
    return {
        "debug": False,
        "reload": True,
        "host": "0.0.0.0",
        "port": 8000,
        "database_url": "***",  # Маскируем sensitive data
        "allowed_hosts": ["*"]
    }