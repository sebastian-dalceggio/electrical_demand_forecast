from decouple import AutoConfig

dconfig = AutoConfig()

DATABASE_API_PORT = dconfig("DATABASE_API_PORT")
DATABASE_API_CONTAINER_NAME = dconfig("DATABASE_API_CONTAINER_NAME")