from google.genai import errors as genai_errors
from youtube_transcript_api._errors import (
    AgeRestricted,
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)


def to_user_message(exc: Exception) -> tuple[int, str]:
    """Maps a backend exception to a (status_code, short human message) pair
    safe to send to the frontend, instead of relaying a raw SDK error dump."""

    if isinstance(exc, genai_errors.APIError):
        if exc.code == 429:
            return 429, "The AI model hit its usage limit. Try again in a bit."
        return 502, "The AI model returned an error. Try again in a moment."

    if isinstance(exc, RequestBlocked):
        return (
            503,
            "YouTube is blocking transcript requests from this network right now. "
            "Try again later, switch networks, or configure a proxy.",
        )
    if isinstance(exc, TranscriptsDisabled):
        return 422, "This video doesn't have captions available."
    if isinstance(exc, NoTranscriptFound):
        return 422, "No transcript could be found for this video."
    if isinstance(exc, AgeRestricted):
        return 422, "This video is age-restricted, so its transcript can't be fetched."
    if isinstance(exc, VideoUnavailable):
        return 422, "This video is unavailable (private, deleted, or region-locked)."
    if isinstance(exc, CouldNotRetrieveTranscript):
        return 422, "Couldn't fetch this video's transcript."

    return 500, "Something went wrong. Please try again."
