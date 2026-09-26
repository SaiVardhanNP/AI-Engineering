from geminiClient import client
from models.query_rewrite import QueryRewriteDecision


class QueryRewriter:
    def rewrite(self, question: str) -> QueryRewriteDecision:
        prompt = f"""
You are a query analysis component for a RAG system.

Determine whether the user's question would benefit from
retrieval-oriented query rewriting.

Rules:
- Preserve the user's original intent.
- Rewrite only when rewriting is likely to improve retrieval.
- Extract important entities, concepts, names, dates, and terminology.
- Make implicit retrieval intent more explicit when possible.
- Do not answer the question.
- Do not add factual claims that are not explicitly present
  or directly implied by the user's question.
- Prefer extracting and reorganizing existing concepts over
  adding domain knowledge.
- If rewriting is unnecessary, rewritten_query must be null.
- If rewriting is necessary, provide a concise retrieval-optimized query.

User question:
{question}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": QueryRewriteDecision,
            },
        )

        return response.parsed
