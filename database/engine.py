from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from config_data import Config, load_config


def create_async_engine(url: URL | str) -> AsyncEngine:
    return _create_async_engine(url=url, echo=True, pool_pre_ping=True)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)


async def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Configure the db connection"""

    config: Config = load_config(None)

    postgres_url = URL.create(
        drivername=config.db.driver,
        username=config.db.db_user,
        password=config.db.db_password,
        host=config.db.db_host,
        port=int(config.db.db_port),
        database=config.db.database
    )

    async_engine = create_async_engine(postgres_url)
    session_maker = create_sessionmaker(async_engine)

    return session_maker
