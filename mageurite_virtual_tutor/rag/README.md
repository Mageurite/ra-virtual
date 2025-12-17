# 📚 RAG part of TutorNet
The Retrieval-Augmented Generation (RAG) in TutorNet supporting both **pure-text** and **multimodal** retrieval modes, with personal and public knowledge base integration.
Currently, the RAG module supports both pure-text and multimodal scenarios; however, the multimodal functionality has not yet been integrated into the overall system due to GPU limitations.
Therefore, default mode is **pure-text** mode.

## 📌 Technical Framework
- **Backend Framework:** Flask (HTTP API)  
- **Database Storage:** Milvus  
- **Programming Language:** Python 3  
- **Deep Learning Framework:** PyTorch  
- **Embedding Frameworks:** SentenceTransformers, ColPali Engine  

---

## ⚙️ Running Port & Performance Requirements
- **Default Port:** `0.0.0.0:9090`  
- **GPU:** NVIDIA GPU (≥ 7GB recommended), CUDA 11.3+  
- **Python:** 3.10+  

---

## 🛠 Configuration
All configuration settings are located in `config.py`:
> ⚠️ **Please set `MODE` to your desired RAG mode and update file paths/addresses to match your environment.**

| Parameter         | Default Value     | Description |
|-------------------|------------------|-------------|
| `MODE`            | `0`              | RAG mode: `0` = pure-text scenario; `1` = multimodal scenario |
| `EMBEDDED_DB_PATH`| `./kb_test.db`    | Path to save the embedded Milvus database file |
| `CHUNK_EMBED_DIM` | `384`             | Embedding dimension for text chunks |
| `PAGE_EMBED_DIM`  | `128`             | Embedding dimension for page-level (image) embeddings |
| `IMG_DIR`         | `./imgs`          | Directory to store images generated from PDF files |

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone <the-repo-url>
cd rag

# 2. Create and activate conda environment
conda create -n rag python=3.12
conda activate rag

# 3. Install poppler (for PDF to image conversion)
conda install -c conda-forge poppler

# 4. Install Python dependencies
pip install -r requirements.txt

```
---
## ▶️ Run
```bash
# 1. Configure settings in config.py 
#    - Set MODE to desired mode (0 = pure-text, 1 = multimodal). 
#      - mode = 0 is integrated to the whole tutornet;mode=1 is implemented the RAG only
#    - Update file paths and addresses to match your environment

# 2. Start the service
python app.py
```

## 📌 Test
```bash
# 1. Navigate to the test folder
cd rag/tests
conda activate rag
# 2. Edit conftest.py
#    - Please check TEST_DIR match your local environment

# 3. Run all tests
pytest -v test_mode0.py # test pure-text rag functions
pytest -v test_mode1.py # test multimodal rag functions
```