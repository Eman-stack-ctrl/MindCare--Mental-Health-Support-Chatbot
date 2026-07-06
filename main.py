"""
main.py
=======
Entry point for MindCare. Run this file to launch the app:
    python main.py

DISCLAIMER: Educational / initial-screening tool only. Not a diagnostic
tool. Always directs the user toward a licensed professional.
"""

from gui_app import MindCareApp

if __name__ == "__main__":
    app = MindCareApp()
    app.mainloop()
