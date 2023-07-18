from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from database import User
from errors import DataError


async def post_lang(data: tuple[int, str], sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    """
    Post info about the user language to the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                user = await session.get(User, data[0])

                if user:
                    # update language info about the existing user
                    user.language = data[1]
                else:
                    # insert language info about the new user
                    user = User(user_id=data[0], language=data[1])
                    session.add(user)

            except:
                await session.rollback()
                raise DataError


async def get_data(user_id: int, sessionmaker: async_sessionmaker[AsyncSession]) -> dict[str, str | float]:
    """
    Get all info about the user from the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                user = await session.get(User, user_id)
                if user:
                    user_info = {
                        'language': user.language,
                        'latitude': user.latitude,
                        'longitude': user.longitude,
                        'temp_unit': user.temp_unit,
                        'wind_unit': user.wind_unit
                    }
                    return user_info
                else:
                    raise DataError

            except:
                await session.rollback()
                raise DataError


async def update_data(data: tuple[int, dict[str, str | float]], sessionmaker: async_sessionmaker[AsyncSession]) -> None:
    """
    Update certain info about the user in the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                user = await session.get(User, data[0])
                if user:
                    user.latitude = data[1]['latitude']
                    user.longitude = data[1]['longitude']
                    user.temp_unit = data[1]['temp_unit']
                    user.wind_unit = data[1]['wind_unit']
                else:
                    raise DataError

            except:
                await session.rollback()
                raise DataError


async def get_language(user_id: int, sessionmaker: async_sessionmaker[AsyncSession]) -> str:
    """
    Get info about the user language from the db.
    """
    async with sessionmaker() as session:
        async with session.begin():
            try:
                user = await session.get(User, user_id)

                if user:
                    return user.language
                else:
                    raise DataError

            except:
                await session.rollback()
                raise DataError
