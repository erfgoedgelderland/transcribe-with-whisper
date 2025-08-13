# Transcribe with Whisper

**Transcribe with Whisper** is een Nederlandstalig, open source transcriptieprogramma gebaseerd op [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper), een snelle en efficiënte implementatie van [OpenAI Whisper](https://github.com/openai/whisper).  
Het programma werkt volledig lokaal: er wordt **geen audio of tekst naar internet verstuurd**.

## Functies

- Zet audiobestanden om naar tekst met hoge nauwkeurigheid
- Snellere verwerking dankzij Faster-Whisper
- Ondersteunt o.a. `.wav`, `.mp3`, `.m4a`, `.ogg`
- Volledig offline en privacyvriendelijk
- Geschikt voor interviews, erfgoedprojecten, podcasts en meer
- Modellen worden lokaal opgeslagen in de map `models/`

## Gebruik

### Windows (.exe-versie)

1. Download de nieuwste release via [GitHub Releases](https://github.com/erfgoedgelderland/transcribe-with-whisper/releases)  
2. Pak het `.zip`-bestand uit  
3. Start `transcribe_with_whisper.exe`  
4. Volg de instructies in het venster  

Geen installatie of internetverbinding nodig.  
**Bij eerste gebruik wordt het gekozen model automatisch gedownload** naar `models/`.  
Dit gebeurt éénmalig per model.

<<<<<<< HEAD
1. Download de nieuwste versie via de [releases-pagina](https://github.com/erfgoedgelderland/transcribe-with-whisper/releases)
2. Pak het `.zip` bestand uit
3. Dubbelklik op `transcribe_with_whisper.exe`
4. Volg de instructies in het venster
5. Je transcript wordt automatisch opgeslagen naast je audiobestand

💡 *Geen installatie nodig. Geen internetverbinding vereist\*.*  
 \*Let op: bij het eerste gebruik wordt het Whisper-taalmodel gedownload. Hiervoor is eenmalig een internetverbinding nodig.

---

### 2. Gebruik de Python-versie (voor ontwikkelaars)

#### 📦 Installatie
=======
### Python-versie (voor ontwikkelaars)
>>>>>>> 775f583 (Release v1.1.0: Faster-Whisper, GUI, .env)

```bash
git clone https://github.com/erfgoedgelderland/transcribe-with-whisper.git
cd transcribe-with-whisper
python -m venv env
env\Scripts\activate  # Op Mac/Linux: source env/bin/activate
pip install -r requirements.txt
python main_app.py
```

## Output

Transcripties worden opgeslagen als `.txt`-bestand.  
De opslaglocatie wordt bepaald door de instelling `TRANSCRIBER_OUTPUT_STRATEGY` in `.env`:

- `next_to_audio` → naast het originele audiobestand (standaard)  
- `outputs_dir` → in de vaste map `outputs/` binnen de project- of exe-map  

Bestandsnaamvoorbeeld:

```
interview.mp3 → interview_transcript_small_20250813.txt
```

## Modellen

- Ondersteunde modellen: `tiny`, `base`, `small`, `medium`, `large-v3`
- Modelgrootte varieert van ca. 75 MB tot 3 GB
- Modellen worden gedownload van [Hugging Face](https://huggingface.co/Systran) en lokaal opgeslagen in `models/`

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
