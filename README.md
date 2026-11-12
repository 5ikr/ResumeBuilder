# Resume Builder

Phase 1 of a Python Streamlit resume builder with a live Markdown preview.

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
session can clear it. PDF generation is outside Phase 1.

## Check

```powershell
python -m unittest -v
```

The Streamlit app test checks live updates, section navigation, multiple entries,
removal, and Markdown escaping.
