class DatabaseError(BaseException):
    def __init__(self) -> None:
        super().__init__("Database error")


class GetWeatherError(BaseException):
    def __init__(self) -> None:
        super().__init__("Can not get weather data")
