from django.apps import AppConfig
import os
from threading import Thread

class SuperadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'superAdmin'

    def ready(self):
        """
        Lance le thread tcpdump uniquement lorsque le serveur Django démarre réellement.
        """
        # RUN_MAIN = true garantit que le thread ne se lance qu'une seule fois avec runserver
        if os.environ.get("RUN_MAIN") == "true":
            from .Analyser_tcpdump import lancer_capture
            Thread(target=lancer_capture, daemon=True).start()

