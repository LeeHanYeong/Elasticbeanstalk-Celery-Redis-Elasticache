from django.conf.urls import url

from .views import MailView

urlpatterns = [
    url(r'^mail/$', MailView.as_view(), name='mail'),
]
