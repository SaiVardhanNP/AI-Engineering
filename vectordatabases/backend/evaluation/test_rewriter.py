from services.query_rewriter import QueryRewriter


rewriter = QueryRewriter()

questions = [
    "Who proposed the Turing Test?",
    "Who did IBM Deep Blue defeat in 1997?",
    "What was that computer that beat the chess champion?",
    "How did expert systems differ from later machine learning?",
    "Why was Watson's achievement more difficult?",
]


for question in questions:
    result = rewriter.rewrite(question)

    print("\nQuestion:", question)
    print("Should rewrite:", result.should_rewrite)
    print("Rewritten:", result.rewritten_query)
