print("==============================================", flush=True)
print(" TRANSCRIBE WITH WHISPER – Erfgoed Gelderland", flush=True)
print("==============================================", flush=True)
print("Gratis en open source programma gebaseerd op het", flush=True)
print("Whisper-taalmodel van OpenAI.", flush=True)
print(flush=True)
print("VEILIG: dit programma draait volledig lokaal.", flush=True)
print("Er worden GEEN gegevens online verstuurd of opgeslagen.", flush=True)
print(flush=True)
print("LET OP: transcriberen kan even duren.", flush=True)
print("Reken op ongeveer 1 minuut verwerkingstijd per minuut audio.", flush=True)
print(flush=True)
print("Versie: 2025v1", flush=True)
print(flush=True)
print(flush=True)
input("> Druk op Enter om verder te gaan...")
print(flush=True)
print("Stap 1/3: Opstarten... even geduld.", flush=True)

import os
import warnings
import sys
import time
from tkinter import Tk, filedialog, messagebox

# Detecteer of we in een gebundelde .exe draaien (PyInstaller)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS  # Tijdelijke map van PyInstaller
    assets_path = os.path.join(base_path, 'whisper', 'assets')
else:
    assets_path = os.path.join(os.path.dirname(__file__), 'env', 'Lib', 'site-packages', 'whisper', 'assets')

# Forceer dat Whisper zijn assets uit de goede map laadt
os.environ["WHISPER_ASSETS"] = assets_path

def transcribe_audio(audio_path):
    import whisper
    print("Stap 2/3: Taalmodel wordt geladen.")
    # ffmpeg toevoegen aan PATH
    ffmpeg_path = os.path.join(os.path.dirname(__file__), "bin")
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

    model_dir = os.path.join(os.path.dirname(__file__), "models")
    model = whisper.load_model("base", download_root=model_dir)
    
    print("Stap 3/3: Transcript wordt gemaakt. Dit kan even duren...")
    print("          Sluit dit venster niet voordat het transcript klaar is.")
    start = time.time()
    result = model.transcribe(audio_path)
    end = time.time()
    duur = end - start
    return result["text"], round(end - start, 2)

def main():
    # Onderdruk FP16 waarschuwingen van Whisper
    warnings.filterwarnings("ignore", message="FP16 is not supported.*")

    root = Tk()
    root.withdraw()
    messagebox.showinfo("Whisper Transcriber", "Selecteer een audiobestand om te transcriberen.")
    audio_file = filedialog.askopenfilename(filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.ogg")])

    if not audio_file:
        messagebox.showwarning("Geen bestand geselecteerd", "Je hebt geen bestand geselecteerd.")
        return

    try:
        transcript, duur = transcribe_audio(audio_file)
        output_file = os.path.splitext(audio_file)[0] + "_transcript.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print()
        print(f"Transcript opgeslagen als: {output_file}")
        print(f"Duur: {duur} seconden")
        print()
    except Exception as e:
        print()
        print("FOUT OPGETREDEN:")
        print(str(e))
    finally:
        input("\nDruk op Enter om dit venster te sluiten...")

if __name__ == "__main__":
    main()
