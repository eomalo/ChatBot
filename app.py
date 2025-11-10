# imports
import flet as ft
import speech_recognition as sr
import os
from ai import (
    get_openai_response,
    create_openai_client,
    text_to_speech_openai,
    OPENAI_API_KEY
)

class Message():
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type

# This is the app
def main(page: ft.Page):
    page.title = "BOB (Brutally Obvious Bot)"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Make the clients
    openai_client = create_openai_client(OPENAI_API_KEY)
    recognizer = sr.Recognizer()
    recording = False

    # My Widgets
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
        padding=20
    )

    new_message = ft.TextField(
        hint_text="Type if you are lazy, otherwise speak to me",
        expand=True,
        multiline=False,
        on_submit=lambda e: send_message(e)  # Enter za slanje
    )

    # Add the functionality
    def add_message(user_name: str, text: str, message_type: str):
        message = Message(user_name, text, message_type)

        if message_type == "system":
            text_color = ft.Colors.RED_400
            bg_color = ft.Colors.GREY_800
        elif message_type == "ai":
            text_color = ft.Colors.WHITE
            bg_color = ft.Colors.BLUE_400
        else:
            text_color = ft.Colors.BLACK
            bg_color = ft.Colors.GREY_400

        # Add messages to my ListView(Widget)
        chat.controls.append(
            ft.Column(
                controls=[
                    ft.Text(message.user_name, size=12, color=ft.Colors.GREY_500),
                    ft.Container(
                        content=ft.Text(
                            message.text,
                            selectable=True,
                            color=text_color
                        ),
                        border_radius=10,
                        padding=10,
                        bgcolor=bg_color
                    ),
                ]
            )
        )
        page.update()

    def send_message(e):
        if not new_message.value:
            return

        # Add messages to the chat
        user_message = new_message.value
        add_message("You", user_message, "user")
        new_message.value = ""
        page.update()

        # Working with AI
        instructions = "You are a helpful assistant. Provide short and overly sarcastic, offensive responses in a southern american mother voice. Keep responses under 100 words."
        ai_res = get_openai_response(openai_client, user_message, instructions)
        add_message("Karen", ai_res, "ai")

        # Convert Text with OpenAI TTS
        try:
            file_path = os.path.abspath("audio.mp3")
            success = text_to_speech_openai(openai_client, ai_res, file_path)

            if success:
                page.overlay.clear()
                page.overlay.append(ft.Audio(src=file_path, autoplay=True))
                page.update()
            else:
                add_message("System", "Failed to generate audio", "system")

        except Exception as e:
            print(f"Error with playing audio: {e}")
            add_message("System", f"Audio error: {e}", "system")

    def start_recording(e):
        """Funkcija za snimanje glasa (opciono - za mic dugme)"""
        try:
            add_message("System", "🎤 Listening...", "system")
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5)
            
            text = recognizer.recognize_google(audio)
            new_message.value = text
            page.update()
            
            # Automatski pošalji
            send_message(e)
            
        except sr.WaitTimeoutError:
            add_message("System", "⏱️ No speech detected", "system")
        except sr.UnknownValueError:
            add_message("System", "❌ Could not understand audio", "system")
        except Exception as e:
            add_message("System", f"❌ Error: {e}", "system")

    # Building out the Container
    chat_container = ft.Container(
        content=chat,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=ft.border_radius.all(10),
        expand=True,
        padding=10
    )

    input_row = ft.Row(
        controls=[
            new_message,
            ft.IconButton(
                icon=ft.Icons.MIC,
                bgcolor=ft.Colors.GREEN_400,
                on_click=start_recording,
                tooltip="Record voice"
            ),
            ft.IconButton(
                icon=ft.Icons.SEND_ROUNDED,
                on_click=send_message,
                bgcolor=ft.Colors.BLUE_400,
                tooltip="Send message"
            )
        ]
    )

    page.add(
        ft.Column(
            controls=[
                chat_container,
                input_row
            ], 
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
