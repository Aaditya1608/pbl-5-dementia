from app.core.database import SessionLocal
from app.services.report_generator import generate_daily_reports
from datetime import date

db = SessionLocal()

try:
    generate_daily_reports(db,report_date=date(2026,11,17))
finally:
    db.close()