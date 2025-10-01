from django.core.mail import send_mail
from django.conf import settings

def enviar_correo(destinatario:str, asunto:str, cuerpo:str):
    # Adapter simple: internamente usa SMTP o consola según settings
    send_mail(asunto, cuerpo, settings.DEFAULT_FROM_EMAIL, [destinatario], fail_silently=False)
