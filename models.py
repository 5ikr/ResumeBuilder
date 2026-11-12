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


@dataclass
class Education:
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""
    details: str = ""


@dataclass
class Experience:
    company: str = ""
    job_title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    achievements: str = ""
