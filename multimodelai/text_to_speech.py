from transformers import pipeline

tts = pipeline(
    "text-to-speech",
    model="suno/bark-small"
)

output = tts("Hello Sai Vardhan, this is a text to speech test.")

print(output.keys())
print(output["sampling_rate"])