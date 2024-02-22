import enum
from dataclasses import dataclass
from datetime import date, datetime


class EncodeType(enum.Enum):
    PLAIN = 'PLAIN'
    ENCODED = 'ENCODED'
    ENCODED_LK = 'ENCODED_LK'
    ENCODED_EXP = 'ENCODED_EXP'
    ENCODED_EXP_LK = 'ENCODED_EXP_LK'


class ActionType(enum.Enum):
    GENERATE = 'GENERATE'
    UPDATE = 'UPDATE'


@dataclass
class ScriptLicenseConfig:
    encode: bool
    user_id: None | int = None
    license_key: None | str = None
    expires: None | date = None
    extra_params: None | dict = None

    @property
    def encode_type(self) -> EncodeType:
        if self.encode:
            got_license_key = self.license_key is not None
            got_expires = self.expires is not None
            if got_license_key and got_expires:
                result = EncodeType.ENCODED_EXP_LK
            elif not got_license_key and got_expires:
                result = EncodeType.ENCODED_EXP
            elif got_license_key and not got_expires:
                result = EncodeType.ENCODED_LK
            else:
                result = EncodeType.ENCODED
        else:
            result = EncodeType.PLAIN
        return result


@dataclass
class IssuedLicense:
    issued_at: None | datetime
    license_key: None | str
    script_id: str
    issued_by_id: None | int
    issue_type: EncodeType
    action: ActionType
    demo_lk: bool
    expires: None | date
    extra_params: None | dict

    @property
    def is_permanent(self):
        return self.expires is None


@dataclass
class Script:
    id: str


@dataclass
class GeneratedScript:
    data: bytes
    filename: str
