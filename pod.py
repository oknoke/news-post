import logging
import sys
from math import ceil
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

CHUNK_SIZE = 1024
OPENAI_KEY = os.environ['OPENAI_KEY']
OPENAI_TTS_MODEL = os.environ['OPENAI_TTS_MODEL']
OPENAI_TTS_VOICE = os.environ['OPENAI_TTS_VOICE']
ELEVEN_API_KEY = os.environ['ELEVEN_API_KEY']
ELEVEN_VOICE_ID = os.environ['ELEVEN_VOICE_ID']
ELEVEN_AUDIO_FORMAT = os.environ['ELEVEN_AUDIO_FORMAT']
MAILGUN_KEY = os.environ['MAILGUN_KEY']
MAILGUN_SANDBOX = os.environ['MAILGUN_SANDBOX']
MAILTO_ADDRESS = os.environ['MAILTO_ADDRESS']
# WHATSAPP_PHONE_ID = os.environ['WHATSAPP_PHONE_ID']
# WHATSAPP_RECIPIENT = os.environ['WHATSAPP_RECIPIENT']
# WHATSAPP_TOKEN = os.environ['WHATSAPP_TOKEN']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']


def elevenlabs_tts(text, voice_id, api_key, audio_format, topic):
    url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream?output_format={audio_format}'
    headers = {
        'Accept': '*/*',
        'xi-api-key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        # 'text': text,
        'model_id': 'eleven_multilingual_v2',
        'voice_settings': {
            'stability': 0.6,
            'similarity_boost': 0.85
        }
    }

    lines = text.split('\n')
    # chunks = ceil(len(text) / 2000)
    chunks = ceil(len(text) / 8000)
    chunk_size = ceil(len(lines) / chunks)

    for i in range(chunks):
        chunk = lines[i * chunk_size: i * chunk_size + chunk_size]
        chunk = '\n'.join(chunk)
        json = {**data, 'text': chunk}
        response = requests.post(url, json=json, headers=headers, stream=True)
        logging.info(f'TTS status: {response.status_code}')
        # print(response.text)

        mode = 'ab' if i else 'wb'
        audio = b''

        with open(os.path.join(os.path.dirname(__file__), topic + '_output.mp3'), mode) as f:
            for audio_chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if audio_chunk:
                    f.write(audio_chunk)
                    audio += audio_chunk
        return audio


def openai_tts(text, model, voice_id, api_key, topic):
    lines = text.split('\n')
    chunks = ceil(len(text) / 3000)
    chunk_size = ceil(len(lines) / chunks)

    client = OpenAI(api_key=api_key)

    for i in range(chunks):
        chunk = lines[i * chunk_size: i * chunk_size + chunk_size]
        chunk = '\n'.join(chunk)
        response = client.audio.speech.create(
            model=model,
            voice=voice_id,
            input=chunk,
        )

        mode = 'ab' if i else 'wb'
        audio = b''

        with open(os.path.join(os.path.dirname(__file__), topic + '_output.mp3'), mode) as f:
            for audio_chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                if audio_chunk:
                    f.write(audio_chunk)
                    audio += audio_chunk
    return audio


def send_mailgun(api_key, sandbox, mailto, topic):
    data = {
        'from': f'PodcastGPT <postmaster@{sandbox}>',
        'to': mailto,
        'subject': 'Your News Podcast',
        'text': 'Hi! Here\'s your news recap for today!',
    }
    with open(os.path.join(os.path.dirname(__file__), topic + 'output.mp3'), 'rb') as f:
        files = [('attachment', ('podcast.mp3', f.read()))]
    
    response = requests.post(
        f'https://api.mailgun.net/v3/{sandbox}/messages',
        auth=('api', api_key),
        data=data,
        files=files)
    return response


def send_telegram_message(bot_token, chat_id, topic):
    url = f'https://api.telegram.org/bot{bot_token}/sendAudio'
    payload = {
        'chat_id': chat_id,
        'performer': 'PodcastGPT',
        'title': 'News',
        'parse_mode': 'HTML',
        'caption': '<b>Hi!</b>\nHere\'s your news recap for today!'
    }
    with open(os.path.join(os.path.dirname(__file__), topic + 'output.mp3'), 'rb') as f:
        audio = f.read()
    files = {
        'audio': ('podcast.mp3', audio)
    }

    response = requests.post(url, data=payload, files=files)
    return response


if __name__ == '__main__':

    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s [%(levelname)s] %(message)s',
        handlers = [
            logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log.txt'), mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    try:

        from data_collection import *
        from gdrive import *

        service = get_service()

        logging.info('Creating AI podcast...')
        ai_stories, ai_stories_es = get_ai_news()
        en1 = make_podcast(ai_stories, 'AI', 'AI1_english_news.txt', outro=False)
        es2 = make_podcast(ai_stories_es, 'AI', 'AI2_spanish_news.txt', intro=False)
        logging.info('Getting translations')
        en2 = translate(es2, 'AI2', lang='english')
        es1 = translate(en1, 'AI1')
        logging.info('Getting TTS')
        en1 = openai_tts(en1, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_KEY, 'AI1_en')
        en2 = openai_tts(en2, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_KEY, 'AI2_en')
        es1 = openai_tts(es1, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_KEY, 'AI1_es')
        es2 = openai_tts(es2, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_KEY, 'AI2_es')
        with open('AI1_en_output.mp3', 'rb') as f:
            en1 = f.read()
        with open('AI2_en_output.mp3', 'rb') as f:
            en2 = f.read()
        with open('AI1_es_output.mp3', 'rb') as f:
            es1 = f.read()
        with open('AI2_es_output.mp3', 'rb') as f:
            es2 = f.read()
        with open(os.path.join(os.path.dirname(__file__), 'AI_output.mp3'), 'wb') as f:
            f.write(en1 + es2)
        with open(os.path.join(os.path.dirname(__file__), 'AI_output_en.mp3'), 'wb') as f:
            f.write(en1 + en2)
        with open(os.path.join(os.path.dirname(__file__), 'AI_output_es.mp3'), 'wb') as f:
            f.write(es1 + es2)
        logging.info('Uploading to Drive')
        for i in range(3):
            try:
                logging.info('Uploading file 1/3')
                upload(service, 'AI_output.mp3')
            except Exception:
                logging.exception(f'Error, try {i + 1}')
            else:
                break
        for i in range(3):
            try:
                logging.info('Uploading file 2/3')
                upload(service, 'AI_output_en.mp3')
            except Exception:
                logging.exception(f'Error, try {i + 1}')
            else:
                break
        for i in range(3):
            try:
                logging.info('Uploading file 3/3')
                upload(service, 'AI_output_es.mp3')
            except Exception:
                logging.exception(f'Error, try {i + 1}')
            else:
                break
    except Exception as e:
        logging.exception(f'Error: {e}')
    try:
        logging.info('Creating Economy podcast...')
        econ_stories = get_econ_news()
        en = make_podcast(econ_stories, 'Economy', 'Econ_english_news.txt', outro='en')
        logging.info('Getting translation')
        es = translate(en, 'Econ')
        logging.info('Getting TTS')
        en = openai_tts(en, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_KEY, 'Econ_en')
        es = openai_tts(es, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE, OPENAI_KEY, 'Econ_es')
        with open('Econ_en_output.mp3', 'rb') as f:
            en = f.read()
        with open('Econ_es_output.mp3', 'rb') as f:
            es = f.read()
        with open(os.path.join(os.path.dirname(__file__), 'Econ_output_en.mp3'), 'wb') as f:
            f.write(en)
        with open(os.path.join(os.path.dirname(__file__), 'Econ_output_es.mp3'), 'wb') as f:
            f.write(es)
        logging.info('Uploading to Drive')
        for i in range(3):
            try:
                logging.info('Uploading file 1/2')
                upload(service, 'Econ_output_en.mp3')
            except Exception:
                logging.exception(f'Error, try {i + 1}')
            else:
                break
        for i in range(3):
            try:
                logging.info('Uploading file 2/2')
                upload(service, 'Econ_output_es.mp3')
            except Exception:
                logging.exception(f'Error, try {i + 1}')
            else:
                break
    except Exception as e:
        logging.exception(f'Error: {e}')
