import os
import shutil
from datetime import datetime
from huggingface_hub import list_repo_files, hf_hub_download
from faster_whisper import WhisperModel
import config
config.ensure_ffmpeg_on_path()

DEFAULT_COMPUTE_TYPE = config.DEFAULT_COMPUTE_TYPE

def _log_safe(log, msg):
    try:
        if log:
            log(msg)
    except Exception:
        pass

def download_model(
    model_name,
    output_dir,
    log=None,
    progress_download=None
):
    
    # Alleen voor logdoeleinden
    model_sizes = {
        "tiny": "ca. 75 MB",
        "base": "ca. 145 MB",
        "small": "ca. 485 MB",
        "medium": "ca. 1.5 GB",
        "large-v3": "ca. 3.0 GB",
    }
    size_str = model_sizes.get(model_name, "onbekend")
    _log_safe(log, f"'{model_name}' wordt gedownload... ({size_str})")

    # Opruimen als er 0‑byte rommel ligt (mislukte eerdere poging)
    if os.path.exists(output_dir):
        zeroes = []
        for root, _dirs, files in os.walk(output_dir):
            for f in files:
                p = os.path.join(root, f)
                try:
                    if os.path.getsize(p) == 0:
                        zeroes.append(p)
                except Exception:
                    pass
        if zeroes:
            _log_safe(log, f"Lege bestanden gevonden, opnieuw proberen ({len(zeroes)} items)...")
            shutil.rmtree(output_dir, ignore_errors=True)

    os.makedirs(output_dir, exist_ok=True)

    repo_id = f"Systran/faster-whisper-{model_name}"

    try:
        files = list_repo_files(repo_id)
        total = max(1, len(files))

        # Vooruitgang 0–100% reserveren voor download
        for i, filename in enumerate(files, start=1):
            # Haal bestand op naar de HF-cache
            cached_path = hf_hub_download(repo_id=repo_id, filename=filename)

            # Kopieer naar jouw models/<model>/
            dest_path = os.path.join(output_dir, os.path.basename(filename))
            shutil.copy2(cached_path, dest_path)

            # Update GUI‑progress
            pct = int((i / total) * 100)
            _progress_safe(progress_download, pct)

        # Opruimen overbodige bestanden indien aanwezig
        for fname in ("README.md", ".gitattributes"):
            try:
                fp = os.path.join(output_dir, fname)
                if os.path.exists(fp):
                    os.remove(fp)
            except Exception:
                pass

        cache_dir = os.path.join(output_dir, ".cache")
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
    except Exception as e:
        _log_safe(log, f"Fout tijdens downloaden: {e}")

def _ensure_model_present(model_name, log, progress_download):
    model_dir = os.path.join(str(config.MODEL_DIR), model_name)
    model_file = os.path.join(model_dir, "model.bin")
    if not os.path.exists(model_file):
        _log_safe(log, f"\nTaalmodel '{model_name}' nog niet gevonden")
        os.makedirs(model_dir, exist_ok=True)
        download_model(model_name, model_dir, log, progress_download=progress_download)
    return model_dir

def _progress_safe(progress_func, pct):
    if progress_func is None:
        return
    try:
        pct = int(max(0, min(100, pct)))
        progress_func(pct)
    except Exception:
        pass

def _reveal_output_path(base_path, model_name, is_partial=False):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    suffix = "partial" if is_partial else "transcript"
    return f"{base_path}_{suffix}_{model_name}_{timestamp}.txt"

def transcribe(audio_file, model_name, log,
               progress_transcript=None,
               timer_start=lambda phase: None,
               timer_stop=lambda phase: None,
               cancel_event=None,
               progress_download=None,
               on_download_start=lambda: None,
               on_download_done=lambda: None,
               on_transcribe_start=lambda: None):
     
    try:
        on_download_start()
        timer_start("download")
        model_dir = _ensure_model_present(model_name, log, progress_download)

        on_download_done()
        timer_stop("download")
        on_transcribe_start()

        _log_safe(log, f"\nTaalmodel '{model_name}' wordt geladen...")
        model = WhisperModel(model_dir, compute_type=DEFAULT_COMPUTE_TYPE)     

        if progress_transcript:
            try:
                progress_transcript(0)
            except Exception:
                pass

        timer_start("transcribe")   

        _log_safe(log, "\nTranscriptie gestart...")
        segments, info = model.transcribe(
            audio_file,
            beam_size=5,
            vad_filter=True,
        )

        transcript = []
        total = float(info.duration) if getattr(info, "duration", None) else 0.0
        done = 0.0

        for segment in segments:
            if cancel_event is not None and cancel_event.is_set():
                _log_safe(log, "Transcriptie geannuleerd")
                break

            transcript.append(segment.text)
            seg_len = float(segment.end - segment.start)
            done += seg_len
            if total <= 0.0:
                total = max(total, float(segment.end))

            if total > 0.0 and progress_transcript:
                pct_audio = int(max(0, min(100, (done / total) * 100)))
                pct_scaled = 0 + int(pct_audio * 0.65)  # 0
                _progress_safe(progress_transcript, pct_scaled)

        is_partial = cancel_event.is_set() if cancel_event is not None else False

        if progress_transcript and not is_partial:
            _progress_safe(progress_transcript, 100)

        tekst = " ".join(transcript).strip()

        # Alleen opslaan als er inhoud is
        output_path = None
        if tekst:
            output_path = str(config.build_output_path(audio_file, model_name, partial=is_partial))
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(tekst)
            if is_partial:
                _log_safe(log, f"\nGedeeltelijk transcript opgeslagen als:\n{output_path}")
            else:
                _log_safe(log, f"\nTranscript opgeslagen als:\n{output_path}")
        else:
            if is_partial:
                _log_safe(log, "\nGeannuleerd voordat er tekst beschikbaar was. Er is geen bestand opgeslagen.")
            else:
                _log_safe(log, "\nEr is geen tekst getranscribeerd.")

        return output_path
    
    except Exception as e:
        _log_safe(log, f"\nFout tijdens transcriberen: {e}")
        if progress_transcript:
            try:
                progress_transcript(0)
            except Exception:
                pass
        raise

    finally:
        timer_stop("Transcriptie")

