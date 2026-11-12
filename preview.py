def resume_markdown(personal_info, education, experience):
    lines = [f"# {personal_info.get('full_name') or 'Your name'}"]
    if personal_info.get("headline"):
        lines.append(personal_info["headline"])
    contact = [
        personal_info.get(field, "")
        for field in ("email", "phone", "location", "website")
    ]
    if any(contact):
        lines.append(" · ".join(value for value in contact if value))
    if personal_info.get("summary"):
        lines.extend(["## Profile", personal_info["summary"]])
    if education:
        lines.append("## Education")
        for entry in education.values():
            title = " — ".join(
                entry[field] for field in ("degree", "field_of_study") if entry[field]
            )
            lines.append(f"### {title or 'Degree'}")
            lines.append(entry["institution"])
            lines.append(" – ".join(filter(None, [entry["start_date"], entry["end_date"]])))
            lines.append(entry["details"])
    if experience:
        lines.append("## Experience")
        for entry in experience.values():
            lines.append(f"### {entry['job_title'] or 'Job title'}")
            lines.append(" · ".join(filter(None, [entry["company"], entry["location"]])))
            lines.append(" – ".join(filter(None, [entry["start_date"], entry["end_date"]])))
            lines.append("\n".join(
                f"- {line.strip()}"
                for line in entry["achievements"].splitlines() if line.strip()
            ))
    return "\n\n".join(line for line in lines if line)
