from gtts import gTTS
import os
import threading
import platform

def speak_text(text, lang="te"):  
    def tts_thread():
        try:
            print(f"Generating speech for: {text} (Language: {lang})")
            tts = gTTS(text=text, lang=lang)
            tts.save("output.mp3")
            print("Audio saved as output.mp3")

            # Identify OS and play the file accordingly
            system_os = platform.system().lower()
            print(f"Detected OS: {system_os}")

            if "darwin" in system_os:  # macOS
                os.system("afplay output.mp3")
            elif "linux" in system_os:
                os.system("mpg321 output.mp3")
            elif "windows" in system_os:
                os.system("start output.mp3")
            else:
                print("Unsupported OS for automatic playback. Play manually.")

        except Exception as e:
            print(f"Error in TTS: {e}")

    threading.Thread(target=tts_thread, daemon=True).start()

if __name__ == "__main__":
    speak_text("dog")
