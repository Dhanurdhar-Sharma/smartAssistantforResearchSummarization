import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import LlamaCpp
from langchain.chains import RetrievalQA

# === Static Paths ===
LLM_FILENAME = "mistral-7b-instruct-v0.2.Q2_K.gguf"
LLM_PATH = os.path.join("models", LLM_FILENAME)
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# === Check if LLM exists ===
if not os.path.exists(LLM_PATH):
    raise FileNotFoundError(
        f"❌ LLM model file not found at {LLM_PATH}. Please place the GGUF file in the models/ folder."
    )

# === Load Models ===
print("🔹 Loading embedding model...")
embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

print("🧠 Loading LLM from:", LLM_PATH)
llm = LlamaCpp(
    model_path=LLM_PATH,
    temperature=0.3,
    max_tokens=512,
    n_ctx=4096,
    verbose=False
)

# === Main QA Function ===
def answer_question_from_pdf(pdf_path, question):
    if not os.path.exists(pdf_path):
        return {"error": "File does not exist."}

    try:
        # Step 1: Load PDF
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            return {"error": "No text found in PDF."}

        # Step 2: Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(documents)

        # Step 3: Embed + Vector Store
        vectorstore = FAISS.from_documents(chunks, embedding_model)

        # Step 4: RetrievalQA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
            return_source_documents=True
        )

        # Step 5: Run Query
        result = qa_chain({"query": question})
        source = result['source_documents'][0].page_content[:500] + "..." if result.get('source_documents') else "No source found."

        return {
            "question": question,
            "answer": result["result"],
            "source": source
        }

    except Exception as e:
        print("❌ QA Error:", e)
        return {"error": f"Failed to process the question: {str(e)}"}
