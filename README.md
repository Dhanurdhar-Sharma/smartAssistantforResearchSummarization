# smartAssistantforResearchSummarization
**Smart Assistant for Research Summarization**
An AI-powered assistant that understands, reasons, and interacts with documents (PDF/TXT). This assistant can:
- Answer questions requiring comprehension & inference
- Generate logic-based questions
- Evaluate user responses with grounded justifications
- Provide concise document summaries

**Features**
✅ Document Upload (PDF/TXT)
✅ Ask Anything mode (context-aware question answering)
✅ Challenge Me mode (logic-based question generation + evaluation)
✅ Auto Summary (≤ 150 words)
✅ Justification from Document for every response
✅ LLM + Embedding Based Retrieval
✅ Local LLM support (e.g., Mistral via GGUF)

**Setup Instructions**
⚠️ Requirements: Python 3.10+, pip, and optionally a CUDA-compatible GPU
1.Clone the Repository
2.Install Dependencies
  pip install -r requirements.txt
3. Run the App
  python app.py, first time it take time run as it download all required models from huggingface and set them in models folder of ripo.
4.Usage
  Upload a PDF or TXT file
  Ask questions freely in Ask Anything
  Try Challenge Me to test your understanding
  View auto-generated document summary

**Project Structure**
├── app.py                  # Main entry point (Flask or Gradio app)
├── summerize.py           # Summarization logic
├── challenge.py     # QA & evaluation logic
├── quationing.py         # Mistral-powered retrieval QA
├── models/                 # Folder for downloaded or local models
│   └── All models will download here
├── requirements.txt        # Python dependencies
├── static/                 # Frontend styling assets, JS File
└── README.md   

 **Models Used**

| **Model Name**                                 | **Purpose**                                     | **Source**                              |
|------------------------------------------------|-------------------------------------------------|-----------------------------------------|
| `google/flan-t5-large`                         | Logic-based question generation + evaluation    | Hugging Face (Text2Text Generation)     |
| `deepset/roberta-base-squad2`                  | Question Answering                              | Hugging Face (QA Pipeline)              |
| `google/flan-t5-large`                         | Document summarization                          | Hugging Face (Summarization Pipeline)   |
| `sentence-transformers/all-MiniLM-L6-v2`       | Embedding documents for retrieval               | Hugging Face (FAISS Embedding)          |
| `mistral-7b-instruct-v0.2.Q2_K.gguf` (local)   | Retrieval-based QA using LangChain + Llama.cpp  | Local GGUF Model for LLM inference      |

**System Architecture**
This AI assistant follows a modular architecture with the following components:

1. Document Ingestion
- Users can upload PDF or TXT files.
- `PyMuPDF` is used to extract text from PDFs.
- Large documents are chunked using `LangChain`'s `RecursiveCharacterTextSplitter`.

2. Summarization
- As soon as a document is uploaded, a concise summary (≤ 150 words) is generated using `google/flan-t5-large`.
- The summary helps users get a quick overview of the content.

3. Interaction Modes
a. Ask Anything
- User asks any free-form question.
- The assistant uses:
  - `deepset/roberta-base-squad2` for question answering.
  - The answer is grounded in the document.
  - `SequenceMatcher` checks similarity if user input is evaluated.

b. Challenge Me
- Automatically generates 2–3 logical/comprehension-based questions using `google/flan-t5-large`.
- User answers them.
- The system compares responses to model answers and gives feedback (correct/incorrect) with justification.

4. Retrieval-Augmented QA (Advanced Mode)
- For deeper semantic reasoning, a `RetrievalQA` chain is used:
  - Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
  - Vector store: `FAISS`
  - LLM: `mistral-7b-instruct-v0.2.Q2_K.gguf` loaded using `llama-cpp-python`
- Enables local, private inference with long-context reasoning.

5. Web Application
- Built with `Flask`.
- Allows document upload, free-form QA, and challenge interactions.

---

**Reasoning Flow**

```plaintext
User Uploads PDF/TXT
        |
        v
+-----------------------+
| Extract & Chunk       |
| (LangChain + PyMuPDF) |
+-----------------------+
        |
        v
+-----------------------------+
| Auto Summary (Flan-T5)      |
+-----------------------------+
        |
        |--> Ask Anything --> Answer (RoBERTa / Mistral)
        |
        |--> Challenge Me --> QGen (Flan-T5)
                           --> Answer Eval (Similarity + Justification)



