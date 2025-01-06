import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = sa.Column(sa.BIGINT, unique=True, nullable=False, primary_key=True)
    language = sa.Column(sa.VARCHAR, nullable=True)
    latitude = sa.Column(sa.DECIMAL, nullable=True)
    longitude = sa.Column(sa.DECIMAL, nullable=True)
    temp_unit = sa.Column(sa.VARCHAR, nullable=True)
    wind_unit = sa.Column(sa.VARCHAR, nullable=True)

    def __str__(self) -> str:
        return f"<User:{self.user_id}>"
