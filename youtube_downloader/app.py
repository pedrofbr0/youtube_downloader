import json
import streamlit as st
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import yt_dlp
import os

# GOOGLE API CONFIGURATION
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
# REDIRECT_URI = "http://localhost:8080/"
REDIRECT_URI = "https://youtube-downloader-x11v.onrender.com/"

# Get the content of CLIENT_SECRET_JSON from environment variables
client_secret_json = os.getenv("CLIENT_SECRET_JSON")

# If all the data was retrieved correclty
if client_secret_json:
    client_secret_info = json.loads(client_secret_json)
else:
    raise ValueError("CLIENT_SECRET_JSON is not configured in environment variables")

def get_authorization_url():
    # Use the information in the client_secret.json to identify
    # the application requesting authorization.
    flow = InstalledAppFlow.Flow.from_client_config(
        client_config=client_secret_json,
        scopes=SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required.
    flow.redirect_uri = 'http://localhost:8000'

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    return authorization_url, state

# Adding credentials to OAuth2
def get_authenticated_service():
    creds = None
    token_json = os.getenv("TOKEN_JSON")
    if token_json:
        creds = Credentials.from_authorized_user_info(json.loads(token_json), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            
            flow = InstalledAppFlow.from_client_config(client_secret_info, SCOPES)
            flow.redirect_uri = REDIRECT_URI
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run (in environment variable for production)
        os.environ['TOKEN_JSON'] = creds.to_json()
    return creds
def format_selector(ctx):
    # Select the best video and the best audio that won't result in an mkv.
    
    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }
    
st.title('YouTube Downloader')

#Streamlit interface
video_url = st.text_input('Video URL')
download_url = None
service = get_authenticated_service()

wanted_format = "mp4"
wanted_quality = "720p"

video_filter = lambda elemento: elemento.get('video_ext') == wanted_format and elemento.get('format_note') == wanted_quality
    
if video_url:
    ydl_opts = {'format': format_selector}        
    # ydl.download([video_url])
    if st.button('Generate Link'):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            sanitized_info = ydl.sanitize_info(info_dict)
            video_title = sanitized_info.get('title')
        # with open("data.json", "w") as file:
        #     json.dump(sanitized_info, file)

        results = list(filter(video_filter, sanitized_info['formats']))
             
        if results:
            video_url = results[0]['url']
            st.success("Download link generated! Click below to download the video.")
            st.download_button('Download Video', video_url, f'{video_title}.{wanted_format}')
        else:
            st.error("Could not find a video with the selected format and quality.")
            raise ValueError("Could not find a video with the selected format and quality.")
