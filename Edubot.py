# === COMPLETE STRUCTURE FOR YOUR EDUBOT.PY ===
# Make sure you have ONLY ONE of each route

import fitz
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
import google.generativeai as genai
import os
import time
import re
from flask import Flask, request, jsonify, render_template_string
import random
from datetime import datetime
import wikipedia

# === PDF FUNCTIONS ===
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

pdf_text = extract_text_from_pdf("static/documents/AI_Book1.pdf")
sentences = sent_tokenize(pdf_text)

def answer_from_pdf(query):
    query = query.lower()
    best_match = ""
    max_overlap = 0
    for sent in sentences:
        words = set(sent.lower().split())
        overlap = len(set(query.split()) & words)
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = sent
    return best_match if best_match else "Sorry, I couldn't find anything relevant."

# === GEMINI FUNCTIONS ===
def clean_gemini_math_text(text):
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = text.replace("**", "")
    text = text.replace("---", "")
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned_lines)

def initialize_gemini():
    """Initialize Gemini with comprehensive debugging and fallbacks"""
    time.sleep(0.5)
    
    print("🔍 DEBUGGING GEMINI INITIALIZATION:")
    print(f"Platform: {os.name}")
    print(f"Working directory: {os.getcwd()}")
    
    possible_keys = ['GEMINI_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'API_KEY']
    
    api_key = None
    key_source = None
    
    print("🔍 Available environment variables with 'API' or 'GEMINI':")
    for k, v in os.environ.items():
        if 'API' in k.upper() or 'GEMINI' in k.upper():
            print(f"   {k}: {'Found' if v else 'Empty'} (length: {len(v) if v else 0})")
    
    for key_name in possible_keys:
        api_key = os.getenv(key_name)
        if api_key:
            key_source = key_name
            print(f"✅ Found API key in {key_name} (length: {len(api_key)})")
            break
        else:
            print(f"❌ {key_name} not found")
    
    if not api_key:
        print("⚠️ No Gemini API key found in environment variables.")
        print("🔍 Checked variables:", possible_keys)
        return None
    
    try:
        print(f"🔧 Configuring Gemini with API key from {key_source}...")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        print("🧪 Testing Gemini connection...")
        test_response = model.generate_content("Hello, respond with just 'Working'")
        
        if hasattr(test_response, 'text') and test_response.text:
            print(f"✅ Gemini model initialized and tested successfully.")
            print(f"✅ Test response: {test_response.text.strip()}")
            return model
        else:
            print("⚠️ Gemini model created but test response was empty.")
            return model
            
    except Exception as e:
        print(f"❌ Gemini Initialization Failed: {e}")
        import traceback
        traceback.print_exc()
        return None

# === INITIALIZE GEMINI ===
print("=" * 50)
print("🚀 STARTING GEMINI INITIALIZATION...")
model = initialize_gemini()

if model:
    print("🎉 SUCCESS: Gemini AI is ready!")
else:
    print("⚠️ WARNING: Gemini AI features will be disabled.")
    print("💡 Make sure your API key is set in Render environment variables.")

print("=" * 50)

# === WIKIPEDIA SETUP ===
wikipedia.set_lang("en")

# === FLASK APP ===
app = Flask(__name__)

# === IMAGE PATHS DICTIONARY ===
image_paths = {
    "Beginner": {
        "10": {
            "Physics": "static/questions/Class-10/Beginner/Physics",
            "Chemistry": "static/questions/Class-10/Beginner/Chemistry",
            "Maths": "static/questions/Class-10/Beginner/Maths",
            "Biology": "static/questions/Class-10/Beginner/Biology",
            "English": "static/questions/Class-10/Beginner/English",
            "Artificial Intelligence": "static/questions/Class-10/Beginner/Artificial_Intelligence"
        },
        "11": {
            "Physics": "static/questions/Class-11/Beginner/Physics",
            "Chemistry": "static/questions/Class-11/Beginner/Chemistry",
            "Maths": "static/questions/Class-11/Beginner/Maths",
            "Biology": "static/questions/Class-11/Beginner/Biology",
            "English": "static/questions/Class-11/Beginner/English",
            "Artificial Intelligence": "static/questions/Class-11/Beginner/Artificial_Intelligence"
        },
        "12": {
            "Physics": "static/questions/Class-12/Beginner/Physics",
            "Chemistry": "static/questions/Class-12/Beginner/Chemistry",
            "Maths": "static/questions/Class-12/Beginner/Maths",
            "Biology": "static/questions/Class-12/Beginner/Biology",
            "English": "static/questions/Class-12/Beginner/English",
            "Artificial Intelligence": "static/questions/Class-12/Beginner/Artificial_Intelligence"
        }
    },
    "Intermediate": {
        "10": {
            "Physics": "static/questions/Class-10/Intermediate/Physics",
            "Chemistry": "static/questions/Class-10/Intermediate/Chemistry",
            "Maths": "static/questions/Class-10/Intermediate/Maths",
            "Biology": "static/questions/Class-10/Intermediate/Biology",
            "English": "static/questions/Class-10/Intermediate/English",
            "Artificial Intelligence": "static/questions/Class-10/Intermediate/Artificial_Intelligence"
        },
        "11": {
            "Physics": "static/questions/Class-11/Intermediate/Physics",
            "Chemistry": "static/questions/Class-11/Intermediate/Chemistry",
            "Maths": "static/questions/Class-11/Intermediate/Maths",
            "Biology": "static/questions/Class-11/Intermediate/Biology",
            "English": "static/questions/Class-11/Intermediate/English",
            "Artificial Intelligence": "static/questions/Class-11/Intermediate/Artificial_Intelligence"
        },
        "12": {
            "Physics": "static/questions/Class-12/Intermediate/Physics",
            "Chemistry": "static/questions/Class-12/Intermediate/Chemistry",
            "Maths": "static/questions/Class-12/Intermediate/Maths",
            "Biology": "static/questions/Class-12/Intermediate/Biology",
            "English": "static/questions/Class-12/Intermediate/English",
            "Artificial Intelligence": "static/questions/Class-12/Intermediate/Artificial_Intelligence"
        }
    },
    "Advanced": {
        "10": {
            "Physics": "static/questions/Class-10/Advanced/Physics",
            "Chemistry": "static/questions/Class-10/Advanced/Chemistry",
            "Maths": "static/questions/Class-10/Advanced/Maths",
            "Biology": "static/questions/Class-10/Advanced/Biology",
            "English": "static/questions/Class-10/Advanced/English",
            "Artificial Intelligence": "static/questions/Class-10/Advanced/Artificial_Intelligence"
        },
        "11": {
            "Physics": "static/questions/Class-11/Advanced/Physics",
            "Chemistry": "static/questions/Class-11/Advanced/Chemistry",
            "Maths": "static/questions/Class-11/Advanced/Maths",
            "Biology": "static/questions/Class-11/Advanced/Biology",
            "English": "static/questions/Class-11/Advanced/English",
            "Artificial Intelligence": "static/questions/Class-11/Advanced/Artificial_Intelligence"
        },
        "12": {
            "Physics": "static/questions/Class-12/Advanced/Physics",
            "Chemistry": "static/questions/Class-12/Advanced/Chemistry",
            "Maths": "static/questions/Class-12/Advanced/Maths",
            "Biology": "static/questions/Class-12/Advanced/Biology",
            "English": "static/questions/Class-12/Advanced/English",
            "Artificial Intelligence": "static/questions/Class-12/Advanced/Artificial_Intelligence"
        }
    }
}

# === MENU TEXT ===
MENU_TEXT = """
Hi! I am EduLink 🤖 Here's what I can help you with:

1. Tell me your class (e.g., "class 10").
2. Mention your subject (e.g., "math", "science").
3. Specify difficulty (Beginner, Intermediate, Advanced) — optional.

Example queries:
- "Give me an easy math question for class 10"
- "I want a hard science problem"
- "Help" or "menu" to see this message again.
"""

# === UTILITY FUNCTIONS ===
def load_images(class_level, subject, difficulty):
    try:
        folder_path = image_paths[difficulty][class_level][subject]
        abs_folder_path = os.path.join(os.getcwd(), folder_path)
        images = [f for f in os.listdir(abs_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            selected_image = random.choice(images)
            web_path = f"/{folder_path}/{selected_image}".replace("\\", "/")
            print(f"✅ Selected image path: {web_path}")
            return web_path
        else:
            print(f"⚠️ No images found in: {abs_folder_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        return None

def get_difficulty(user_input):
    user_input = user_input.lower()
    if any(word in user_input for word in ["beginner", "easy", "simple", "basic"]):
        return "Beginner"
    elif any(word in user_input for word in ["intermediate", "medium", "normal"]):
        return "Intermediate"
    elif any(word in user_input for word in ["advanced", "hard", "difficult", "challenging"]):
        return "Advanced"
    return "Beginner"

def get_question(student_class, subject, difficulty):
    class_level = student_class.split()[-1]
    image_path = load_images(class_level, subject, difficulty)
    return image_path if image_path else "Sorry, I don't have questions for your request yet."

# === FLASK ROUTES ===
# Make sure you have ONLY ONE of each route!

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query")
    return jsonify({"answer": answer_from_pdf(query)})

@app.route("/get_pdf_text")
def get_pdf_text():
    pdf_path = "static/documents/AI_Book1.pdf"  
    extracted_text = extract_text_from_pdf(pdf_path)
    return jsonify({"text": extracted_text})

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    class_selected = request.json.get("class")
    subject_selected = request.json.get("subject")
    difficulty_selected = request.json.get("difficulty")
    ai_mode = request.json.get("ai_mode", False)

    # === AI MODE HANDLING ===
    if ai_mode:
        if not model:
            return jsonify({
                "reply": "❌ Gemini AI is not initialized. Please check server logs or contact administrator."
            })
        
        try:
            print(f"🤖 Sending to Gemini: {user_msg[:50]}...")
            response = model.generate_content(user_msg)
            
            if hasattr(response, 'text') and response.text:
                clean_text = clean_gemini_math_text(response.text)
                print(f"✅ Gemini responded with {len(clean_text)} characters")
                return jsonify({"reply": f"🌟 Gemini AI: {clean_text}"})
            else:
                print("⚠️ Gemini returned empty response")
                return jsonify({"reply": "⚠️ Gemini AI returned an empty response. Please try again."})
                
        except Exception as e:
            print(f"❌ Gemini API Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            error_msg = str(e)
            if "API_KEY" in error_msg or "authentication" in error_msg.lower():
                return jsonify({"reply": "❌ API Key authentication failed. Please check server configuration."})
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                return jsonify({"reply": "❌ API quota exceeded. Please try again later."})
            else:
                return jsonify({"reply": f"❌ Gemini AI Error: {error_msg}"})

    # === BELOW RUNS ONLY IF ai_mode IS OFF ===

    # --- PDF Query Handling ---
    if "pdf" in user_msg:
        try:
            with fitz.open("static/documents/AI_Book1.pdf") as doc:
                pdf_text = ""
                for page in doc:
                    pdf_text += page.get_text()
            answer = answer_from_pdf(user_msg)
            return jsonify({"reply": f"📄 PDF Answer: {answer}"})
        except Exception as e:
            print("PDF ERROR:", e)
            return jsonify({"reply": "❌ Sorry! I couldn't read the PDF right now."})

    # --- Help/Menu Handling ---
    if any(word in user_msg for word in ["help", "menu", "options", "Help", "HELP"]):
        return jsonify({"reply": MENU_TEXT})

    # --- Wikipedia Summary Handling ---
    if "define" in user_msg or "what is" in user_msg or "who is" in user_msg:
        try:
            term = user_msg.replace("define", "").replace("what is", "").replace("who is", "").strip()
            summary = wikipedia.summary(term, sentences=2)
            return jsonify({"reply": f"📘 Here's what I found about {term.title()}:\n\n{summary}"})
        except wikipedia.exceptions.DisambiguationError as e:
            return jsonify({"reply": f"⚠️ That term is ambiguous. Try one of these: {', '.join(e.options[:5])}"})
        except wikipedia.exceptions.PageError:
            return jsonify({"reply": f"❌ Sorry, I couldn't find anything for '{term}'."})
        except Exception as e:
            return jsonify({"reply": f"⚠️ Error: {str(e)}"})

    # --- Subject-Based Image Question Handling ---
    user_msg_lower = user_msg.lower()

    if "class 12" in user_msg_lower or "class xii" in user_msg_lower:
        student_class = "Class 12"
    elif "class 11" in user_msg_lower or "class xi" in user_msg_lower:
        student_class = "Class 11"
    elif "class 10" in user_msg_lower or "class x" in user_msg_lower:
        student_class = "Class 10"
    else:
        student_class = "Unknown class"

    if "artificial intelligence" in user_msg_lower or "ai" in user_msg_lower:
        subject = "Artificial Intelligence"
    elif "physics" in user_msg_lower:
        subject = "Physics"
    elif "chemistry" in user_msg_lower or "chem" in user_msg_lower:
        subject = "Chemistry"
    elif "biology" in user_msg_lower or "bio" in user_msg_lower:
        subject = "Biology"
    elif "english" in user_msg_lower:
        subject = "English"
    elif "math" in user_msg_lower or "mathematics" in user_msg_lower or "maths" in user_msg_lower:
        subject = "Maths"
    else:
        subject = "General"

    difficulty = get_difficulty(user_msg)
    question_image_path = get_question(student_class, subject, difficulty)

    if question_image_path:
        question_image_html = f'<img src="{question_image_path}" alt="Question Image" style="max-width: 100%; height: auto;">'
    else:
        question_image_html = "Sorry, I couldn't find an image for your request."

    reply = f"Here's a {difficulty} question for {student_class} {subject}:\n{question_image_html}"
    return jsonify({"reply": reply})

@app.route("/")
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>EduLink 🤖 | AI Learning Assistant</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100 min-h-screen">
  <!-- Your existing HTML content here -->
</body>
</html>
''', now=datetime.now().strftime("%I:%M %p"))

if __name__ == "__main__":
    app.run(debug=True)
