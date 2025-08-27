import os
import sys
import threading
import subprocess
import time
from config import ALLOWED_MODELS
from tkinter import filedialog, messagebox

__all__ = [
    "init_gui", "kies_bestand",
    "append_log", "toon_progress", "verberg_progress", "update_progress",
    "toon_progress_download", "verberg_progress_download", "update_progress_download",
    "button_start", "button_cancel", "button_open_folder", "button_back"
]

gui = None
_cancel_event = None
_timer_start = None
_timer_running = False

button_links_x = 0.065
button_links_y = 0.90
button_links_width = 100
button_links_height = 30
button_rechts_x = 0.80

def init_gui(gui_ref):
    global gui
    gui = gui_ref
    gui.Text1.configure(state="disabled")
    gui.Text1.place_forget()
    show_start_button()

def kies_bestand():
    pad = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.ogg")])
    if pad:
        gui.audio_path = pad
        gui.Lable_pad.configure(text=os.path.basename(pad))

# ---------- Thread-safe UI helpers ----------
def _ui_append_log(message):
    gui.Text1.configure(state="normal")
    gui.Text1.insert("end", message + "\n")
    gui.Text1.see("end")
    gui.Text1.update_idletasks()
    gui.Text1.configure(state="disabled")

def append_log(message):
    try:
        gui.top.after(0, _ui_append_log, message)
    except Exception:
        pass

# Progress helpers
def _ui_show_progress():
    _ui_update_progress(0)
    gui.progress.place(relx=gui.progress_x, rely=gui.progress_y,
                       relwidth=gui.progress_width, height=gui.progress_height)
    gui.progress.update_idletasks()
    gui.LabelProgressTX.place(relx=0.022, rely=gui.progress_y - 0.035, height=18, relwidth=0.94)

def toon_progress():
    try:
        gui.top.after(0, _ui_show_progress)
    except Exception:
        pass

def _ui_hide_progress():
    gui.progress.place_forget()
    gui.LabelProgressTX.place_forget()

def verberg_progress():
    try:
        gui.top.after(0, _ui_hide_progress)
    except Exception:
        pass

def _ui_update_progress(percentage):
    gui.progress["value"] = int(max(0, min(100, percentage)))
    gui.progress.update_idletasks()

def update_progress(percentage):
    try:
        gui.top.after(0, _ui_update_progress, percentage)
    except Exception:
        pass

def _ui_update_progress_download(percentage): 
    gui.progress_download["value"] = int(max(0, min(100, percentage))) 
    gui.progress_download.update_idletasks()

def update_progress_download(percentage): 
    try: 
        gui.top.after(0, _ui_update_progress_download, percentage) 
    except Exception: 
        pass

def toon_progress_download(): 
    try: 
        gui.top.after(0, _ui_show_progress_download) 
    except Exception: 
        pass

def _ui_hide_progress_download(): 
    gui.progress_download.place_forget() 
    gui.LabelProgressDL.place_forget() 

def verberg_progress_download(): 
    try: 
        gui.top.after(0, _ui_hide_progress_download) 
    except Exception: 
        pass

def _update_timer_label():
    if not _timer_running:
        return
    elapsed = int(time.time() - _timer_start)
    mins, secs = divmod(elapsed, 60)
    gui.LabelTimer.config(text=f"{mins:02d}:{secs:02d}")
    gui.top.after(1000, _update_timer_label)

# ---------- Tweede balk: download ----------
def _ui_show_progress_download():
    gui.progress_download["value"] = 0
    gui.progress_download.place(
        relx=gui.progress_x, rely=gui.progress_y_download,
        relwidth=gui.progress_width, height=gui.progress_height
    )
    gui.progress_download.update_idletasks()
    gui.LabelProgressDL.place(relx=0.022, rely=gui.progress_y_download - 0.035, height=18, relwidth=0.94)

# --------------------------------------------

# Button placement helpers
def _place_button(button, x_offset=25):
    button.place(x=x_offset + button_links_x, rely=button_links_y,
                 height=button_links_height, width=button_links_width)

def reset_buttons_positions():
    # Plaats alle knoppen
    try:
        gui.ButtonStart.place_forget()
        gui.ButtonCancel.place_forget()
        gui.ButtonBack.place_forget()
        gui.ButtonOpen.place_forget()
        gui.ButtonClose.place_forget()
    except Exception as e:
        pass

def show_buttons_for_transcription():
    # Toon knoppen relevant voor transcriptie
    reset_buttons_positions()
    _place_button(gui.ButtonCancel)

def show_buttons_after_transcription():
    reset_buttons_positions()
    _place_button(gui.ButtonBack)
    _place_button(gui.ButtonOpen, 135)
    _place_button(gui.ButtonClose, 300)

def show_start_button():
    reset_buttons_positions()
    _place_button(gui.ButtonStart)

# Action functions
def _run_transcription(bestand, model, output_mode): 
    import transcriber 
    bestandsnaam = os.path.basename(bestand) 
    
    try: 
        append_log(f"Bestand: {bestandsnaam}") 
        append_log(f"Model: {model}") 
        append_log(f"Output mode: {output_mode}") 
        output = transcriber.transcribe( 
            audio_file=bestand, 
            model_name=model, 
            output_mode=output_mode, 
            log=append_log, 
            progress_transcript=update_progress, 
            progress_download=update_progress_download, 
            on_download_start=toon_progress_download, 
            on_download_done=verberg_progress_download, 
            on_transcribe_start=toon_progress, 
            cancel_event=_cancel_event, 
            timer_start=start_timer, 
            timer_stop=stop_timer 
            ) 
        
        gui.output_path = bestand 

        if _cancel_event.is_set(): 
            append_log("Geannuleerd door gebruiker.") 
    except Exception as e: 
        append_log(f"Fout: {e}") 

    try: 
        gui.top.after(0, messagebox.showerror, "Fout", str(e)) 
    except Exception: 
        pass 
    finally: 
        try: 
            show_buttons_after_transcription()
        except Exception: 
            pass

def button_start():
    global _cancel_event
    bestand = getattr(gui, "audio_path", None)
    model = gui.selectedButton.get()
    output_mode = gui.output_mode.get()

    if not bestand:
        messagebox.showwarning("Geen bestand", "Selecteer eerst een audiobestand.")
        return
    if not model:
        messagebox.showwarning("Geen model", "Selecteer eerst een taalmodel.")
        return
    if model not in ALLOWED_MODELS:
        messagebox.showwarning("Model niet toegestaan", f"Kies een van: {', '.join(ALLOWED_MODELS)}")
        return

    _cancel_event = threading.Event()
    gui.output_path = None

    gui.toon_text1()

    show_buttons_for_transcription()

    t = threading.Thread(target=_run_transcription, args=(bestand, model, output_mode), daemon=True)
    t.start()

def button_cancel():
    if _cancel_event is not None:
        _cancel_event.set()
        append_log("Annuleren wordt aangevraagd...")

def button_back():
    # Herstel knoppen bij teruggaan
    gui.Text1.configure(state="normal")
    gui.Text1.delete("1.0", "end")
    gui.Text1.configure(state="disabled")
    gui.Text1.place_forget()
    show_start_button()

def _reveal_in_explorer(path):
    folder = os.path.dirname(path) if os.path.isfile(path) else path
    try:
        if sys.platform.startswith("win"):
            if path and os.path.isfile(path):
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            else:
                os.startfile(os.path.normpath(folder))
        elif sys.platform == "darwin":
            if path and os.path.isfile(path):
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    except Exception as e:
        messagebox.showerror("Open map", f"Kan de map niet openen: {e}")

def button_open_folder():
    target = getattr(gui, "output_path", None)
    if not target:
        target = getattr(gui, "audio_path", None)
        if not target:
            messagebox.showinfo("Open map", "Geen bestand beschikbaar om te tonen.")
            return
    _reveal_in_explorer(target)

# Timer functions
def start_timer(phase=None):
    global _timer_start, _timer_running
    _timer_start = time.time()
    _timer_running = True
    gui.LabelTimer.place(relx=0.022, rely=0.85, relwidth=0.94, height=20)
    _update_timer_label()

def stop_timer(phase=None):
    global _timer_running
    _timer_running = False
    gui.LabelTimer.place_forget()

    # Bereken de totale duur
    if _timer_start:
        elapsed = int(time.time() - _timer_start)
        if elapsed > 0:
            mins, secs = divmod(elapsed, 60)
            hours, mins = divmod(mins, 60)
            tijd_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            append_log(f"\n{phase.capitalize() if phase else 'Taak'} voltooid in {tijd_str}")
    