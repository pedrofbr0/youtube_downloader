import streamlit as st
import yt_dlp

def download_youtube_video(url: str, quality: str, audio_only: bool) -> str:
    """
    Downloads a YouTube video or audio using yt-dlp.

    :param url: URL of the YouTube video
    :param quality: Quality of the video to download
    :param audio_only: If True, download only the audio
    :return: Filename of the downloaded video/audio
    """
    ydl_opts = {}
    
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([url])
        return result

def main():
    st.title("YouTube Video Downloader")

    url = st.text_input("Enter the URL of the YouTube video:")
    
    if url:
        ydl = yt_dlp.YoutubeDL()
        meta = ydl.extract_info(url, download=False)
        video_title = meta.get('title', 'video')
        
        quality = st.selectbox(
            "Select quality", 
            options=["144p", "360p", "480p", "720p", "1080p", "Audio Only"]
        )
        
        audio_only = quality == "Audio Only"

        if st.button("Download"):
            st.write(f"Downloading {video_title} at {quality}...")
            download_youtube_video(url, quality.replace("p", ""), audio_only)
            st.success("Download complete!")

if __name__ == "__main__":
    main()
