import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)

# ==========================================
# 1. THE FRONT DOOR BOUNCER (The Guest List)
# ==========================================

CORS(app, resources={
    r"/*": {
        "origins": [
            "https://exametric.netlify.app", 
            
        ]
    }
})

# Securely fetch the API key from the environment variables
api_key_oracle = os.environ.get("API_KEY_ORACLE")
api_key_tutor = os.environ.get("API_KEY_TUTOR")


# Initialize TWO separate clients
try:
    client_oracle = genai.Client(api_key=api_key_oracle)
    client_tutor = genai.Client(api_key=api_key_tutor)
except Exception as e:
    print(f"Error initializing AI clients: {e}")


def getSystemPrompt(bot_id, subject=None):
    if (bot_id == 1):
        return """
You are the official 'Olympiad Oracle' for a Pakistani student resource hub. 
You help students prepare for the NSTC (National Science Talent Contest), specifically the NMTC (Math), NPTC (Physics), NBTC (Biology), and NCTC (Chemistry), POAI (Pakistan Olympiad of Artificial Intelligence), POI (Pakistan Olympiad of Informatics).
Be supportive, encouraging, and talk like a helpful senior student. 

CRITICAL ROUTING INSTRUCTIONS:
Our website contains dedicated "Subject Guides" that include curated book recommendations, cheat sheets, and downloadable past papers for each specific exam. 
Whenever a student asks how to prepare, what books to read, or where to find practice questions, you MUST explicitly direct them to check the relevant Subject Guide on our website. 

If a student specifically ask for link, reply them with the link for specific test that they mentioned (you can find the links for all tests here):

[Link to NMTC Subject Guide] = https://exametric.netlify.app/nmtc
[Link to NPTC Subject Guide] = https://exametric.netlify.app/nptc
[Link to NCTC Subject Guide] = https://exametric.netlify.app/nctc
[Link to NBTC Subject Guide] = https://exametric.netlify.app/nbtc
[Link to POAI Subject Guide] = https://exametric.netlify.app/poai
[Link to POI Subject Guide] = https://exametric.netlify.app/poi

For example, if they ask about Physics, give them a brief answer but end with: "Make sure to check out our NPTC Subject Guide on this website for a full list of recommended books and downloadable past papers! [Link to NPTC Subject Guide]"

If a student asks something outside of Olympiads or standard Pakistani high school academics (like F.Sc or A-Levels), politely guide them back to NSTC topics.
If you don't know an exact answer, suggest they check the "Community Resources" board on the website.
"""
    elif (bot_id == 2):
        return f"""You are an elite Pakistani Olympiad tutor for the NSTC. Your domain is: {subject}.
Follow this methodology once the student picks a topic:
1. THEORY: Explain intuitively.
2. EXAMPLE: Walk through a basic example.
3. CONCEPT CHECK: Ask a simple question and wait.
4. ESCALATION: Introduce advanced theory.
5. FINAL TEST: Give an NSTC-level question. 
Rules: No direct answers for mistakes, give hints. Format cleanly. If they pass the final test, append: [STATUS: PASSED]."""


@app.route("/",methods=['GET'])
def hello():
    return jsonify({"message":"Hello! Welcome to the site"})

# ==========================================
# 2. THE VERCEL STREET GUARD BYPASS
# ==========================================
@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    # Catch the browser's Preflight CORS request and give it a thumbs up
    if request.method == 'OPTIONS':
        return jsonify({"message": "CORS preflight successful"}), 200

    # Proceed with normal POST logic
    data = request.json
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    
    bot_id = data.get("bot_id", 1)  # Default to bot 1 (Oracle) if not provided

    try:
        # ==========================================
        # BOT 1: ORACLE (Uses client_oracle)
        # ==========================================
        if (bot_id == 1):
            system_instruction_oracle = getSystemPrompt(bot_id=1)

            combined_input = f"{system_instruction_oracle}\n\nUser: {user_message}"

            response = client_oracle.models.generate_content(
                model='gemma-4-31b-it',
                contents=combined_input
            )
            
            return jsonify({"reply": response.text})
        
        # ==========================================
        # BOT 2: AI TUTOR (Uses client_tutor)
        # ==========================================
        elif (bot_id == 2):
            
            subject = data.get("subject")
            if subject:
                system_instruction_tutor = getSystemPrompt(bot_id=2, subject=subject)
                
            else: 
                raise Exception("Subject not provided for tutor bot")
            
            combined_input_tutor = f"{system_instruction_tutor}\n\nUser: {user_message}"
            
            response = client_tutor.models.generate_content(
                model='gemma-4-31b-it',
                contents=combined_input_tutor
            )
            
            return jsonify({"reply": response.text})
        else:
            return jsonify({"error": "Invalid bot_id"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cloud servers provide a 'PORT' variable. If not, it defaults to 5000 for local testing.
if __name__ == '__main__':
    app.run()
