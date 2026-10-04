// Evidence receipts: link each sentence of a reply to the claims the evaluator
// checked and the quote from the findings that supports each one.

const STOP = new Set([
  "the", "and", "for", "with", "that", "this", "you", "your", "are", "was", "were", "has", "have",
  "had", "not", "but", "will", "been", "from", "they", "their", "its", "our", "can", "may", "any", "all",
]);

const MIN_COVERAGE = 0.6;

const DASHES = /[‐-—]/g;

export function normalize(text) {
  return (text ?? "")
    .replace(DASHES, "-")
    .replace(/[  ]/g, " ")
    .replace(/[‘’]/g, "'")
    .replace(/[*`|]/g, "")
    .replace(/^[ \t]*(?:[-•]|#{1,6}|\d+\.)[ \t]+/gm, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function words(text) {
  return normalize(text)
    .replace(/[^a-z0-9$.]+/g, " ")
    .split(" ")
    .map((w) => w.replace(/\.+$/, ""))
    .filter((w) => w.length >= 3 && !STOP.has(w));
}

// Split on sentence ends followed by a capital, so "$25.00 USD" stays in one
// piece. Each sentence remembers the whitespace that followed it, so paragraph
// breaks survive when the reply is shown again.
export function splitSentences(text) {
  const source = text ?? "";
  const pieces = [];
  let start = 0;

  for (const match of source.matchAll(/(?<=[.!?])(\s+)(?=[A-Z"'(])/g)) {
    pieces.push({ text: source.slice(start, match.index).trim(), after: match[1] });
    start = match.index + match[1].length;
  }
  pieces.push({ text: source.slice(start).trim(), after: "" });

  return pieces.filter((piece) => piece.text);
}

function coverage(claim, sentenceWords) {
  const claimWords = words(claim.statement);
  if (claimWords.length === 0) return 0;
  return claimWords.filter((w) => sentenceWords.has(w)).length / claimWords.length;
}

// "exact" when the quote appears word for word in the findings, "approximate"
// when it was stitched together or paraphrased, "missing" when there is none.
export function quoteStatus(claim, findings) {
  const quote = normalize(claim.supporting_quote);
  if (!quote) return "missing";
  return normalize(findings).includes(quote) ? "exact" : "approximate";
}

export function matchClaims(reply, claims, findings = "") {
  const sentences = splitSentences(reply);
  const withStatus = (claim) => ({ ...claim, quote_status: quoteStatus(claim, findings) });
  const used = new Set();

  const matched = sentences.map(({ text, after }) => {
    const sentenceWords = new Set(words(text));
    const receipts = [];

    claims.forEach((claim, index) => {
      if (coverage(claim, sentenceWords) >= MIN_COVERAGE) {
        receipts.push(withStatus(claim));
        used.add(index);
      }
    });

    return { text, after, receipts };
  });

  return {
    sentences: matched,
    unattached: claims.filter((_, index) => !used.has(index)).map(withStatus),
  };
}

// The findings are stored as "## BILLING FINDINGS\n...\n\n## TECHNICAL FINDINGS\n...".
export function parseFindings(findings) {
  if (!findings) return [];

  return findings
    .split(/^## /m)
    .map((chunk) => chunk.trim())
    .filter(Boolean)
    .map((chunk) => {
      const newline = chunk.indexOf("\n");
      const heading = newline === -1 ? chunk : chunk.slice(0, newline);
      return {
        name: heading.replace(/\s*findings\s*$/i, "").trim().toLowerCase(),
        text: newline === -1 ? "" : chunk.slice(newline + 1).trim(),
      };
    });
}

export function timeAgo(iso, now = Date.now()) {
  const seconds = Math.max(0, Math.round((now - new Date(iso).getTime()) / 1000));
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.round(seconds / 60)} min ago`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)} h ago`;
  return `${Math.round(seconds / 86400)} d ago`;
}
