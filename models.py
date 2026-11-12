from dataclasses import dataclass


@dataclass
class PersonalInfo:
    full_name: str = ""
    headline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    website: str = ""
    summary: str = ""
