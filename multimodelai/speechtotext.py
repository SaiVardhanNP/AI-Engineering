from transformers import pipeline

transcriber = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small"
)

result = transcriber("sai_vardhan_asr_test.wav")

print(result["text"])