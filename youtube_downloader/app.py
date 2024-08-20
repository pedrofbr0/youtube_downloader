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
CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

# Adicionando as credenciais do OAuth2
def get_authenticated_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES, redirect_uri=REDIRECT_URI)
            creds = flow.run_local_server(port=8501)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

import requests
import os

# Interface do Streamlit
url = st.text_input('Insira a URL do vídeo do YouTube:')
download_url = None

if url:
    ydl_opts = {'noplaylist': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']
        # Use `.get()` para evitar o KeyError se 'format_note' não existir
        format_options = [f"{f.get('format_note', 'Unknown')} ({f.get('width', 'N/A')}x{f.get('height', 'N/A')})" for f in formats if 'vcodec' in f and 'acodec' in f]
        selected_format = st.selectbox('Escolha a qualidade de download:', format_options)
        
        if st.button('Download'):
            selected_format_info = formats[format_options.index(selected_format)]
            video_url = selected_format_info['url']
            audio_format = next((f for f in formats if 'acodec' in f and f['acodec'] != 'none'), None)
            
            if audio_format:
                audio_url = audio_format['url']
                st.write(f"Baixando com formato ID: {selected_format_info['format_id']}")
                
                # Baixar vídeo e áudio separadamente usando requests
                video_file = 'video.mp4'
                audio_file = 'audio.mp4'
                
                # Função para baixar arquivos
                def download_file(url, filename):
                    with requests.get(url, stream=True) as r:
                        r.raise_for_status()
                        with open(filename, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                
                # Baixando arquivos
                download_file(video_url, video_file)
                download_file(audio_url, audio_file)
                
                # Mesclar vídeo e áudio usando ffmpeg
                output_file = 'final_video.mp4'
                os.system(f'ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}')
                
                st.success('Download completo!')
                st.markdown(f"[Baixar vídeo](final_video.mp4)")
            else:
                st.error('Não foi possível encontrar uma faixa de áudio.')

