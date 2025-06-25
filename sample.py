import pickle
import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import tkinter as tk
from tkinter import StringVar, Label, Button, Frame
from PIL import Image, ImageTk
import threading
import time
import warnings
from gtts import gTTS
import os
from googletrans import Translator

warnings.filterwarnings("ignore", category=UserWarning)

# Load Model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Mediapipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.5, max_num_hands=1)

# Text-to-Speech setup
engine = pyttsx3.init()
translator = Translator()

# Label mapping
labels_dict = {i: chr(65 + i) for i in range(26)}  # A-Z
labels_dict.update({26: ' ', 27: '.'})  # Space & Period
expected_features = 42

# Buffers
word_buffer = ""
sentence = ""
current_alphabet = StringVar(value="N/A")
current_word = StringVar(value="N/A")
current_sentence = StringVar(value="N/A")
translated_telugu = StringVar(value="N/A")

# Function to speak text
def speak_text(text, lang='en'):
    if lang == 'te':  # Telugu conversion
        translated = translator.translate(text, src='en', dest='te').text
        translated_telugu.set(translated)
        tts = gTTS(text=translated, lang='te')
        tts.save("output.mp3")
        os.system("afplay output.mp3")  # macOS audio playback
    else:
        engine.say(text)
        engine.runAndWait()

def reset_sentence():
    global word_buffer, sentence
    word_buffer, sentence = "", ""
    current_word.set("N/A")
    current_sentence.set("N/A")
    translated_telugu.set("N/A")
    current_alphabet.set("N/A")

# GUI Setup
root = tk.Tk()
root.title("Sign Language to Speech Conversion")
root.geometry("1400x700")
root.configure(bg="#2c2f33")
root.resizable(False, False)

# Layout Frames
video_frame = Frame(root, bg="#2c2f33", bd=5, relief="solid", width=500, height=400)
video_frame.grid(row=1, column=0, rowspan=3, padx=20, pady=20)
video_label = tk.Label(video_frame)
video_label.pack(expand=True)

content_frame = Frame(root, bg="#2c2f33")
content_frame.grid(row=1, column=1, sticky="n", padx=(20, 40), pady=(60, 20))

button_frame = Frame(root, bg="#2c2f33")
button_frame.grid(row=3, column=1, pady=(10, 20), padx=(10, 20), sticky="n")

# Labels
Label(content_frame, text="Current Alphabet:", font=("Arial", 20), fg="#ffffff", bg="#2c2f33").pack(anchor="w")
Label(content_frame, textvariable=current_alphabet, font=("Arial", 24, "bold"), fg="#1abc9c", bg="#2c2f33").pack(anchor="center")

Label(content_frame, text="Current Word:", font=("Arial", 20), fg="#ffffff", bg="#2c2f33").pack(anchor="w")
Label(content_frame, textvariable=current_word, font=("Arial", 20), fg="#f39c12", bg="#2c2f33").pack(anchor="center")

Label(content_frame, text="Sentence:", font=("Arial", 20), fg="#ffffff", bg="#2c2f33").pack(anchor="w")
Label(content_frame, textvariable=current_sentence, font=("Arial", 20), fg="#9b59b6", bg="#2c2f33").pack(anchor="center")

Label(content_frame, text="Telugu Translation:", font=("Arial", 20), fg="#ffffff", bg="#2c2f33").pack(anchor="w")
Label(content_frame, textvariable=translated_telugu, font=("Arial", 20), fg="#e67e22", bg="#2c2f33").pack(anchor="center")

# Buttons
Button(button_frame, text="Reset", font=("Arial", 16), command=reset_sentence, bg="#e74c3c", fg="#ffffff").grid(row=0, column=0, padx=10)
Button(button_frame, text="Speak (Eng)", font=("Arial", 16), command=lambda: speak_text(current_sentence.get(), 'en'), bg="#27ae60", fg="#ffffff").grid(row=0, column=1, padx=10)
Button(button_frame, text="Speak (Telugu)", font=("Arial", 16), command=lambda: speak_text(current_sentence.get(), 'te'), bg="#9b59b6", fg="#ffffff").grid(row=0, column=2, padx=10)

# Video Capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

def process_frame():
    global word_buffer, sentence
    ret, frame = cap.read()
    if not ret:
        return

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            data_aux = [coord for lm in hand_landmarks.landmark for coord in (lm.x, lm.y)]
            data_aux = data_aux[:expected_features] + [0] * (expected_features - len(data_aux))
            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]
            current_alphabet.set(predicted_character)
            
            if predicted_character in labels_dict.values():
                if predicted_character == ' ':
                    sentence += word_buffer + " "
                    current_sentence.set(sentence.strip())
                    word_buffer = ""
                else:
                    word_buffer += predicted_character
                current_word.set(word_buffer)

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    video_label.imgtk = ImageTk.PhotoImage(image=img)
    video_label.configure(image=video_label.imgtk)
    root.after(10, process_frame)

process_frame()
root.mainloop()