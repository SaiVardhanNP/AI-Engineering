from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig, WebshareProxyConfig
import re

from config import settings


def _build_proxy_config():
    if settings.webshare_proxy_username and settings.webshare_proxy_password:
        return WebshareProxyConfig(
            proxy_username=settings.webshare_proxy_username,
            proxy_password=settings.webshare_proxy_password,
        )
    if settings.transcript_proxy_url:
        return GenericProxyConfig(
            http_url=settings.transcript_proxy_url,
            https_url=settings.transcript_proxy_url,
        )
    return None


class TranscriptService:
    def __init__(self):
        self.transcriber = YouTubeTranscriptApi(proxy_config=_build_proxy_config())

    def fetch(self, video_id):
        return self.transcriber.fetch(video_id)

    def clean(self, raw_transcript):
        cleaned_segments = []

        for snippet in raw_transcript:
            text = snippet.text

            text = text.strip()
            text = re.sub(r"\s+", " ", text)

            if not text:
                continue

            cleaned_segment = {
                "text": text,
                "start": snippet.start,
                "end": round(snippet.start + snippet.duration, 3),
            }

            cleaned_segments.append(cleaned_segment)

        return cleaned_segments

    def chunk(self, segments, chunk_size=80, overlap=20):
        chunks = []
        current_segments = []
        current_word_count = 0

        for segment in segments:
            segment_word_count = len(segment["text"].split())

            current_segments.append(segment)
            current_word_count += segment_word_count

            if current_word_count >= chunk_size:
                chunk = {
                    "text": " ".join(
                        s["text"] for s in current_segments
                    ),
                    "start": current_segments[0]["start"],
                    "end": current_segments[-1]["end"],
                }

                chunks.append(chunk)

                # Build the overlapping window from the tail
                overlap_segments = []
                overlap_word_count = 0

                for seg in reversed(current_segments):
                    overlap_segments.insert(0, seg)
                    overlap_word_count += len(seg["text"].split())

                    if overlap_word_count >= overlap:
                        break

                current_segments = overlap_segments
                current_word_count = overlap_word_count

        # Only create a tail chunk if there is new text beyond the overlap
        if current_segments and current_word_count > overlap:
            chunks.append(
                {
                    "text": " ".join(
                        s["text"] for s in current_segments
                    ),
                    "start": current_segments[0]["start"],
                    "end": current_segments[-1]["end"],
                }
            )

        return chunks
    
    def get_video_id(self, url):
        return url.split("v=")[-1].split("&")[0]