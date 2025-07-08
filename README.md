# smartAssistantforResearchSummarization
**Smart Assistant for Research Summarization**<br>
An AI-powered assistant that understands, reasons, and interacts with documents (PDF/TXT). This assistant can:<br>
- Answer questions requiring comprehension & inference<br>
- Generate logic-based questions<br>
- Evaluate user responses with grounded justifications<br>
- Provide concise document summaries<br>

**Features**<br>
✅ Document Upload (PDF/TXT)<br>
✅ Ask Anything mode (context-aware question answering)<br>
✅ Challenge Me mode (logic-based question generation + evaluation)<br>
✅ Auto Summary (≤ 150 words)<br>
✅ Justification from Document for every response<br>
✅ LLM + Embedding Based Retrieval<br>
✅ Local LLM support (e.g., Mistral via GGUF)<br>

**Setup Instructions**<br>
⚠️ Requirements: Python 3.10+, pip, and optionally a CUDA-compatible GPU<br>
1.Clone the Repository<br>
2.Install Dependencies<br>
  pip install -r requirements.txt<br>
3. Run the App <br>
  python app.py, first time it take time run as it download all required models from huggingface and set them in models folder of ripo.<br>
4.Usage<br>
  Upload a PDF or TXT file<br>
  Ask questions freely in Ask Anything<br>
  Try Challenge Me to test your understanding<br>
  View auto-generated document summary<br>

**Project Structure**<br>
.
├── app.py                   # Main entry point (Flask or Gradio app) <br>
├── summerizer.py           # Summarization logic<br>
├── challenge.py     # QA & evaluation logic
├── quationing.py         # Mistral-powered retrieval QA<br>
├── models/                 # Folder for downloaded or local models<br>
│   └── All models download here<br>
├── requirements.txt        # Python dependencies<br>
├── static/                 # (optional) Frontend styling assets<br>
└── README.md               # You're reading this!<br>


 **Models Used**<br>

| **Model Name**                                 | **Purpose**                                     | **Source**                              |<br>
|------------------------------------------------|-------------------------------------------------|-----------------------------------------|<br>
| `google/flan-t5-large`                         | Logic-based question generation + evaluation    | Hugging Face (Text2Text Generation)     |<br>
| `deepset/roberta-base-squad2`                  | Question Answering                              | Hugging Face (QA Pipeline)              |<br>
| `google/flan-t5-large`                         | Document summarization                          | Hugging Face (Summarization Pipeline)   |<br>
| `sentence-transformers/all-MiniLM-L6-v2`       | Embedding documents for retrieval               | Hugging Face (FAISS Embedding)          |<br>
| `mistral-7b-instruct-v0.2.Q2_K.gguf` (local)   | Retrieval-based QA using LangChain + Llama.cpp  | Local GGUF Model for LLM inference      |<br>

**System Architecture**<br>
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



