from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/sites", response_model=List[schemas.SiteOut])
def get_sites(db: Session = Depends(get_db)):
    return crud.list_sites(db)


@router.get("/pollutants", response_model=List[schemas.PollutantOut])
def get_pollutants(db: Session = Depends(get_db)):
    return crud.list_pollutants(db)


@router.get("/analysis", response_model=List[schemas.ChartDataPoint])
def get_analysis_data(
    site_id: int = Query(..., description="监测站点ID"),
    pollutant_id: int = Query(..., description="污染物ID"),
    start_date: date = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: date = Query(..., description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    schemas.DateRangeIn(start_date=start_date, end_date=end_date)
    return crud.build_chart_data(db, site_id, pollutant_id, start_date, end_date)

