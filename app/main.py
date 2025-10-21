import sys
import os

# Добавляем путь к корню проекта
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем все роутеры
from app.api import (
    measuring_points,
    calculated_data,
    analytics,
    system,
    calculator,
    reports,
    export
)
from app.database import engine, Base

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gas Humidity Calculation System API",
    description="API для системы расчета влажности газа согласно ТЗ ООО «Газпром трансгаз Ухта»",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
app.include_router(measuring_points.router, prefix="/api/v1", tags=["Точки измерений"])
app.include_router(calculated_data.router, prefix="/api/v1", tags=["Расчетные данные"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Аналитика и отчеты"])
app.include_router(calculator.router, prefix="/api/v1", tags=["Калькулятор влажности"])
app.include_router(reports.router, prefix="/api/v1", tags=["Специализированные отчеты"])
app.include_router(export.router, prefix="/api/v1", tags=["Экспорт данных"])
app.include_router(system.router, tags=["Система"])

@app.get("/")
def read_root():
    return {
        "message": "Gas Humidity Calculation System API работает!",
        "documentation": "/docs",
        "version": "2.0.0",
        "modules": [
            "Точки измерений",
            "Расчетные данные",
            "Аналитика и отчеты",
            "Калькулятор влажности",
            "Специализированные отчеты",
            "Экспорт данных",
            "Системa"
        ]
    }

@app.get("/api/health")
def api_health():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "service": "Gas Humidity Calculation System",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)