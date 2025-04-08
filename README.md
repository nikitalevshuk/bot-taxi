# Taxi Driver Work Schedule Bot

A Telegram bot that helps taxi drivers manage their work schedules and monitor city statistics.

## Features

- Multi-language support (English, Polish, Russian, Ukrainian, Turkish)
- City-based work schedule management
- Daily work hours tracking
- City statistics monitoring
- Automatic daily schedule reset

## Requirements

- Python 3.13.0
- Dependencies listed in requirements.txt

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file:
```bash
cp .env.example .env
```

4. Edit .env and add your Telegram Bot Token:
```
BOT_TOKEN=your_bot_token_here
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the bot:
```bash
python main.py
```

## Usage

1. Start the bot by sending `/start`
2. Select your language
3. Choose your country and city
4. Use `/schedule` to set your work hours for the day
5. Use `/stats` to view city statistics

## Work Schedule Format

Enter work hours in the format: `HH:MM-HH:MM`
You can specify up to 3 time intervals separated by commas.

Examples:
- Single interval: `09:00-17:00`
- Multiple intervals: `09:00-11:00, 15:00-20:00`
