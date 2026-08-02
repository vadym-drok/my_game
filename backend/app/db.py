import os

from sqlmodel import SQLModel, create_engine

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

