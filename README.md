
### 1) Start backend API
```bash
cd server
uvicorn app.main:app --reload --port 8000
```

### 2) Start Celery worker
Run this in a second terminal:
```bash
cd server
celery -A app.celery_worker:celery_app worker --loglevel=info --pool=solo
```

### 3) Start frontend
```bash
cd client
npm run dev
```

