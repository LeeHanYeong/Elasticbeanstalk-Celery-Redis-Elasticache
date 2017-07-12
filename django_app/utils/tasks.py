from celery import shared_task


@shared_task
def utils_add(x, y):
    return x + y
