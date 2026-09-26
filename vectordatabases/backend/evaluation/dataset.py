# evaluation/dataset.py

EVALUATION_DATASET = [

    # ---------------------------------------------------------
    # Directly answerable
    # ---------------------------------------------------------

    {
        "question": "Who proposed the Turing Test?",
        "reference": "Alan Turing proposed the Turing Test in 1950.",
    },

    {
        "question": "Who did IBM Deep Blue defeat in 1997?",
        "reference": "IBM Deep Blue defeated Garry Kasparov in 1997.",
    },

    # ---------------------------------------------------------
    # Multi-context / synthesis
    # ---------------------------------------------------------

    {
        "question": "How did expert systems differ from later machine learning?",
        "reference": (
            "Expert systems relied on explicitly programmed rules and "
            "constraints and were often brittle, while machine learning "
            "learned patterns from examples at larger scale."
        ),
    },

    {
        "question": (
            "Why was Watson's Jeopardy achievement considered more "
            "difficult than Deep Blue's chess victory?"
        ),
        "reference": (
            "Jeopardy required Watson to handle natural language, including "
            "puns, idioms, figures of speech, broad subject matter, and "
            "quickly produce answers, whereas chess had a more constrained "
            "and structured problem space."
        ),
    },

    # ---------------------------------------------------------
    # Ambiguous / likely rewrite candidate
    # ---------------------------------------------------------

    {
        "question": "What was that computer that beat the chess champion?",
        "reference": (
            "IBM Deep Blue defeated Garry Kasparov in a chess match."
        ),
    },

    # ---------------------------------------------------------
    # Unanswerable
    # ---------------------------------------------------------

    {
        "question": "What programming language was used to build IBM Watson?",
        "reference": None,
    },
]