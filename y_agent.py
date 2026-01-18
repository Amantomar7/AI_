import webbrowser
import os
from google import genai
from dotenv import load_dotenv
import yt_dlp
import speech_recognition as sr

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

def search_youtube_for_url(query: str):
    """Searches YouTube using yt-dlp for a more stable result."""
    print(f"Logic: Searching YouTube for '{query}'...")
    
    # ydl_opts configures yt-dlp to just get the URL, not download anything
    ydl_opts = {
        'quiet': True,
        'default_search': 'ytsearch1', # Search and get 1 result
        'format': 'best'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                video = info['entries'][0]
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                print(f"Logic: Found '{video['title']}'")
                return video_url
        except Exception as e:
            print(f"Error: {e}")
            
    return "No YouTube link found."

# 1. Define your "Personal Assistant" Tools
def open_youtube_video(video_url: str):
    """Opens the URL in your Windows browser."""
    if "youtube.com" in video_url:
        os.system(f'cmd.exe /c "start {video_url}"')
        return f"Opened: {video_url}"
    return "Invalid link."

def surf_website(url: str):
    """Navigates to any website URL provided via Windows CMD."""
    # Use 'start' command through cmd.exe to open the URL in Windows
    os.system(f'cmd.exe /c "start {url}"')
    return f"Navigated to {url} on Windows browser."

# 2. Setup the Client and Tools
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# Combine your custom functions and Gemini's built-in Google Search
tools_list = [open_youtube_video, surf_website, search_youtube_for_url]

chat = client.chats.create(
    model="gemini-2.5-flash", # Best for tool-use speed in 2026
    config={'tools': tools_list}
)

def listen_to_user():
    """Captures audio from the mic and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index = 1) as source:
        print("\nListening... (Speak now)")
        # Adjust for ambient noise for better accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError as e:
        print("Speech service is down.", e)
        return None

# 3. Running the Agent Loop
print("Assistant: I can open YouTube, search the web, or surf sites for you.")
while True:
    # user_prompt = input("You: ")
    listened_text = listen_to_user()
    if listened_text:
        user_prompt = listened_text
    else:
        continue
    if user_prompt.lower() in ["exit", "quit"]: break
    # The 'chat' automatically executes the functions and returns the result to Gemini
    response = chat.send_message(user_prompt)
    print(f"Assistant: {response.text}")