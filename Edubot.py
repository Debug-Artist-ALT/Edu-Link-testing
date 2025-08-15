import fitz

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

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


from flask import Flask, request, jsonify, render_template_string
import random
import os
from datetime import datetime
import wikipedia

import google.generativeai as genai
import os

import re

def clean_gemini_math_text(text):
    # Remove markdown headers (like ##, ###)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove bold markers like **text**
    text = text.replace("**", "")
    
    # Remove horizontal rules (---)
    text = text.replace("---", "")
    
    # Replace LaTeX-style math ($...$) with just the math content
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    
    # Strip leading/trailing whitespace from lines and remove empty lines
    lines = text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    return "\n".join(cleaned_lines)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ GEMINI_API_KEY not found in environment. Gemini AI features will be disabled.")
    model = None
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Gemini model initialized.")
    except Exception as e:
        print("❌ Gemini Initialization Failed:", e)
        model = None
        
wikipedia.set_lang("en")  # English

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    query = request.json.get("query")
    return jsonify({"answer": answer_from_pdf(query)})

@app.route("/get_pdf_text")
def get_pdf_text():
    pdf_path = "static/documents/AI_Book1.pdf"  
    extracted_text = extract_text_from_pdf(pdf_path)
    return jsonify({"text": extracted_text})

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

def load_images(class_level, subject, difficulty):
    try:
        folder_path = image_paths[difficulty][class_level][subject]
        abs_folder_path = os.path.join(os.getcwd(), folder_path)

        images = [f for f in os.listdir(abs_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if images:
            selected_image = random.choice(images)
            web_path = f"/{folder_path}/{selected_image}".replace("\\", "/")  # Normalize slashes for web
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
    if any(word in user_input for word in ["beginner", "easy", "simple", "basic", "Beginner", "Easy", "Simple", "Basic", "BEGINNER", "EASY", "SIMPLE", "BASIC"]):
        return "Beginner"
    elif any(word in user_input for word in ["intermediate", "medium", "normal", "Intermediate", "Medium", "Normal", "INTERMEDIATE", "MEDIUM", "NORMAL"]):
        return "Intermediate"
    elif any(word in user_input for word in ["advanced", "hard", "difficult", "challenging", "advanced", "Hard", "Difficult", "Challenging", "ADVANCED", "HARD", "DIFFICULT", "CHALLENGING"]):
        return "Advanced"
    return "Beginner"

def get_question(student_class, subject, difficulty):
    class_level = student_class.split()[-1]
    image_path = load_images(class_level, subject, difficulty)
    return image_path if image_path else "Sorry, I don't have questions for your request yet."


@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    class_selected = request.json.get("class")
    subject_selected = request.json.get("subject")
    difficulty_selected = request.json.get("difficulty")
    ai_mode = request.json.get("ai_mode", False)

    if ai_mode:
        if not model:
            return jsonify({"reply": "❌ Gemini AI is not initialized properly. Check API key or logs."})
        try:
            response = model.generate_content(user_msg)
            if hasattr(response, 'text') and response.text:
                return jsonify({"reply": f"🌟 Gemini AI: {response.text}"})
            else:
                print("⚠️ Gemini returned no text. Response:", response)
                return jsonify({"reply": "⚠️ Gemini did not return any text."})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"reply": f"❌ Gemini API Error:\n{str(e)}"})

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
    if any(word in user_msg for word in ["help", "menu", "options", "Help", "HELP" ]):
        return jsonify({"reply": MENU_TEXT})

    # --- Wikipedia Summary Handling ---
    if "define" in user_msg or "what is" in user_msg or "who is" in user_msg or "Define" in user_msg or "What is" in user_msg or "Who is" in user_msg:
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
  <div class="container mx-auto max-w-4xl p-4">
    <header class="bg-white rounded-t-xl shadow-md p-6 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-blue-600">EduLink <span class="text-blue-400">🤖</span></h1>
        <p class="text-gray-600">Your AI-powered learning assistant</p>
      </div>
      <div class="flex items-center space-x-2">
        <span class="relative flex h-3 w-3">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
        </span>
        <span class="text-sm text-gray-500">Online</span>
        <button id="aiModeButton" onclick="toggleAIMode()" class="bg-gray-200 hover:bg-blue-600 hover:text-white text-blue-700 px-4 py-2 rounded-full text-sm transition-all">
  AI Mode: OFF
</button>

      </div>
    </header>

    <div class="chat-container bg-white rounded-b-xl shadow-md overflow-hidden flex flex-col" style="height: 70vh;">
      <div id="chatArea" class="flex-1 p-6 overflow-y-auto">
        <div class="flex mb-4">
          <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
            <i class="fas fa-robot text-blue-600"></i>
          </div>
          <div class="max-w-xl">
            <div class="bg-blue-50 text-blue-900 p-4 rounded-lg rounded-tl-none">
              <p>Hi there! 👋 I'm EduLink, your AI learning assistant.</p>
              <p class="mt-2">I can help you with questions for Class 10, 11, and 12 in various subjects.</p>
            </div>
            <div class="text-xs text-gray-500 ml-2 mt-1">{{ now }}</div>
          </div>
        </div>
        <div class="flex flex-wrap gap-2 mt-6">
          <button onclick="sendSuggestion('Help')" class="suggestion-chip bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-full text-sm font-medium transition-all">
            Show Help
          </button>
        </div>
      </div>

      <div class="border-t border-gray-200 p-4 bg-gray-50">
        <div class="flex items-center gap-2">
          <input id="userInput" type="text" placeholder="Ask me anything about Class 10 subjects..." 
                 class="flex-1 border border-gray-300 rounded-full py-3 px-6 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
          <button onclick="sendMessage()" class="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full w-12 h-12 flex items-center justify-center transition-all">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
        <div class="text-xs text-gray-500 mt-2 text-center">
          Example: "Give me a medium difficulty math question"
        </div>
      </div>
    </div>

    <!-- Colored Info Boxes Section -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
      <div class="bg-blue-100 p-4 rounded-lg shadow-md">
        <h4 class="font-bold text-lg text-blue-800">24/7 Availability</h4>
        <p class="text-gray-700">EduLink is available anytime to assist you with your learning needs.</p>
      </div>
      <div class="bg-green-100 p-4 rounded-lg shadow-md">
        <h4 class="font-bold text-lg text-green-800">Personalized Learning</h4>
        <p class="text-gray-700">Get questions tailored to your class and difficulty level.</p>
      </div>
      <div class="bg-yellow-100 p-4 rounded-lg shadow-md">
        <h4 class="font-bold text-lg text-yellow-800">Difficulty Levels Include</h4>
        <p class="text-gray-700">Beginner, Intermediate, Advanced and Competitive Exams for classes 10 to 12!</p>
      </div>
    </div>
  </div>

  <script>
  const chatArea = document.getElementById('chatArea');
  const userInput = document.getElementById('userInput');
  
  function styleBotReply(text) {
  if (text.includes("Here's what I found about")) {
    return `
      <div class="flex items-start bg-yellow-100 border-l-4 border-yellow-500 text-yellow-900 p-4 rounded shadow-sm">
        <div class="mr-2 mt-1 text-yellow-500">
          <i class="fas fa-book-open"></i>
        </div>
        <div>${text}</div>
      </div>`;
  }
  return `<p>${text}</p>`;
}                                

  function appendMessage(sender, text, isBot = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex mb-4 ${isBot ? '' : 'justify-end'}`;
    const messageContent = `
      ${!isBot ? `
        <div class="max-w-xl order-1">
          <div class="bg-blue-600 text-white p-4 rounded-lg rounded-tr-none">
            <p>${text}</p>
          </div>
          <div class="text-xs text-gray-500 mr-2 mt-1 text-right">${formatTime()}</div>
        </div>
        <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center ml-3 order-2">
          <i class="fas fa-user text-white"></i>
        </div>
      ` : `
        <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
          <i class="fas fa-robot text-blue-600"></i>
        </div>
        <div class="max-w-xl">
          <div class="bg-blue-50 text-blue-900 p-4 rounded-lg rounded-tl-none">
            ${styleBotReply(text)}


          </div>
          <div class="text-xs text-gray-500 ml-2 mt-1">${formatTime()}</div>
        </div>
      `}
    `;
    messageDiv.innerHTML = messageContent;
    chatArea.appendChild(messageDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  function sendSuggestion(text) {
    userInput.value = text;
    sendMessage();
  }

 async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;
  appendMessage('You', message, false);
  userInput.value = '';

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, ai_mode: aiMode })
    });
    const data = await response.json();
    appendMessage('EduLink', data.reply, true);
  } catch (err) {
    appendMessage('EduLink', 'Error: Could not connect to the server.', true);
  }
}

  function formatTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12;
    minutes = minutes < 10 ? '0' + minutes : minutes;
    return `${hours}:${minutes} ${ampm}`;
  }

  userInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      sendMessage();
    }
  });

  // ✅ Add mic button for voice input
  const micButton = document.createElement('button');
  micButton.innerHTML = '<i class="fas fa-microphone"></i>';
  micButton.className = "bg-gray-300 hover:bg-gray-400 text-black p-3 rounded-full w-12 h-12 flex items-center justify-center transition-all ml-2";
  micButton.onclick = () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.start();

    recognition.onresult = function(event) {
      const speechText = event.results[0][0].transcript;
      userInput.value = speechText;
      sendMessage();
    };

    recognition.onerror = function(event) {
      alert('Speech recognition error: ' + event.error);
    };
  };

  // ✅ Attach mic to input row on page load
  window.addEventListener('DOMContentLoaded', () => {
    const inputRow = document.querySelector('.border-t .flex');
    inputRow.appendChild(micButton);
  });

  let aiMode = false;

function toggleAIMode() {
  aiMode = !aiMode;
  const button = document.getElementById('aiModeButton');
  button.textContent = `AI Mode: ${aiMode ? 'ON 🤖' : 'OFF'}`;
  button.className = aiMode 
    ? 'bg-blue-600 text-white px-4 py-2 rounded-full text-sm transition-all'
    : 'bg-gray-200 hover:bg-blue-600 hover:text-white text-blue-700 px-4 py-2 rounded-full text-sm transition-all';
}
</script>

</body>
</html>
''', now=datetime.now().strftime("%I:%M %p"))

if __name__ == "__main__":
    app.run(debug=True)
