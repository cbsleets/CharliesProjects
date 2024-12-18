from obswebsocket import obsws, requests
import random
import requests as http_requests
import pygame
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from queue import PriorityQueue
import time
import os
import uuid
import openai


# OBS WebSocket connection details
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""

# Initialize WebSocket connection
ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
ws.connect()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Queue to manage audio playback
audio_queue = PriorityQueue()

# Event to keep the audio queue processing thread running
keep_running = threading.Event()
keep_running.set()

# Your Eleven Labs API key
API_KEY = ""

openai.api_key = ""

# Your cloned voice ID from Eleven Labs (replace with the new voice ID if different)
VOICE_ID = ""

# Scene item names
IDLE_ITEM = "PerchIdle"
TALKING_ITEM = "PerchTalking1"
SCENE_NAME = "PerchPerkins1"  # Replace with your actual scene name


# Initialize pygame mixer
pygame.mixer.init()

# Audio files mapping
AUDIO_FILES = {
""
}

SPECIAL_ENDINGS = [
""
]
HI_ENDINGS = [
""
]

FOLLOW_RESPONSES = [
""
]

LIKES_RESPONSES = [
""
]

SHARE_RESPONSES = [
""
]

# SpongeBob character dictionary with personalized ending messages
SPONGEBOB_CHARACTERS = {
    "SpongeBob": "SpongeBob thanks you for making his day the best ever!",
    "Patrick": "Patrick says, 'Wow, you're smarter than I thought!'",
    "Squidward": "Squidward appreciates your generosity, but please don't disturb his clarinet practice!",
    "MrKrabs": "Mr. Krabs is thrilled and shouts, 'Money, money, money!'",
    "Sandy": "Sandy says, 'Yeehaw! You're the best thing to happen since Texas!'"
}

BREAKING_NEWS_AUDIO = ""

def ensure_mixer_initialized():
    """Ensure the pygame mixer is initialized."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()

def get_perch_perkins_response(user_input):
    """Get a ChatGPT response in character as Perch Perkins."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Perch Perkins, a news reporter from Bikini Bottom. Stay in character and respond with a news anchor style."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error with ChatGPT API: {e}")
        return "Sorry, I encountered an issue fetching the news!"

def toggle_dance(source_name, filters, loop=True):
    """
    Toggle dance loop by enabling/disabling Move Source filters.
    :param source_name: Name of the source in OBS.
    :param filters: List of Move Source filter names to toggle.
    :param loop: Whether to enable or disable the loop.
    """
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    ws.connect()
    print(f"{'Starting' if loop else 'Stopping'} dance loop for {source_name}")

    try:
        for filter_name in filters:
            ws.call(requests.SetSourceFilterEnabled(sourceName=source_name, filterName=filter_name, filterEnabled=loop))
            time.sleep(0.1)  # Small delay for smooth transitions
    except Exception as e:
        print(f"Error toggling dance: {e}")
    finally:
        ws.disconnect()
        print(f"{'Started' if loop else 'Stopped'} dance loop.")

def toggle_scene_item(scene_name, item_name, visibility):
    """
    Toggle visibility of a scene item.
    :param scene_name: The name of the scene.
    :param item_name: The name of the item in the scene.
    :param visibility: True to show, False to hide.
    """
    try:
        # Retrieve the scene item ID
        response = ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=item_name))
        scene_item_id = response.getSceneItemId()

        if scene_item_id is None:
            print(f"Could not retrieve sceneItemId for {item_name} in {scene_name}")
            return

        # Use the correct field `sceneItemEnabled` to set visibility
        ws.call(requests.SetSceneItemEnabled(sceneName=scene_name, sceneItemId=scene_item_id, sceneItemEnabled=visibility))
        print(f"Set visibility for {item_name} in {scene_name} to {visibility}")
    except Exception as e:
        print(f"Error toggling scene item {item_name} in scene {scene_name}: {e}")

def play_audio_file(file_path):
    """Play an audio file using pygame."""
    try:
        ensure_mixer_initialized()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.5)
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing audio file {file_path}: {e}")

# Function to play audio and control scene visibility
def play_audio_with_scene_control(file_path):
    try:
        ensure_mixer_initialized()
        toggle_scene_item(SCENE_NAME,TALKING_ITEM, True)  # Show Talking scene
        toggle_scene_item(SCENE_NAME, IDLE_ITEM, False)   # Hide Idle scene

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(0.5)
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing audio file {file_path}: {e}")
    finally:
        toggle_scene_item(SCENE_NAME,TALKING_ITEM, False)  # Hide Talking scene
        toggle_scene_item(SCENE_NAME,IDLE_ITEM, True)   # Show Idle scene

def handle_donut_sequence(tts_file):
    """Handle the Donut sequence with a fun dance."""
    try:
        if tts_file:
            # Play the TTS file with Talking animation
            play_audio_with_scene_control(tts_file)

        # Enable dancing scene and song
        print("Starting dance sequence...")
        toggle_scene_item(SCENE_NAME,IDLE_ITEM,False)
        toggle_scene_item(SCENE_NAME, "PerchDancing", True)
        toggle_scene_item(SCENE_NAME, "DanceSong", True)

        # Start the disco effect in a separate thread to avoid blocking
        disco_thread = threading.Thread(target=disco_effect, args=("Media Source 4", "DiscoEffect", 13))
        disco_thread.start()

        # Wait for 13 seconds
        time.sleep(13)

        # Disable dancing scene and song, return to idle
        toggle_scene_item(SCENE_NAME, "PerchDancing", False)
        toggle_scene_item(SCENE_NAME, "DanceSong", False)
        toggle_scene_item(SCENE_NAME, IDLE_ITEM, True)

        # Wait for the disco thread to finish
        disco_thread.join()
        print("Dance sequence ended. Back to idle.")
    except Exception as e:
        print(f"Error during Donut action: {e}")
    finally:
        if tts_file and os.path.exists(tts_file):
            try:
                pygame.mixer.quit()
                os.remove(tts_file)
                print(f"Deleted temporary TTS file: {tts_file}")
            except Exception as e:
                print(f"Error deleting TTS file {tts_file}: {e}")

def disco_effect(source_name, filter_name, duration=13, interval=0.1):
    """
    Create a disco effect by changing the hue of a source over a duration.
    :param source_name: The name of the source to apply the effect.
    :param filter_name: The name of the color correction filter.
    :param duration: Total duration of the effect in seconds.
    :param interval: Time interval between hue changes in seconds.
    """
    ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
    ws.connect()

    try:
        print("Starting disco effect...")
        start_time = time.time()
        hue = 0  # Initial hue value

        while time.time() - start_time < duration:
            # Set the hue value in the filter
            ws.call(requests.SetSourceFilterSettings(
                sourceName=source_name,
                filterName=filter_name,
                filterSettings={"hue_shift": hue}
            ))
            # Increment hue and loop back to 0 after 360
            hue = (hue + 30) % 360
            time.sleep(interval)

        # Reset the hue to 0 after the effect
        ws.call(requests.SetSourceFilterSettings(
            sourceName=source_name,
            filterName=filter_name,
            filterSettings={"hue_shift": 0}
        ))
        print("Disco effect ended.")
    except Exception as e:
        print(f"Error during disco effect: {e}")
    finally:
        ws.disconnect()

def generate_tts_file(text):
    """Generate TTS audio file using Eleven Labs and return the file path."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": API_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.9, "similarity_boost": 0.95},
        "uuid_idempotency_token": str(uuid.uuid4())
    }
    response = http_requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        unique_filename = f"temp_audio_{uuid.uuid4().hex}.mp3"
        with open(unique_filename, "wb") as temp_file:
            temp_file.write(response.content)
        return unique_filename
    else:
        print(f"Error generating TTS: {response.status_code} - {response.text}")
        return None

def handle_tts_action(tts_file):
    """Play TTS file, then play random ending based on conditions."""
    try:
        play_audio_with_scene_control(tts_file)
        rnd_choice = random.randint(1, 6)  # Use alias to avoid conflict with random module
        if rnd_choice <= 4:
            play_audio_with_scene_control(random.choice(HI_ENDINGS))
        elif rnd_choice == 5:
            play_audio_with_scene_control(random.choice(SPECIAL_ENDINGS))
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()  # Ensure pygame releases the file
        time.sleep(0.1)  # Slight delay to allow file release
        try:
            os.remove(tts_file)
        except Exception as e:
            print(f"Error deleting temp audio file: {e}")

def handle_gift_tts_action(tts_file):
    """Play TTS file, then play random ending based on conditions."""
    try:
        play_audio_with_scene_control(tts_file)
    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()  # Ensure pygame releases the file
        time.sleep(0.1)  # Slight delay to allow file release
        try:
            os.remove(tts_file)
        except Exception as e:
            print(f"Error deleting temp audio file: {e}")

def handle_breaking_news_action(username, tts_file, character):
    """Handle Breaking News scene for high-value gifts."""
    try:
        # Step 1: Switch to BreakingNewsScene
        ws.call(requests.SetCurrentProgramScene(sceneName="BreakingNewsScene"))
        print("Switched to BreakingNewsScene")

        # Step 2: Show BreakingNews image and play "Breaking News" audio
        toggle_scene_item("BreakingNewsScene", "BreakingNews", True)
        play_audio_file(BREAKING_NEWS_AUDIO)
        toggle_scene_item("BreakingNewsScene", "BreakingNews", False)

        # Step 3: Show PerchTalking and character image, and play TTS
        toggle_scene_item("BreakingNewsScene", "PerchTalking", True)
        toggle_scene_item("BreakingNewsScene", character, True)
        play_audio_file(tts_file)
        toggle_scene_item("BreakingNewsScene", character, False)

        # Step 4: Return to idle state and original scene
        toggle_scene_item("BreakingNewsScene", "PerchTalking", False)
        toggle_scene_item("BreakingNewsScene", "PerchIdle", True)
        ws.call(requests.SetCurrentProgramScene(sceneName=SCENE_NAME))  # Back to default scene

        pygame.mixer.quit()
        # Clean up TTS file
        os.remove(tts_file)
    except Exception as e:
        print(f"Error handling Breaking News action: {e}")

def play_random_follow_response():
    """Play a random follow response."""
    play_audio_with_scene_control(random.choice(FOLLOW_RESPONSES))

def play_random_like_response():
    """Play a random Like response"""
    play_audio_with_scene_control(random.choice(LIKES_RESPONSES))

def play_random_share_response():
    """Play a random share response"""
    play_audio_with_scene_control(random.choice(SHARE_RESPONSES))

# Process audio queue
def process_audio_queue():
    while keep_running.is_set():
        if not audio_queue.empty():
            priority, action_name, data = audio_queue.get()
            if action_name == "HiUsername":
                handle_tts_action(data)
            elif action_name == "Donut":
                handle_donut_sequence(data)
            elif action_name == "Follow":
                play_audio_with_scene_control(data)
                pygame.mixer.quit()
                os.remove(data)
                play_audio_with_scene_control(random.choice(SPECIAL_ENDINGS))
            elif action_name == "Like":
                play_random_like_response()
            elif action_name == "Share":
                play_random_share_response()
            elif action_name == "BreakingNews":
                username, tts_file, character = data
                handle_breaking_news_action(username, tts_file, character)  # Call the breaking news handler
            elif action_name == "ChatMessage":
                # Play the ChatGPT-generated TTS response
                play_audio_with_scene_control(data)
            else: 
                play_audio_with_scene_control(data)
            audio_queue.task_done()
        else:
            time.sleep(0.1)

# Adjust priority based on gift type and ensure HiUsername actions have a distinct priority
@app.route('/api/features/actions/exec', methods=['POST'])
def handle_action():
    data = request.json
    action_id = data.get("actionId")
    coins = data.get("coins", data.get("gift_value", 0))  # Fallback for alternative fields
    print(f"Action ID: {action_id}, Coins: {coins}")  # Debugging parsed values
    priority = 5  # Default priority if no conditions change it

    if action_id == "MiscGift":
        # Generate TTS message and file
        username = data.get("context", {}).get("nickname")
        character, ending_message = random.choice(list(SPONGEBOB_CHARACTERS.items()))
        tts_message = (
            f"{username} has sent us an absolutely MASSIVE gift! "
            f"{ending_message}"
        )
        tts_file = generate_tts_file(tts_message)
        if not tts_file:
            print("Failed to generate TTS file")
            return jsonify({"message": "Failed to generate TTS audio"}), 500

        # Enqueue Breaking News action
        audio_queue.put((1, "BreakingNews", (username, tts_file, character)))
        return jsonify({"message": "Breaking News queued successfully!"})
    elif action_id == "ChatMessage":
        # Extract the user's message from the request
        user_message = data.get("context", {}).get("message", "What's the news?")
        username = data.get("context", {}).get("username", "Viewer")

        # Generate a response from ChatGPT
        perch_response = get_perch_perkins_response(user_message)
        print(f"Generated Perch Perkins response: {perch_response}")

        # Generate TTS for the ChatGPT response
        tts_file = generate_tts_file(f"{username}, {perch_response}")
        if not tts_file:
            print("Failed to generate TTS file for ChatMessage")
            return jsonify({"message": "Failed to generate TTS audio"}), 500

        # Enqueue the ChatMessage action with the TTS file
        audio_queue.put((3, "ChatMessage", tts_file))
        return jsonify({"message": "ChatMessage action queued successfully!"})
    elif action_id == "Donut":
        username = data.get("context", {}).get("username", "Viewer")
        # Generate a TTS message
        tts_message = f"Thank's for the Donut '{username}! Here's a fun dance for you!"
        tts_file = generate_tts_file(tts_message)
        if tts_file:
            audio_queue.put((1, action_id, tts_file))  # Use fixed priority for HiUsername greetings
            return jsonify({"message": "Added Donut action with dance sequence to the queue"})
        else:
            return jsonify({"message": "Failed to generate TTS audio"}), 500
    elif action_id in AUDIO_FILES:
        file_path = AUDIO_FILES[action_id]
        # Assign priorities based on coins or specific gifts
        if coins > 1:
            priority = 1  # High priority for big gifts
            print("HI!")
        elif coins > 0:
            priority = 2  # Medium priority for smaller gifts
        else:
            priority = 4  # Low priority for small repetitive gifts like roses
        audio_queue.put((priority, action_id, file_path))
        return jsonify({"message": f"Added {action_id} to the queue with priority {priority}"})
    
    elif action_id == "HiUsername":
        # Ensure a unique priority level for HiUsername and implement cooldown if needed
        username = data.get("context", {}).get("nickname")
        tts_message = f"Hi {username}!"
        tts_file = generate_tts_file(tts_message)
        if tts_file:
            audio_queue.put((5, action_id, tts_file))  # Use fixed priority for HiUsername greetings
            return jsonify({"message": "Added TTS greeting to the queue"})
        else:
            return jsonify({"message": "Failed to generate TTS audio"}), 500
    elif action_id in ["Follow", "Like", "Share"]:
        priority = 3  # Specific priority for follow actions
        username = data.get("context", {}).get("username", "Viewer")
    
        # Generate a TTS message based on the action
        if action_id == "Follow":
            tts_message = f"Thank you for the follow, {username}!"
            tts_file = generate_tts_file(tts_message)
        elif action_id == "Like":
            tts_message = f"Thanks for the like, {username}!"
            tts_file = generate_tts_file(tts_message)
        elif action_id == "Share":
            tts_message = f"Appreciate the share, {username}!"
            tts_file = generate_tts_file(tts_message)
        else:
            tts_file = None  # Default to None if no TTS is needed
    
        if tts_file:
            audio_queue.put((priority, action_id, tts_file))  # Add to the queue with TTS
            return jsonify({"message": f"Added {action_id} response to the queue"})
        else:
            return jsonify({"message": "Failed to generate TTS audio"}), 500
    
# Flask app endpoints
@app.route('/api/app/info', methods=['GET'])
def app_info():
    return jsonify({"data": {"author": "YourName", "name": "SpongebobFishScript", "version": "1.0"}})

@app.route('/api/features/categories', methods=['GET'])
def get_categories():
    return jsonify({"data": [{"categoryId": "audio_control", "categoryName": "Audio Control"}]})

@app.route('/api/features/actions', methods=['GET'])
def get_actions():
    category_id = request.args.get("categoryId")
    if category_id == "audio_control":
        actions = [{"actionId": action_id, "actionName": f"Play {action_id} audio"} for action_id in AUDIO_FILES]
        actions.append({"actionId": "HiUsername", "actionName": "Say Hi to Username"})
        actions.append({"actionId": "Follow", "actionName": "Random Follow Response"})
        actions.append({"actionId": "Like", "actionName": "Random Like Response"})
        actions.append({"actionId": "Share", "actionName": "Random Share Response"})
        actions.append({"actionId": "Donut", "actionName": "Donut Gift"})
        actions.append({"actionId": "MiscGift", "actionName": "Misc Big Gift"})
        actions.append({"actionId": "ChatMessage", "actionName":"Chat Message"})
        return jsonify({"data": actions})
    return jsonify({"data": []})

if __name__ == "__main__":
    # Start the audio processing thread
    audio_thread = threading.Thread(target=process_audio_queue)
    audio_thread.start()

    # Run the Flask app
    try:
        app.run(port=8832)
    finally:
        keep_running.clear()
        audio_thread.join()
        ws.disconnect()