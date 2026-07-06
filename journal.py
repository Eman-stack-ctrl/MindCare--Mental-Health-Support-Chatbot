"""
journal.py
==========
The Mood Journal popup window: shows past screening entries and any
personal notes attached to them, newest first.
"""

import tkinter as tk

from theme import COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_MUTED, COLOR_PRIMARY, COLOR_ACCENT
from assessments import _color_for_short_name
from storage import load_journal_entries


class JournalWindow(tk.Toplevel):
    def __init__(self, parent, user_name):
        super().__init__(parent)
        self.title("Mood Journal")
        self.geometry("480x560")
        self.configure(bg=COLOR_BG)

        tk.Label(self, text="📔 Your Mood Journal", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_BG, fg=COLOR_PRIMARY).pack(pady=(20, 4))
        tk.Label(self, text=f"History of screenings for {user_name}",
                 font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(0, 15))

        entries = load_journal_entries(user_name)

        outer = tk.Frame(self, bg=COLOR_BG)
        outer.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        canvas = tk.Canvas(outer, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        list_frame = tk.Frame(canvas, bg=COLOR_BG)

        list_frame.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=list_frame, anchor="nw", width=430)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if not entries:
            tk.Label(list_frame, text="No screenings yet. Complete one from the\n"
                                       "left panel and it will show up here with the date!",
                     font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_MUTED,
                     justify="center").pack(pady=40)
            return

        for entry in entries:
            color, icon = _color_for_short_name(entry["test"])
            card = tk.Frame(list_frame, bg=COLOR_CARD, highlightbackground=color,
                             highlightthickness=1)
            card.pack(fill="x", pady=6, padx=2)

            top_row = tk.Frame(card, bg=COLOR_CARD)
            top_row.pack(fill="x", padx=12, pady=(10, 2))
            tk.Label(top_row, text=f"{icon} {entry['test']}", bg=COLOR_CARD, fg=color,
                     font=("Segoe UI", 11, "bold")).pack(side="left")
            tk.Label(top_row, text=entry["timestamp"], bg=COLOR_CARD, fg=COLOR_MUTED,
                     font=("Segoe UI", 8)).pack(side="right")

            tk.Label(card, text=f"Score: {entry['score']}", bg=COLOR_CARD, fg=COLOR_TEXT,
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x", padx=12)
            if entry["interpretation"]:
                tk.Label(card, text=entry["interpretation"], bg=COLOR_CARD, fg=COLOR_MUTED,
                         font=("Segoe UI", 9), wraplength=390, justify="left",
                         anchor="w").pack(fill="x", padx=12, pady=(0, 4 if entry.get("note") else 10))

            if entry.get("note"):
                tk.Label(card, text=f"📝 \"{entry['note']}\"", bg=COLOR_CARD, fg=COLOR_ACCENT,
                         font=("Segoe UI", 9, "italic"), wraplength=390, justify="left",
                         anchor="w").pack(fill="x", padx=12, pady=(0, 10))
            elif not entry["interpretation"]:
                tk.Frame(card, bg=COLOR_CARD, height=6).pack()
