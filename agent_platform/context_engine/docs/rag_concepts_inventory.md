# Advanced RAG & Graph Concepts Inventory

A comprehensive catalog of 50+ architectures, patterns, and techniques for "Industry Standard" Code RAG.

## Legend
- **Impact**: High (Critical for quality), Med (Optimization), Low (Niche).
- **Feasibility**: High (Easy to add), Med (Requires specific infra), Low (Research/Complex).
- **Status**: ✅ Implemented | 🚧 Planned | ⭕ Candidate

---

## 1. Indexing & Chunking Strategy (Data Layer)
Foundation of retrieval quality.

| # | Concept | Description | Impact | Feasibility | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **AST-Based Chunking** | Splitting code by syntax (Class, Def) vs lines. | **High** | High | 🚧 |
| 2 | **Markdown Header Splitting** | Chunking documentation by `#` headers. | **High** | High | 🚧 |
| 3 | **Parent-Child Indexing** | Index small chunks (vector) but return parent context (window). | **High** | Med | ⭕ |
| 4 | **Summary Indexing** | Index summaries of files/modules alongside raw code. | **Med** | High | ⭕ |
| 5 | **Metadata Enrichment** | Tagging chunks with `file_path`, `author`, `last_modified`. | **High** | High | ⭕ |
| 6 | **Deterministic IDs** | Hashing content to allow idempotent UPSERTS. | **High** | High | 🚧 |
| 7 | **Graph Construction** | Building explicit nodes for Classes/Functions/Imports. | **High** | High | ✅ |
| 8 | **Call Graph Verification** | Tracing function calls across files (Static Analysis). | **Med** | Med | ⭕ |
| 9 | **Import Dependency Mapping** | "Uses" edges between file nodes. | **Med** | High | ✅ |
| 10 | **Git History Indexing** | Indexing commit messages/diffs (for "why" context). | Low | Med | ⭕ |
| 11 | **Docstring Extraction** | Storing docstrings as separate semantic nodes. | **Med** | High | ✅ |
| 12 | **Zombie Pruning** | Removing vectors for deleted files. | **High** | High | 🚧 |
| 13 | **Multi-Representation Indexing** | One chunk -> 3 vectors (Code, Summary, Hypothetical Question). | **High** | Med | ⭕ |

## 2. Retrieval Patterns (The Search)
Finding the right needle in the haystack.

| # | Concept | Description | Impact | Feasibility | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 14 | **Hybrid Search** | Combining Sparse (BM25) and Dense (Vector) retrieval. | **High** | High | ✅ |
| 15 | **Semantic Reranking** | Re-scoring top-N results using a Cross-Encoder (FlashRank). | **High** | High | ✅ |
| 16 | **Context Caching** | Uploading full codebase to LLM context (Google-specific). | **High** | High | ✅ |
| 17 | **HyDE (Hypothetical Doc Embeddings)** | Generating a fake code snippet to match the query. | Med | Med | ⭕ |
| 18 | **Multi-Query Expansion** | Generating 3 variations of the user's prompt. | **High** | High | ⭕ |
| 19 | **Sub-Question Decomposition** | Breaking complex tasks into atomic searches. | **High** | Med | ⭕ |
| 20 | **Graph Traversal Retrieval** | Fetching neighbors (e.g., `Class` -> `Methods`) of a vector hit. | **High** | High | ✅ |
| 21 | **Metadata Filtering** | pre-filtering search by `file_type=.py`. | **Med** | High | ⭕ |
| 22 | **Recursive Retrieval** | Searching summaries first, then fetching detail. | **Med** | Med | ⭕ |
| 23 | **Sentence Window Retrieval** | Fetching surrounding sentences of a hit. | **Med** | High | ⭕ |
| 24 | **Small-to-Big Retrieval** | Linking specific lines to their parent File node. | **High** | Med | ⭕ |
| 25 | **Time-Weighted Retrieval** | Boosting more recent files/docs. | Low | Med | ⭕ |
| 26 | **Ensemble Retrieval** | Voting mechanism across different embedding models. | Low | Low | ⭕ |
| 27 | **Self-Querying** | LLM converting natural language to structured Metadata filters. | **Med** | Med | ⭕ |

## 3. Graph RAG (Structured Reasoning)
Leveraging the Neo4j Knowledge Graph.

| # | Concept | Description | Impact | Feasibility | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 28 | **Text2Cypher** | Converting QA to Graph Queries ("Show me dependencies of X"). | **High** | Med | ⭕ |
| 29 | **Community Detection** | Clustering related code modules (Louvain method). | **Med** | Med | ⭕ |
| 30 | **Path Finding** | "How does module A connect to module B?" queries. | **High** | Med | ⭕ |
| 31 | **Centrality Ranking** | Identifying "God Classes" or critical utilities (PageRank). | Low | Med | ⭕ |
| 32 | **Graph-Enhanced Vector Search** | Using graph connections to boost vector scores. | **High** | High | ✅ |
| 33 | **Sub-Graph Extraction** | Retrieving a fully connected component as context. | **High** | Med | ⭕ |
| 34 | **Entity Resolution** | Mapping "auth service" string to `AuthService` class node. | **High** | Med | ⭕ |

## 4. Generation & Evaluation (The Output)
Ensuring the answer is correct.

| # | Concept | Description | Impact | Feasibility | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 35 | **System 2 Attention** | Asking LLM to re-read and critique its own retrieved context. | **Med** | High | ⭕ |
| 36 | **Chain-of-Note** | Generating notes while reading documents. | Low | Med | ⭕ |
| 37 | **Corrective RAG (CRAG)** | If retrieval score is low, fallback to web search/knowledge. | **High** | Med | ⭕ |
| 38 | **Self-RAG** | LLM outputs "retrieval tokens" to self-critique relevance. | **Med** | Low | ⭕ |
| 39 | **RAG-as-a-Judge** | Using an LLM (Gemini 1.5) to grade Faithfulness/answer. | **High** | High | ✅ |
| 40 | **Contextual Precision** | Measuring if relevant chunks were at the top. | **Med** | High | ✅ |
| 41 | **Context Compaction** | Summarizing retrieved context to fit window/reduce noise. | **Med** | Med | ⭕ |
| 42 | **Citation Tracking** | Forcing LLM to cite the file/line number used. | **High** | High | ⭕ |

## 5. Agentic & Specialized (The Frontier)
Autonomy and specialized workflows.

| # | Concept | Description | Impact | Feasibility | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 43 | **Query Routing** | Decisions: "Is this a graph query or vector query?". | **High** | High | ⭕ |
| 44 | **Tool-Use RAG** | Giving the agent a "Search Tool" vs implicit retrieval. | **High** | High | ⭕ |
| 45 | **MemGPT / Long-Term Memory** | Storing user preferences/history in vector store. | **Med** | Med | ⭕ |
| 46 | **Plan-and-Execute** | "Find all references, THEN refactor" (Multi-step). | **High** | Med | ⭕ |
| 47 | **Dynamic Context Selection** | Agent choosing *which* files to load into context cache. | **High** | High | ⭕ |
| 48 | **Skeleton-of-Thought** | Generating outline first, then filling retrieval. | Low | Med | ⭕ |
| 49 | **Multi-Modal Code RAG** | Indexing UI screenshots alongside code. | Low | Low | ⭕ |
| 50 | **Draft-Verify-Refine** | Loop: Generate code -> Run Compiler -> Refine context. | **High** | Low | ⭕ |

## TOP 5 Recommendations for Immediate Implementation
Based on your stack (Gemini/Neo4j/Qdrant) and goals (Code Understanding):

1.  **AST-Based Chunking**: (#1) Essential for quality.
2.  **Query Routing**: (#43) Distinguish "list dependencies" (Graph) vs "how does this work" (Vector).
3.  **Parent-Child Indexing**: (#3) Retrieve the line, show the function.
4.  **Zombie Pruning**: (#12) Essential for hygiene.
5.  **Multi-Query Expansion**: (#18) Improves recall on vague queries.
