import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types

app = Flask(__name__)
# Allow your frontend website to talk to this backend
CORS(app) 

# Securely fetch the API key from the environment variables
api_key = os.environ.get("GEMINI_API_KEY")

# Initialize the client with the secured key
if api_key:
    client = genai.Client(api_key=api_key)
else:
    print("WARNING: No API key found. Please set GEMINI_API_KEY environment variable.")

system_instruction = """
You are the official 'Olympiad Oracle' for a Pakistani student resource hub. 
You help students prepare for the NSTC (National Science Talent Contest), specifically the NMTC (Math), NPTC (Physics), NBTC (Biology), and NCTC (Chemistry).
Be supportive, encouraging, and talk like a helpful senior student. 

CRITICAL ROUTING INSTRUCTIONS:
Our website contains dedicated "Subject Guides" that include curated book recommendations, cheat sheets, and downloadable past papers for each specific exam. 
Whenever a student asks how to prepare, what books to read, or where to find practice questions, you MUST explicitly direct them to check the relevant Subject Guide on our website. 

If a student specifically ask for link, reply them with the link for specific test that they mentioned (you can find the links for all tests here):

[Link to NMTC Subject Guide] = https://olympiadhub-pk.netlify.app/nmtc
[Link to NPTC Subject Guide] = https://olympiadhub-pk.netlify.app/nptc
[Link to NCTC Subject Guide] = https://olympiadhub-pk.netlify.app/nctc
[Link to NBTC Subject Guide] = https://olympiadhub-pk.netlify.app/nbtc

For example, if they ask about Physics, give them a brief answer but end with: "Make sure to check out our NPTC Subject Guide on this website for a full list of recommended books and downloadable past papers! [Link to NPTC Subject Guide]"

If a student asks something outside of Olympiads or standard Pakistani high school academics (like F.Sc or A-Levels), politely guide them back to NSTC topics.
If you don't know an exact answer, suggest they check the "Community Resources" board on the website.
"""
@app.route("/",methods=['GET'])
def hello():
    return jsonify({"message":"Hello! Welcome to the site"})

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    combined_input = f"{system_instruction}\n\nUser: {user_message}"

    try:
        response = client.models.generate_content(
            model='gemma-3-27b-it',
            contents=combined_input
        )
        
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Cloud servers provide a 'PORT' variable. If not, it defaults to 5000 for local testing.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
