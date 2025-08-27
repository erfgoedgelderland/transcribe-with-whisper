# paths.py
from pathlib import Path
from datetime import datetime
from typing import Optional
from config import OUTPUT_STRATEGY, OUTPUT_DIR

TEXT_LIKE_EXTS = {"txt", "srt", "vtt", "md"}

def build_output_path(
    input_audio: str,
    model_name: str,
    output_mode: Optional[str] = None,
    partial: bool = False,
    ext: str = "txt",
    with_timestamp: bool = True,
) -> Path:
    stem = Path(input_audio).stem
    suffix = "partial" if partial else "transcript"
    ext_norm = ext.lstrip(".").lower()
    parts = [f"{stem}_{suffix}", f"[{model_name}]"]
    if output_mode and ext_norm in TEXT_LIKE_EXTS:
        parts.append(f"[{output_mode}]")
    if with_timestamp:
        parts.append(f"[{datetime.now().strftime('%Y%m%d-%H%M')}]")
    fname = "".join(parts) + f".{ext_norm}"
    return (OUTPUT_DIR / fname) if OUTPUT_STRATEGY == "outputs_dir" else Path(input_audio).with_name(fname)
