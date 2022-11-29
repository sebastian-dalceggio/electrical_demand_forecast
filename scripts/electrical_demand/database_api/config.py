from decouple import AutoConfig

dconfig = AutoConfig()

DATABASE_TYPE = dconfig("DATABASE_TYPE")
DATABASE_USER = dconfig("DATABASE_USER")
DATABASE_PASSWORD = dconfig("DATABASE_PASSWORD")
DATABASE_HOST = dconfig("DATABASE_HOST")
DATABASE_NAME = dconfig("DATABASE_NAME")