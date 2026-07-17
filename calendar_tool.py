import os
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

def get_calendar_service():
    # 1. Try to load token from environment variable first (cloud-native)
    token_json_env = os.getenv("GOOGLE_TOKEN_JSON")
    if token_json_env:
        import json
        info = json.loads(token_json_env)
        creds = Credentials.from_authorized_user_info(info, ['https://www.googleapis.com/auth/calendar.events'])
        return build('calendar', 'v3', credentials=creds)

    # 2. Fall back to local file load resolved relative to this script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, 'token.json')

    if not os.path.exists(token_path):
        raise Exception("Calendar is not authenticated. Missing token.json or GOOGLE_TOKEN_JSON env variable.")
    creds = Credentials.from_authorized_user_file(token_path, ['https://www.googleapis.com/auth/calendar.events'])
    return build('calendar', 'v3', credentials=creds)
# In-memory mock calendar database
_MOCK_EVENTS = [
    {"summary": "Design review sync", "date": "2026-07-18", "start": "10:00", "end": "10:30"},
    {"summary": "Lunch break", "date": "2026-07-18", "start": "13:00", "end": "14:00"},
]

def check_availability(date_iso: str) -> str:
    """Checks Google Calendar for busy slots on a specific date."""
    # Cross-platform / cross-version robust ISO datetime parsing
    try:
        dt = datetime.datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
    except ValueError:
        # Clean string format fallback if older Python versions struggle with suffix colons or milliseconds
        clean_str = date_iso.split('.')[0].split('+')[0].split('-')[0]
        if len(clean_str) > 10:
            dt = datetime.datetime.strptime(clean_str[:19], "%Y-%m-%dT%H:%M:%S")
        else:
            dt = datetime.datetime.strptime(clean_str[:10], "%Y-%m-%d")
            
    date_str = dt.strftime('%Y-%m-%d')
    
    try:
        service = get_calendar_service()
        
        start_of_day = dt.replace(hour=0, minute=0, second=0).isoformat()
        end_of_day = dt.replace(hour=23, minute=59, second=59).isoformat()
        
        calendar_id = os.getenv("HOST_CALENDAR_ID", "primary")
        
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=start_of_day, timeMax=end_of_day, 
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return f"The calendar is completely free on {date_str}."
            
        busy_times = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'Busy')
            busy_times.append(f"- Blocked from {start} to {end} ({summary})")
            
        return f"Existing events on {date_str}:\n" + "\n".join(busy_times)
        
    except Exception as e:
        # Fallback to Mock Calendar
        print(f"⚠️ [MOCK CALENDAR] Using mock database: {e}")
        
        day_events = [ev for ev in _MOCK_EVENTS if ev["date"] == date_str]
        if not day_events:
            return f"The calendar is completely free on {date_str} (Mock Calendar)."
            
        busy_times = []
        for ev in day_events:
            busy_times.append(f"- Blocked from {ev['start']} to {ev['end']} ({ev['summary']})")
            
        return f"Existing events on {date_str} (Mock Calendar):\n" + "\n".join(busy_times)

def book_meeting(date_time_iso: str, name: str = "User") -> str:
    """Creates a 30-minute Google Calendar meeting."""
    try:
        start_time = datetime.datetime.fromisoformat(date_time_iso.replace('Z', '+00:00'))
    except ValueError:
        clean_str = date_time_iso.split('.')[0].split('+')[0].split('-')[0]
        start_time = datetime.datetime.strptime(clean_str[:19], "%Y-%m-%dT%H:%M:%S")
        
    end_time = start_time + datetime.timedelta(minutes=30)
    date_str = start_time.strftime('%Y-%m-%d')
    start_time_str = start_time.strftime('%H:%M')
    end_time_str = end_time.strftime('%H:%M')
    
    try:
        service = get_calendar_service()
        calendar_id = os.getenv("HOST_CALENDAR_ID", "primary")

        event = {
            'summary': f'NovaVoice Demo: {name}',
            'description': 'Automated booking created via Gemini Live AI Calling Assistant.',
            'start': {'dateTime': start_time.isoformat()},
            'end': {'dateTime': end_time.isoformat()},
        }

        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"✅ REAL CALENDAR BOOKING SUCCESS: {event_result.get('htmlLink')}")
        return f"Success! Meeting booked on Google Calendar for {name}."
        
    except Exception as e:
        # Fallback to Mock Calendar
        print(f"⚠️ [MOCK CALENDAR] Booking mock meeting: {e}")
        
        new_event = {
            "summary": f"NovaVoice Demo: {name}",
            "date": date_str,
            "start": start_time_str,
            "end": end_time_str
        }
        _MOCK_EVENTS.append(new_event)
        return f"Success! Meeting booked on Mock Calendar for {name}."