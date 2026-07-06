"""
trends.py
=========
The Progress Trends popup: a matplotlib line chart showing how each
screening's score has moved across all of the user's past sessions.
"""

import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from theme import COLOR_CARD, COLOR_TEXT, COLOR_MUTED, COLOR_PRIMARY
from assessments import _color_for_short_name
from storage import load_journal_entries


class TrendWindow(tk.Toplevel):
    def __init__(self, parent, user_name):
        super().__init__(parent)
        self.title("Progress Trends")
        self.geometry("580x540")
        self.minsize(580, 540)
        self.configure(bg=COLOR_CARD)

        tk.Label(self, text="📈 Your Long-Term Progress", font=("Segoe UI", 13, "bold"),
                 bg=COLOR_CARD, fg=COLOR_PRIMARY).pack(pady=(20, 5))

        entries = [e for e in load_journal_entries(user_name) if e.get("pct") is not None]
        entries.sort(key=lambda e: e["timestamp"])  # oldest -> newest for a left-to-right trend

        if len(entries) < 2:
            tk.Label(self, text="Not enough history yet. Complete at least 2\n"
                                 "screenings (any type) to see your trend over time.",
                     font=("Segoe UI", 10), bg=COLOR_CARD, fg=COLOR_MUTED,
                     justify="center").pack(pady=60)
            return

        by_test = {}
        for e in entries:
            by_test.setdefault(e["test"], []).append(e)

        fig = Figure(figsize=(5.4, 3.6), dpi=100, facecolor=COLOR_CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLOR_CARD)

        for test_name, test_entries in by_test.items():
            color, _icon = _color_for_short_name(test_name)
            xs = list(range(len(test_entries)))
            ys = [e["pct"] for e in test_entries]
            ax.plot(xs, ys, marker="o", label=test_name, color=color, linewidth=2)

        ax.set_ylim(0, 100)
        ax.set_ylabel("Score (%)", color=COLOR_TEXT)
        ax.set_xlabel("Screening # (over time)", color=COLOR_TEXT)
        ax.set_title("Lower is generally better (except Wellbeing)", color=COLOR_TEXT, fontsize=9)
        ax.tick_params(colors=COLOR_TEXT)
        for spine in ax.spines.values():
            spine.set_color(COLOR_MUTED)
        ax.legend(facecolor=COLOR_CARD, labelcolor=COLOR_TEXT, fontsize=8, loc="upper right")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=15, pady=10)

        tk.Label(self, text=f"Based on {len(entries)} screenings across all your sessions.",
                 font=("Segoe UI", 9), bg=COLOR_CARD, fg=COLOR_MUTED).pack(pady=(0, 15))
