from django.conf import settings as sett

from .app_settings import AppSettings
from .license_key_service import LicenseKeyService
from .encoding_service import ScriptEncodingService
from .repo_service import RepoService
from .script_license_manager_service import ScriptLicenseManagerService


def init_services():
    settings = AppSettings(
        demo_key_default_expiration_days=sett.DEMO_KEY_DEFAULT_EXPIRATION_DAYS,
        demo_key_max_expiration_days=sett.DEMO_KEY_MAX_EXPIRATION_DAYS,
        user_key_max_expiration_days=sett.USER_KEY_MAX_EXPIRATION_DAYS,
    )
    lic_key_service = LicenseKeyService()
    se_service = ScriptEncodingService()
    rs_service = RepoService()
    slm_service = ScriptLicenseManagerService(
        lk_service=lic_key_service,
        app_settings=settings
    )
    return lic_key_service, se_service, rs_service, slm_service


(
    lk_service, script_encoding_service,
    repo_script_service, script_license_manager_service
) = init_services()
