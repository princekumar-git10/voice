from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import webbrowser
from calendar_tool import book_meeting, check_availability

app = Flask(__name__)
CORS(app)

def open_local_app(app_name: str) -> dict:
    app_name_lower = app_name.lower().strip()
    
    # Common mappings for applications and web fallbacks
    app_map = {
        "whatsapp": ("WhatsApp", "whatsapp://"),
        "chrome": ("Google Chrome", "https://www.google.com"),
        "google chrome": ("Google Chrome", "https://www.google.com"),
        "safari": ("Safari", "https://www.google.com"),
        "spotify": ("Spotify", "spotify://"),
        "slack": ("Slack", "slack://"),
        "zoom": ("zoom.us", "zoommtg://"),
        "calculator": ("Calculator", "https://www.google.com/search?q=calculator"),
        "notes": ("Notes", "https://keep.google.com"),
        "calendar": ("Calendar", "https://calendar.google.com"),
        "youtube": (None, "https://www.youtube.com"),
        "gmail": (None, "https://mail.google.com"),
        "github": (None, "https://github.com"),
    }
    
    mac_name = None
    url = None
    if app_name_lower in app_map:
        mac_name, url = app_map[app_name_lower]
    else:
        if app_name_lower.startswith("http://") or app_name_lower.startswith("https://"):
            url = app_name
        else:
            url = f"https://www.google.com/search?q={app_name}"
            mac_name = app_name

    # Check if running locally on macOS
    import sys
    if sys.platform == "darwin":
        if mac_name:
            try:
                subprocess.run(["open", "-a", mac_name], check=True)
                return {"result": f"Successfully opened {app_name} locally.", "url": url}
            except Exception:
                pass
        
        if url:
            try:
                webbrowser.open(url)
                return {"result": f"Successfully opened {app_name} in your browser.", "url": url}
            except Exception:
                pass

    # Serverless fallback: pass URL back to the frontend browser
    return {"result": f"Instructed browser to open {app_name}.", "url": url}

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
    result_data = open_local_app(app_name)
    print(f"✅ [API RESPONSE] {result_data['result']}")
    return jsonify(result_data)

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
