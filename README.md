# Transcribe with Whisper

**Transcribe with Whisper** is een Nederlandstalig, open source transcriptieprogramma gebaseerd op [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper), een snelle en efficiënte implementatie van [OpenAI Whisper](https://github.com/openai/whisper).  

Het programma werkt volledig lokaal: er wordt **geen audio of tekst naar internet verstuurd**.

## Functies

- Zet audiobestanden om naar tekst met hoge nauwkeurigheid
- Snellere verwerking dankzij Faster-Whisper
- Ondersteunt o.a. `.wav`, `.mp3`, `.m4a`, `.ogg`
- Volledige offline transcripties en privacyvriendelijk
- Geschikt voor interviews, erfgoedprojecten, podcasts en meer
- Modellen worden lokaal opgeslagen in de map `models/`

## Gebruik

### Windows (.exe-versie)

1. Download de nieuwste release via [GitHub Releases](https://github.com/erfgoedgelderland/transcribe-with-whisper/releases)  
2. Pak het `.zip`-bestand uit  
3. Start `transcribe_with_whisper.exe`  
4. Volg de instructies in het venster  

Bij eerste gebruik wordt het gekozen model automatisch gedownload naar `models/`. Hiervoor is eenmalig internetverbinding voor nodig. 

### Python-versie (voor ontwikkelaars)

```bash
git clone https://github.com/erfgoedgelderland/transcribe-with-whisper.git
cd transcribe-with-whisper
python -m venv env
env\Scripts\activate  # Op Mac/Linux: source env/bin/activate
pip install -r requirements.txt
python app.py
```

## Output

Transcripties worden opgeslagen als `.txt`-bestand.  
De opslaglocatie wordt bepaald door de instelling `TRANSCRIBER_OUTPUT_STRATEGY` in `.env`:

- `next_to_audio` → naast het originele audiobestand (standaard)  
- `outputs_dir` → in de vaste map `outputs/` binnen de project- of exe-map  

Bestandsnaamvoorbeeld:

```
interview.mp3 → interview_transcript[model][output][datum].txt
```
- `[mode]` = gekozen model `tiny`, `base`, `small`, `medium`, `large-v3`
- `[output]` = gekozen output `text`, `segments`, `sentences`
- `[datum]` = datum van transcript `yyyymmdd-hhmm`

## Modellen

- Ondersteunde modellen: `tiny`, `base`, `small`, `medium`, `large-v3`
- Modelgrootte varieert van ca. 75 MB tot 3 GB
- Modellen worden gedownload van [Hugging Face](https://huggingface.co/Systran) en lokaal opgeslagen in `models/`

## Output

Het transcript kan in drie formats opgeslagen worden.
- **Doorlopende tekst** (`text`): Transcriptie zonder tijdstempels.
- **Segmenten met tijdscode** (`segments`): Transcriptie per segment met tijdstempels.
- **Zinnen met tijdscode** (`sentences`): Transcriptie per zin met tijdstempels.

## FFmpeg

Voor audioverwerking maakt Transcribe with Whisper gebruik van [FFmpeg](https://ffmpeg.org/).

- **Windows (.exe)**: FFmpeg wordt meegeleverd in de map `bin/`, geen installatie nodig.  
- **Python-versie**: Installeer FFmpeg handmatig via je pakketbeheerder of [ffmpeg.org/download.html](https://ffmpeg.org/download.html).

## Systeemvereisten

- Windows 10/11  
- Voor de Python-versie: Python 3.9 of hoger  
- Genoeg vrije schijfruimte voor het gekozen model

## Licentie

Deze software is beschikbaar onder de [MIT-licentie](LICENSE).  
Zie ook de meegeleverde licentiebestanden `LICENSE_ffmpeg` en `LICENSE_whisper` voor componenten van derden.

## Bijdragen

Ontwikkeld door **Erfgoed Gelderland**.  
Je mag de code vrij gebruiken, aanpassen en uitbreiden. Pull requests zijn welkom.
