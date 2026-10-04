import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(treatment: str, summary: str, retries: int = 3) -> str:
    prompt = f"""
    Based on the following research summary for treatment '{treatment}', 
    provide one singular number (ex: 0.43) describing its predicted tumor reduction size.
    {summary}
    """

    for attempt in range(retries):
        try:
            # Use the Chat endpoint (Interactions API) as recommended by the SDK error
            chat = client.chats.create(model="gemini-3.8-flash")
            response = chat.send_message(prompt)
            return response.text
        except APIError as e:
            if e.code in (503, 429) and attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Service busy ({e.code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Gemini API Error: {e}")
                break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

    return "Error: Unable to generate response from Gemini API."