from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from config_data import Config, load_config


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """
    Configure the db connection
    """

    config: Config = load_config()

    postgres_url = URL.create(
        drivername=config.db.driver,
        username=config.db.db_user,
        password=config.db.db_password,
        host=config.db.db_host,
        port=int(config.db.db_port),
        database=config.db.database
    )

    async_engine = create_async_engine(url=postgres_url, pool_pre_ping=True)
    session_maker = async_sessionmaker(bind=async_engine, class_=AsyncSession)

    return session_maker
