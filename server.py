from flask import Flask, send_file, jsonify
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/playlist')
def playlist():
    return jsonify({
        "success": True,
        "tracks": [
            {
                "title": "Демо трек 1",
                "artist": "Player Club", 
                "duration": 180,
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            },
            {
                "title": "Демо трек 2", 
                "artist": "Player Club",
                "duration": 200,
                "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3"
            }
        ]
    })

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(host='0.0.0.0', port=5000, debug=False)
