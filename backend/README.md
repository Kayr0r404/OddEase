# OddEase API

## Prerequisites

- Python 3.11+
- PostgreSQL and/or MongoDB (depending on configured DB providers)

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

## Run

```bash
uvicorn main:app --reload --port <your-port-number> --host 127.0.0.1
```

The API will be available at `http://localhost:<your-port-number>`. Interactive docs at `http://localhost:<your-port-number>/docs`.
