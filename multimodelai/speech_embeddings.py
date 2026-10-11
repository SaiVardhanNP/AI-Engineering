import torch
import librosa
import torch.nn.functional as F

from transformers import Wav2Vec2FeatureExtractor, WavLMModel


model_id = "microsoft/wavlm-base-plus"

processor = Wav2Vec2FeatureExtractor.from_pretrained(model_id)
model = WavLMModel.from_pretrained(model_id)

model.eval()

def get_embedding(audio_path):
    audio,sample_rate= librosa.load(audio_path,sr=16000)
    inputs= processor(audio,sampling_rate=sample_rate,return_tensors="pt")
    with torch.no_grad():
        outputs= model(**inputs)
    
    embedding= outputs.last_hidden_state.mean(dim=1)
    embedding= F.normalize(embedding,p=2, dim=1)
    
    return embedding

embedding_1 = get_embedding("sai_vardhan_asr_test.wav")
embedding_2 = get_embedding("sai_vardhan_asr_test_2.wav")

similarity = F.cosine_similarity(embedding_1, embedding_2)

print("Similarity:", similarity.item())