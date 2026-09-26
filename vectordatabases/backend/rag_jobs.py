from rag_dependencies import rag_service


def run_rag_job(
    question: str,
    video_id: str,
    top_k: int,
):
    return rag_service.ask(
        question=question,
        video_id=video_id,
        top_k=top_k,
    )