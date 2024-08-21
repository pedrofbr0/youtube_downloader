import json
import streamlit as st
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import yt_dlp
import os
import requests
import subprocess


# Configurações da API do Google
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
# CLIENT_SECRETS_FILE = "../etc/secrets/client_secret.json"
# TOKEN_FILE = "../etc/secrets/token.json"
REDIRECT_URI = "http://localhost:8080/"

# Obtém o diretório onde o script atual está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configura os caminhos completos dos arquivos .json baseados no diretório do script
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, 'etc', 'secrets', 'client_secret.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'etc','secrets', 'token.json')

# Adding credentials to OAuth2
def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        # Salva o token para reutilização futura
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def format_selector(ctx):
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }
    
st.title('YouTube Video Downloader')


#Streamlit interface
video_url = st.text_input('Video URL')
download_url = None
service = get_authenticated_service()

ydl_opts = {}

# format_options = {'format': 'best[ext=mp4]'} # "bestvideo[ext=mp4]+bestaudio[ext=m4a]"

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     info = ydl.extract_info(video_url, download=False)
#     sanitized_info = ydl.sanitize_info(info)
    
if video_url:
    ydl_opts = {'format': format_selector}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # ydl.download([video_url])
    
    
        if st.button('Gerar Link de Download'):
            info_dict = ydl.extract_info(video_url, download=False)
            sanitized_info = ydl.sanitize_info(info_dict)
            # video_url = sanitized_info['url']
            with open("data.json", "w") as file:
                json.dump(sanitized_info, file)
            video_url = info_dict['url']
            # selected_format_id = format_list[format_options.index(selected_format)][0]
            st.success('Link de download gerado! Clique abaixo para baixar o vídeo.')
            st.markdown(f"[Download Video]({video_url})", unsafe_allow_html=True)

    if download_url:
        st.markdown(f"[Download Video]({download_url})", unsafe_allow_html=True)

# # Interface do Streamlit
# url = st.text_input('Insira a URL do vídeo do YouTube:')
# download_url = None

# if url:
#     ydl_opts = {'noplaylist': True, 'quiet': True}
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
#         formats = info['formats']
#         # Use `.get()` para evitar o KeyError se 'format_note' não existir
#         format_options = [f"{f.get('format_note', 'Unknown')} ({f.get('width', 'N/A')}x{f.get('height', 'N/A')})" for f in formats if 'vcodec' in f and 'acodec' in f]
#         selected_format = st.selectbox('Escolha a qualidade de download:', format_options)
        q
#         if st.button('Download'):
#             selected_format_info = formats[format_options.index(selected_format)]
#             video_url = selected_format_info['url']
#             audio_format = next((f for f in formats if 'acodec' in f and f['acodec'] != 'none'), None)
            
#             if audio_format:
#                 audio_url = audio_format['url']
#                 st.write(f"Baixando com formato ID: {selected_format_info['format_id']}")
                
#                 # Baixar vídeo e áudio separadamente usando requests
#                 video_file = 'video.mp4'
#                 audio_file = 'audio.mp4'
                
#                 # Função para baixar arquivos
#                 def download_file(url, filename):
#                     with requests.get(url, stream=True) as r:
#                         r.raise_for_status()
#                         with open(filename, 'wb') as f:
#                             for chunk in r.iter_content(chunk_size=8192):
#                                 f.write(chunk)
                
#                 # Baixando arquivos
#                 download_file(video_url, video_file)
#                 download_file(audio_url, audio_file)
                
#                 # Mesclar vídeo e áudio usando ffmpeg
#                 output_file = 'final_video.mp4'
#                 os.system(f'ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}')
                
#                 st.success('Download completo!')
#                 st.markdown(f"[Baixar vídeo](final_video.mp4)")
#             else:
#                 st.error('Não foi possível encontrar uma faixa de áudio.')

