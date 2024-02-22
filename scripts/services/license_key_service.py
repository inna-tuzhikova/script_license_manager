from django.conf import settings


class LicenseKeyService:
    def __init__(self):
        self._lm_service_url = settings.LM_SERVICE_URL

    def is_demo_key(self, license_key: str) -> bool:
        # TODO add redis lk caching
        return True
