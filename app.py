import os
import subprocess
import streamlit as st
from yt_dlp import YoutubeDL
from faster_whisper import WhisperModel

VIDEO_DIR = "downloads"
SHORT_DIR = "shorts"
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(SHORT_DIR, exist_ok=True)

st.set_page_config(page_title="AI YouTube Shorts Maker", page_icon="🎬")
st.title("🎬 AI YouTube → Shorts")
st.caption("Paste a YouTube URL and create multiple vertical clips.")

url = st.text_input("YouTube URL")
duration = st.slider("Short length (seconds)", 20, 60, 45)
count = st.slider("Number of Shorts", 1, 10, 3)

@st.cache_resource
def load_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

def download_video(url):
    path = os.path.join(VIDEO_DIR, "source.%(ext)s")
    opts = {
        "format": "best[height<=720]/best",
        "outtmpl": path,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded = ydl.prepare_filename(info)
    if not os.path.exists(downloaded):
        mp4 = os.path.splitext(downloaded)[0] + ".mp4"
        if os.path.exists(mp4):
            downloaded = mp4
    return downloaded

def transcribe(video):
    model = load_model()
    segments, _ = model.transcribe(video, vad_filter=True)
    return [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segments if s.text.strip()]

def find_highlights(segments, clip_len, n):
    keywords = [
        "important","secret","amazing","best","worst","why","how",
        "never","always","mistake","truth","problem","tip","fact",
        "actually","remember","because"
    ]
    scored = []
    for i, s in enumerate(segments):
        t = s["text"].lower()
        score = sum(2 for k in keywords if k in t)
        score += 2 if len(t.split()) >= 12 else 0
        score += 2 if "?" in t else 0
        scored.append((score, i))
    scored.sort(reverse=True)

    selected = []
    for _, i in scored:
        start = max(0, segments[i]["start"] - 6)
        if any(abs(start - old) < clip_len * 0.65 for old in selected):
            continue
        selected.append(start)
        if len(selected) == n:
            break
    return sorted(selected)

def make_short(video, start, clip_len, number):
    out = os.path.join(SHORT_DIR, f"short_{number}.mp4")
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920"
    )
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", video,
        "-t", str(clip_len), "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", out
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out

if st.button("🚀 Generate Shorts", type="primary"):
    if not url.strip():
        st.error("YouTube URL paste karo.")
        st.stop()

    try:
        with st.spinner("📥 Video download ho raha hai..."):
            video = download_video(url)

        with st.spinner("🧠 Video analyze ho raha hai..."):
            segments = transcribe(video)

        if not segments:
            st.error("Speech detect nahi hui.")
            st.stop()

        starts = find_highlights(segments, duration, count)
        if not starts:
            st.error("Suitable clips nahi mile.")
            st.stop()

        progress = st.progress(0)
        outputs = []

        for i, start in enumerate(starts, 1):
            with st.spinner(f"🎬 Short {i} ban raha hai..."):
                out = make_short(video, start, duration, i)
                outputs.append(out)
            progress.progress(i / len(starts))

        st.success(f"✅ {len(outputs)} Shorts ready!")

        for i, out in enumerate(outputs, 1):
            st.video(out)
            with open(out, "rb") as f:
                st.download_button(
                    f"⬇️ Download Short {i}",
                    f.read(),
                    file_name=f"short_{i}.mp4",
                    mime="video/mp4",
                    key=f"download_{i}"
                )

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Tip: YouTube video par download/edit karne ka right hona chahiye.")
