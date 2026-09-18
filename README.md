# 📄 Local Document Chat — Offline RAG System

A fully offline document chatbot powered by a local LLM (Llama 3.2 3B). Query your PDFs, Word docs, Excel sheets, and text files — no cloud API, no internet required.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

- 🔒 100% offline — no API keys, nothing leaves your machine
- 📁 Supports PDF, DOCX, TXT, XLSX
- ⚡ Auto-reindexes when files change
- 🤖 Local LLM (Llama 3.2 3B, CPU-optimized)
- 💬 Simple Tkinter chat interface

**Tested on:** AMD Ryzen 5 PRO 4650U, 16GB RAM, no GPU — query response ~3–12s, indexing ~5s/doc.

---

## Tech Stack

LangChain · ChromaDB (vector store) · Llama 3.2 3B Instruct (GGUF, quantized) · all-MiniLM-L6-v2 embeddings · Tkinter GUI

---

## Quick Start

```bash
git clone https://github.com/shahriar151/local-doc-chat.git
cd local-doc-chat
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python setup.py     # downloads the model, ~2GB
python app.py
```

Drop documents into `watched_folder/`, click **Re-Index**, and start asking questions.

---

## Known Limitations

- Context window limited to ~2048 tokens; long documents get chunked
- Small model can occasionally mix items when documents contain multiple similar lists
- CPU-only inference, so response time scales with document/query complexity

---

## Why I Built This

A self-study project to understand Retrieval-Augmented Generation (RAG), vector databases, and running language models locally on consumer hardware without a GPU.

---

## Author

**Shahriar Mahmood** — Physics graduate, working with Python and computational tools; explores AI/ML methods as part of self-study.

---

## License

MIT — see [LICENSE](LICENSE)
