from flask import Flask, send_file, jsonify, request
from telethon import TelegramClient, events
import json
import os
import asyncio
from threading import Thread

app = Flask(__name__)

# ========== ВАШИ ДАННЫЕ ==========
API_ID = '37818079'
API_HASH = '1568fa6df3d7ddb1b26f758dc96cfce8'
BOT_TOKEN = '8003441506:AAHg2z317ew9KZn3Jo60T__f740BcnZaJmU'
CHANNEL_ID = -1001378493465
# =================================

playlist_file = 'playlist.json'
playlist = []

# Загружаем плейлист
def load_playlist():
    global playlist
    if os.path.exists(playlist_file):
        with open(playlist_file, 'r', encoding='utf-8') as f:
            playlist = json.load(f)
    return playlist

# Сохраняем плейлист
def save_playlist(data):
    with open(playlist_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# API для плеера
@app.route('/')
def index():
    return send_file('static/index.html')

@app.route('/playlist')
def get_playlist():
    return jsonify({
        'success': True,
        'tracks': load_playlist(),
        'count': len(playlist)
    })

# Запуск Telegram бота
async def start_bot():
    try:
        print("🤖 Запускаю бота...")
        print(f"📡 API_ID: {API_ID}")
        print(f"🔑 API_HASH: {API_HASH[:10]}...")
        print(f"🤖 BOT_TOKEN: {BOT_TOKEN[:10]}...")
        print(f"📢 CHANNEL_ID: {CHANNEL_ID}")
        
        client = TelegramClient('player_club_bot', int(API_ID), API_HASH)
        await client.start(bot_token=BOT_TOKEN)
        
        print("✅ Бот авторизован в Telegram")
        
        @client.on(events.NewMessage(chats=CHANNEL_ID))
        async def handler(event):
            if event.message.audio:
                audio = event.message.audio
                
                track = {
                    'id': audio.id,
                    'title': audio.title or 'Без названия',
                    'artist': audio.performer or 'Неизвестный исполнитель',
                    'duration': audio.duration or 0,
                    'url': f'https://t.me/c/{str(CHANNEL_ID)[4:]}/{event.message.id}'
                }
                
                playlist = load_playlist()
                
                # Проверяем, нет ли уже такого трека
                if not any(t['id'] == track['id'] for t in playlist):
                    playlist.insert(0, track)
                    playlist = playlist[:500]  # максимум 500 треков
                    save_playlist(playlist)
                    
                    print(f'🎵 Добавлен: {track["title"]} - {track["artist"]}')
                else:
                    print(f'⚠️ Трек уже есть: {track["title"]}')
        
        print(f"👂 Бот слушает канал ID: {CHANNEL_ID}")
        print("💡 Добавляйте аудиофайлы в канал - они автоматически появятся в плеере!")
        
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {type(e).__name__}: {e}")
        print("🔄 Перезапуск через 30 секунд...")
        await asyncio.sleep(30)
        await start_bot()

def run_bot():
    asyncio.run(start_bot())

# Простая проверка API
@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'service': 'PLAYER CLUB',
        'playlist_count': len(load_playlist()),
        'bot_configured': bool(BOT_TOKEN and API_ID and API_HASH)
    })

if __name__ == '__main__':
    # Создаем папки если нет
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Создаем файл плейлиста если нет
    if not os.path.exists(playlist_file):
        save_playlist([])
    
    # Запускаем бота в фоне
    bot_thread = Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем сервер
    print("=" * 50)
    print("🌐 PLAYER CLUB Music Server")
    print("=" * 50)
    print(f"📁 Плейлист: {playlist_file}")
    print(f"🎵 Треков в плейлисте: {len(load_playlist())}")
    print(f"🔗 API плейлиста: /playlist")
    print(f"📊 Статус системы: /status")
    print(f"🎮 Плеер: /")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
