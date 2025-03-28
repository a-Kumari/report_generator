from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from database import get_db
from models import Report, User
from auth import get_current_user
from schemas import  ReportOut
from task import generate_report
from math import ceil


router = APIRouter(prefix="/reports")


@router.post("/", response_model=ReportOut)
async def create_weather_report(
    background_tasks: BackgroundTasks,
    city: str = Query(),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_report = Report(
        user_id=current_user["user_id"],
        status="pending"
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    background_tasks.add_task(
        generate_report,
        db_report.report_id,
        user.email,
        user.username,
        city,
        db
    )
    
    return db_report

@router.get("/")
async def list_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Report)
    
    if current_user["role"] != "admin":
        query = query.filter(Report.user_id == current_user["user_id"])
    
    total = query.count()
    offset = max(0, (page - 1) * limit)

    total_pages = ceil(total / limit) if limit else 1

    items = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "current_page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": items
    }

@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if current_user["role"] != "admin" and report.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if current_user["role"] != "admin" and report.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if report.file_path and os.path.exists(report.file_path):
        os.remove(report.file_path)
    
    db.delete(report)
    db.commit()
    return None

@router.get("/{report_id}/download", include_in_schema=False)
async def download_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if not report.file_path:
        raise HTTPException(status_code=404, detail="Report not ready")
    
    
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file missing")
    
    return FileResponse(
        report.file_path,
        media_type="text/csv",
        filename=f"report_{report_id}.csv"
    )
