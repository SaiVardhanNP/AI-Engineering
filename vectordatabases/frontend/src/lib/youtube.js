const VIDEO_ID_RE =
  /(?:youtube\.com\/(?:watch\?(?:.*&)?v=|shorts\/|embed\/|live\/)|youtu\.be\/)([A-Za-z0-9_-]{11})/;

export function isYoutubeUrl(raw) {
  return /(youtube\.com\/|youtu\.be\/)/i.test(String(raw || ''));
}

export function extractVideoId(raw) {
  const match = VIDEO_ID_RE.exec(String(raw || '').trim());
  return match ? match[1] : null;
}

export function formatTime(totalSeconds) {
  const s = Math.max(0, Math.round(Number(totalSeconds) || 0));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, '0')}`;
}

export function parseTimeToSeconds(label) {
  const parts = String(label).split(':').map(Number);
  if (parts.length !== 2 || parts.some(Number.isNaN)) return 0;
  const [m, s] = parts;
  return m * 60 + s;
}

export async function fetchVideoMeta(videoId) {
  try {
    const url = `https://www.youtube.com/oembed?url=${encodeURIComponent(
      `https://www.youtube.com/watch?v=${videoId}`
    )}&format=json`;
    const res = await fetch(url);
    if (!res.ok) return null;
    const data = await res.json();
    return { title: data.title, channel: data.author_name };
  } catch {
    return null;
  }
}
