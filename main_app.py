import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import ui
import config

_bgcolor = '#d9d9d9'

class Instellingen:
    def __init__(self, top=None):
        self.selected_model = None
        self.log = None
        self.audio_path = None
        self.output_path = None

        top.geometry("700x480+452+250")
        top.minsize(560, 380)
        top.title("Transcribe with Whisper")
        top.configure(background=_bgcolor)

        self.top = top

        # Bestand selectie
        self.Label1 = tk.Label(self.top, text="Selecteer het bestand", background=_bgcolor, anchor='w')
        self.Label1.place(relx=0.044, rely=0.063, height=15, width=179)

        self.Button1 = tk.Button(self.top, text="Bladeren", command=ui.kies_bestand)
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

        # Log
        self.Text1 = tk.Text(self.top, wrap="word", background="white", foreground="black")
        self.Text1.place(relx=0.022, rely=0.03, relheight=0.70, relwidth=0.94)
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

        # Knoppenrij (onderaan):
        # Start (initieel), tijdens run: Annuleer op dezelfde plek,
        # na afloop: Open map op die plek en daarnaast Afsluiten.

        self.button_links_x = 0.065
        self.button_links_y = 0.90
        self.button_links_width = 100
        self.button_links_height = 30
        self.button_rechts_x = 0.80

        self.ButtonStart = tk.Button(self.top, text="Start", command=ui.button_start)
        self.ButtonStart.place(relx=self.button_links_x, rely=self.button_links_y, height=self.button_links_height, width=self.button_links_width)

        self.ButtonCancel = tk.Button(self.top, text="Annuleer", command=ui.button_cancel)
        self.ButtonCancel.place(relx=self.button_links_x, rely=self.button_links_y, height=self.button_links_height, width=self.button_links_width)
        self.ButtonCancel.place_forget()  # tonen tijdens run

        self.ButtonOpen = tk.Button(self.top, text="Open map", command=ui.button_open_folder)
        self.ButtonOpen.place(relx=self.button_links_x, rely=self.button_links_y, height=self.button_links_height, width=self.button_links_width)
        self.ButtonOpen.place_forget()  # tonen na run

        self.ButtonClose = tk.Button(self.top, text="Afsluiten", command=self.top.destroy)
        self.ButtonClose.place(relx=self.button_rechts_x, rely=self.button_links_y, height=self.button_links_height, width=self.button_links_width)
        self.ButtonClose.place_forget()  # tonen na run

        # Timer label bovenop de progressbar
        self.LabelTimer = tk.Label(self.top, text="", background=_bgcolor, anchor="center")
        self.LabelTimer.place(relx=0.022, rely=0.81, relwidth=0.94, height=20)
        self.LabelTimer.place_forget()

    def toon_text1(self):
        self.Text1.place(relx=0.022, rely=0.03, relheight=0.70, relwidth=0.94)
        self.Text1.update()

def start_up():
    ui.main()

if __name__ == '__main__':
    root = tk.Tk()
    gui = Instellingen(root)
    ui.init_gui(gui)
    root.mainloop()