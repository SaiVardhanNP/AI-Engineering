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
        video_id,
        candidate_k=20,
        final_k=3,
    ):
        # 1. Analyze whether the query should be rewritten
        decision = self.query_rewriter.rewrite(question)

        # 2. Always generate embedding for the original question
        original_embedding = self.embedding_service.embed_query(question)

        # 3. Load BM25 retriever
        bm25_retriever = self.bm25_repository.get(video_id)

        result_lists = []

        # 4. Original query → Vector search
        original_vector_results = self.pinecone_repository.search(
            original_embedding,
            video_id,
            top_k=candidate_k,
        )

        result_lists.append(original_vector_results)

        # 5. Original query → BM25
        original_bm25_results = bm25_retriever.search(
            question,
            top_k=candidate_k,
        )

        result_lists.append(original_bm25_results)

        # 6. Optional rewritten-query retrieval
        rewritten_query = None
        rewritten_embedding = None

        if decision.should_rewrite:
            rewritten_query = decision.rewritten_query

            rewritten_embedding = self.embedding_service.embed_query(rewritten_query)

            # Rewritten query → Vector search
            rewritten_vector_results = self.pinecone_repository.search(
                rewritten_embedding,
                video_id,
                top_k=candidate_k,
            )

            result_lists.append(rewritten_vector_results)

            # Rewritten query → BM25
            rewritten_bm25_results = bm25_retriever.search(
                rewritten_query,
                top_k=candidate_k,
            )

            result_lists.append(rewritten_bm25_results)

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
            video_id,
        )

        # 10. Attach embeddings required by MMR
        for result in reranked_results:
            result["_embedding"] = embeddings_by_id[result["id"]]

        # 11. MMR using original query embedding
        final_results = self.mmr.select(
            original_embedding,
            reranked_results,
            top_k=final_k,
        )

        return final_results

    def debug_search(
        self,
        question,
        video_id,
        candidate_k=20,
        final_k=3,
    ):
        # 1. Analyze whether the query should be rewritten
        decision = self.query_rewriter.rewrite(question)

        rewritten_query = None

        print("\n========== QUERY REWRITE ==========")
        print("Original:", question)
        print("Should rewrite:", decision.should_rewrite)

        if decision.should_rewrite:
            rewritten_query = decision.rewritten_query
            print("Rewritten:", rewritten_query)
        else:
            print("Rewritten: None")

        # 2. Generate embedding for original query
        original_embedding = self.embedding_service.embed_query(question)

        # 3. Load BM25 retriever
        bm25_retriever = self.bm25_repository.get(video_id)

        # 4. Original → Vector
        original_vector_results = self.pinecone_repository.search(
            original_embedding,
            video_id,
            top_k=candidate_k,
        )

        # 5. Original → BM25
        original_bm25_results = bm25_retriever.search(
            question,
            top_k=candidate_k,
        )

        result_lists = [
            original_vector_results,
            original_bm25_results,
        ]

        # Defaults for debug output
        rewritten_vector_results = []
        rewritten_bm25_results = []

        # 6. Optional rewritten-query retrieval
        rewritten_embedding = None

        if decision.should_rewrite:
            rewritten_embedding = self.embedding_service.embed_query(rewritten_query)

            # Rewritten → Vector
            rewritten_vector_results = self.pinecone_repository.search(
                rewritten_embedding,
                video_id,
                top_k=candidate_k,
            )

            # Rewritten → BM25
            rewritten_bm25_results = bm25_retriever.search(
                rewritten_query,
                top_k=candidate_k,
            )

            result_lists.extend(
                [
                    rewritten_vector_results,
                    rewritten_bm25_results,
                ]
            )

        # 7. RRF
        rrf_results = self.rrf_fusion.fuse(
            result_lists,
            top_k=candidate_k,
        )

        # 8. Reranker uses ORIGINAL question
        reranked_results = self.reranker.rerank(
            question,
            rrf_results,
            top_k=10,
        )

        # 9. Fetch embeddings
        result_ids = [result["id"] for result in reranked_results]

        embeddings_by_id = self.pinecone_repository.fetch_embeddings(
            result_ids,
            video_id,
        )

        # 10. Attach embeddings
        for result in reranked_results:
            result["_embedding"] = embeddings_by_id[result["id"]]

        # 11. MMR uses ORIGINAL query embedding
        final_results = self.mmr.select(
            original_embedding,
            reranked_results,
            top_k=final_k,
        )

        return {
            "original_query": question,
            "should_rewrite": decision.should_rewrite,
            "rewritten_query": rewritten_query,
            "original_vector": original_vector_results,
            "original_bm25": original_bm25_results,
            "rewritten_vector": rewritten_vector_results,
            "rewritten_bm25": rewritten_bm25_results,
            "rrf": rrf_results,
            "reranked": reranked_results,
            "mmr": final_results,
        }
