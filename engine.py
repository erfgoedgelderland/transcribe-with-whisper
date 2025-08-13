import os
import shutil
from datetime import datetime
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
    timer_start=lambda phase: None,   # <-- callbacks van buiten
    timer_stop=lambda phase: None,
):
    # Schatting van de downloadgrootte per model (alleen voor log)
    model_sizes = {
        "tiny": "ca. 75 MB",
        "base": "ca. 145 MB",
        "small": "ca. 485 MB",
        "medium": "ca. 1.5 GB",
        "large-v3": "ca. 3.0 GB",
    }
    size_str = model_sizes.get(model_name, "onbekend")
    _log_safe(log, f"'{model_name}' wordt gedownload... ({size_str})")

    timer_start("download")
    try:
        snapshot_download(
            repo_id=f"Systran/faster-whisper-{model_name}",
            local_dir=output_dir,
            local_dir_use_symlinks=False,   # handig op Windows
            ignore_patterns=["*.md", ".gitattributes", ".cache/**"]
        )
    finally:
        timer_stop("download")

    # Opruimen
    for fname in ("README.md", ".gitattributes"):
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

    cache_dir = os.path.join(output_dir, ".cache")
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
        except Exception as e:
            _log_safe(log, f"Kon cache niet verwijderen: {e}")

def _ensure_model_present(model_name, log):
    model_dir = os.path.join(str(config.MODEL_DIR), model_name)
    model_file = os.path.join(model_dir, "model.bin")
    if not os.path.exists(model_file):
        _log_safe(log, f"\nTaalmodel '{model_name}' nog niet gevonden")
        os.makedirs(model_dir, exist_ok=True)
        download_model(model_name, model_dir, log)
        _log_safe(log, "Download voltooid")
    return model_dir

def _reveal_output_path(base_path, model_name, is_partial=False):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    suffix = "partial" if is_partial else "transcript"
    return f"{base_path}_{suffix}_{model_name}_{timestamp}.txt"

def transcribe(audio_file, model_name, log, update_progress=None, cancel_event=None, timer_start=lambda phase: None, timer_stop=lambda phase: None):

    try:
        model_dir = _ensure_model_present(model_name, log)
        _log_safe(log, f"\nTaalmodel '{model_name}' wordt geladen...")
        model = WhisperModel(model_dir, compute_type=DEFAULT_COMPUTE_TYPE)

        if update_progress:
            try:
                update_progress(0)
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

            if total > 0.0 and update_progress:
                pct = int(max(0, min(100, (done / total) * 100)))
                try:
                    update_progress(pct)
                except Exception:
                    pass

        is_partial = cancel_event.is_set() if cancel_event is not None else False

        if update_progress and not is_partial:
            try:
                update_progress(100)
            except Exception:
                pass

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
        if update_progress:
            try:
                update_progress(0)
            except Exception:
                pass
        raise

    finally:
        timer_stop("Transcriptie")
