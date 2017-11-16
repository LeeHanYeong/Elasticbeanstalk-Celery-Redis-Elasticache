from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import send_mail_task

User = get_user_model()


class MailView(APIView):
    def post(self, request):
        subject = request.data['subject']
        message = request.data['message']

        users = User.objects.exclude(email='')
        success_count = send_mail_task.delay(
            subject,
            message,
        )
        return Response('success')
        # data = {
        #     'try': users.count(),
        #     'success': success_count,
        # }
        # return Response(data)
