from datetime import date
from typing import List

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from .models import Measurement, MeasurementTif, Pollutant, Site


def list_sites(db: Session) -> List[Site]:
    stmt = select(Site).order_by(Site.site_name.asc())
    return db.scalars(stmt).all()


def list_pollutants(db: Session) -> List[Pollutant]:
    stmt = select(Pollutant).order_by(Pollutant.pollutant_name.asc())
    return db.scalars(stmt).all()


def build_chart_data(
    db: Session,
    site_id: int,
    pollutant_id: int,
    start_date: date,
    end_date: date,
):
    base_filter = and_(
        Measurement.site_id == site_id,
        Measurement.pollutant_id == pollutant_id,
        Measurement.date >= start_date,
        Measurement.date <= end_date,
    )

    station_stmt = select(Measurement).where(base_filter)
    tif_stmt = select(MeasurementTif).where(
        and_(
            MeasurementTif.site_id == site_id,
            MeasurementTif.pollutant_id == pollutant_id,
            MeasurementTif.date >= start_date,
            MeasurementTif.date <= end_date,
        )
    )

    station_rows = db.scalars(station_stmt).all()
    tif_rows = db.scalars(tif_stmt).all()

    merged: dict[str, dict] = {}

    def key(date_value, hour_value) -> str:
        return f"{date_value.isoformat()} {hour_value:02d}:00"

    for row in station_rows:
        k = key(row.date, row.hour)
        merged[k] = {
            "date": row.date,
            "hour": row.hour,
            "timestamp": k,
            "stationValue": row.value,
            "tifValue": None,
        }

    for row in tif_rows:
        k = key(row.date, row.hour)
        if k not in merged:
            merged[k] = {
                "date": row.date,
                "hour": row.hour,
                "timestamp": k,
                "stationValue": None,
                "tifValue": row.value,
            }
        else:
            merged[k]["tifValue"] = row.value

    sorted_values = sorted(
        merged.values(), key=lambda item: (item["date"], item["hour"])
    )
    return sorted_values

