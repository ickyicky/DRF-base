from django.db import connection
from django.conf import settings
from django.core.mail import send_mail

from celery import Task
from project.celery import app


class FaultTolerantTask(Task):
    """ Implements after return hook to close the invalid connection.
    This way, django is forced to serve a new connection for the next
    task.
    """

    abstract = True

    def after_return(self, *args, **kwargs):
        connection.close()


@app.task(name="send_email", base=FaultTolerantTask)
def mail(subject, recipients, message):
    print(f"[EMAIL] Sending email to {recipients}")
    send_mail(
        subject=subject,
        recipient_list=recipients,
        message=message,
        from_email=settings.project_MAIL,
        fail_silently=False,
    )
    return "success"
