"""
gui_app.py
==========
The main application window (MindCareApp): welcome, consent, login,
dashboard, and chat screens. Also the AssessmentWindow popup used to
run a single screening (PHQ-9 / GAD-7 / PSS-4 / WHO-5).
"""

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from theme import (
    COLOR_BG, COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_ACCENT, COLOR_CARD,
    COLOR_TEXT, COLOR_MUTED, COLOR_USER_BUBBLE, COLOR_BOT_BUBBLE, COLOR_INPUT_BG,
)
from chatbot import get_bot_reply, HELPLINE_INFO
from assessments import ASSESSMENTS, COPING_TIPS, JOURNAL_PROMPTS, get_severity_band
from storage import save_result_to_file, save_journal_note, has_prior_history
from journal import JournalWindow
from trends import TrendWindow
from reports import ProgressWindow


class MindCareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MindCare - Mental Health Support Chatbot")
        self.geometry("760x640")
        self.minsize(760, 640)
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)

        self.title_font = tkfont.Font(family="Segoe UI", size=26, weight="bold")
        self.subtitle_font = tkfont.Font(family="Segoe UI", size=12)
        self.body_font = tkfont.Font(family="Segoe UI", size=11)
        self.emoji_font = tkfont.Font(family="Segoe UI Emoji", size=48)

        self.session_records = []  # list of dicts: name, score, max, pct, interpretation
        self.user_name = "there"
        self.user_age = None
        self.is_returning_user = False
        self.awaiting_note = False
        self.pending_note_key = None

        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True)

        self.show_welcome_screen()

    # ---------- UI polish helper ----------
    def _add_hover(self, widget, base_color):
        def lighten(hex_color, amount=25):
            hex_color = hex_color.lstrip("#")
            r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r, g, b = (min(255, c + amount) for c in (r, g, b))
            return f"#{r:02x}{g:02x}{b:02x}"
        hover_color = lighten(base_color)
        widget.bind("<Enter>", lambda e: widget.config(bg=hover_color))
        widget.bind("<Leave>", lambda e: widget.config(bg=base_color))

    # ---------- screen switching helper ----------
    def _clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------- SCREEN 1: WELCOME ----------
    def show_welcome_screen(self):
        self._clear()
        frame = tk.Frame(self.container, bg=COLOR_BG)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="🧠", font=self.emoji_font, bg=COLOR_BG).pack(pady=(90, 10))
        tk.Label(frame, text="MindCare", font=self.title_font,
                 bg=COLOR_BG, fg=COLOR_PRIMARY).pack()
        tk.Label(frame, text="Mental Health Support Chatbot",
                 font=self.subtitle_font, bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(4, 40))

        get_started_btn = tk.Button(
            frame, text="Get Started", bg=COLOR_PRIMARY, fg="white",
            font=("Segoe UI", 12, "bold"), relief="flat", padx=30, pady=12,
            activebackground=COLOR_PRIMARY_DARK, activeforeground="white",
            cursor="hand2", bd=0, command=self.show_consent_screen
        )
        get_started_btn.pack()
        self._add_hover(get_started_btn, COLOR_PRIMARY)

        tk.Label(
            frame, text="An initial screening & support tool - not a replacement\nfor professional care.",
            font=("Segoe UI", 9), bg=COLOR_BG, fg=COLOR_MUTED, justify="center"
        ).pack(side="bottom", pady=20)

    # ---------- SCREEN 2: CONSENT ----------
    def show_consent_screen(self):
        self._clear()
        frame = tk.Frame(self.container, bg=COLOR_BG)
        frame.pack(fill="both", expand=True)

        card = tk.Frame(frame, bg=COLOR_CARD, padx=40, pady=40,
                         highlightbackground=COLOR_PRIMARY, highlightthickness=1)
        card.pack(pady=110, padx=60, fill="x")

        tk.Label(card, text="👋", font=("Segoe UI Emoji", 32), bg=COLOR_CARD).pack()
        tk.Label(
            card,
            text=("Hi, I'm MindCare. I will help you understand your mental "
                  "wellbeing through a friendly conversation and a few short, "
                  "science-based screenings for depression, anxiety, stress "
                  "and overall wellbeing.\n\nWould you like to avail this opportunity?"),
            font=self.body_font, bg=COLOR_CARD, fg=COLOR_TEXT,
            wraplength=520, justify="center"
        ).pack(pady=20)

        btn_row = tk.Frame(card, bg=COLOR_CARD)
        btn_row.pack(pady=10)

        tk.Button(
            btn_row, text="Yes, let's begin", bg=COLOR_ACCENT, fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=10,
            cursor="hand2", command=self.show_userinfo_screen
        ).pack(side="left", padx=10)

        tk.Button(
            btn_row, text="Not now", bg="#3a3a52", fg=COLOR_TEXT,
            font=("Segoe UI", 11), relief="flat", padx=20, pady=10,
            cursor="hand2", command=self.show_decline_screen
        ).pack(side="left", padx=10)

    def show_decline_screen(self):
        self._clear()
        frame = tk.Frame(self.container, bg=COLOR_BG)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="🌿", font=self.emoji_font, bg=COLOR_BG).pack(pady=(120, 10))
        tk.Label(
            frame, text="That's okay. Come back anytime you feel ready.",
            font=self.subtitle_font, bg=COLOR_BG, fg=COLOR_TEXT
        ).pack(pady=10)
        tk.Button(
            frame, text="Back to Start", bg=COLOR_PRIMARY, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8,
            cursor="hand2", command=self.show_welcome_screen
        ).pack(pady=20)

    # ---------- SCREEN 2b: NAME / AGE ----------
    def show_userinfo_screen(self):
        self._clear()
        frame = tk.Frame(self.container, bg=COLOR_BG)
        frame.pack(fill="both", expand=True)

        card = tk.Frame(frame, bg=COLOR_CARD, padx=40, pady=30,
                         highlightbackground=COLOR_PRIMARY, highlightthickness=1)
        card.pack(pady=60, padx=80, fill="x")

        tk.Label(card, text="🙂", font=("Segoe UI Emoji", 32), bg=COLOR_CARD).pack()
        tk.Label(
            card, text="Welcome — please log in to continue",
            font=("Segoe UI", 13, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT
        ).pack(pady=(10, 20))

        tk.Label(card, text="Name", font=self.body_font, bg=COLOR_CARD,
                 fg=COLOR_MUTED).pack(anchor="w")
        name_entry = tk.Entry(card, font=self.body_font, relief="flat", bg=COLOR_INPUT_BG,
                               fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        name_entry.pack(fill="x", ipady=8, pady=(2, 15))

        tk.Label(card, text="Age", font=self.body_font, bg=COLOR_CARD,
                 fg=COLOR_MUTED).pack(anchor="w")
        age_entry = tk.Entry(card, font=self.body_font, relief="flat", bg=COLOR_INPUT_BG,
                              fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        age_entry.pack(fill="x", ipady=8, pady=(2, 5))

        error_lbl = tk.Label(card, text="", font=("Segoe UI", 9), bg=COLOR_CARD, fg="#ff6b6b")
        error_lbl.pack(anchor="w", pady=(0, 10))

        def submit(event=None):
            name = name_entry.get().strip()
            age_text = age_entry.get().strip()
            if not name:
                error_lbl.config(text="Please enter your name.")
                return
            if not age_text.isdigit() or not (5 <= int(age_text) <= 120):
                error_lbl.config(text="Please enter a valid age.")
                return
            self.user_name = name
            self.user_age = int(age_text)
            self.is_returning_user = has_prior_history(name)
            self.show_dashboard_screen()

        continue_btn = tk.Button(
            card, text="Log In ▶", bg=COLOR_PRIMARY, fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", padx=20, pady=10,
            cursor="hand2", command=submit
        )
        continue_btn.pack(pady=(10, 0))

        # Enter key on either field also submits
        name_entry.bind("<Return>", submit)
        age_entry.bind("<Return>", submit)
        name_entry.focus_set()

    # ---------- SCREEN 2c: DASHBOARD (features overview) ----------
    def show_dashboard_screen(self):
        self._clear()
        frame = tk.Frame(self.container, bg=COLOR_BG)
        frame.pack(fill="both", expand=True)

        greeting = f"Welcome back, {self.user_name}! 👋" if self.is_returning_user \
            else f"Nice to meet you, {self.user_name}! 👋"

        tk.Label(frame, text=greeting, font=("Segoe UI", 16, "bold"),
                 bg=COLOR_BG, fg=COLOR_PRIMARY).pack(pady=(20, 2))
        tk.Label(frame, text="Here's everything MindCare can help you with:",
                 font=("Segoe UI", 10), bg=COLOR_BG, fg=COLOR_MUTED).pack(pady=(0, 15))

        outer = tk.Frame(frame, bg=COLOR_BG)
        outer.pack(fill="both", expand=True, padx=20)

        canvas = tk.Canvas(outer, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        cards_frame = tk.Frame(canvas, bg=COLOR_BG)
        cards_frame.bind("<Configure>",
                         lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=cards_frame, anchor="nw", width=680)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        descriptions = {
            "phq9": "Understand feelings of sadness, hopelessness, or low energy.",
            "gad7": "Measure worry, nervousness, or restlessness.",
            "pss4": "Check how overwhelmed or in-control you've been feeling.",
            "who5": "See how positive and energized your daily life has been.",
        }

        def make_card(icon, title, desc, color, btn_text, command):
            card = tk.Frame(cards_frame, bg=COLOR_CARD, highlightbackground=color,
                             highlightthickness=1)
            card.pack(fill="x", pady=6)
            left = tk.Frame(card, bg=COLOR_CARD)
            left.pack(side="left", fill="both", expand=True, padx=15, pady=12)
            tk.Label(left, text=f"{icon}  {title}", bg=COLOR_CARD, fg=color,
                     font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x")
            tk.Label(left, text=desc, bg=COLOR_CARD, fg=COLOR_MUTED,
                     font=("Segoe UI", 9), anchor="w", wraplength=460,
                     justify="left").pack(fill="x")
            btn = tk.Button(card, text=btn_text, bg=color, fg="white",
                             font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                             padx=14, cursor="hand2", command=command)
            btn.pack(side="right", padx=15)
            self._add_hover(btn, color)

        for key, data in ASSESSMENTS.items():
            make_card(data["icon"], data["short"], descriptions[key], data["color"],
                      "Start →", lambda k=key: self.open_feature_from_dashboard(k))

        make_card("📔", "Mood Journal", "View your past entries, scores, and personal notes over time.",
                   "#2d4a63", "Open →", self.show_journal_window)
        make_card("📈", "Progress Trends", "See how your scores have changed over time, across sessions.",
                   COLOR_PRIMARY_DARK, "View →", self.show_trend_window)

        chat_btn = tk.Button(
            frame, text="💬 Go to Chat", bg=COLOR_ACCENT, fg="white",
            font=("Segoe UI", 11, "bold"), relief="flat", bd=0, padx=25, pady=10,
            cursor="hand2", command=self.show_chat_screen
        )
        chat_btn.pack(pady=15)
        self._add_hover(chat_btn, COLOR_ACCENT)

    def open_feature_from_dashboard(self, key):
        self.show_chat_screen()
        self.after(200, lambda: self.start_assessment(key))

    # ---------- SCREEN 3: MAIN CHAT + ASSESSMENT HUB ----------
    def show_chat_screen(self):
        self._clear()
        root = tk.Frame(self.container, bg=COLOR_BG)
        root.pack(fill="both", expand=True)

        # ---- Sidebar ----
        sidebar = tk.Frame(root, bg="#0a1628", width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="🧠 MindCare", bg="#0a1628", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(pady=(25, 4), padx=15, anchor="w")
        tk.Label(sidebar, text=f"Hi, {self.user_name}", bg="#0a1628", fg="#f5f0fa",
                 font=("Segoe UI", 9)).pack(padx=15, pady=(0, 16), anchor="w")

        tk.Label(sidebar, text="SCREENING TOOLS", bg="#0a1628", fg="#f5f0fa",
                 font=("Segoe UI", 8, "bold")).pack(padx=15, anchor="w")

        for key, data in ASSESSMENTS.items():
            btn = tk.Button(
                sidebar, text=f"{data['icon']}  {data['short']}", bg=data["color"], fg="white",
                font=("Segoe UI", 10, "bold"), relief="flat", anchor="w",
                padx=15, pady=10, cursor="hand2", bd=0, activebackground=data["color"],
                command=lambda k=key: self.start_assessment(k)
            )
            btn.pack(fill="x", padx=15, pady=5)
            self._add_hover(btn, data["color"])

        tk.Frame(sidebar, bg="#0a1628", height=15).pack()
        progress_btn = tk.Button(
            sidebar, text="📊  My Progress", bg=COLOR_PRIMARY_DARK, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=10, bd=0,
            cursor="hand2", command=self.show_progress_window
        )
        progress_btn.pack(fill="x", padx=15, pady=5)
        self._add_hover(progress_btn, COLOR_PRIMARY_DARK)

        journal_btn = tk.Button(
            sidebar, text="📔  Mood Journal", bg="#2d4a63", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=10, bd=0,
            cursor="hand2", command=self.show_journal_window
        )
        journal_btn.pack(fill="x", padx=15, pady=5)
        self._add_hover(journal_btn, "#2d4a63")

        trend_btn = tk.Button(
            sidebar, text="📈  Trends", bg="#2d4a63", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=10, bd=0,
            cursor="hand2", command=self.show_trend_window
        )
        trend_btn.pack(fill="x", padx=15, pady=5)
        self._add_hover(trend_btn, "#2d4a63")

        tk.Frame(sidebar, bg="#0a1628", height=10).pack()
        dash_btn = tk.Button(
            sidebar, text="🏠  Dashboard", bg="#0a1628", fg=COLOR_MUTED,
            font=("Segoe UI", 9), relief="flat", padx=15, pady=8, bd=0,
            cursor="hand2", command=self.show_dashboard_screen
        )
        dash_btn.pack(fill="x", padx=15, pady=5, side="bottom")
        self._add_hover(dash_btn, "#0a1628")

        # ---- Chat area ----
        chat_col = tk.Frame(root, bg=COLOR_BG)
        chat_col.pack(side="left", fill="both", expand=True)

        canvas_frame = tk.Frame(chat_col, bg=COLOR_BG)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_frame, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.chat_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.chat_frame.bind("<Configure>",
                              lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=500)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        input_row = tk.Frame(chat_col, bg=COLOR_BG)
        input_row.pack(fill="x", padx=10, pady=(0, 10))

        self.entry = tk.Entry(input_row, font=self.body_font, relief="flat", bg=COLOR_INPUT_BG,
                               fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
        self.entry.pack(side="left", fill="x", expand=True, ipady=9, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.on_send())

        tk.Button(
            input_row, text="Send", bg=COLOR_ACCENT, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=18,
            cursor="hand2", command=self.on_send
        ).pack(side="right")

        self._bot_say(
            f"Great, let's get started, {self.user_name}! You can just talk "
            "to me about how you're feeling, or pick a screening tool from "
            "the left panel any time (Depression, Anxiety, Stress, or Wellbeing)."
        )
        if self.user_age is not None and self.user_age < 18:
            self._bot_say(
                "Since you're under 18, please also consider talking to a "
                "parent, guardian, teacher, or school counselor about how "
                "you're feeling - you don't have to handle this alone."
            )

    # ---------- chat bubble helpers ----------
    def _add_bubble(self, text, sender="bot"):
        align = "e" if sender == "user" else "w"
        bg = COLOR_USER_BUBBLE if sender == "user" else COLOR_BOT_BUBBLE
        fg = "white" if sender == "user" else COLOR_TEXT

        row = tk.Frame(self.chat_frame, bg=COLOR_BG)
        row.pack(fill="x", pady=5, anchor=align)

        bubble = tk.Label(row, text=text, bg=bg, fg=fg, font=self.body_font,
                           wraplength=380, justify="left", padx=14, pady=10,
                           highlightbackground=COLOR_MUTED, highlightthickness=1)
        bubble.pack(side="right" if sender == "user" else "left", padx=10)

        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _bot_say(self, text):
        self._add_bubble(text, sender="bot")

    def _bot_say_with_typing(self, text, delay=500):
        typing_row = tk.Frame(self.chat_frame, bg=COLOR_BG)
        typing_row.pack(fill="x", pady=5, anchor="w")
        typing_lbl = tk.Label(typing_row, text="typing...", bg=COLOR_BOT_BUBBLE,
                               fg=COLOR_MUTED, font=("Segoe UI", 9, "italic"),
                               padx=14, pady=8)
        typing_lbl.pack(side="left", padx=10)
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)

        def replace():
            typing_row.destroy()
            self._bot_say(text)

        self.after(delay, replace)

    def _user_say(self, text):
        self._add_bubble(text, sender="user")

    # ---------- events ----------
    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._user_say(text)

        if self.awaiting_note:
            self.awaiting_note = False
            save_journal_note(self.user_name, text)
            self._bot_say_with_typing(
                "Thank you for sharing that with me 💙 — I've saved it in your Mood Journal.",
                delay=450
            )
            return

        reply = get_bot_reply(text)
        self._bot_say_with_typing(reply, delay=450)

    def start_assessment(self, key):
        data = ASSESSMENTS[key]
        self._bot_say(f"Starting: {data['name']}. Please answer for the LAST 2 WEEKS.")
        AssessmentWindow(self, key, on_finish=self.show_assessment_result)

    def show_assessment_result(self, key, score, answers):
        data = ASSESSMENTS[key]
        interpretation = data["interpret"](score)
        pct = round((score / data["max"]) * 100)

        msg = (
            f"Assessment complete ✅  ({data['short']})\n\n"
            f"Score: {score} / {data['max']}\n"
            f"Result: {interpretation}\n\n"
            "This is NOT a clinical diagnosis. If your result is moderate or "
            "higher, please consider speaking with a licensed mental health "
            "professional."
        )
        self._bot_say(msg)
        save_result_to_file(self.user_name, data["short"], score, data["max"], interpretation)

        self.session_records.append({
            "name": data["short"], "score": score, "max": data["max"],
            "pct": pct, "interpretation": interpretation,
        })

        if key != "who5" and (pct >= 75 or "severe" in interpretation.lower()):
            self._bot_say(HELPLINE_INFO)
        elif key == "who5" and pct <= 25:
            self._bot_say(HELPLINE_INFO)
        elif key == "phq9" and answers[-1] > 0:
            self._bot_say(HELPLINE_INFO)

        # ---- Personalized coping tip ----
        band = get_severity_band(key, pct)
        tip = COPING_TIPS[key][band]
        self._bot_say(f"💡 {tip}")

        # ---- Journaling prompt ----
        self._bot_say(JOURNAL_PROMPTS[key])
        self.awaiting_note = True
        self.pending_note_key = key

    # ---------- progress dashboard ----------
    def show_progress_window(self):
        if not self.session_records:
            self._bot_say("You haven't completed any screenings yet in this session. "
                           "Try one from the left panel!")
            return
        ProgressWindow(self, self.session_records)

    # ---------- mood journal ----------
    def show_journal_window(self):
        JournalWindow(self, self.user_name)

    # ---------- long-term trends ----------
    def show_trend_window(self):
        TrendWindow(self, self.user_name)


class AssessmentWindow(tk.Toplevel):
    """Popup used to run a single screening tool, themed per test, with a progress bar."""

    def __init__(self, parent, key, on_finish):
        super().__init__(parent)
        self.data = ASSESSMENTS[key]
        self.key = key
        self.on_finish = on_finish
        self.current_q = 0
        self.answers = []

        self.title(self.data["name"])
        self.geometry("520x600")
        self.minsize(520, 600)
        self.configure(bg=COLOR_CARD)

        header = tk.Frame(self, bg=self.data["color"], height=55)
        header.pack(fill="x")
        tk.Label(header, text=self.data["name"], bg=self.data["color"], fg="white",
                 font=("Segoe UI", 12, "bold")).pack(pady=14, padx=15, anchor="w")

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate",
                                             maximum=len(self.data["questions"]))
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))

        self.progress_lbl = tk.Label(self, text="", font=("Segoe UI", 9),
                                      bg=COLOR_CARD, fg=COLOR_MUTED)
        self.progress_lbl.pack(anchor="w", padx=20)

        self.q_label = tk.Label(self, text="", wraplength=440, font=("Segoe UI", 12, "bold"),
                                 bg=COLOR_CARD, fg=COLOR_TEXT, justify="left")
        self.q_label.pack(pady=(20, 10), padx=20, anchor="w")

        self.options_frame = tk.Frame(self, bg=COLOR_CARD)
        self.options_frame.pack(pady=10, fill="x", padx=20)

        self.selected = tk.IntVar(value=-1)

        self.next_btn = tk.Button(
            self, text="Next ▶", bg=self.data["color"], fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8,
            cursor="hand2", command=self.next_question
        )
        self.next_btn.pack(side="bottom", pady=20)

        self.render_question()

    def render_question(self):
        for w in self.options_frame.winfo_children():
            w.destroy()
        self.selected.set(-1)

        q_text = self.data["questions"][self.current_q]
        total = len(self.data["questions"])
        self.q_label.config(text=f"{self.current_q + 1}. {q_text}")
        self.progress_lbl.config(text=f"Question {self.current_q + 1} of {total}")
        self.progress_bar["value"] = self.current_q

        for label, value in self.data["options"]:
            tk.Radiobutton(
                self.options_frame, text=label, variable=self.selected, value=value,
                font=("Segoe UI", 11), bg=COLOR_CARD, fg=COLOR_TEXT,
                anchor="w", justify="left", selectcolor=COLOR_CARD
            ).pack(fill="x", pady=4)

        if self.current_q == total - 1:
            self.next_btn.config(text="Finish ✔")

    def next_question(self):
        if self.selected.get() == -1:
            self.q_label.config(fg="#e63946")
            self.after(900, lambda: self.q_label.config(fg=COLOR_TEXT))
            return

        self.answers.append(self.selected.get())
        self.current_q += 1

        if self.current_q < len(self.data["questions"]):
            self.render_question()
        else:
            self.progress_bar["value"] = len(self.data["questions"])
            score = sum(self.answers)
            self.destroy()
            self.on_finish(self.key, score, self.answers)
