# 🎬 YouTube Video Downloader
A fast and ad-free web application that allows users to download YouTube videos or extract their audio in MP3/MP4 formats. Built with Flask, Bootstrap, and integrated with FFmpeg for high-quality audio/video processing.
Download videos from YouTube, Twitter, DailyMotion, and many more platforms — all in one place. Fast, secure, and easy to use. Paste your video URL and get your content in seconds in MP4, MP3, or your preferred format. No registration required.

----

## 🚀 Features

- 🎥 Download videos in MP4 format
- 🎵 Extract audio in MP3 format
- 🔎 Fetch video preview and thumbnail
- 🌙 Light/Dark mode toggle
- 🌐 Language switch (English 🇬🇧 / French 🇫🇷)
- 📄 Transcription (when available via YouTube captions)
- 📦 Clean, mobile-friendly UI

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **Transcription**: `youtube_transcript_api`
- **Video/Audio Processing**: `yt_dlp`, FFmpeg
- **Multilingual**: English and French support via session and dictionary-based translations

---

## 📥 Installation

### Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/youtube-downloader.git
cd youtube-downloader