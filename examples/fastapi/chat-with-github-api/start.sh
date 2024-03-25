#!/bin/bash
sleep 10 && solara run client/main.py --host=0.0.0.0 --port=80 &
(nohup redis-server &
celery --app=api.task.app worker --concurrency=1 --loglevel=DEBUG &
uvicorn api.app:app --host=0.0.0.0 --port=8765 )


 