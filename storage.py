"""
storage.py
==========
All reading/writing to assessment_history.txt: saving screening
results, saving journal notes, checking returning users, and
parsing the file back into structured entries for the Mood Journal
and Trends charts.
"""

import datetime
import os


def save_result_to_file(user_name, name, score, max_score, interpretation):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("assessment_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] | {user_name} | {name} | {score}/{max_score} | {interpretation}\n")


def save_journal_note(user_name, note_text):
    """Saves a free-text journal note, linked to the user's most recent entry."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_note = note_text.replace("|", "-").replace("\n", " ")
    with open("assessment_history.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] | {user_name} | NOTE | {safe_note}\n")


def has_prior_history(user_name):
    """Checks whether this user has any past screening history (for login greeting)."""
    if not os.path.exists("assessment_history.txt"):
        return False
    with open("assessment_history.txt", "r", encoding="utf-8") as f:
        for line in f:
            if f"| {user_name} |" in line:
                return True
    return False


def load_journal_entries(user_name=None):
    """Reads assessment_history.txt and returns parsed entries (newest first).
    NOTE lines are attached to the immediately preceding entry as 'note'."""
    entries = []
    if not os.path.exists("assessment_history.txt"):
        return entries
    with open("assessment_history.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ts_part, rest = line.split("]", 1)
                timestamp = ts_part.lstrip("[")
                parts = [p.strip() for p in rest.split("|")]
                if len(parts) == 4:
                    name, test, score_str = parts[1], parts[2], parts[3]
                    interpretation = ""
                elif len(parts) == 5:
                    name, test, score_str, interpretation = parts[1], parts[2], parts[3], parts[4]
                else:
                    continue

                if user_name and name != user_name:
                    continue

                if test == "NOTE":
                    if entries and entries[-1]["user"] == name:
                        entries[-1]["note"] = score_str
                    continue

                pct = None
                if "/" in score_str:
                    try:
                        s, m = score_str.split("/")
                        pct = round((float(s) / float(m)) * 100)
                    except (ValueError, ZeroDivisionError):
                        pct = None

                entries.append({
                    "timestamp": timestamp, "user": name,
                    "test": test, "score": score_str,
                    "interpretation": interpretation, "pct": pct,
                    "note": "",
                })
            except Exception:
                continue
    entries.reverse()
    return entries
