from flask import Flask, send_file, jsonify, request
from telethon import TelegramClient, events
import json
import os
import asyncio
from threading import Thread
import time

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
        try:
            with open(playlist_file, 'r', encoding='utf-8') as f:
                playlist = json.load(f)
        except:
            playlist = []
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
        print("=" * 50)
        print("🤖 ЗАПУСК ТЕЛЕГРАМ БОТА")
        print("=" * 50)
        print(f"📡 API_ID: {API_ID}")
        print(f"🔑 API_HASH: {API_HASH[:10]}...")
        print(f"🤖 BOT_TOKEN: {BOT_TOKEN[:15]}...")
        print(f"📢 CHANNEL_ID: {CHANNEL_ID}")
        print(f"📁 Playlist file: {playlist_file}")
        print("=" * 50)
        
        # Подключаемся к Telegram
        client = TelegramClient(
            session='player_club_session',
            api_id=int(API_ID),  # Конвертируем в число!
            api_hash=API_HASH,
            timeout=30,
            connection_retries=5
        )
        
        print("🔗 Подключаюсь к Telegram...")
        await client.start(bot_token=BOT_TOKEN)
        
        # Проверяем доступ к каналу
        try:
            channel = await client.get_entity(CHANNEL_ID)
            print(f"✅ Канал найден: {channel.title}")
        except Exception as e:
            print(f"❌ Не могу найти канал {CHANNEL_ID}: {e}")
            print("⚠️ Убедитесь что:")
            print("   1. Бот добавлен в канал как администратор")
            print("   2. CHANNEL_ID правильный (отрицательное число)")
            return
        
        print("✅ Бот авторизован в Telegram")
        print("👂 Слушаю сообщения в канале...")
        
        # Обработчик новых сообщений
        @client.on(events.NewMessage(chats=CHANNEL_ID))
        async def handler(event):
            print(f"📩 Новое сообщение в канале: ID={event.message.id}")
            
            if event.message.audio:
                audio = event.message.audio
                print(f"🎵 Найден аудиофайл: {audio.title or 'Без названия'}")
                
                track = {
                    'id': str(audio.id),
                    'title': audio.title or 'Без названия',
                    'artist': audio.performer or 'Неизвестный исполнитель',
                    'duration': audio.duration or 0,
                    'url': f'https://t.me/c/{str(CHANNEL_ID)[4:]}/{event.message.id}',
                    'date': time.time()
                }
                
                # Загружаем текущий плейлист
                current_playlist = load_playlist()
                
                # Проверяем дубликаты
                track_exists = False
                for t in current_playlist:
                    if t['id'] == track['id']:
                        track_exists = True
                        break
                
                if not track_exists:
                    current_playlist.insert(0, track)
                    # Ограничиваем до 200 треков
                    if len(current_playlist) > 200:
                        current_playlist = current_playlist[:200]
                    
                    save_playlist(current_playlist)
                    print(f"✅ Добавлен трек: {track['title']} - {track['artist']}")
                    print(f"📊 Всего треков: {len(current_playlist)}")
                else:
                    print(f"⚠️ Трек уже есть: {track['title']}")
            else:
                print(f"📄 Это не аудио (тип: {event.message.media})")
        
        print("\n💡 БОТ ГОТОВ К РАБОТЕ!")
        print("💡 Добавляйте аудиофайлы в канал - они появятся в плеере")
        print("=" * 50)
        
        # Запускаем прослушивание
        await client.run_until_disconnected()
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {type(e).__name__}")
        print(f"📝 Детали: {e}")
        print("🔄 Перезапуск через 30 секунд...")
        await asyncio.sleep(30)
        await start_bot()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot())

# Статус системы
@app.route('/status')
def status():
    bot_status = "unknown"
    try:
        import threading
        for thread in threading.enumerate():
            if "start_bot" in thread.name:
                bot_status = "running"
                break
    except:
        pass
    
    return jsonify({
        'status': 'online',
        'service': 'PLAYER CLUB',
        'playlist_count': len(load_playlist()),
        'bot_status': bot_status,
        'channel_id': CHANNEL_ID,
        'timestamp': time.time()
    })

# Тестовая страница
@app.route('/test')
def test():
    return jsonify({
        'api_id_ok': bool(API_ID),
        'api_hash_ok': bool(API_HASH),
        'bot_token_ok': bool(BOT_TOKEN),
        'channel_id': CHANNEL_ID,
        'playlist_file_exists': os.path.exists(playlist_file),
        'static_folder_exists': os.path.exists('static')
    })

if __name__ == '__main__':
    # Создаем папки если нет
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Создаем файл плейлиста если нет
    if not os.path.exists(playlist_file):
        save_playlist([])
        print(f"📁 Создан файл плейлиста: {playlist_file}")
    
    # Запускаем бота в фоне
    print("🎬 Запуск системы PLAYER CLUB...")
    bot_thread = Thread(target=run_bot, name="telegram_bot")
    bot_thread.daemon = True
    bot_thread.start()
    
    # Даем боту время на запуск
    time.sleep(3)
    
    print("=" * 50)
    print("🌐 PLAYER CLUB Music Server запущен!")
    print("=" * 50)
    print(f"📊 Треков в плейлисте: {len(load_playlist())}")
    print(f"🔗 Плеер: https://player-club-live.onrender.com")
    print(f"📡 Статус: https://player-club-live.onrender.com/status")
    print(f"🧪 Тест: https://player-club-live.onrender.com/test")
    print(f"🎵 Плейлист: https://player-club-live.onrender.com/playlist")
    print("=" * 50)
    print("📢 Добавляйте аудиофайлы в Telegram канал")
    print("💡 Бот автоматически добавит их в плеер")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
