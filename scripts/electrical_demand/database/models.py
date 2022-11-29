"""
Data model definition.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Identity,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete

Base = declarative_base()

class Demand(Base):
    """Demand data model."""

    __tablename__ = "demand"
    id = Column(Integer, Identity(start=1, cycle=True), primary_key=True)
    datetime = Column(DateTime, nullable=False)
    region = Column(String, nullable=False)
    demand = Column(Integer)
    demand_forecast = Column(Integer)
    day_type = Column(String)
    temperature = Column(Float)
    temperature_forecast = Column(Float)
    __table_args__ = (
        UniqueConstraint(datetime, region, name="one_value_per_datetime_per_region"),
    )

    @staticmethod
    def insert(session, demand):
        """
        Insert or update demand rows in the database.

        Parameters
        ----------
        session : SQLAlchemy session
            Session in which the insert or update is committed.
        demand : list of dicts
            Demand to insert or update in the database as a list of dicts. All dicts must have the same keys.
        """
        stmt = insert(Demand).values(demand)
        keys = demand[0].keys()
        update_dict = {c.name: c for c in stmt.excluded if c.name in keys}
        update_stmt = stmt.on_conflict_do_update(
            constraint="one_value_per_datetime_per_region",
            set_=update_dict,
        )
        session.execute(update_stmt)

    @staticmethod
    def select_query(region):
        """
        Returns the query needed to get the demand data for a given region.

        Parameters
        ----------
        region : string
            SQL query to select the demand data for a given region
        """
        stmt = select(Demand).where(Demand.region == region)
        return stmt