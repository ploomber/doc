#!/bin/bash
nohup redis-server &
celery --app=task.app worker --concurrency=1 --loglevel=DEBUG &
uvicorn app:app --host=0.0.0.0 --port=80
