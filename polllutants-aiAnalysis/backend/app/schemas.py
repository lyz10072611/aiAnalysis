from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class SiteOut(BaseModel):
    site_id: int
    site_name: str
    longitude: float
    latitude: float

    class Config:
        from_attributes = True


class PollutantOut(BaseModel):
    pollutant_id: int
    pollutant_name: str

    class Config:
        from_attributes = True


class ChartDataPoint(BaseModel):
    date: date
    hour: int
    timestamp: str
    stationValue: Optional[float] = None
    tifValue: Optional[float] = None


class DateRangeIn(BaseModel):
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def validate_range(cls, end_date: date, info):
        start_date = info.data.get("start_date")
        if start_date and end_date < start_date:
            raise ValueError("end_date 必须晚于 start_date")
        return end_date

