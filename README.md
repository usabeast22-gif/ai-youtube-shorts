# AI YouTube Shorts Maker

A simple web app that:
1. Takes a YouTube URL
2. Downloads the video
3. Transcribes speech with Whisper
4. Finds potentially interesting moments
5. Creates 9:16 vertical Shorts
6. Provides separate download buttons

## Free/easy run options

### Streamlit Community Cloud
Upload these files to a GitHub repository:
- app.py
- requirements.txt
- packages.txt

Then deploy the repository as a Streamlit app.

### Local computer
Install FFmpeg, then:
pip install -r requirements.txt
streamlit run app.py

## Important
Use only videos you own or have permission to download/edit. This app does not bypass DRM or private content.

## Current version
This is a lightweight automatic clip finder. It is not a full semantic video editor yet: clip selection is based mainly on transcript signals/keywords.
