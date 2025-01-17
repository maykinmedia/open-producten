from django.core.management import call_command

from open_producten.celery import app


@app.task
def prune_logs(keep_days):
    call_command("prune_timeline_logs", keep_days=keep_days)
