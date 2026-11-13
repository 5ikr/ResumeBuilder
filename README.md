# Resume Builder

A Python Streamlit resume builder with a live Markdown preview and resume uploads.

## Run

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use the sidebar to switch between Personal Info, Education, Experience, and Preview.
Inputs update the preview when you press Enter or leave a field. Add and remove
degrees and jobs with the buttons. Put each job achievement on its own line.

Data lives in `st.session_state` and survives navigation between sections during
the current session. It is not saved to disk; reloading or disconnecting the
session can clear it. PDF export and JSON profile saving/loading are included.

## Resume Upload

Upload a `.pdf` or `.txt` file in the sidebar to fill your name, email, phone,
summary, Education, and Experience.
The app reads PDF text with pdfplumber and accepts UTF-8 or UTF-16 text files.
Scanned PDFs need a text version; OCR is not included.

The parser uses simple patterns, so review the imported values. It only updates
fields it finds and keeps your other data. Recognized Education and Experience
sections replace the existing entries in those sections. You can edit imported values without the upload overwriting them on
each rerun. Uploading another file imports again.

Use `Education` and `Experience` (or `Work Experience`) headings, with blank lines
between entries. Labeled fields such as `Institution:`, `Degree:`, `Company:`,
`Job title:`, `Start date:`, `End date:`, and `Achievements:` are supported.
Unlabeled entries can list institution, degree, field, start date, end date, then
details; jobs can list company, job title, location, start date, end date, then
achievements. Date ranges such as `2020 - Present` also work. Complex PDF layouts
may need manual corrections. Use JSON profiles for exact restoration of all fields.

Use **Clear Data** to reset all forms, remove the uploaded file, and clear import
messages. Files are read in memory and are not saved by the app.

## Check

```powershell
python -m unittest -v
```

The tests check live updates, navigation, multiple entries, removal, Markdown
escaping, PDF and text extraction, contact parsing, import callbacks, and reset.


## Export and saved profiles

Use **Save Profile (JSON)** to download the current form data. Upload that file
under **Load a saved profile** to restore all three sections.

Choose a PDF colour theme, then select **Generate PDF** and download the result.
The download stays available until the resume or theme changes. Generate again
after editing. The current PDF font supports Latin-1 text; unsupported characters
show an error instead of being silently replaced. Unicode fonts and OCR are not
included.

The integration tests also check profile loading, current JSON data, generated
PDF text, download persistence, colour changes, invalid profiles, and clearing.
