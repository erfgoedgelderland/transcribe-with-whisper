import sys, io
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import ui_actions
import os

_bgcolor = '#d9d9d9'

def resource_path(relative_path):
    """Geeft het juiste pad in zowel PyInstaller build als tijdens dev-run."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Instellingen:
    def __init__(self, top=None):
        self.selected_model = None
        self.log = None
        self.audio_path = None
        self.output_path = None
        self.output_mode = tk.StringVar(value="text")

        top.geometry("700x480+452+250")
        top.minsize(560, 380)
        top.title("Transcribe with Whisper")
        top.configure(background=_bgcolor)

        self.top = top

        # Bestand selectie
        self.Label1 = tk.Label(self.top, text="Selecteer het bestand", background=_bgcolor, anchor='w')
        self.Label1.place(relx=0.044, rely=0.063, height=15, width=179)

        self.Button1 = tk.Button(self.top, text="Bladeren", command=ui_actions.kies_bestand)
        self.Button1.place(relx=0.065, rely=0.125, height=26, width=100)

        self.Lable_pad = tk.Label(self.top, background=_bgcolor, anchor='w')
        self.Lable_pad.place(relx=0.25, rely=0.125, relwidth=0.70, height=22)

        # Modellen
        self.Label2 = tk.Label(self.top, text="Kies taalmodel", background=_bgcolor, anchor='w')
        self.Label2.place(relx=0.044, rely=0.20, height=15, width=142)

        models = [
            ("Tiny", "tiny", "Snelste model, lage nauwkeurigheid"),
            ("Base", "base", "Redelijk snel, acceptabele nauwkeurigheid"),
            ("Small", "small", "Goede balans tussen snelheid en kwaliteit"),
            ("Medium", "medium", "Hoge nauwkeurigheid, trager"),
            ("Large-v3", "large-v3", "Beste kwaliteit, traag"),
        ]

        self.selectedButton = tk.StringVar(value="tiny")

        for i, (label, value, toelichting) in enumerate(models):
            y = 0.24 + i * 0.06
            rb = tk.Radiobutton(self.top, text=label, variable=self.selectedButton, value=value, background=_bgcolor, anchor='w')
            rb.place(relx=0.065, rely=y, relheight=0.048, relwidth=0.2)
            lb = tk.Label(self.top, text=toelichting, background=_bgcolor, anchor='w')
            lb.place(relx=0.305, rely=y, height=21, relwidth=0.65)

        # Output-keuze
        self.output_mode = tk.StringVar(value="text")

        lbl_output = tk.Label(self.top, text="Output", background=_bgcolor, anchor='w')
        lbl_output.place(relx=0.044, rely=y + 0.08, height=15, width=142)

        output_opts = [
            ("Doorlopende tekst", "text"),
            ("Segmenten met tijdscode", "segments"),
            ("Zinnen met tijdscode", "sentences"),
        ]

        for j, (opt_label, opt_value) in enumerate(output_opts):
            yy = y + 0.12 + j * 0.05
            rb = tk.Radiobutton(self.top, text=opt_label, variable=self.output_mode,
                                value=opt_value, background=_bgcolor, anchor='w')
            rb.place(relx=0.065, rely=yy, relheight=0.048, relwidth=0.6)

        # Log
        self.Text1 = tk.Text(self.top, wrap="word", background="white", foreground="black")
        self.Text1.place(relx=0.022, rely=0.03, relheight=0.71, relwidth=0.94)
        self.Text1.place_forget()  # Verberg bij opstart

        self.progress_x = 0.022
        self.progress_y = 0.76
        self.progress_width = 0.94
        self.progress_height = 20

        # Progressbalk – onder de log, boven de knoppen
        self.progress = ttk.Progressbar(self.top, orient="horizontal", length=400, mode="determinate")
        self.progress.place(relx=self.progress_x, rely=self.progress_y, relwidth=self.progress_width, height=self.progress_height)
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.progress.place_forget()  # Verberg bij opstart

        # Labels voor balken
        self.LabelProgressDL = tk.Label(self.top, text="Model downloaden", background=_bgcolor, anchor='w')
        self.LabelProgressTX = tk.Label(self.top, text="Transcriberen", background=_bgcolor, anchor='w')
        self.LabelProgressDL.place_forget()
        self.LabelProgressTX.place_forget()

        # Posities (download boven transcriptie)
        self.progress_y_download = 0.72  # download iets hoger
        self.progress_y = 0.81          # transcriptie onder download

        # Bestaande transcriptie-balk label tonen wanneer nodig
        self.LabelProgressTX.place(relx=0.022, rely=self.progress_y - 0.045, height=18, relwidth=0.94)
        self.LabelProgressTX.place_forget()

        # Tweede balk (download)
        self.progress_download = ttk.Progressbar(self.top, orient="horizontal", mode="determinate")
        self.progress_download.place(relx=self.progress_x, rely=self.progress_y_download,
                                     relwidth=self.progress_width, height=self.progress_height)
        self.progress_download["value"] = 0
        self.progress_download["maximum"] = 100
        self.progress_download.place_forget()

        # Knoppenrij (onderaan):
        self.ButtonStart = tk.Button(self.top, text="Start", command=ui_actions.button_start)
        self.ButtonCancel = tk.Button(self.top, text="Annuleren", command=ui_actions.button_cancel)
        self.ButtonOpen = tk.Button(self.top, text="Open map", command=ui_actions.button_open_folder)
        self.ButtonBack = tk.Button(self.top, text="Terug", command=ui_actions.button_back)
        self.ButtonClose = tk.Button(self.top, text="Afsluiten", command=self.top.quit)

        # Timer label bovenop de progressbar
        self.LabelTimer = tk.Label(self.top, text="", background=_bgcolor, anchor="center")
        self.LabelTimer.place(relx=0.022, rely=0.85, relwidth=0.94, height=20)
        self.LabelTimer.place_forget()

    def toon_text1(self):
        self.Text1.place(relx=0.022, rely=0.03, relheight=0.71, relwidth=0.94)
        self.Text1.update()

def start_up():
    ui_actions.main()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Transcribe with Whisper")
    root.iconbitmap(resource_path("assets/app.ico"))
    gui = Instellingen(root)
    ui_actions.init_gui(gui)
    root.mainloop()
