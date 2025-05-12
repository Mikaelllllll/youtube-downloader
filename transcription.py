# transcription.py
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcription(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = ' '.join([entry['text'] for entry in transcript])

        return full_text
    except Exception as e:
        return f"An error occurred: {e}"

