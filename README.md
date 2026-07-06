# MindCare — Mental Health Support Chatbot

A Python/Tkinter desktop app that offers a guided, multi-screen mental
health check-in experience: a rule-based chatbot, four standardized
screening tools, a Mood Journal, progress trend charts, and PDF report
export.

**Disclaimer:** Educational / initial-screening tool only. Not a
diagnostic tool. Always directs the user toward a licensed professional.

## Features

- Guided flow: Welcome → Consent → Login → Dashboard → Chat / Assessments / Journal / Trends
- Rule-based chatbot with keyword/intent detection and a simulated "typing..." effect
- Four screening tools: PHQ-9 (Depression), GAD-7 (Anxiety), PSS-4 (Stress), WHO-5 (Wellbeing)
- Personalized coping tip + journaling prompt after every assessment
- Crisis helpline info shown automatically for high-severity results
- Mood Journal: persistent history across sessions with dates and notes
- Progress Trends: long-term line chart across all past sessions
- My Progress: bar chart for the current session + one-click PDF export
- History saved to `assessment_history.txt`

## Project structure

| File              | What it contains                                             |
|-------------------|---------------------------------------------------------------|
| `main.py`         | Entry point — run this to launch the app                     |
| `gui_app.py`      | Main window (MindCareApp) and the AssessmentWindow popup      |
| `chatbot.py`      | NLP intent detection and chatbot replies                      |
| `assessments.py`  | PHQ-9/GAD-7/PSS-4/WHO-5 definitions, scoring, coping tips      |
| `storage.py`      | Reading/writing assessment history and journal entries        |
| `journal.py`      | Mood Journal popup window                                     |
| `trends.py`       | Progress Trends line chart popup                               |
| `reports.py`      | Session bar chart popup + PDF report export                    |
| `theme.py`        | Shared color palette                                           |

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Requirements

- Python 3.8+
- matplotlib
- reportlab (optional — only needed for PDF export)
