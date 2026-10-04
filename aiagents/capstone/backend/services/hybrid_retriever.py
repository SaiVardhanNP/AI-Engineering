class HybridRetriever:
    def __init__(
        self,
        embedding_service,
        pinecone_repository,
        bm25_repository,
        rrf_fusion,
        reranker,
        mmr,
        query_rewriter,
    ):
        self.embedding_service = embedding_service
        self.pinecone_repository = pinecone_repository
        self.bm25_repository = bm25_repository
        self.rrf_fusion = rrf_fusion
        self.reranker = reranker
        self.mmr = mmr
        self.query_rewriter = query_rewriter

    def search(
        self,
        question,
        kb_id,
        candidate_k=20,
        final_k=3,
    ):
        # 1. Analyze whether the query should be rewritten
        decision = self.query_rewriter.rewrite(question)

        # 2. Always generate embedding for the original question
        original_embedding = self.embedding_service.embed_query(question)

        # 3. Load BM25 retriever
        bm25_retriever = self.bm25_repository.get(kb_id)

        if bm25_retriever is None:
            raise ValueError(f"Knowledge base '{kb_id}' has not been ingested")

        result_lists = []

        # 4. Original query -> Vector search
        result_lists.append(
            self.pinecone_repository.search(
                original_embedding,
                kb_id,
                top_k=candidate_k,
            )
        )

        # 5. Original query -> BM25
        result_lists.append(
            bm25_retriever.search(
                question,
                top_k=candidate_k,
            )
        )

        # 6. Optional rewritten-query retrieval
        if decision.should_rewrite:
            rewritten_query = decision.rewritten_query

            rewritten_embedding = self.embedding_service.embed_query(rewritten_query)

            result_lists.append(
                self.pinecone_repository.search(
                    rewritten_embedding,
                    kb_id,
                    top_k=candidate_k,
                )
            )

            result_lists.append(
                bm25_retriever.search(
                    rewritten_query,
                    top_k=candidate_k,
                )
            )

        # 7. Fuse all retrieval results
        rrf_results = self.rrf_fusion.fuse(
            result_lists,
            top_k=candidate_k,
        )

        # 8. Rerank using ORIGINAL user question
        reranked_results = self.reranker.rerank(
            question,
            rrf_results,
            top_k=10,
        )

        # 9. Fetch embeddings for reranked candidates
        result_ids = [result["id"] for result in reranked_results]

        embeddings_by_id = self.pinecone_repository.fetch_embeddings(
            result_ids,
            kb_id,
        )

        # 10. Attach embeddings required by MMR
        for result in reranked_results:
            result["_embedding"] = embeddings_by_id[result["id"]]

        # 11. MMR using original query embedding
        return self.mmr.select(
            original_embedding,
            reranked_results,
            top_k=final_k,
        )
