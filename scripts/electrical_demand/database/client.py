"""
This module provides clients for different types of databases.
You can create a Client instance and then call diferent methods to interact with the database.
"""
import abc
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SqlClient():
    """
    Abstract class used as a client of a database.
    This is an abstract class. For each database type there is a class that inherits this one.
    ...

    Attributes
    ----------
    dialect : str
        Database dialect.
    database_name : str
        Database name.
    host : str
        Database host.
    user : str
        Database user.
    password : str
        Database password.
    driver : str
        Database driver.
    _engine : SQLAlchemy engine
        SQLAlchemy engine to operate with the database.
    ...
    Methods
    -------
    _get_engine()
        Creates and returns an engine to be used to interact with the database.
    get_session()
        Returns an session to be used to interact with the database.
    get_dataframe(query)
        Return a table as a Pandas dataframe.
    """

    def __init__(
        self, dialect, database_name, host=None, user=None, password=None, driver=None
    ):
        """
        Parameters
        ----------
        dialect : {"sqlite", "postgresql"}
            Database dialect.
        database_name : str
            Database name.
        host : str, optional
            Database host.
        user : str, optional
            Database user.
        password : str, optional
            Database password.
        driver : str, optional
            Database driver.
        """
        self.dialect = dialect
        self.database_name = database_name
        self.host = host
        self.user = user
        self.password = password
        self.driver = driver
        self._engine = None

    @abc.abstractmethod
    def _get_engine(self):
        """
        Returns
        -------
        engine : SQLAlchemy engine
            Return the client engine.
        """

    def get_session(self):
        """
        Returns
        -------
        session : SQLAlchemy session
            Return a SQLAlchemy session.
        """
        if not self._engine:
            self._engine = self._get_engine()
        return sessionmaker(self._engine)

    def get_dataframe(self, query, index_col=None, parse_dates=None):
        """
        Parameters
        ----------
        query : str
            Query to send to the database.

        Returns
        -------
        df : Pandas dataframe
            Result of the query as a Pandas dataframe
        """
        if not self._engine:
            self._engine = self._get_engine()
        return pd.read_sql(query, self._engine, index_col=index_col, parse_dates=parse_dates)


class ComplexClient(SqlClient):
    def _get_engine(self):
        db_uri = f"{self.dialect if not self.driver else f'{self.dialect} + {self.driver}'}://{self.user}:{self.password}@{self.host}/{self.database_name}"
        if not self._engine:
            self._engine = create_engine(db_uri)
        return self._engine


class SqLiteClient(SqlClient):
    def _get_engine(self):
        db_uri = f"{self.dialect}:///{self.database_name}"
        if not self._engine:
            self._engine = create_engine(db_uri)
        return self._engine