import os
import psycopg2
from psycopg2 import pool

class Database:
    _instances = {}  # <-- FIXED (dict instead of None)

    def __new__(cls, db_key, *args, **kwargs):
        if db_key not in cls._instances:
            cls._instances[db_key] = super(Database, cls).__new__(cls)
        return cls._instances[db_key]

    def __init__(self, db_key):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

        # Rabbit inbound credentials
        if db_key == "DB1":
            self.name = os.getenv("DB1_NAME")
            self.schema = os.getenv("DB1_SCHEMA")
            self.table = os.getenv("DB1_TABLE")

        # IMO lookup DB
        elif db_key == "DB2":
            self.name = os.getenv("DB2_NAME")
            self.schema = os.getenv("DB2_SCHEMA")
            self.table = os.getenv("DB2_TABLE")

        # Prompts DB
        elif db_key == "DB3":
            self.name = os.getenv("DB3_NAME")
            self.schema = os.getenv("DB3_SCHEMA")
            self.table = os.getenv("DB3_TABLE")

        # Ship table DB
        elif db_key == "DB4":
            self.name = os.getenv("DB4_NAME")
            self.schema = os.getenv("DB4_SCHEMA")
            self.table = os.getenv("DB4_TABLE")
        
        # Mapped DB final
        elif db_key == "DB5":
            self.name = os.getenv("DB5_NAME")
            self.schema = os.getenv("DB5_SCHEMA")
            self.table = os.getenv("DB5_TABLE")

        else:
            raise ValueError(f"Invalid DB key provided: {db_key}")

        self.dsn = (
            f"host={self.host} port={self.port} dbname={self.name} "
            f"user={self.user} password={self.password}"
        )

        self.pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=self.dsn
        )

        self._initialized = True

    def get_conn(self):
        return self.pool.getconn()

    def put_conn(self, conn):
        self.pool.putconn(conn)
