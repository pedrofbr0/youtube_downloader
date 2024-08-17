import streamlit as st
from pytubefix import YouTube
import os

def download_youtube_video(url: str, resolution: str, audio_only: bool) -> str:
    """
    Downloads a YouTube video and saves it to the specified path.

    :param url: URL of the YouTube video
    :param resolution: Resolution of the video to download
    :param audio_only: If True, download only the audio
    :return: Filename of the downloaded video/audio
    """
    yt = YouTube(url)

    if audio_only:
        stream = yt.streams.filter(only_audio=True).first()
        output_file = stream.download()
        base, ext = os.path.splitext(output_file)
        new_file = base + '.mp3'
        os.rename(output_file, new_file)
        return new_file
    else:
        stream = yt.streams.filter(res=resolution, progressive=True).first()
        if not stream:
            st.error(f"No stream available for resolution: {resolution}")
            return None
        return stream.download()

def main():
    st.title("YouTube Video Downloader")

    url = st.text_input("Enter the URL of the YouTube video:")
    
    if url:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True).all()
        resolutions = list(set([stream.resolution for stream in streams if stream.resolution]))
        resolutions.sort(reverse=True)
        resolutions.append("Audio Only")
        
        resolution = st.selectbox("Select resolution", resolutions)

        download_button = st.button("Download")

        if download_button:
            if resolution == "Audio Only":
                audio_only = True
                resolution = None
            else:
                audio_only = False

            st.write(f"Downloading {resolution}...")
            video_file = download_youtube_video(url, resolution, audio_only)
            
            if video_file:
                with open(video_file, "rb") as file:
                    st.download_button(label="Download", data=file, file_name=os.path.basename(video_file), mime="application/octet-stream")
                st.success("Download complete!")

if __name__ == "__main__":
    main()
