from django.utils import timezone

from scripts.models import IssuedLicense as IssuedLicenseModel

from .structures import (
    ActionType,
    EncodeType,
    IssuedLicense,
    Script,
    ScriptLicenseConfig,
)


class IssuedLicenseDAO:
    """Data access object to connect with issued license storage"""

    @staticmethod
    def add(entity: IssuedLicense) -> None:
        """Adds record with issued script"""
        IssuedLicenseModel.objects.create(
            issued_at=entity.issued_at or timezone.now(),
            license_key=entity.license_key,
            script_id=entity.script_id,
            issued_by_id=entity.issued_by_id,
            issue_type=entity.issue_type.name,
            action=entity.action.name,
            demo_lk=entity.demo_lk,
            expires=entity.expires,
            extra_params=entity.extra_params,
        )

    @staticmethod
    def find_existing_license(
        script: Script,
        config: ScriptLicenseConfig
    ) -> None | IssuedLicense:
        """Searches for generated license for script + lk pair"""
        result = None
        issued: IssuedLicenseModel = IssuedLicenseModel.objects.filter(
            script_id=script.id,
            license_key=config.license_key,
            expires=None
        ).first()
        if issued is not None:
            result = IssuedLicense(
                issued_at=issued.issued_at,
                license_key=issued.license_key,
                script_id=issued.script.id,
                issued_by_id=issued.issued_by.id,
                issue_type=EncodeType(issued.issue_type),
                action=ActionType(issued.action),
                demo_lk=issued.demo_lk,
                expires=issued.expires,
                extra_params=issued.extra_params,
            )
        return result
