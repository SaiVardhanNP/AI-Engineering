import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

function unwrapError(err) {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return new Error(detail);
  if (err?.request && !err?.response) {
    return new Error("Couldn't reach the backend. Is the API running?");
  }
  return new Error(err?.message || 'Request failed');
}

export async function ingestVideo(videoId) {
  try {
    const { data } = await client.post('/ingest', { video_id: videoId });
    return data;
  } catch (err) {
    throw unwrapError(err);
  }
}

export async function askQuestion(videoId, question, topK = 3) {
  try {
    const { data } = await client.post('/query', {
      video_id: videoId,
      question,
      top_k: topK,
    });
    return data;
  } catch (err) {
    throw unwrapError(err);
  }
}
