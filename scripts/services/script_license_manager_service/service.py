from datetime import date, timedelta

from .structures import (
    ScriptLicenseConfig,
    Script,
    IssuedLicense,
    ActionType,
    GeneratedScript
)
from .storage_adapters import IssuedLicenseDAO
from scripts.services.license_key_service import LicenseKeyService
from scripts.services.app_settings import AppSettings


class ScriptLicenseManagerService:
    def __init__(
        self,
        lk_service: LicenseKeyService,
        app_settings: AppSettings,
    ):
        self._lk_service = lk_service
        self._app_settings = app_settings

    def generate_script(
        self,
        script: Script,
        config: ScriptLicenseConfig
    ) -> GeneratedScript:
        demo = self._validate_expiration(config)
        generated = self._generate_script(script, config)
        self._finalize(script, config, action=ActionType.GENERATE, demo=demo)
        return generated

    def update_issued(
        self,
        script: Script,
        config: ScriptLicenseConfig
    ) -> GeneratedScript:
        issued = IssuedLicenseDAO.find_existing_license(script, config)
        if issued is None or not issued.is_permanent():
            raise PermissionError(
                'Script has not been generated permanently for this key'
            )
        demo = self._validate_expiration(config)
        generated = self._generate_script(script, config)
        self._finalize(script, config, action=ActionType.UPDATE, demo=demo)
        return generated

    def _generate_script(
        self,
        script: Script,
        config: ScriptLicenseConfig
    ) -> GeneratedScript:
        return GeneratedScript(
            data='print("Hello World!")\n'.encode(),
            filename='script.py'
        )

    def _validate_expiration(self, config: ScriptLicenseConfig) -> bool:
        is_demo_key = False
        if config.license_key is not None:
            today = date.today()
            is_demo_key = self._lk_service.is_demo_key(config.license_key)
            if is_demo_key:
                if config.expires is None:
                    config.expires = today + timedelta(
                        days=self._app_settings.demo_key_default_expiration_days
                    )
                else:
                    max_date = today + timedelta(
                        days=self._app_settings.demo_key_max_expiration_days
                    )
                    if config.expires > max_date:
                        config.expires = max_date
            else:
                if config.expires is not None:
                    max_date = today + timedelta(
                        days=self._app_settings.user_key_max_expiration_days
                    )
                    if config.expires > max_date:
                        raise PermissionError(
                            f'Trial for non demo key cannot exceed '
                            f'{self._app_settings.user_key_max_expiration_days}'
                            f' days',
                        )
        return is_demo_key

    def _finalize(
        self,
        script: Script,
        config: ScriptLicenseConfig,
        action: ActionType,
        demo: bool
    ) -> None:
        IssuedLicenseDAO.add(IssuedLicense(
            issued_at=None,
            license_key=config.license_key,
            script_id=script.id,
            issued_by_id=config.user_id,
            issue_type=config.encode_type,
            action=action,
            demo_lk=demo,
            expires=config.expires,
            extra_params=config.extra_params,
        ))
