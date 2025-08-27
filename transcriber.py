import os
import shutil
from datetime import datetime
from tkinter import messagebox
from huggingface_hub import list_repo_files, hf_hub_download
from faster_whisper import WhisperModel
from paths import build_output_path
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

def _format_hhmmss(t: float) -> str:
    # Rond naar beneden op hele seconden (pas aan naar round() als je dat liever hebt)
    total = int(t)
    hh = total // 3600
    mm = (total % 3600) // 60
    ss = total % 60
    return f"{hh:02d}:{mm:02d}:{ss:02d}"

import json

def transcribe_audio(audio_file, model_name, output_mode, log,
                     progress_transcript=None,
                     timer_start=lambda phase: None,
                     timer_stop=lambda phase: None,
                     cancel_event=None,
                     progress_download=None,
                     on_download_start=lambda: None,
                     on_download_done=lambda: None,
                     on_transcribe_start=lambda: None):

    # Start download en transcribeerlogica
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
    segments_iter, info = model.transcribe(
        audio_file,
        beam_size=5,
        vad_filter=True,
    )

    segments = []
    total = float(info.duration) if getattr(info, "duration", None) else 0.0
    done = 0.0

    for seg in segments_iter:
        if cancel_event is not None and cancel_event.is_set():
            _log_safe(log, "Transcriptie geannuleerd")
            break

        segments.append({
            "start": float(seg.start),
            "end": float(seg.end),
            "text": seg.text.strip()
        })

        seg_len = float(seg.end - seg.start)
        done += seg_len
        if total <= 0.0:
            total = max(total, float(seg.end))

        if total > 0.0 and progress_transcript:
            pct_audio = int(max(0, min(100, (done / total) * 100)))
            pct_scaled = int(pct_audio * 0.65)
            _progress_safe(progress_transcript, pct_scaled)

    # JSON-cache zonder output_mode en zonder timestamp
    json_cache_path = build_output_path(
        audio_file,
        model_name,
        output_mode=None,         # expliciet geen mode
        ext="json",
        with_timestamp=False,
    )

    with open(json_cache_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    return segments, json_cache_path


def transcribe(audio_file, model_name, output_mode, log,
               progress_transcript=None,
               timer_start=lambda phase: None,
               timer_stop=lambda phase: None,
               cancel_event=None,
               progress_download=None,
               on_download_start=lambda: None,
               on_download_done=lambda: None,
               on_transcribe_start=lambda: None):
     
    try:
        # Pad voor JSON-cache
        json_cache_path = build_output_path(
            audio_file, model_name, output_mode=None, ext="json", with_timestamp=False
        )

        json_cache_file = os.path.basename(json_cache_path)

        # -------------------------------
        # 1. Segmenten ophalen of laden
        # -------------------------------
        if os.path.exists(json_cache_path):
            _log_safe(log, f"\nBestaande transcriptie gevonden:\n{json_cache_file}")

            antwoord = messagebox.askyesno(
                "Bestaande transcriptie gevonden",
                "Er is al een transcript voor dit bestand. Wil je opnieuw transcriberen (dit zal de transcriptie overschrijven) of het bestaande transcript gebruiken om de gekozen output te genereren?\n\nJa = Transcribeer opnieuw\nNee = Gebruik bestaand"
            )
            if antwoord:  # Ja = Transcribeer opnieuw
                _log_safe(log, "Nieuw transcript wordt aangemaakt.")
                segments, json_cache_path = transcribe_audio(
                    audio_file, model_name, output_mode, log,
                    progress_transcript, timer_start, timer_stop,
                    cancel_event, progress_download,
                    on_download_start, on_download_done, on_transcribe_start
                )
            else:  # Nee = Gebruik bestaand transcript
                _log_safe(log, "Bestaand transcript wordt gebruikt.")
                with open(json_cache_path, "r", encoding="utf-8") as f:
                    segments = json.load(f)
        else:
            # Het transcriptie-bestand bestaat niet, dus doe het transcriptieproces
            segments, json_cache_path = transcribe_audio(
                audio_file, model_name, output_mode, log,
                progress_transcript, timer_start, timer_stop,
                cancel_event, progress_download,
                on_download_start, on_download_done, on_transcribe_start
            )

        # -------------------------------
        # 2. Formatteren volgens output_mode
        # -------------------------------
        if output_mode == "text":
            tekst = " ".join(seg["text"] for seg in segments).strip()

        elif output_mode == "segments":
            # Start–eind als [hh:mm:ss - hh:mm:ss]
            tekst = "\n".join(
                f"[{_format_hhmmss(seg['start'])} - {_format_hhmmss(seg['end'])}] {seg['text']}"
                for seg in segments
            )

        elif output_mode == "sentences":
            import re
            tekst_lines = []
            for seg in segments:
                sentences = re.split(r'([.!?])', seg["text"])
                sentence_list = ["".join(pair).strip() for pair in zip(sentences[0::2], sentences[1::2])]
                for sent in sentence_list:
                    if sent:
                        # Voor zinnen: alleen de starttijd als [hh:mm:ss]
                        tekst_lines.append(f"[{_format_hhmmss(seg['start'])}] {sent}")
            tekst = "\n".join(tekst_lines)

        else:
            tekst = " ".join(seg["text"] for seg in segments).strip()

        # -------------------------------
        # 3. Opslaan als txt
        # -------------------------------
        is_partial = cancel_event.is_set() if cancel_event is not None else False

        if progress_transcript and not is_partial:
            _progress_safe(progress_transcript, 100)

        output_path = None
        if tekst:
            
            # Tekst-output mét output_mode en mét timestamp
            output_path = str(build_output_path(
                audio_file,
                model_name,
                output_mode=output_mode,  # bv. "segments" of "sentences"
                partial=is_partial,
                ext="txt",
                with_timestamp=True,
            ))

            output_file = os.path.basename(output_path)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(tekst)
            if is_partial:
                _log_safe(log, f"\nGedeeltelijk transcript opgeslagen als:\n{output_file}")
            else:
                _log_safe(log, f"\nTranscript opgeslagen als:\n{output_file}")
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


