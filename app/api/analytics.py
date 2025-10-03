from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

from app.database import get_db

router = APIRouter()

@router.get("/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """Получить сводную аналитику по всем данным"""
    # Статистика по точкам
    points_stats = db.execute(text("""
        SELECT 
            COUNT(*) as total_points,
            COUNT(DISTINCT id_parent_point) as hierarchy_levels
        FROM "Measuring_point"
    """)).first()
    
    # Статистика по данным
    data_stats = db.execute(text("""
        SELECT 
            COUNT(*) as total_records,
            MIN(data_and_time) as first_record,
            MAX(data_and_time) as last_record,
            AVG(parametr_ttr) as global_avg_ttr,
            AVG(parametr_q) as global_avg_q
        FROM "Calculated_data"
    """)).first()
    
    return {
        "points_summary": {
            "total_points": points_stats[0],
            "hierarchy_levels": points_stats[1]
        },
        "data_summary": {
            "total_records": data_stats[0],
            "date_range": {
                "first": data_stats[1],
                "last": data_stats[2]
            },
            "averages": {
                "parametr_ttr": float(data_stats[3]) if data_stats[3] else 0,
                "parametr_q": float(data_stats[4]) if data_stats[4] else 0
            }
        }
    }

@router.get("/analytics/trends")
def get_analytics_trends(
    period: str = "month",
    db: Session = Depends(get_db)
):
    """Получить тренды данных за период"""
    if period == "week":
        interval = "DATE_TRUNC('week', data_and_time)"
    elif period == "month":
        interval = "DATE_TRUNC('month', data_and_time)"
    else:  # day
        interval = "DATE(data_and_time)"
    
    trends = db.execute(text(f"""
        SELECT 
            {interval} as period,
            AVG(parametr_ttr) as avg_ttr,
            AVG(parametr_q) as avg_q,
            COUNT(*) as record_count
        FROM "Calculated_data"
        GROUP BY period
        ORDER BY period DESC
        LIMIT 30
    """)).fetchall()
    
    return [dict(row) for row in trends]

@router.get("/reports/daily")
def get_daily_report(
    date: str = None,  # Если None - берется вчерашний день
    db: Session = Depends(get_db)
):
    """Сформировать ежедневный отчет"""
    if not date:
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    report_data = db.execute(text("""
        SELECT 
            mp.name_point,
            mp.id_point,
            COUNT(cd.id_data) as records_count,
            AVG(cd.parametr_ttr) as avg_ttr,
            AVG(cd.parametr_q) as avg_q,
            MIN(cd.parametr_ttr) as min_ttr,
            MAX(cd.parametr_ttr) as max_ttr
        FROM "Measuring_point" mp
        LEFT JOIN "Calculated_data" cd ON mp.id_point = cd.id_point 
            AND DATE(cd.data_and_time) = :date
        GROUP BY mp.id_point, mp.name_point
        ORDER BY mp.id_point
    """), {"date": date}).fetchall()
    
    return {
        "report_date": date,
        "points": [dict(row) for row in report_data]
    }

@router.post("/reports/generate")
def generate_custom_report(
    report_config: dict,
    db: Session = Depends(get_db)
):
    """Сгенерировать кастомный отчет по конфигурации"""
    # Пример конфигурации отчета
    # {
    #     "type": "summary",
    #     "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
    #     "point_ids": [1, 2, 3],
    #     "metrics": ["parametr_ttr", "parametr_q"]
    # }
    
    # Здесь будет логика генерации отчета по конфигурации
    return {"status": "report_generated", "config": report_config}