import os
import fitz  # PyMuPDF
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer, AutoModelForSeq2SeqLM
from difflib import SequenceMatcher

# === Paths for local model caching ===
BASE_MODEL_DIR = os.path.join(os.getcwd(), "models")
QG_MODEL_DIR = os.path.join(BASE_MODEL_DIR, "google-flan-t5-large")
QA_MODEL_DIR = os.path.join(BASE_MODEL_DIR, "deepset-roberta-base-squad2")

# === Download models if not present ===
def download_model(model_name, save_dir, task):
    if not os.path.exists(save_dir):
        print(f"⬇️ Downloading {model_name} for task '{task}'...")
        if task == "text2text-generation":
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        elif task == "question-answering":
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        else:
            raise ValueError(f"Unsupported task: {task}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.save_pretrained(save_dir)
        tokenizer.save_pretrained(save_dir)
    else:
        print(f"✅ Model already downloaded: {save_dir}")

# === Load Models ===
print("🚀 Checking and loading models...")
download_model("google/flan-t5-large", QG_MODEL_DIR, "text2text-generation")
download_model("deepset/roberta-base-squad2", QA_MODEL_DIR, "question-answering")

qg_pipeline = pipeline("text2text-generation", model=QG_MODEL_DIR, tokenizer=QG_MODEL_DIR)
qa_pipeline = pipeline("question-answering", model=QA_MODEL_DIR, tokenizer=QA_MODEL_DIR)

# === Utility: Extract PDF Text ===
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = " ".join([page.get_text() for page in doc])
        return text
    except Exception as e:
        return f"[Error] {str(e)}"

# === Main Challenge Function ===
def process_pdf_and_evaluate_answer(pdf_path, user_answer):
    # 1. Extract context
    context = extract_text_from_pdf(pdf_path)
    if context.startswith("[Error]"):
        return { "error": context }

    # 2. Generate a question
    try:
        prompt = f"Generate a question from: {context[:300]}"
        generated_question = qg_pipeline(prompt, max_new_tokens=64)[0]['generated_text']
    except Exception as e:
        return { "error": f"[Error generating question] {str(e)}" }

    # 3. Get expected answer
    try:
        qa_result = qa_pipeline(question=generated_question, context=context)
        expected_answer = qa_result['answer']
    except Exception as e:
        return { "error": f"[Error getting expected answer] {str(e)}" }

    # 4. Compare with user answer
    similarity = SequenceMatcher(None, user_answer.lower(), expected_answer.lower()).ratio()
    feedback = "🎉 Correct or very close!" if similarity > 0.6 else "❌ Incorrect or not matching."

    # 5. Return expected output format
    return {
        "question": generated_question,
        "expected": expected_answer,
        "feedback": feedback
    }
