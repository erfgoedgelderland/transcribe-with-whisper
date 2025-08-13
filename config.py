from __future__ import annotations
import os
import sys
from pathlib import Path
from datetime import datetime

from env_loader import load_env
load_env()

# ============ App metadata ============
APP_NAME = "Transcribe with Whisper"
APP_VERSION = "1.1.0"

# ============ Basislocatie ============
# Map van de exe of script
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent

# ============ Models ============
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ============ Compute type ============
DEFAULT_COMPUTE_TYPE = os.getenv("FASTER_WHISPER_COMPUTE", "int8_float32")

# ============ Output instellingen ============
# Strategie: next_to_audio (standaard) of outputs_dir
OUTPUT_STRATEGY = os.getenv("TRANSCRIBER_OUTPUT_STRATEGY", "next_to_audio").strip()

# Output map alleen relevant als OUTPUT_STRATEGY == outputs_dir
OUTPUT_DIR = Path(os.getenv("TRANSCRIBER_OUTPUT_DIR", BASE_DIR / "outputs"))
if OUTPUT_STRATEGY == "outputs_dir":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ====== Output pad bouwen ======
def build_output_path(input_audio: str, model_name: str, partial: bool = False) -> Path:
    stem = Path(input_audio).stem
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    suffix = "partial" if partial else "transcript"
    fname = f"{stem}_{suffix}_{model_name}_{timestamp}.txt"

    if OUTPUT_STRATEGY == "outputs_dir":
        return OUTPUT_DIR / fname
    else:
        return Path(input_audio).with_name(fname)

# ============ FFmpeg zoeken ============
def resolve_ffmpeg_path() -> Path | None:
    exe_suffix = ".exe" if sys.platform.startswith("win") else ""
    fname = f"ffmpeg{exe_suffix}"

    # 1) PyInstaller onefile unpack dir
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidate = Path(meipass) / "bin" / fname
        if candidate.exists():
            return candidate

    # 2) Next to executable/script
    base = BASE_DIR
    candidate = base / "bin" / fname
    if candidate.exists():
        return candidate

    return None

def ensure_ffmpeg_on_path() -> None:
    ffmpeg = resolve_ffmpeg_path()
    if ffmpeg:
        bin_dir = str(ffmpeg.parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
