from django.apps import AppConfig

class JobPlatformConfig(AppConfig):
    name = 'job_platform'

    def ready(self):
        import job_platform.signals