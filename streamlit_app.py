import streamlit as st
import pytube
import os
import requests
import platform
import streamlit.components.v1 as components
import moviepy.editor as mp
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

# Create a session state object for user login
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

# Function to simulate user login
def login(username, password):
    if username == "123" and password == "123":
        st.session_state.is_logged_in = True
        return True
    return False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None

# Function to check if the user is logged in
def check_login():
    return st.session_state.is_logged_in

# Sidebar navigation options
st.sidebar.title("WELCOME 👋")
if not check_login():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if login(username, password):
            st.sidebar.success("Login successful!")
        else:
            st.sidebar.error("Invalid credentials. Please try again.")
else:
    st.sidebar.subheader("Chosse Your Option !")
    if st.sidebar.button("Download YouTube Video"):
        st.session_state.selected_option = "Download Video"
    if st.sidebar.button("Download MP3 from YouTube"):
        st.session_state.selected_option = "Download MP3"
    if st.sidebar.button("Image to PDF Converter"):
        st.session_state.selected_option = "Image to PDF"
    

# Main content based on user selection
st.title("ALL YOUR DAILY SERVICES IN 1 WEB APP 🌐 ")

if check_login():
    
    if st.session_state.selected_option == "Download Video":
        st.title("Download Video from YouTube 🎬🎥🔴▶ ")
        # Input for the YouTube URL
        url = st.text_input("Enter the URL of the Video", help="e.g., https://www.youtube.com/watch?v=your_video_id")

        yt = None  # Initialize yt as None

        # Display the video thumbnail and get yt object
        if url:
            try:
                yt = pytube.YouTube(url)
                thumbnail = yt.thumbnail_url
                st.image(thumbnail, use_column_width=True, caption="Video Thumbnail")
            except Exception as e:
                st.warning("Thumbnail not available for this video.")

        # Create a dictionary of human-readable video quality labels
        quality_labels = {
            "18": "360p (MP4)",
            "22": "720p (MP4)",
            "137": "1080p (MP4)",
            "248": "1080p (WebM)",
            "43": "360p (WebM)",
        }

        # Dropdown for selecting video quality
        if yt:
            available_streams = yt.streams.filter(progressive=True, file_extension="mp4")
            video_quality_labels = [quality_labels.get(str(stream.itag), f"itag={stream.itag} mime_type={stream.mime_type}") for stream in available_streams]
            selected_quality_label = st.selectbox("Select Video Quality", video_quality_labels)

            # Find the selected stream based on the selected label
            selected_stream = None
            for stream in available_streams:
                if quality_labels.get(str(stream.itag), f"itag={stream.itag} mime_type={stream.mime_type}") == selected_quality_label:
                    selected_stream = stream
                    break

        # Detect the user's device type
        device_type = platform.system()

        if device_type == "Linux" or device_type == "Windows":
            # For PC users, provide options for a custom path
            # Button to select the local storage path
            download_path = st.text_input("Choose Local Storage Path", "", help="e.g., /path/to/your/directory")

            # Button to start the download
            if st.button("Download in PC"):
                if not download_path:
                    st.error("Please choose a local storage path.")
                else:
                    try:
                        st.info(f"Downloading: {yt.title}")

                        # Normalize the download path and create the folder if it doesn't exist
                        download_path = os.path.normpath(download_path)
                        os.makedirs(download_path, exist_ok=True)

                        selected_stream.download(output_path=download_path)
                        st.success(f"Download Completed! Video saved to {download_path}")

                        # Provide a link to download the video
                        st.markdown(f"Download the video: [Download Link]({os.path.join(download_path, yt.title + selected_stream.subtype)})")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        elif device_type == "Darwin":
            # For macOS users, provide an automatic download option
            if st.button("Download in Mac"):
                if yt and selected_stream:
                    try:
                        st.info(f"Downloading: {yt.title}")

                        response = requests.get(selected_stream.url)
                        with open(f"{yt.title}.{selected_stream.subtype}", "wb") as video_file:
                            video_file.write(response.content)

                        st.success(f"Download Completed! Video saved to current directory")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        else:
            st.error("Device type not supported for automatic download")
    elif st.session_state.selected_option == "Download MP3":
        st.title("Download Music from YouTube  🎵 ")
        # Input for the YouTube URL
        url = st.text_input("Enter the URL of the Video", help="e.g., https://www.youtube.com/watch?v=your_video_id")

        yt = None  # Initialize yt as None

        # Display the video thumbnail and get yt object
        if url:
            try:
                yt = pytube.YouTube(url)
                thumbnail = yt.thumbnail_url
                st.image(thumbnail, use_column_width=True, caption="Video Thumbnail")
            except Exception as e:
                st.warning("Thumbnail not available for this video.")

        # Check if the Download button is pressed
        if st.button("Download MP3"):
            if yt:
                try:
                    st.info(f"Downloading MP3 from: {yt.title}")

                    audio_stream = yt.streams.filter(only_audio=True).first()
                    download_path = f"./downloads/{yt.title}.mp4"
                    audio_stream.download(output_path="./downloads", filename=yt.title)

                    # Extract audio to MP3
                    video = mp.VideoFileClip(download_path)
                    audio = video.audio
                    mp3_filename = f"./downloads/{yt.title}.mp3"
                    audio.write_audiofile(mp3_filename)
                    audio.close()

                    st.success("Audio Extraction Completed!")
                    st.markdown(f"Download the audio: [Download Link]({mp3_filename})")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
       
    if st.session_state.selected_option == "Image to PDF":
            st.title("Image to PDF Converter 📷➡️📄")

            st.write("Select multiple images and convert them to a PDF.")

            uploaded_images = st.file_uploader("Upload Images (JPEG, PNG, or GIF)", type=["jpg", "jpeg", "png", "gif"], accept_multiple_files=True)

            if uploaded_images:
                st.write("Images to convert to PDF:")
                for image in uploaded_images:
                    st.image(image, use_column_width=True)

                if st.button("Convert to PDF"):
                    try:
                        pdf_filename = "converted_images.pdf"
                        pdf_path = os.path.join(os.getcwd(), pdf_filename)
                        pdf = canvas.Canvas(pdf_path, pagesize=letter)

                        for image in uploaded_images:
                            img = Image.open(image)
                            img_reader = ImageReader(img)
                            pdf.drawImage(img_reader, 0, 0, width=letter[0], height=letter[1])
                            pdf.showPage()

                        pdf.save()
                        st.success("Images converted to PDF.")

                        # Provide a download button for the PDF
                        st.download_button(
                        label="Download PDF",
                        data=open(pdf_path, "rb").read(),
                        key="pdf",
                        on_click=None,
                        file_name="converted_images.pdf",  # Specify the filename as "converted_images.pdf"
                        mime="application/pdf",  # Specify the file type as PDF
                    )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


# Display some note to users
st.write("Follow me on GitHub: [https://github.com/wahidpanda](https://github.com/wahidpanda)")
