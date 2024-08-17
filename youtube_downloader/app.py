import os
from pytubefix import YouTube
import streamlit as st

def download_youtube_video(url: str, download_path: str) -> str:
    """
    Downloads a YouTube video and saves it to the specified path.

    :param url: URL of the YouTube video
    :param download_path: Directory where the video should be saved
    :return: Path to the downloaded video
    """
    yt = YouTube(url)
    stream = yt.streams.filter(
        progressive=True, file_extension="mp4"
    ).order_by("resolution").desc().first()
    downloaded_file = stream.download(output_path=download_path)
    return downloaded_file


def main():
    """Main function to render the Streamlit web app."""
    st.title("YouTube Video Downloader")

    url = st.text_input("Enter the URL of the YouTube video:")
    download_path = st.text_input(
        "Enter the download path (default is current directory):",
        value=os.getcwd(),
    )

    if st.button("Download Video"):
        if url:
            try:
                video_path = download_youtube_video(url, download_path)
                st.success(f"Video downloaded successfully! You can find it here: {video_path}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a valid YouTube URL.")


if __name__ == "__main__":
    main()