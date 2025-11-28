import fitz
import difflib
import re
import nltk
nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template_string
import random
import os
from datetime import datetime
import wikipedia

# === NEW: Gemini Response Cleaner ===
def clean_gemini_response(raw_text):
    """Transforms messy Gemini responses into clean, organized format"""
    
    if not raw_text or len(raw_text.strip()) == 0:
        return "No response received."
    
    # Clean markdown artifacts
    text = re.sub(r'^Gemini AI:\s*', '', raw_text.strip(), flags=re.MULTILINE)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)  # Remove headers
    text = text.replace('**', '')  # Remove bold
    text = text.replace('---', '')  # Remove dividers
    text = re.sub(r'\$(.*?)\$', r'\1', text)  # Clean LaTeX
    
    # Split into logical sections
    paragraphs = re.split(r'\n\s*\n', text)
    cleaned_sections = []
    
    for para in paragraphs:
        para = para.strip()
        if len(para) > 20:  # Keep substantial content
            # Convert numbered lists to markdown bullets
            if re.match(r'^\d+\.', para):
                lines = para.split('\n')
                bullet_lines = [f"- {re.sub(r'^\d+\.\s*', '', line.strip())}" for line in lines if line.strip()]
                if bullet_lines:
                    cleaned_sections.append('\n'.join(bullet_lines))
            else:
                cleaned_sections.append(para)
    
    # Organize into clean format
    cleaned = []
    if cleaned_sections:
        cleaned.append("## 📚 Clean Answer")
        for i, section in enumerate(cleaned_sections[:5], 1):  # Limit sections
            if section.startswith('-'):
                cleaned.append(section)
            else:
                cleaned.append(f"**Point {i}:** {section[:200]}...")
        cleaned.append("")
        cleaned.append("---")
    else:
        cleaned = [text[:300] + "..." if len(text) > 300 else text]
    
    return '\n'.join(cleaned)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []
    for page in doc:
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            if text and len(text) > 20:
                full_text.append(text)
    doc.close()
    return "\n\n".join(full_text)

# Load PDFs
pdf_text10 = extract_text_from_pdf("static/documents/AI_Book10.pdf")
pdf_text11 = extract_text_from_pdf("static/documents/AI_Book11.pdf")
pdf_text12 = extract_text_from_pdf("static/documents/AI_Book12.pdf")

pdf_sources = {
    "book10": sent_tokenize(pdf_text10),
    "book11": sent_tokenize(pdf_text11),
    "book12": sent_tokenize(pdf_text12)
}

def answer_from_pdf(query, source):
    query_low = query.lower().strip()
    best_matches = []

    sentences = pdf_sources.get(source.lower())
    if not sentences:
        return f"❌ Source '{source}' not found. Available: {list(pdf_sources.keys())}"

    raw_text = "\n\n".join(sentences)
    paragraphs = re.split(r'\n\s*\n', raw_text)
    if len(paragraphs) <= 1:
        paragraphs = [s.strip() for s in sentences if s.strip()]

    query_words = set(query_low.split())
    
    for para in paragraphs:
        para_low = para.lower().strip()
        if not para_low or len(para_low) < 30:
            continue
            
        para_words = set(para_low.split())
        common_words = query_words.intersection(para_words)
        if len(common_words) < 1:
            continue
            
        score = difflib.SequenceMatcher(None, query_low, para_low).ratio()
        best_matches.append((score, para.strip()))

    if not best_matches:
        return "❌ No relevant content found. Try rephrasing your query."

    best_matches.sort(reverse=True, key=lambda x: x[0])
    top_results = [m[1] for m in best_matches[:3] if m[0] > 0.25]

    if top_results:
        return "\n\n---\n\n".join(top_results[:2])
    return "❌ No good matches found (similarity too low)."

# Gemini Setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
model = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Gemini model initialized.")
    except Exception as e:
        print("❌ Gemini Initialization Failed:", e)
        model = None

wikipedia.set_lang("en")
app = Flask(__name__)

# Routes (keeping existing ones unchanged)
@app.route("/debug-env")
def debug_env():
    return {"env_keys": sorted(list(os.environ.keys()))}

@app.route("/test-env")
def test_env():
    return {"value": os.getenv("GEMINI_API_KEY") or "MISSING"}

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json or {}
    query = data.get("query", "")
    source = data.get("source", "book10")
    
    if not query:
        return jsonify({"answer": "❌ Please provide a query."})
    
    answer = answer_from_pdf(query, source)
    return jsonify({"answer": answer})

@app.route("/get_pdf_text")
def get_pdf_text():
    pdf_path = "static/documents/AI_Book1.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    return jsonify({"text": extracted_text})

@app.route("/test_pdf/<source>")
def test_pdf(source):
    test_query = "supervised learning"
    result = answer_from_pdf(test_query, source)
    return jsonify({"query": test_query, "source": source, "result": result})

# Keep your image_paths, MENU_TEXT, INSTRUCTIONS_TEXT, load_images, get_difficulty, get_question functions EXACTLY THE SAME
# [All your existing functions here - no changes needed]

image_paths = {  # Your existing image_paths dictionary - unchanged
    # ... (keeping exactly as is)
}

MENU_TEXT = """..."""  # Your existing MENU_TEXT - unchanged
INSTRUCTIONS_TEXT = """..."""  # Your existing INSTRUCTIONS_TEXT - unchanged

# FIXED: Updated /chat route with clean Gemini responses
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    class_selected = request.json.get("class")
    subject_selected = request.json.get("subject")
    difficulty_selected = request.json.get("difficulty")
    ai_mode = request.json.get("ai_mode", False)

    if ai_mode:
        if not model:
            return jsonify({"reply": "❌ Gemini AI is not initialized. Check API key."})
        
        try:
            # IMPROVED: Better prompt for clean, structured responses
            structured_prompt = f"""
            Answer this student query clearly and concisely for Class 12 CBSE level:
            
            Query: "{user_msg}"
            
            Format your answer like this:
            ## Main Answer
            - Key point 1
            - Key point 2  
            - Key point 3
            
            ## Additional Info (if needed)
            - Extra details here
            
            Keep it short, use bullet points, no extra formatting.
            """
            
            response = model.generate_content(structured_prompt)
            
            if hasattr(response, 'text') and response.text:
                # CLEAN THE RESPONSE
                cleaned_reply = clean_gemini_response(response.text)
                return jsonify({"reply": f"🌟 AI Answer:\n\n{cleaned_reply}"})
            else:
                return jsonify({"reply": "⚠️ No response from AI."})
                
        except Exception as e:
            return jsonify({"reply": f"❌ AI Error: {str(e)}"})

    # === ALL EXISTING NON-AI LOGIC REMAINS EXACTLY THE SAME ===
    # PDF handling, Wikipedia, questions, etc. - no changes needed
    if "pdf" in user_msg.lower():
        # ... your existing PDF logic unchanged
        pass
    
    if any(word in user_msg for word in ["help", "menu", "options"]):
        return jsonify({"reply": MENU_TEXT})

    # ... rest of your existing logic unchanged ...

    return jsonify({"reply": "Default response"})

# Keep your index() route EXACTLY THE SAME
@app.route("/")
def index():
    # Your existing HTML template - no changes needed
    return render_template_string('''...your existing HTML...''')

if __name__ == "__main__":
    app.run(debug=True)
