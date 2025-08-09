import os
import time
import tempfile
import requests
from flask import Flask, request, jsonify
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID', '4hF8FODW3hjMTvUWqCxk')
HEYGEN_API_KEY = os.getenv('HEYGEN_API_KEY')
HEYGEN_AVATAR_ID = os.getenv('HEYGEN_AVATAR_ID', '2e4fd9de3aaa4f92bcda52fbe2161431')
TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')

def generate_speech_elevenlabs(text):
    """Generate speech using ElevenLabs API"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.85,
            "similarity_boost": 0.74,
            "style": 0.75,
            "use_speaker_boost": True,
            "speed": 1.08
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"ElevenLabs API error: {response.status_code} - {response.text}")

def convert_mp3_to_mpeg(mp3_data):
    """Convert MP3 to MPEG format"""
    temp_mp3_path = None
    temp_mpeg_path = None

    try:
        # Save MP3 data to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
            temp_mp3.write(mp3_data)
            temp_mp3_path = temp_mp3.name

        # Convert to MPEG
        audio = AudioSegment.from_mp3(temp_mp3_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mpeg') as temp_mpeg:
            audio.export(temp_mpeg.name, format='mp2')
            temp_mpeg_path = temp_mpeg.name

        # Read converted file
        with open(temp_mpeg_path, 'rb') as f:
            mpeg_data = f.read()

        return mpeg_data

    finally:
        # Cleanup temporary files
        if temp_mp3_path and os.path.exists(temp_mp3_path):
            os.remove(temp_mp3_path)
        if temp_mpeg_path and os.path.exists(temp_mpeg_path):
            os.remove(temp_mpeg_path)

def upload_asset_to_heygen(mpeg_data):
    """Upload MPEG asset to HeyGen"""
    url = "https://upload.heygen.com/v1/asset"

    headers = {
        "X-API-KEY": HEYGEN_API_KEY,
        "Content-Type": "audio/mpeg"
    }

    response = requests.post(url, data=mpeg_data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"HeyGen upload error: {response.status_code} - {response.text}")

def create_heygen_video(audio_asset_id):
    """Create video using HeyGen API"""
    url = "https://api.heygen.com/v2/video/generate"

    headers = {
        "X-API-KEY": HEYGEN_API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "caption": False,
        "dimension": {
            "width": 1080,
            "height": 1920
        },
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": HEYGEN_AVATAR_ID
                },
                "voice": {
                    "type": "audio",
                    "audio_asset_id": audio_asset_id
                }
            }
        ]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"HeyGen video creation error: {response.status_code} - {response.text}")

def check_video_status(video_id, max_attempts=60, wait_time=30):
    """Check video generation status with polling"""
    url = "https://api.heygen.com/v1/video_status.get"

    headers = {
        "X-API-KEY": HEYGEN_API_KEY
    }

    params = {
        "video_id": video_id
    }

    for attempt in range(max_attempts):
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get('data', {}).get('status')

            if status == 'completed':
                return status_data
            elif status == 'failed':
                raise Exception(f"Video generation failed: {status_data}")

            # Wait before next check
            time.sleep(wait_time)
        else:
            raise Exception(f"Status check error: {response.status_code} - {response.text}")

    raise Exception("Video generation timed out")

def send_teams_notification(title, video_url, references):
    """Send notification to Microsoft Teams (optional)"""
    if not TEAMS_WEBHOOK_URL:
        return

    message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "Nueva noticia generada",
        "sections": [{
            "activityTitle": "Te paso noticia nueva:",
            "activitySubtitle": title,
            "facts": [
                {
                    "name": "Referencias:",
                    "value": references
                }
            ],
            "potentialAction": [{
                "@type": "OpenUri",
                "name": "Descargar video",
                "targets": [{
                    "os": "default",
                    "uri": video_url
                }]
            }]
        }]
    }

    try:
        requests.post(TEAMS_WEBHOOK_URL, json=message)
    except Exception as e:
        print(f"Teams notification failed: {e}")

@app.route('/generate-video', methods=['POST'])
def generate_video():
    """Main endpoint that processes the complete workflow"""
    try:
        # Validate request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        script = data.get('Script', '').strip()
        title = data.get('Titulo', '').strip()
        references = data.get('Referencias', '').strip()

        if not script:
            return jsonify({"error": "Script is required"}), 400

        # Step 1: Generate speech with ElevenLabs
        print("Generating speech with ElevenLabs...")
        mp3_data = generate_speech_elevenlabs(script)

        # Step 2: Convert MP3 to MPEG
        print("Converting MP3 to MPEG...")
        mpeg_data = convert_mp3_to_mpeg(mp3_data)

        # Step 3: Upload asset to HeyGen
        print("Uploading asset to HeyGen...")
        asset_response = upload_asset_to_heygen(mpeg_data)
        audio_asset_id = asset_response.get('data', {}).get('id')

        if not audio_asset_id:
            raise Exception("Failed to get audio asset ID from HeyGen")

        # Step 4: Create video
        print("Creating video with HeyGen...")
        video_response = create_heygen_video(audio_asset_id)
        video_id = video_response.get('data', {}).get('video_id')

        if not video_id:
            raise Exception("Failed to get video ID from HeyGen")

        # Step 5: Wait for video completion
        print("Waiting for video completion...")
        final_status = check_video_status(video_id)
        video_url = final_status.get('data', {}).get('video_url')

        if not video_url:
            raise Exception("Failed to get video URL")

        # Step 6: Send Teams notification (optional)
        if TEAMS_WEBHOOK_URL:
            print("Sending Teams notification...")
            send_teams_notification(title, video_url, references)

        # Return success response
        return jsonify({
            "success": True,
            "message": "Video generated successfully",
            "data": {
                "video_id": video_id,
                "video_url": video_url,
                "audio_asset_id": audio_asset_id,
                "title": title,
                "references": references
            }
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "video-generator"})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with service information"""
    return jsonify({
        "service": "Video Generator API",
        "version": "1.0.0",
        "endpoints": {
            "/generate-video": "POST - Generate video from script",
            "/health": "GET - Health check"
        }
    })

if __name__ == '__main__':
    # Validate required environment variables
    if not ELEVENLABS_API_KEY:
        print("Warning: ELEVENLABS_API_KEY not set")
    if not HEYGEN_API_KEY:
        print("Warning: HEYGEN_API_KEY not set")

    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
