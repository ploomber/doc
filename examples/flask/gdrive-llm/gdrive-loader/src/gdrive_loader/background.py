from celery import Celery
from gdrive_loader import load
from gdrive_loader.db import engine
from sqlalchemy.orm import Session
from gdrive_loader.models import User

app = Celery("gdrive_loader.background", broker="amqp://localhost")
app.conf.broker_connection_retry_on_startup = True


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    # 60 minutes
    PERIOD = 60 * 60

    sender.add_periodic_task(
        PERIOD,
        schedule_document_loading,
        name="schedule_document_loading",
    )


@app.task
def schedule_document_loading():
    with Session(engine) as db_session:
        users = db_session.query(User).all()
        for user in users:
            print(f"Scheduling document loading for user: {user.email}")
            load_documents_from_user.delay(
                email=user.email,
                limit=50,
            )


@app.task
def load_documents_from_user(email, limit=50):
    load.load_documents_from_user(email, dry_run=False, limit=limit)
