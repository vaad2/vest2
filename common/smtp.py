import smtplib

from django.core.mail.utils import DNS_NAME
from django.core.mail.backends.smtp import EmailBackend
from common.models import SiteSettings


class SSLEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            try:
                username = SiteSettings.objects.get(name='EMAIL_HOST_USER').value
                password = SiteSettings.objects.get(name='EMAIL_HOST_PASSWORD').value
                host = SiteSettings.objects.get(name='EMAIL_HOST').value
                port = SiteSettings.objects.get(name='EMAIL_PORT').value


            except Exception, e:
                username = self.username
                password = self.password
                host = self.host
                port = self.port


            self.connection = smtplib.SMTP_SSL(host, port,
                                           local_hostname=DNS_NAME.get_fqdn())

            self.connection.login(username, password)

            return True
        except:
            if not self.fail_silently:
                raise
