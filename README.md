# Project: Huginn

> The intelligent backend for Muninn — processes, organizes, and retrieves your
> notes with NLP, embeddings, and LLM-powered insights.

---

## Vision

Huginn is the **processing and retrieval layer** of your personal knowledge
system. While Muninn captures raw notes, Huginn transforms them into a
structured, searchable, and intelligent knowledge base.

Think of Huginn as your **mind** — it organizes, connects, and reflects on what
Muninn captures.

---

## Features (Planned)

- **Storage & API**
  - Centralized note database (SQLite/Postgres)
  - REST/GraphQL API for Muninn clients
  - Attachment handling

- **Processing**
  - Auto-categorization (rule-based + NLP)
  - Semantic similarity linking (`[[links]]`)
  - Fuzzy + semantic search across all notes

- **LLM Capabilities**
  - Smart categorization & tagging
  - Summarization & weekly digests
  - Semantic Q&A (chat with your notes via RAG)
  - Note linking & relationship discovery
  - Knowledge expansion (turn short notes into detailed ideas)

- **Sync**
  - Multi-device sync via FastAPI server
  - Git-based backup option

---

## Tech Stack

- **Language**: Python (FastAPI)
- **Storage**: SQLite/Postgres
- **NLP**: sentence-transformers, scikit-learn
- **LLM**: OpenAI API (or local models)
- **Search**: FAISS (semantic), rapidfuzz (fuzzy)
- **Sync**: REST API for Muninn clients

---

## Roadmap

### Phase 1
- [ ] REST API for note ingestion from Muninn
- [ ] Centralized database for notes + metadata
- [ ] Basic fuzzy search

### Phase 2
- [ ] Embedding generation for notes
- [ ] Semantic search (FAISS)
- [ ] Auto-categorization (rule-based + NLP)

### Phase 3
- [ ] Auto-linking of related notes (`[[NoteID]]`)
- [ ] Export to Markdown with links
- [ ] Weekly digest / resurfacing old notes

### Phase 4
- [ ] LLM-powered features:
- [ ] Categorization & tagging
- [ ] Summarization
- [ ] Semantic Q&A
- [ ] Knowledge expansion

### Phase 5
- [ ] Multi-device sync
- [ ] Optional graph visualization (perhaps some heatmap)

---

## Relationship to Muninn

Muninn = **capture client**  
Huginn = **processing + intelligence server**

