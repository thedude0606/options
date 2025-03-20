# Fixing .env File Issues

If you're seeing dotenv parsing warnings, follow these steps:

1. Delete your current `.env` file
2. Create a new `.env` file with exactly these three lines (no extra spaces or characters):
```
SCHWAB_APP_KEY=kQjNEtGHLhWUE0ZCdiaAkLDUfjBGT8G0
SCHWAB_APP_SECRET=dYPIYuVJiIuHMc1Y
SCHWAB_CALLBACK_URL=https://127.0.0.1:8080
```

You can also copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
