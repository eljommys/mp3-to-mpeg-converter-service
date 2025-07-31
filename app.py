import os
from flask import Flask, request, send_file, jsonify, after_this_request
from pydub import AudioSegment
import tempfile

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({"error": "No selected file"}), 400

    if file.filename.endswith('.mp3'):
        temp_mp3_path = None
        temp_mpeg_path = None
        try:
            # Save the uploaded mp3 file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
                file.save(temp_mp3.name)
                temp_mp3_path = temp_mp3.name

            # Convert mp3 to mpeg
            audio = AudioSegment.from_mp3(temp_mp3_path)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mpeg') as temp_mpeg:
                audio.export(temp_mpeg.name, format='mp2')
                temp_mpeg_path = temp_mpeg.name

            @after_this_request
            def cleanup(response):
                if temp_mpeg_path and os.path.exists(temp_mpeg_path):
                    os.remove(temp_mpeg_path)
                return response

            return send_file(
                temp_mpeg_path,
                as_attachment=True,
                download_name=os.path.basename(file.filename).replace('.mp3', '.mpeg'),
                mimetype='audio/mpeg',
                max_age=0
            )

        except Exception as e:
            if temp_mpeg_path and os.path.exists(temp_mpeg_path):
                os.remove(temp_mpeg_path)
            return jsonify({"error": str(e)}), 500
        finally:
            if temp_mp3_path and os.path.exists(temp_mp3_path):
                os.remove(temp_mp3_path)
    else:
        return jsonify({"error": "Invalid file type, please upload an MP3 file"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
