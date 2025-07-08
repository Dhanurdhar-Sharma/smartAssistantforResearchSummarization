from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import fitz  # PyMuPDF
import torch
import os

# === DEVICE SETUP ===
device = 0 if torch.cuda.is_available() else -1
print("✅ Device set to:", "cuda" if device == 0 else "cpu")

# === MODEL DOWNLOAD & CACHING ===
model_name = "google/flan-t5-large"  # or your preferred summarization model
model_dir = os.path.join("models", "summary_model")

if not os.path.exists(model_dir):
    print(f"⬇️ Downloading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer.save_pretrained(model_dir)
    model.save_pretrained(model_dir)
else:
    print(f"📂 Using cached model from: {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)

# === PIPELINE INITIALIZATION ===
try:
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=device)
except Exception as e:
    print("❌ Model loading error:", e)
    summarizer = None

# === EXTRACT PDF TEXT ===
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = " ".join([page.get_text() for page in doc])
        return text.strip()
    except Exception as e:
        print("❌ PDF Extraction Error:", e)
        return ""

# === CHUNK TEXT ===
def chunk_text(text, max_tokens=400):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    print(f"🔹 Total chunks: {len(chunks)}")
    return chunks

# === SUMMARIZE PDF ===
def summarize_pdf(pdf_path):
    if summarizer is None:
        return "Model not loaded. Please check your model path or setup."

    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        print("⚠️ No text extracted from PDF.")
        return "No readable content found in the document."

    chunks = chunk_text(full_text)

    summaries = []
    for i, chunk in enumerate(chunks):
        try:
            print(f"🔸 Summarizing chunk {i + 1}/{len(chunks)}...")
            summary_output = summarizer(
                chunk,
                max_length=130,
                min_length=30,
                do_sample=False
            )
            summaries.append(summary_output[0]['summary_text'])
        except Exception as e:
            print(f"❌ Error summarizing chunk {i + 1}: {e}")
            summaries.append("[Failed to summarize chunk]")

    combined_summary = " ".join(summaries)

    try:
        print("🧠 Compressing final summary...")
        compressed_output = summarizer(
            combined_summary,
            max_length=150,
            min_length=50,
            do_sample=False
        )
        final_summary = compressed_output[0]['summary_text']
        print("✅ Summary generated")
    except Exception as e:
        print("❌ Final compression error:", e)
        final_summary = combined_summary[:800] + "..." if len(combined_summary) > 800 else combined_summary

    return final_summary
