# Aiogram weather bot

<p align="center">
  <a href="https://github.com/j3rrryy/weather_bot/actions/workflows/main.yml">
    <img src="https://github.com/j3rrryy/weather_bot/actions/workflows/main.yml/badge.svg" alt="CI/CD">
  </a>
  <a href="https://www.python.org/downloads/release/python-3120/">
    <img src="https://img.shields.io/badge/Python-3.12-FFD64E.svg" alt="Python 3.12">
  </a>
  <a href="https://github.com/j3rrryy/weather_bot/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff">
  </a>
</p>

## :book: Key features

- Main DB - PostgreSQL
- DB for states - Redis
- Uses phone location for accurate forecast
- Uses English or Russian language to communicate
- Supports changing units of measurement
- Supports showing weather plots

## :computer: Requirements

- Docker

## :hammer_and_wrench: Getting started

- Create Telegram bot in [@BotFather](https://t.me/BotFather) and receive token
- Sign up in [Weather API](https://www.weatherapi.com/) and receive token
- Create `.env` file with variables as in the `examples/.env.example`

### :rocket: Start

```shell
docker compose up --build -d
```

### :x: Stop

```shell
docker compose stop
```

### :email: DM [@J3rry_Weather_Bot](https://t.me/J3rry_Weather_Bot) in Telegram
