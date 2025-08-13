import os
import sys
from pathlib import Path

def load_env():
    """
    Eenvoudige .env loader:
    - Leest KEY=VALUE regels uit een .env bestand.
    - Zoekt alleen in dezelfde map als de .exe of script.
    - Overschrijft GEEN variabelen die al in de environment staan.
    - Als er geen .env wordt gevonden → alleen defaults in config.py gebruiken.
    """

    # Map van de exe (PyInstaller) of van dit script
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).resolve().parent

    env_path = base_dir / ".env"

    if env_path.exists():
        try:
            with env_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception:
            # Niet crashen als er iets mis is met het lezen
            pass
