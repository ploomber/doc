from celery import Celery
from hubspot_loader import load


app = Celery("hubspot_loader.background", broker="amqp://localhost")
app.conf.broker_connection_retry_on_startup = True


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    # 60 minutes
    PERIOD = 60 * 60

    sender.add_periodic_task(
        PERIOD,
        load_documents,
        name="load_documents",
    )


@app.task
def load_tickets(limit=50):
    load.load_tickets(limit=limit)
