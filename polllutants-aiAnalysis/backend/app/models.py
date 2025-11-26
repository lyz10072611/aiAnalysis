from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


class Site(Base):
    __tablename__ = "sites"

    site_id = Column(Integer, primary_key=True, autoincrement=True)
    site_name = Column(String, unique=True, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)

    measurements = relationship("Measurement", back_populates="site")
    tif_measurements = relationship("MeasurementTif", back_populates="site")


class Pollutant(Base):
    __tablename__ = "pollutants"

    pollutant_id = Column(Integer, primary_key=True, autoincrement=True)
    pollutant_name = Column(String, unique=True, nullable=False)

    measurements = relationship("Measurement", back_populates="pollutant")
    tif_measurements = relationship("MeasurementTif", back_populates="pollutant")


class Measurement(Base):
    __tablename__ = "measurements"
    __table_args__ = (
        UniqueConstraint(
            "site_id",
            "pollutant_id",
            "date",
            "hour",
            name="unique_record",
        ),
        CheckConstraint("hour >= 0 AND hour <= 23", name="measurements_hour_check"),
    )

    distinct_id = Column(String, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.site_id"), nullable=False)
    pollutant_id = Column(Integer, ForeignKey("pollutants.pollutant_id"), nullable=False)
    date = Column(Date, nullable=False)
    hour = Column(Integer, nullable=False)
    value = Column(Float, nullable=True)

    site = relationship("Site", back_populates="measurements")
    pollutant = relationship("Pollutant", back_populates="measurements")


class MeasurementTif(Base):
    __tablename__ = "measurements_tif"
    __table_args__ = (
        UniqueConstraint(
            "site_id",
            "pollutant_id",
            "date",
            "hour",
            name="unique_record2",
        ),
        CheckConstraint(
            "hour >= 0 AND hour <= 23",
            name="measurements_tif_hour_check",
        ),
    )

    distinct_id = Column(String, primary_key=True)
    site_id = Column(Integer, ForeignKey("sites.site_id"), nullable=False)
    pollutant_id = Column(Integer, ForeignKey("pollutants.pollutant_id"), nullable=False)
    date = Column(Date, nullable=False)
    hour = Column(Integer, nullable=False)
    value = Column(Float, nullable=True)
    data_dir = Column(String, nullable=False)

    site = relationship("Site", back_populates="tif_measurements")
    pollutant = relationship("Pollutant", back_populates="tif_measurements")