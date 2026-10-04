class SupportRAG:

    def retrieve(self, query: str) -> list[str]:

        knowledge = {
            "refund": [
                "Customers can request a refund within 30 days."
            ],
            "password": [
                "Customers can reset their password from account settings."
            ],
            "shipping": [
                "Standard shipping takes 5-7 business days."
            ],
        }

        query = query.lower()

        results = []

        for keyword, docs in knowledge.items():
            if keyword in query:
                results.extend(docs)

        return results