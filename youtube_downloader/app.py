import json
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
import yt_dlp
import os

# Configurações da API do Google
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
CLIENT_SECRETS_FILE = "client_secret.json"

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        SCOPES
    )
    creds = flow.run_local_server(port=8080)
    return creds

def get_download_url(url, format_id):
    ydl_opts = {
        'format': format_id,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_url = info_dict['url']
        return video_url

st.title('YouTube Video Downloader')

# Verifica se está autenticado
service = get_authenticated_service()

url = st.text_input('Insira a URL do vídeo do YouTube:')
download_url = None

if url:
    ydl_opts = {'noplaylist': True}
    formats = []
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info= ydl.extract_info(url, download=False)
        info_dict = ydl.sanitize_info(info)
        print(info_dict)
        print(json.dumps(info_dict))
        info_dict = ydl.extract_info(url, download=False)
        video_formats = info_dict.get('formats', [])
        

        
        for f in video_formats:
            format_id = f.get('format_id')
            format_note = f.get('format_note', 'N/A')
            resolution = f.get('resolution', 'N/A')
            if format_id and format_note:
                formats.append({"id": format_id, "display": f"{resolution} ({format_note})"})

    
    # format_options = [f['display'] for f in formats]
    # selected_format = st.selectbox("Escolha a qualidade de download:", format_options)
    
    format_options = [f['display'] for f in formats]
    selected_format_display = st.selectbox("Escolha a qualidade de download:", format_options)
        
    if st.button("Download"):
        selected_format = next((f for f in formats if f['display'] == selected_format_display), None)
        if selected_format:
            st.success(f"Baixando com formato ID: {selected_format['id']}")
            # Lógica para baixar o vídeo usando o `selected_format['id']`
            download_url = get_download_url(url, selected_format['id'])
        else:
            st.error("Formato não encontrado.")
    # if st.button('Gerar Link de Download'):
    #     selected_format_id = formats[format_options.index(selected_format)][0]
    #     download_url = get_download_url(url, selected_format_id)
    #     st.success('Link de download gerado! Clique abaixo para baixar o vídeo.')
    #     st.markdown(f"[Download Video]({download_url})", unsafe_allow_html=True)

if download_url:
    st.markdown(f"[Download Video]({download_url})", unsafe_allow_html=True)
