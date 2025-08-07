# Transcribe with Whisper

Een eenvoudig transcriptieprogramma op basis van [OpenAI Whisper](https://github.com/openai/whisper).  
Veilig, open source en Nederlandstalig.

---

## 🧠 Wat doet dit programma?

- Zet audiobestanden automatisch om naar tekst
- Werkt volledig lokaal op je eigen computer
- Verstuurd **geen** gegevens via internet
- Ondersteunt o.a. `.wav`, `.mp3`, `.m4a`, `.ogg`
- Geschikt voor interviews, erfgoedprojecten, podcasts en meer

---

## 🚀 Hoe gebruik je het?

Je kunt het programma op twee manieren gebruiken:

### 1. Gebruik de `.exe` (aanbevolen voor Windows-gebruikers)

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

```bash
git clone https://github.com/erfgoedgelderland/transcribe-with-whisper.git
cd transcribe-with-whisper
python -m venv env
env\Scripts\activate  # Of source env/bin/activate op Mac/Linux
pip install -r requirements.txt
```

#### ▶️ Uitvoeren

```bash
python transcribe_with_whisper.py
```

---

## 📁 Output

De transcriptie wordt opgeslagen als een `.txt` bestand met dezelfde naam als je audiobestand, bijvoorbeeld:

```
interview.mp3  →  interview_transcript.txt
```

---

## ℹ️ Vereisten

- Windows 10/11
- Voor de Python-versie: Python 3.9 of hoger

---

## 🛡️ Veiligheid

- Dit programma draait volledig **offline**
- Geen audio of transcriptie wordt online verstuurd
- Gemaakt met privacy in gedachten

---

## 📄 Licentie

Deze software is open source onder de [MIT-licentie](LICENSE).

---

## 👥 Ontwikkeling en bijdragen

Dit project is ontwikkeld door Erfgoed Gelderland.  
Je mag deze code gebruiken, aanpassen en doorontwikkelen. Pull requests zijn welkom!
