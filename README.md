# Resume Builder

A Python / Streamlit workspace for building, refining, reviewing, and exporting professional resumes. The app works without an AI key. No database, account, or cloud storage is required.

## Run

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Start with your contact information, add relevant sections, then use **Preview** to choose a template and **Generate PDF** to prepare a download. Inputs update when you press Enter or leave a field; multiline fields also support Ctrl+Enter.

## What you can build

- Personal information, headline, and professional summary.
- Multiple degrees and jobs, with editable descriptions and one achievement per line.
- Skills with editable custom categories and optional text proficiency. Suggested categories include languages, frameworks, databases, tools, technical and soft skills. Skills display in compact groups without bars or percentages.
- Multiple projects: title, description, technologies, contributions, links, and optional dates. Projects and all new entry sections support moving entries up/down and removing individual entries.
- Certifications with issuer, date, and credential link; achievements with descriptions and optional dates.
- Languages, professional links, portfolio, GitHub, LinkedIn, and extracurricular activities.

The warm light workspace uses serif headings, restrained terracotta accents, refined forms, and an editor beside a live resume sheet. At smaller widths the columns stack. Import and workspace tools are grouped in sidebar disclosures.

## Templates and export

Choose **Preview → Resume template**:

1. **Classic Professional**: a single column with traditional serif typography and section rules.
2. **Modern Minimal**: sans-serif typography with restrained accent headings.
3. **Technical Resume**: a compact layout that brings skills and projects forward.

The template affects preview styling, section order, and PDF typography/spacing. **Student / entry-level emphasis** prioritizes education, skills, and projects. Hide optional sections and move sections up/down in Preview. Technical and student modes pin their priority sections before applying your remaining custom order. Empty sections stay off the resume.

The browser preview represents resume content and hierarchy; the PDF is the print layout, with its own measured wrapping and pagination. PDF exports support multiple pages, long links, bullet lists, page numbers, clickable email and supported HTTP(S) links, and selectable text colours. A generated download remains available until content, layout, or colour changes.

Noto Sans and Noto Serif fonts are bundled under the SIL Open Font License in `assets/fonts/`; export never downloads fonts at runtime. They support Latin, Greek, and Cyrillic, including accented names and typographic punctuation. These fonts do **not** cover every script or emoji. Unsupported characters produce an explicit error instead of disappearing. CJK, Indic shaping, and RTL typesetting would need additional fonts and shaping configuration.

## Profiles, autosave, and history

Everything autosaves **within the current Streamlit session only**. Navigation preserves edits. Restarting the server, losing the session, or reloading can clear data. Use **Save Profile (JSON)** for a durable local backup.

Version 2 JSON profiles include all sections, template, visibility, section order, and student mode. Existing version 1 profiles continue loading with empty defaults for new sections. Profile validation completes before replacing current data. Unknown fields are ignored; unsupported future format versions are rejected.

In **Workspace & history**, duplicate a resume under a new name and switch between independent profiles. **Undo / Redo** keeps up to 40 snapshots of content/layout changes in this session. A new edit after Undo clears the redo stack. Imported profiles can also be undone. AI suggestions and PDF bytes are not included in exported JSON or history. Download each named profile separately; JSON contains the selected resume, not the entire workspace. PDF colour is a workspace preference.

**Clear Data** asks for confirmation before clearing the entire session, including all profiles, history, imports, and generated downloads. Individual entry removal is recoverable with Undo.

## Resume import

Upload a PDF with extractable text, or UTF-8 / UTF-16 TXT. Files are read in memory; the app does not save them. Scanned PDFs need a text version (OCR is not included). Review all parsed values before using them.

Recognized headings: Summary / Profile / Professional Summary, Education, Experience / Work Experience / Professional Experience, Skills / Technical Skills, Projects, Certifications, Achievements, and Languages. Contact parsing retains existing fields it cannot recognize. Recognized nonempty sections replace only that section; unparseable sections retain existing entries and report a warning. Re-importing is explicit; normal reruns never overwrite edits.

Education and jobs accept labeled fields, or simple institution/degree and company/role blocks with dates. Separate entries with blank lines. Date ranges such as `2020 - Present` work. An experience entry's `Achievements:` label is retained as job content.

Skills accept comma, pipe, or semicolon-separated names, optionally prefixed by a category. New structured sections use labeled records to avoid guessing facts:

```text
Skills
Programming Languages: Python | SQL
Developer Tools: Git, Docker

Projects
Title: Resume workspace
Description: Built a resume editor.
Technologies: Python, Streamlit
Contributions: Implemented profile imports.
URL: https://example.com/project
Start date: Aug 2024
End date: Present

Certifications
Name: Cloud fundamentals
Issuer: Example Academy
Date: 2024
URL: https://example.com/credential

Achievements
Title: Student showcase
Description: Presented the editor.
Date: 2024

Languages
English, French
```

Freeform new-section paragraphs, multi-column PDFs, and arbitrary professional-link layouts are not reliably reconstructed. Use JSON for exact restoration of every field. Additional Information is edited manually; a Languages heading imports reliably.

## Optional AI writing assistant

`ai_service.py` separates the provider interface, requests, response validation, and OpenAI transport from Streamlit. It uses the [OpenAI Responses API with structured output](https://developers.openai.com/api/docs/guides/structured-outputs), through Python's standard library, without adding an SDK dependency.

Set environment variables **in the terminal that starts Streamlit**, then restart the app:

```powershell
$env:OPENAI_API_KEY = 'your-api-key'
$env:OPENAI_MODEL = 'gpt-4.1-mini'  # Optional; choose a Responses / structured-output capable model available to your account.
python -m streamlit run app.py
```

The app does not automatically load `.env` files. Never put keys in source code or profiles. `.env` and `.streamlit/secrets.toml` are ignored by Git; this integration reads environment variables only. Keys are never shown in the UI, sent in profile exports, or included in error messages.

Use **AI Improve** beside relevant writing fields. Actions: improve wording, make concise, expand, make more technical, make achievement-oriented, fix grammar, convert to bullets, and simplify. Select Professional, Concise, Technical, Achievement-oriented, or ATS-friendly style and Very concise, Short, Balanced, or Detailed length.

**Professional Summary → Summary assistant** generates a summary using existing education, experience, projects, skills, achievements, certifications, and headline. It avoids sending contact details. Change tone/length and regenerate, edit manually, or reject the result.

Before each request, the app displays source text and any context. You must explicitly consent to sending that information to **OpenAI**. Clicking Generate is the only way to initiate a call. The UI uses an in-flight guard, does not automatically retry, and does not call the API while typing or navigating. Regenerate is an intentional new request and may incur another charge. Requests have a timeout and set `store: false`; this does not replace OpenAI's service-side data policies. Job-aligned rewriting also sends the displayed job description and current entry.

Original and suggestion are displayed separately. **Accept** applies one suggestion; **Reject** discards it. Changed source text requires regeneration. Prompts prohibit invented facts, and validation rejects empty/malformed responses, unsupported new numeric claims, and added skills from the checked vocabulary. The assistant asks for details when input is vague. No automated validator can guarantee semantic truth: review all experience, outcomes, titles, qualifications, and technical claims before accepting. Length is a generation preference rather than forced word padding.

Missing keys, connectivity errors, API limits, refused/incomplete responses, and invalid output show safe, actionable messages. Editing, matching, quality checks, JSON, and PDFs continue working. Automated tests mock all API calls; no real resume data is sent during testing. A paid live-provider smoke test is deliberately excluded.

## Review & Match

**Quality checker** runs locally. It checks missing name/email/phone, email format, summary and skills, empty entries, inconsistent date formats, descriptions over 100 words, summaries over 90 words, duplicate lines of four or more words, incomplete projects, long unbroken text, hidden skills, and absence of supporting education/experience/projects. Recommendations are actionable; no arbitrary quality score is assigned.

**Job Match Analyzer** runs a separate local keyword comparison against the visible resume. It shows detected keywords, present and unevidenced terms, relevant experience/projects, quality issues, and alignment guidance. Optional AI Improve controls refine relevant entries individually with consent and review.

Coverage is **matched detected keywords / all detected keywords × 100**, rounded to a whole percent. Detection uses a defined technical vocabulary plus repeated meaningful words; matching uses case-insensitive boundaries, including C++/C#. Hidden sections do not count. This estimate is **not an ATS score**, a guarantee, or a semantic assessment of qualifications. Synonyms, negated requirements, and nuanced relevance can be missed. Missing terms are review/learning topics: add a qualification only when you actually possess it.

The sidebar completion indicator checks six draft essentials: name, email, summary, at least one named skill, an education institution, and experience or a project. Optional certifications and achievements never lower completion.

## Validation

```powershell
python -m unittest -v
python -m compileall -q app.py models.py ui.py profiles.py preview.py exporter.py resume_upload.py ai_service.py ai_ui.py analysis_tools.py editor_sections.py
```

The suite covers existing workflows, new entry editing/removal/reordering, session navigation, complete and legacy profiles, atomic invalid imports, named profiles/history, mocked AI success/failure/consent/validation, local analysis, all three templates, Unicode/link extraction, multi-page wrapping and content bounds, import feedback, and confirmed reset. Two original reset tests now explicitly confirm the destructive action before asserting cleared state.

See `UPGRADE_NOTES.md` for implementation files, validation evidence, and deliberate limits. Generated samples and validation output belong under ignored `samples/` and `output/`, never in commits.
