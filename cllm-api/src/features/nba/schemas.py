from uuid import uuid4
from sqlmodel import SQLModel, Field


class NBAActionBase(SQLModel):
    pass

class NBABase(SQLModel):

    uuid: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)

class NBACreate(NBABase, table=True):
    __tablename__ = "nbas"

    nba_id: str