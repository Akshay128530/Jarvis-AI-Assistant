# I switched the pyttsx3 library to edge-tts for better voice quality and more natural speech synthesis. The code now uses edge-tts to generate speech and plays it using pygame.
import speech_recognition as sr
import webbrowser
import edge_tts
import asyncio
import pygame
import os
import time
import requests  # The requests library is used to make HTTP requests to the API to fetch data
import re 
import json
from google import genai

r = sr.Recognizer()
newsapi = "1c209ea3d2c34d338ac6a5690e8aab4d"  # This is the API key for the NewsAPI service. You can get your own API key by signing up at https://newsapi.org/

gemini_api_key = os.getenv("GEMINI_API_KEY")
print("Gemini key found:", bool(gemini_api_key))
if gemini_api_key:
    client = genai.Client(api_key=gemini_api_key)
else:
    client = None

async def async_speak(text):
    filename = "voice.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-ChristopherNeural"   # You can change the voice later
    )

    await communicate.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.music.unload()
    os.remove(filename)


def speak(text):
    asyncio.run(async_speak(text))   # asyncio run is used to run the async function in a synchronous context

def get_weather(city):
    try:
        # Convert city name into latitude and longitude
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(geo_url, params=geo_params)
        geo_data = geo_response.json()

        if "results" not in geo_data:
            speak(f"Sorry, I couldn't find {city}.")
            return

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]

        # Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }

        weather_response = requests.get(weather_url, params=weather_params)
        weather_data = weather_response.json()

        current = weather_data["current"]

        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]

        # Convert weather code to readable text
        weather_conditions = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "foggy",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "heavy drizzle",
            61: "light rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "light snow",
            73: "moderate snow",
            75: "heavy snow",
            80: "rain showers",
            81: "moderate rain showers",
            82: "heavy rain showers",
            95: "thunderstorm"
        }

        condition = weather_conditions.get(
            weather_code,
            "unknown weather conditions"
        )

        message = (
            f"The current temperature in {city_name} is "
            f"{temperature} degrees Celsius with {condition}. "
            f"The humidity is {humidity} percent and the wind speed is "
            f"{wind_speed} kilometers per hour."
        )

        print(message)
        speak(message)

    except Exception as e:
        print("Weather Error:", e)
        speak("Sorry, I couldn't fetch the weather.")

def ask_gemini(question):

    if not client:
        print("Gemini API key is not configured.")
        speak("Gemini API key is not configured.")
        return

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=(
                "You are JARVIS, a helpful voice assistant. "
                "Answer clearly and briefly because your answer "
                "will be spoken aloud. "
                "Do not use markdown formatting.\n\n"
                f"User: {question}"
            )
        )
        answer = response.text.strip()

        print("Gemini:", answer)

        speak(answer)

    except Exception as e:

        print("Gemini Error:", e)

        speak(
            "Sorry, I couldn't connect to the AI service."
        )

def processCommand(c):
    print("process command called with :", c)
    print("Processing:", c)

    if "open google" in c.lower():
        print("Matched google command")
        speak("Opening Google")
        webbrowser.open("https://www.google.com")

    elif "open youtube" in c.lower():             # you can add more commands here for other websites or applications
        print("Matched youtube command")
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open whatsapp" in c.lower():
        print("Matched whatsapp command")
        speak("Opening WhatsApp")
        webbrowser.open("https://web.whatsapp.com/")
    elif "open facebook" in c.lower():
        print("Matched facebook command")
        speak("Opening Facebook")
        webbrowser.open("https://www.facebook.com/")
    elif "open instagram" in c.lower():
        print("Matched instagram command")
        speak("Opening Instagram")
        webbrowser.open("https://www.instagram.com/")
    elif "open linkedin" in c.lower():
        print("Matched linkedin command")
        speak("Opening LinkedIn")
        webbrowser.open("https://www.linkedin.com/")
    elif "open twitter" in c.lower():
        print("Matched twitter command")
        speak("Opening Twitter")
        webbrowser.open("https://twitter.com/")

    elif "weather" in c.lower():
        print("Fetching weather...")

        match = re.search(r"weather\s+in\s+(.+)", c, re.IGNORECASE)

        if match:
          city = match.group(1).strip()
          get_weather(city)
        else:
         get_weather("Ghaziabad")

    elif "news" in c.lower():
        print("Fetching news...")
        url = f"https://newsapi.org/v2/everything?q=India&language=en&sortBy=publishedAt&apiKey={newsapi}"  # This URL is constructed to fetch news articles related to India in English, sorted by the most recent publication date. The API key is included in the URL for authentication.
        print(url)
        r = requests.get(url)

        print("Status Code:", r.status_code) # The status code is printed to check if the request was successful (200 OK) or if there was an error (e.g., 404 Not Found, 500 Internal Server Error). This helps in debugging and understanding the response from the API.
        print(r.text)

        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])

            print("Articles found:", len(articles))

            for article in articles[:5]:
             print(article["title"])
             speak(article["title"])
        else:
         speak("Sorry, I couldn't fetch the news.")

    else:
        print("No built-in command matched. Asking Gemini...")
        ask_gemini(c)
       
if __name__ == "__main__":
    speak("Initializing Jarvis....")
    time.sleep(1)
    while True:
        # listen for wake word "jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()
       
        print("Recognizing...")
        # recognize speech using google

        try:
            with sr.Microphone() as source:
             r.adjust_for_ambient_noise(source,duration=1)   # adjust for ambient noise to improve recognition accuracy
             print("listening....")
             audio = r.listen(source ,timeout=5,phrase_time_limit=5)
            word = r.recognize_google(audio)                          # I used google speech recognition to convert audio to text
            print("heard: " + word)

            if "jarvis" in word.lower():             # if the wake word "jarvis" is detected, it first convert it to lowercase letters and then it will proceed to listen for commands
               print("Wake word detected!")
               speak("Yes Sir ")  
               time.sleep(0.5)
                
             # listening for commands after wake word
               with sr.Microphone() as source:
                 print("Jarvis active...")
                 r.adjust_for_ambient_noise(source, duration=0.5)

                 audio = r.listen(source, timeout=5, phrase_time_limit=5)   

                 command = r.recognize_google(audio)
                 print("Command:", command)
                 processCommand(command)
        
        except Exception as e:
            print("Error ; {0}".format(e))  # Print any errors that occur during speech recognition
