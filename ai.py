import os
from api_keys import OPENAI_API_KEY
from openai import OpenAI
from pathlib import Path

def create_openai_client(api_key):
    return OpenAI(api_key=api_key)

def get_openai_response(client, user_input, instructions, model="gpt-4o-mini"):
    """
    Dobija odgovor od OpenAI GPT modela
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_input}
            ],
            temperature=0.9,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"ERROR in OpenAI response: {e}")
        return "Sorry, I couldn't process that."

def text_to_speech_openai(client, text, output_path):
    """
    Konvertuje tekst u govor koristeći OpenAI TTS
    Glasovi: alloy, echo, fable, onyx, nova, shimmer
    """
    try:
        print(f"Converting text to speech: {text[:50]}...")
        
        response = client.audio.speech.create(
            model="tts-1",  # ili "tts-1-hd" za bolji kvalitet
            voice="nova",   # ženski glas (kao Karen) - možeš probati: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            speed=1.0  # 0.25 do 4.0
        )
        
        # Snimi audio fajl
        response.stream_to_file(output_path)
        print(f'Audio file created at: {output_path}')
        return True
        
    except Exception as e:
        print(f'ERROR in Text to Speech: {e}')
        return False

# Test glasova (opciono)
def list_available_voices():
    """
    OpenAI TTS glasovi:
    - alloy (neutralan)
    - echo (muški)
    - fable (britanski muški)
    - onyx (duboki muški)
    - nova (ženski, energičan) - PREPORUČUJEM ZA KAREN
    - shimmer (ženski, mekan)
    """
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    print("Available OpenAI TTS voices:")
    for voice in voices:
        print(f"  - {voice}")
    return voices
