from pydantic import BaseModel
from google.genai import types


class RAGResponse(BaseModel):
    answer: str
    source_ids: list[str]


class RAGService:
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm_client = llm_client

    def ask(self, question, video_id, top_k=3):
        llm_result, search_results = self._run_rag(
            question,
            video_id,
            top_k,
        )

        sources = self._build_sources(
            llm_result.source_ids,
            search_results,
        )

        return {
            "answer": llm_result.answer,
            "sources": sources,
        }

    def ask_for_evaluation(self, question, video_id, top_k=3):
        llm_result, search_results = self._run_rag(
            question,
            video_id,
            top_k,
        )

        return {
            "answer": llm_result.answer,
            "contexts": [
                result["text"]
                for result in search_results
            ],
        }

    def _run_rag(self, question, video_id, top_k):
        search_results = self.retriever.search(
            question=question,
            video_id=video_id,
            final_k=top_k,
        )

        context = self._build_context(search_results)

        prompt = self._prompt_builder(
            context,
            question,
        )

        llm_result = self._llm_response(prompt)

        return llm_result, search_results

    def _build_context(self, results):
        formatted_chunks = [
            f"[Source: {result['id']}]\n"
            f"[{result['start']} - {result['end']}]\n"
            f"{result['text']}"
            for result in results
        ]

        return "\n\n".join(formatted_chunks)

    def _prompt_builder(self, context, question):
        prompt = f"""
You are answering questions about a YouTube video.

Use ONLY the provided transcript context.

If the answer cannot be found in the provided context:
- Say that the information was not found in the transcript.
- Return an empty source_ids list.

Do not use outside knowledge.

For every answer you provide:
- Select only the source IDs that directly support your answer.
- Do not include sources that are merely related.
- Use the exact source IDs provided in the context.
- Never invent source IDs.

Transcript context:
{context}

Question:
{question}
"""

        return prompt

    def _llm_response(self, prompt):
        response = self.llm_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RAGResponse,
            ),
        )

        return RAGResponse.model_validate_json(response.text)

    def _build_sources(self, source_ids, search_results):
        results_by_id = {
            result["id"]: result
            for result in search_results
        }

        return [
            {
                "start": results_by_id[source_id]["start"],
                "end": results_by_id[source_id]["end"],
            }
            for source_id in source_ids
            if source_id in results_by_id
        ]