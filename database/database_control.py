from mysql.connector import connect

from config_data import Config, load_config
from errors import DataError


config: Config = load_config(None)


def post_lang(data: tuple[int, str]) -> None:
    """
    Post info about the user language to the db.
    """

    try:
        with connect(database=config.db.database,
                    host=config.db.db_host,
                    port='3306',
                    user=config.db.db_user,
                    password=config.db.db_password) as connection:

            data_res = f"{data[0]}, '{data[1]}'"

            post_data = f"""
                            INSERT INTO users(user_id, language)
                            VALUES ({data_res});
                        """

            update_data = f"""
                            UPDATE users
                            SET language = {f"'{data[1]}'"}
                            WHERE user_id = {data[0]}
                        """
            with connection.cursor() as cursor:
                try:
                    # try to insert language info about the new user
                    cursor.execute(post_data)
                    connection.commit()
                except Exception:
                    # update language info about the existing user
                    cursor.execute(update_data)
                    connection.commit()

    except Exception:
        raise DataError

def get_data(user_id: int) -> dict[str, str | float]:
    """
    Get all info about the user from the db.
    """

    try:
        with connect(database=config.db.database,
                    host=config.db.db_host,
                    port='3306',
                    user=config.db.db_user,
                    password=config.db.db_password) as connection:

            get_data = f"""
                            SELECT language, latitude, longitude, temp_unit, wind_unit
                            FROM users
                            WHERE user_id = {user_id};
                        """

            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(get_data)
                return cursor.fetchall()[0] # type: ignore

    except Exception:
        raise DataError


def update_data(data: tuple[int, dict]) -> None:
    """
    Update certain info about the user in the db.
    """

    try:
        with connect(database=config.db.database,
                    host=config.db.db_host,
                    port='3306',
                    user=config.db.db_user,
                    password=config.db.db_password) as connection:

            data_elements = []

            for k, v in data[1].items():
                if isinstance(v, int):
                    data_elements.append(f'{k} = {v}')
                else:
                    data_elements.append(f"{k} = '{v}'")

            data_process = ',\n'.join(data_elements)

            update_data = f"""
                            UPDATE users
                            SET {data_process}
                            WHERE user_id = {data[0]};
                        """

            with connection.cursor() as cursor:
                cursor.execute(update_data)
                connection.commit()

    except Exception:
        raise DataError


def get_language(user_id: int) -> str:
    """
    Get info about the user language from the db.
    """

    try:
        with connect(database=config.db.database,
                    host=config.db.db_host,
                    port='3306',
                    user=config.db.db_user,
                    password=config.db.db_password) as connection:

            get_lang = f"""
                            SELECT language
                            FROM users
                            WHERE user_id = {user_id};
                        """

            with connection.cursor() as cursor:
                cursor.execute(get_lang)
                return cursor.fetchone()[0]

    except Exception:
        raise DataError
