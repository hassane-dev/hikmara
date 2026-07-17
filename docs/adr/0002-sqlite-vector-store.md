# ADR 0002: SQLite-Backed Vector Store with Cosine-Similarity

## Status
Accepted

## Context
An offline-first AI agent platform requires a robust long-term vector memory to perform retrieval-augmented generation (RAG) and maintain contextual awareness. Traditional vector databases (such as Pinecone, Qdrant, Milvus) either run in the cloud or introduce complex local Docker/server setups.

For a lightweight desktop application, introducing heavy server-side database containers contradicts our ease-of-use and low resource overhead principles.

## Decision
We decide to implement and use a **SQLite-backed Vector Store** using native relational structures paired with a lightweight mathematical array library (`numpy`) to execute **Cosine-Similarity calculations**.

- Vector coordinates are serialized and stored inside localized SQLite database tables.
- Query lookups calculate vector distances on the fly using standard cosine similarity formulas powered by NumPy.
- Long-term contextual statements are cataloged and retrieved directly on-device without running heavy daemon processes.

## Consequences
- **Pros**:
  - Extremely lightweight. No background daemon or Docker requirements.
  - High portability: the entire memory database is contained within a single `.db` file (such as `database/hikmara.db`).
  - Seamless transactional reliability inherited from SQLite.
- **Cons**:
  - Linear scan cosine-similarity calculations may degrade in performance with millions of active vectors, though perfectly optimized for standard agent workspace sizes (thousands of documents).
