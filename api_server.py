from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import webbrowser
from calendar_tool import book_meeting, check_availability

app = Flask(__name__)
CORS(app)

def open_local_app(app_name: str) -> str:
    app_name_lower = app_name.lower().strip()
    
    # Common mappings for macOS applications and websites
    app_map = {
        "whatsapp": ("WhatsApp", None),
        "chrome": ("Google Chrome", None),
        "google chrome": ("Google Chrome", None),
        "safari": ("Safari", None),
        "spotify": ("Spotify", None),
        "slack": ("Slack", None),
        "zoom": ("zoom.us", None),
        "calculator": ("Calculator", None),
        "notes": ("Notes", None),
        "calendar": ("Calendar", None),
        "youtube": (None, "https://www.youtube.com"),
        "gmail": (None, "https://mail.google.com"),
        "github": (None, "https://github.com"),
    }
    
    if app_name_lower in app_map:
        mac_name, url = app_map[app_name_lower]
        if url:
            webbrowser.open(url)
            return f"Successfully opened {app_name}."
        else:
            try:
                subprocess.run(["open", "-a", mac_name], check=True)
                return f"Successfully opened {app_name}."
            except Exception as e:
                return f"Failed to open desktop app {app_name}. Error: {str(e)}"
    
    # General fallback: try as macOS application name first, then URL/Google search
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Successfully opened {app_name}."
    except Exception:
        if app_name_lower.startswith("http://") or app_name_lower.startswith("https://"):
            webbrowser.open(app_name)
            return f"Successfully opened URL: {app_name}."
        else:
            search_url = f"https://www.google.com/search?q={app_name}"
            webbrowser.open(search_url)
            return f"Could not find application {app_name}. Opened a web search instead."

@app.route('/api/book_meeting', methods=['POST'])
def handle_booking():
    data = request.json
    print(f"\n🔔 [API REQUEST] Booking {data.get('title')} at {data.get('date_time')}")
    result = book_meeting(date_time_iso=data.get('date_time'), name=data.get('guest_email'))
    print(f"✅ [API RESPONSE] {result}")
    return jsonify({"result": result})

@app.route('/api/check_availability', methods=['POST'])
def handle_availability():
    data = request.json
    print(f"\n📅 [API REQUEST] Checking availability for {data.get('date')}")
    result = check_availability(date_iso=data.get('date'))
    print(f"✅ [API RESPONSE] {result}")
    return jsonify({"result": result})

@app.route('/api/open_application', methods=['POST'])
def handle_open_application():
    data = request.json
    app_name = data.get('application_name')
    print(f"\n🚀 [API REQUEST] Opening application: {app_name}")
    result = open_local_app(app_name)
    print(f"✅ [API RESPONSE] {result}")
    return jsonify({"result": result})

@app.route('/api/generate_image', methods=['POST'])
def handle_generate_image():
    data = request.json
    prompt = data.get('prompt')
    print(f"\n🎨 [API REQUEST] Generating image for prompt: {prompt}")
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&nologo=true"
    print(f"✅ [API RESPONSE] Image URL: {image_url}")
    return jsonify({"result": "Image generated successfully.", "image_url": image_url})

if __name__ == '__main__':
    print("🚀 Local API Bridge running on http://127.0.0.1:5000")
    app.run(port=5000)
