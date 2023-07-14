import smtplib
import os.path
import json

from email.message          import EmailMessage
from email.headerregistry   import Address
from io                     import BytesIO
from modelo                 import Modelo
from jinja2                 import (Environment, select_autoescape, FileSystemLoader,)

class Correo:

    ENV = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape())

    def __init__(self, archivoJson, emaRec, serRec, namRec, modelo):
        with open(os.path.join('json', archivoJson), 'r') as conex:
            arc = json.load(conex)
        self._emaEnv = arc["emailRemitente"] 
        self._serEnv = arc["servidorRemitente"] 
        self._namEnv = arc["nombreRemitente"] 
        self._emaCc = arc["emailCc"] 
        self._serCc = arc["servidorCc"] 
        self._namCc = arc["nombreCc"] 
        self._emaBcc = arc["emailBcc"] 
        self._serBcc = arc["servidorBcc"] 
        self._namBcc = arc["nombreBcc"]         
        self._asunto = arc["asunto"] 
        self._templa = arc["template"]
        self._adjunt = arc["adjunto"]

        self._emaRec = emaRec
        self._serRec = serRec
        self._namRec = namRec
        self._modelo = modelo

    def render_html(self, modelo: Modelo):
        template_result = Correo.ENV.get_template(self._templa)
        template_result = template_result.render(user=modelo)
        return template_result

    def open_file(self):
        file_image: BytesIO = None
        with open(self._adjunt, mode="rb") as file:
            file_image = file.read()
        return file_image

    def send_email(self, email_message: EmailMessage):

        remitente = self._emaEnv + "@" + self._serEnv
        destinatarios = [self._emaRec + "@" + self._serRec, self._emaCc + "@" + self._serCc, self._emaBcc + "@" + self._serBcc ]

        smtp = smtplib.SMTP_SSL("smtp.gmail.com")
        smtp.login(remitente, "ghpflywujadbastq")
        smtp.sendmail(remitente, destinatarios, email_message.as_string())
        smtp.quit()

    def build_email(self, user: Modelo):

        html_data: str = self.render_html(user)

        email_message               = EmailMessage()

        email_message["Subject"]    = self._asunto
        email_message["From"]       = Address(username=self._emaEnv, domain=self._serEnv, display_name=self._namEnv)
        email_message["To"]         = Address(username=self._emaRec, domain=self._serRec, display_name=self._namRec)
        email_message["Cc"]         = Address(username=self._emaCc, domain=self._serCc, display_name=self._namCc)
        email_message["Bcc"]        = Address(username=self._emaBcc, domain=self._serBcc, display_name=self._namBcc)

        email_message.add_alternative(html_data, subtype="html")
        
        if user.argregarArchivo:
            email_message.add_attachment(self.open_file(), maintype="application", subtype="xls", filename="otro.xls") #self._adjunt)
        
        self.send_email(email_message=email_message)
