from dataclasses import dataclass


@dataclass
class AppSettings:
    """App business logic settings"""
    demo_key_default_expiration_days: int
    demo_key_max_expiration_days: int
    user_key_max_expiration_days: int
