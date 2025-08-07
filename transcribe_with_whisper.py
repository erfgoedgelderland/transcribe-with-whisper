import os
import sys
import time
import warnings
from tkinter import Tk, filedialog, messagebox

MODEL_SIZE = "base"  # Kies uit: tiny, base, small, medium, large

# ==============================================
# Intro
# ==============================================
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
print("Versie: 2025v1.1", flush=True)
print(flush=True)
input("> Druk op Enter om verder te gaan...")
print("Stap 1/3: Opstarten... even geduld.", flush=True)


# ==============================================
# Setup paden voor modellen en ffmpeg
# ==============================================

# Detecteer of we in een gebundelde .exe draaien (PyInstaller)
if getattr(sys, 'frozen', False):
    app_dir = os.path.dirname(sys.executable)
else:
    app_dir = os.path.dirname(__file__)

model_dir = os.path.join(app_dir, "models")
ffmpeg_dir = os.path.join(app_dir, "bin")
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]


# ==============================================
# Transcriptie-functie
# ==============================================

def transcribe_audio(audio_path):
    import whisper

    model_path = os.path.join(model_dir, MODEL_SIZE + ".pt")
    print("Stap 2/3: Taalmodel wordt geladen...", flush=True)

    if not os.path.exists(model_path):
        print("          Bij het eerste gebruik wordt het Whisper-taalmodel gedownload.", flush=True)
        print("          Hier is eenmalig een internetverbinding voor nodig.", flush=True)
    
    model = whisper.load_model(MODEL_SIZE, download_root=model_dir)

    print("Stap 3/3: Transcript wordt gemaakt. Dit kan even duren...", flush=True)
    print("          Sluit dit venster niet voordat het transcript klaar is.", flush=True)
    start = time.time()
    result = model.transcribe(audio_path)
    end = time.time()

    return result["text"], round(end - start, 2)


# ==============================================
# Hoofdprogramma
# ==============================================

def main():
    # Onderdruk FP16-waarschuwingen
    warnings.filterwarnings("ignore", message="FP16 is not supported.*")

    # Open bestandsdialoog
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
