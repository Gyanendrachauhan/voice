import streamlit as st
import speech_recognition as sr
import openai
import sounddevice as sd
import wavio
from gtts import gTTS
import io
from decouple import config
openai.api_key = config('openai.api_key')





def transcribe_from_microphone():
    samplerate = 44100  # Sample rate
    duration = 5 # Duration in seconds
    st.write("Please speak into the microphone.")

    myrecording = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=2, dtype='int16')
    sd.wait()  # Wait until recording is finished

    recognizer = sr.Recognizer()

    # Convert the NumPy array to a WAV file in memory
    with io.BytesIO() as f:
        wavio.write(f, myrecording, samplerate, sampwidth=2)
        f.seek(0)
        with sr.WavFile(f) as source:
            audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language='en-US')
        return text
    except sr.UnknownValueError:
        return "Google Web Speech API could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Web Speech API; {e}"


def get_response_from_openai(text):
    response = openai.Completion.create(engine="text-davinci-003", prompt=text, max_tokens=300)
    return response.choices[0].text.strip()


def text_to_speech(text, language='en'):
    tts = gTTS(text=text, lang=language, slow=False)
    filename = "response.mp3"
    tts.save(filename)

    with open(filename, 'rb') as audio_file:
        audio_bytes = audio_file.read()
    return audio_bytes


if __name__ == '__main__':
    st.title("Speech Recognition and Response App")

    if st.button("Start Recording"):
        transcribed_text = transcribe_from_microphone()
        st.write(f"You said: {transcribed_text}")

        response_text = get_response_from_openai(transcribed_text)
        st.write(f"Response: {response_text}")

        audio_bytes = text_to_speech(response_text)
        st.audio(audio_bytes, format='audio/mp3')
