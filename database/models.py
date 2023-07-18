from sqlalchemy import Column, Integer, VARCHAR, DECIMAL
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    # Telegram user id
    user_id = Column(Integer, unique=True, nullable=False, primary_key=True)

    language = Column(VARCHAR(2), nullable=True)
    latitude = Column(DECIMAL(8, 6), nullable=True)
    longitude = Column(DECIMAL(9, 6), nullable=True)
    temp_unit = Column(VARCHAR(10), nullable=True)
    wind_unit = Column(VARCHAR(4), nullable=True)

    def __str__(self) -> str:
        return f'<User:{self.user_id}>'
