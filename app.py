import os
import re
import time
import logging
from threading import Thread
from flask import Flask, redirect, render_template, request, send_file, jsonify, make_response, url_for, session
from flask_socketio import SocketIO
import yt_dlp
from transcription import get_transcription
from googletrans import Translator
from deep_translator import GoogleTranslator
# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

translator = Translator()

# Répertoire de téléchargement
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Détection automatique de ffmpeg
FFMPEG_PATH = "C:/ffmpeg/bin" if os.name == "nt" else "/usr/bin/ffmpeg"

# Regex pour valider les URLs YouTube
YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/"
    r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
)

translations = {"title": {"en": "YouTube Video Downloader", "fr": "Téléchargeur de vidéos YouTube"},
    "home": {"en": "Home", "fr": "Accueil"},
    "download": {"en": "Download", "fr": "Télécharger"},
    "video-preview": {"en": "Video Preview", "fr": "Aperçu de la vidéo"},
    "url_label": {"en": "Enter YouTube Video URL:", "fr": "Entrez l’URL de la vidéo YouTube :"},
    "submit": {"en": "Transcribe Video", "fr": "Transcrire la vidéo"},
    "back": {"en": "Back to Home", "fr": "Retour à l’accueil"},
    "spinner": {"en": "Loading...", "fr": "Téléchargement en cours, veuillez patienter..."},
    "error-url": {"en": "Invalid URL", "fr": "URL invalide"},
    "error-download": {"en": "Error downloading video", "fr": "Erreur lors du téléchargement de la vidéo"},
    "error-transcription": {"en": "Error during transcription", "fr": "Erreur lors de la transcription"},
    "download-options": {"en": "Download Options", "fr": "Options de téléchargement"},
    "mp3-download": {"en": "Download MP3", "fr": "Télécharger MP3"},
    "mp3-download-info": {"en": "Convert YouTube to MP3", "fr": "Convertissez l'audio au format MP3"},
    "transcription-info": {"en": "Transcribe YouTube Video", "fr": "Transcrire la vidéo YouTube"},
    "success-download": {"en": "Download successful", "fr": "Téléchargement réussi"},
    "success-copy": {"en": "URL copied to clipboard", "fr": "URL copiée dans le presse-papiers"},
    "free-resources": {"en": "Free Resources", "fr": "Ressources gratuites"},
    "toggle-dark-mode": {"en": "Toggle Dark Mode", "fr": "Activer le mode sombre"},
    "start": {"en": "Start", "fr": "Commencer"},
    "video-download": {"en": "Video Download", "fr": "Téléchargement de vidéo"},
    "place-holder-url": {"en": "Paste URL here", "fr": "Coller l'URL ici"},
    #transcription
    "transcription-title": {"en": "YouTube Video Transcription", "fr": "Transcription de vidéo YouTube"},
    "transcribing": {"en": "Transcribing...", "fr": "Transcription en cours..."},
    "spinner-transcription": {"en": "Transcribing video, please wait...", "fr": "Transcription de la vidéo, veuillez patienter..."},
    "transcribe-video": {"en": "Transcribe Video", "fr": "Transcrire la vidéo"},
    "select-language": {"en": "Select Language", "fr": "Sélectionner la langue"},
    "translate": {"en": "Translate", "fr": "Traduire"},

    #MP3
    "mp3-title": {"en": "YouTube to MP3 Converter", "fr": "Convertisseur YouTube vers MP3"},
    "download-mp3": {"en": "Download MP3", "fr": "Télécharger MP3"},
    "mp3-conversion": {"en": "Converting to MP3, please wait...", "fr": "Conversion en MP3, veuillez patienter..."},
    "mp3-convertir": {"en": "Convert to MP3", "fr": "Convertir en MP3"},

    #information
    "information-title": {"en": "Information", "fr": "Informations"},
    "about": {"en": "About Free Download 999", "fr": "À propos de Free Download 999"},
    "about-paragraph-1": {
        "en": (
            "FreeMP3Music is the fastest and free MP3 search engine to download music on your "
            "computer or mobile devices. Easily find and download your favorite tracks from multiple sources in MP3 or MP4 formats, "
            "all for free. We offer you a unique service ad-free, you can forget about the other sites like mp3 juice that will "
            "fill your browser with ads and in the end you can't download anything at all."
        ),
        "fr": (
            "FreeMP3Music est le moteur de recherche MP3 le plus rapide et gratuit pour télécharger de la musique sur votre "
            "ordinateur ou appareil mobile. Trouvez et téléchargez facilement vos morceaux préférés à partir de plusieurs sources au format MP3 ou MP4, "
            "le tout gratuitement. Nous vous offrons un service unique sans publicité, oubliez les autres sites comme mp3 juice "
            "qui encombrent votre navigateur de publicités sans vous permettre de télécharger quoi que ce soit."
        )
    },
    "about-paragraph-2": {
        "en": (
            "Are you looking for new music? Or you want to search for old songs you want to download? "
            "Nothing simpler — with our online music extractor, "
            "you can download any song in just a few seconds. "
            "We have a large database where you'll definitely find what you want without further effort."
        ),
        "fr": (
            "Vous cherchez de la nouvelle musique ? Ou vous voulez retrouver de vieilles chansons à télécharger ? "
            "Rien de plus simple — avec notre extracteur de musique en ligne, "
            "vous pouvez télécharger n'importe quelle chanson en quelques secondes. "
            "Nous disposons d'une vaste base de données où vous trouverez certainement ce que vous cherchez sans effort supplémentaire."
        )
    },
    "utilisation": {
        "en": (
            "How to use FreeMP3Music?"
        ),
        "fr": (
            "Comment utiliser FreeMP3Music ?"
        )
    },
    "utilisation-paragraph-1": {
        "en": (
            "To use FreeMP3Music, simply enter the name of the song or artist you want to download in the search bar. "
            "Our search engine will provide you with a list of available tracks. "
            "Click on the download button next to the desired track to save it to your device."
        ),
        "fr": (
            "Pour utiliser FreeMP3Music, il vous suffit d'entrer le nom de la chanson ou de l'artiste que vous souhaitez télécharger dans la barre de recherche. "
            "Notre moteur de recherche vous fournira une liste des pistes disponibles. "
            "Cliquez sur le bouton de téléchargement à côté de la piste souhaitée pour l'enregistrer sur votre appareil."
        )
    },
    "utilisation-paragraph-2": {
        "en": (
            "The video will begin processing. Please wait until the download is ready."
        ),
        "fr": (
            "La vidéo va commencer à être traitée. Veuillez patienter jusqu'à ce que le téléchargement soit prêt."
        )
    },
    "utilisation-paragraph-3.1": {
        "en": (
            "If you are downloading a merged video/audio file or converting formats, make sure "
        ),
        "fr": (
            "Si vous téléchargez un fichier vidéo/audio fusionné ou convertissez des formats, assurez-vous "
        )
    },
    "utilisation-paragraph-3.2": {
        "en": (
            "is installed on your system."
        ),
        "fr": (
            "est installé sur votre système."
        )
    },
    "utilisation-paragraph-4": {
        "en": (
            "FFmpeg is used on the server to combine or convert files (e.g., merge video and audio into MP4)."
        ),
        "fr": (
            "FFmpeg est utilisé sur le serveur pour combiner ou convertir des fichiers (par exemple, fusionner la vidéo et l'audio en MP4)."
        )
    },
    "utilisation-paragraph-5": {
        "en": (
            "No configuration needed on your end if you’re using the web tool. Just enjoy the final file!"
        ),
        "fr": (
            "Aucune configuration n'est nécessaire de votre part si vous utilisez l'outil web. Profitez simplement du fichier final !"
        )
    },

    "contact": {
        "en": (
            "Contact Us"
        ),
        "fr": (
            "Contactez-nous"
        )

    },
    "contact-paragraph": {
        "en": (
            "If you have any questions or need assistance, feel free to reach out to us. "
            "We are here to help you make the most of FreeMP3Music."
        ),
        "fr": (
            "Si vous avez des questions ou avez besoin d'aide, n'hésitez pas à nous contacter. "
            "Nous sommes là pour vous aider à tirer le meilleur parti de FreeMP3Music."
        )
    }

    }

@app.route('/set_language', methods=['POST'])
def set_language():
    lang = request.form.get('lang')
    if lang in ['en', 'fr']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('home'))



# Fonction pour valider les URLs YouTube
def is_valid_youtube_url(url):
    return bool(YOUTUBE_REGEX.match(url))

# Suppression automatique des fichiers après téléchargement
def delete_file_after_download(file_path, delay=30):
    time.sleep(delay)
    try:
        os.remove(file_path)
        logging.info(f"Fichier supprimé : {file_path}")
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du fichier : {e}")

def download_video(url, ydl_opts):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info_dict)
            logging.info(f"Téléchargement terminé : {file_name}")
            return file_name
    except Exception as e:
        logging.error(f"Erreur yt-dlp : {e}")
        return None

def translate_text(text, target_lang):
    translator = Translator()
    translated = translator.translate(text, dest=target_lang)
    return translated.text

@app.route("/", methods=["GET", "POST"])
def home():
    language = session.get("lang", "en")  # Défaut: anglais

    if request.method == "POST":
        url = request.form.get("url")
        if not is_valid_youtube_url(url):
            return jsonify({"error": "URL invalide"}), 400

        ydl_opts = {
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        file_name = download_video(url, ydl_opts)
        if file_name:
            return send_file(file_name, as_attachment=True)
        return jsonify({"error": "Erreur lors du téléchargement"}), 500

    return render_template("index.html", lang=language, translations=translations)

@app.route("/info", methods=["GET", "POST"])
def information():
    language = session.get("lang", "en")

    return render_template("information.html", lang=language, translations=translations)

@app.route("/mp3", methods=["GET", "POST"])
def mp3_downloader():
    language = session.get("lang", "en")

    if request.method == "POST":
        url = request.form.get("url")
        if not is_valid_youtube_url(url):
            return jsonify({"error": "URL invalide"}), 400

        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "ffmpeg_location": FFMPEG_PATH,
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "quiet": True,
        }
        file_name = download_video(url, ydl_opts)
        if file_name:
            mp3_file = f"{os.path.splitext(file_name)[0]}.mp3"
            response = send_file(mp3_file, as_attachment=True)
            Thread(target=delete_file_after_download, args=(mp3_file,)).start()
            return response
        return jsonify({"error": "Erreur lors du téléchargement"}), 500

    return render_template("MP3.html", lang=language, translations=translations)

@app.route('/download_transcript')
def download_transcript():
    text = request.args.get('text', '')
    response = make_response(text)
    response.headers.set('Content-Type', 'text/plain')
    response.headers.set('Content-Disposition', 'attachment', filename='transcript.txt')
    return response


@app.route('/transcription', methods=['GET', 'POST'])
def transcription_page():
    language = session.get("lang", "en")

    if request.method == 'POST':
        video_url = request.form.get('url')
        video_id = extract_video_id(video_url)
        if not video_id:
            return render_template('transcription.html', error="Invalid YouTube URL.",
                                   lang=language, translations=translations)

        transcript = get_transcription(video_id)

        if transcript.startswith("An error occurred") or transcript.endswith("video."):
            return render_template('transcription.html', error=transcript,
                                   lang=language, translations=translations)
        else:
            return render_template('transcription.html', transcript=transcript,
                                   lang=language, translations=translations)

    return render_template('transcription.html', lang=language, translations=translations)

@app.route('/translate', methods=['POST'])
def translate_transcript():
    transcript = request.form.get('transcript')
    language = request.form.get('language', 'en')

    if not transcript:
        return render_template('transcription.html', error="No transcript provided for translation.")

    try:
        translated_text = GoogleTranslator(source='auto', target=language).translate(transcript)
        return render_template('transcription.html',
                               transcript=translated_text,
                               selected_language=language,)
    except Exception as e:
        return render_template('transcription.html', error=f"Translation failed: {str(e)}")


def extract_video_id(url):
    import re
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None



if __name__ == "__main__":
    socketio.run(app, debug=True)
