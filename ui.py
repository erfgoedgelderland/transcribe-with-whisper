import os
import sys
import threading
import subprocess
import time
from tkinter import filedialog, messagebox

__all__ = [
    "init_gui", "kies_bestand",
    "append_log", "toon_progress", "verberg_progress", "update_progress",
    "button_start", "button_cancel", "button_open_folder"
]


TOEGESTAAN_MODELLEN = ["tiny", "base", "small", "medium", "large-v3"]

gui = None
_cancel_event = None
_timer_start = None
_timer_running = False

def init_gui(gui_ref):
    global gui
    gui = gui_ref
    gui.Text1.configure(state="disabled")
    gui.Text1.place_forget()

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

def _ui_show_progress():
    gui.progress["value"] = 0
    gui.progress.place(relx=gui.progress_x, rely=gui.progress_y,
                       relwidth=gui.progress_width, height=gui.progress_height)
    gui.progress.update_idletasks()

def toon_progress():
    try:
        gui.top.after(0, _ui_show_progress)
    except Exception:
        pass

def _ui_hide_progress():
    gui.progress.place_forget()

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
# --------------------------------------------

def _place_button_start():
    gui.ButtonStart.place(relx=gui.button_links_x, rely=gui.button_links_y,
                          height=gui.button_links_height, width=gui.button_links_width)

def _place_button_cancel():
    gui.ButtonCancel.place(relx=gui.button_links_x, rely=gui.button_links_y,
                           height=gui.button_links_height, width=gui.button_links_width)

def _place_button_open():
    gui.ButtonOpen.place(relx=gui.button_links_x, rely=gui.button_links_y,
                         height=gui.button_links_height, width=gui.button_links_width)

def _place_button_close():
    gui.ButtonClose.place(relx=gui.button_rechts_x, rely=gui.button_links_y,
                          height=gui.button_links_height, width=gui.button_links_width)

def _show_postrun_buttons():
    gui.ButtonOpen.lift(); _place_button_open()
    gui.ButtonClose.lift(); _place_button_close()

def _hide_postrun_buttons():
    gui.ButtonOpen.place_forget()
    gui.ButtonClose.place_forget()

def _show_cancel_button():
    gui.ButtonCancel.lift(); _place_button_cancel()

def _hide_cancel_button():
    gui.ButtonCancel.place_forget()

def _hide_start_button():
    gui.ButtonStart.place_forget()

def _show_start_button():
    gui.ButtonStart.lift(); _place_button_start()

def _run_transcription(bestand, model):
    import engine
    try:
        append_log(f"Bestand: {bestand}")
        append_log(f"Model: {model}")
        output = engine.transcribe(
            audio_file=bestand,
            model_name=model,
            log=append_log,
            update_progress=update_progress,
            cancel_event=_cancel_event,
            timer_start=start_timer,
            timer_stop=stop_timer
        )
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
            gui.top.after(0, _hide_cancel_button)
            gui.top.after(0, _show_postrun_buttons)
        except Exception:
            pass

def button_start():
    global _cancel_event
    bestand = getattr(gui, "audio_path", None)
    model = gui.selectedButton.get()

    if not bestand:
        messagebox.showwarning("Geen bestand", "Selecteer eerst een audiobestand.")
        return
    if not model:
        messagebox.showwarning("Geen model", "Selecteer eerst een taalmodel.")
        return
    if model not in TOEGESTAAN_MODELLEN:
        messagebox.showwarning("Model niet toegestaan", f"Kies een van: {', '.join(TOEGESTAAN_MODELLEN)}")
        return

    _cancel_event = threading.Event()
    gui.output_path = None

    gui.toon_text1()
    toon_progress()
    try:
        _hide_start_button()
        _hide_postrun_buttons()
        _show_cancel_button()
    except Exception:
        pass

    t = threading.Thread(target=_run_transcription, args=(bestand, model), daemon=True)
    t.start()

def button_cancel():
    if _cancel_event is not None:
        _cancel_event.set()
        append_log("Annuleren wordt aangevraagd...")

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

# ----- TIMER ---------------------

def start_timer(phase=None):
    global _timer_start, _timer_running
    _timer_start = time.time()
    _timer_running = True
    gui.LabelTimer.place(relx=0.022, rely=0.81, relwidth=0.94, height=20)
    _update_timer_label()

def stop_timer(phase=None):
    global _timer_running
    _timer_running = False
    gui.LabelTimer.place_forget()

    # bereken totale duur
    if _timer_start:
        elapsed = int(time.time() - _timer_start)
        mins, secs = divmod(elapsed, 60)
        tijd_str = f"{mins} min {secs} sec"
        append_log(f"{phase.capitalize() if phase else 'Taak'} voltooid in {tijd_str}")

def _update_timer_label():
    if not _timer_running:
        return
    elapsed = int(time.time() - _timer_start)
    mins, secs = divmod(elapsed, 60)
    gui.LabelTimer.config(text=f"{mins:02d}:{secs:02d}")
    gui.top.after(1000, _update_timer_label)