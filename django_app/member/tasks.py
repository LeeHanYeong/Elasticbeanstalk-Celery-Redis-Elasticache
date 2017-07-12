from celery import shared_task


@shared_task
def member_add(x, y):
    return x + y
