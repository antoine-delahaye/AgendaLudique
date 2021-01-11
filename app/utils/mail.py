from threading import Thread

from flask import render_template

from flask_mail import Mail, Message


class MailTool(Mail):
    def __init__(self, app):
        self.init_app(app)
        self.app = app  # au cas où

    def __async_send_mail(self, msg):
        with self.app.app_context():
            self.send(msg)

    def send_mail(self, subject, recipient, template, **kwargs):
        """
                envoie un mail de manière asynchrone
                :param subject: le sujet du mail
                :param recipient: l'adresse mail de destination, un str
                :param template: le fichier (html) contenannant toutes les informations utiles à un envoie de mail
                :param kwargs tous les arguments nécessaire au rendu du template
                """
        msg = Message(subject, sender=(self.app.config['MAIL_DEFAULT_SENDER'],self.app.config["MAIL_USERNAME"]), recipients=[recipient])
        msg.html = render_template(template, **kwargs)
        thr = Thread(target=self.__async_send_mail, args=[msg])
        thr.start()
        return thr
