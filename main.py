# Импортируем необходимые библиотеки из фреймворка Flask
from flask import Flask, request, jsonify, abort
# Импортируем модели БД и объект БД из нашего модульного файла
from models import Song, Playlist, PlaylistSong, db

# Создаём экземпляр приложения Flask
app = Flask(__name__)
# Настраиваем подключение к БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://amepifanov:fhntv2003@localhost:5050/postgres'

# Инициализируем наше приложение с объектом БД
db.init_app(app)

# Определяем маршрут для создания новой песни
@app.route('/songs', methods=['POST'])
def add_song():
    # Получаем данные из запроса
    title = request.json.get('title')
    artist = request.json.get('artist')
    genre = request.json.get('genre')
    duration = request.json.get('duration')
    album = request.json.get('album')

    # Если каких-то данных нет, возвращаем ошибку
    if not all([title, artist, genre, duration, album]):
        abort(400, description="All song attributes (title, artist, genre, duration, album) are required")

    if duration <= 0:
        abort(400, description="Duration less than zero")

    # Создаем новую песню
    song = Song(title=title, artist=artist, genre=genre, duration=duration, album=album)

    # Добавляем песню в БД и сохраняем изменения
    db.session.add(song)
    db.session.commit()

    # Возвращаем ответ с сообщением и ID созданной песни
    return jsonify({'message': 'song added', 'id': song.id}), 201

# Определяем маршрут для получения всех песен
@app.route('/songs', methods=['GET'])
def get_songs():
    # Получаем все песни из БД
    songs = Song.query.all()
    # Возвращаем ответ со списком песен
    return jsonify([{
        'title': song.title,
        'artist': song.artist,
        'genre': song.genre,
    } for song in songs])

# Определяем маршрут для получения информации о конкретной песне
@app.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    # Получаем песню по ID
    song = Song.query.get(song_id)
    # Если песни с таким ID нет, возвращаем ошибку
    if song is None:
        abort(404, description="Song not found")
    # Возвращаем информацию о песне
    return jsonify({
        'title': song.title,
        'artist': song.artist,
        'genre': song.genre,
        'duration': song.duration,
        'album': song.album,
        'rating': song.rating
    })

# Определяем маршрут для создания нового плейлиста
@app.route('/playlists', methods=['POST'])
def create_playlist():
    # Получаем название плейлиста из запроса
    title = request.json.get('title')
    # Если название не указано, возвращаем ошибку
    if title is None:
        abort(400, description="Title is required")
    # Создаем новый плейлист
    playlist = Playlist(title=title)
    # Добавляем плейлист в БД и сохраняем изменения
    db.session.add(playlist)
    db.session.commit()
    # Возвращаем ответ с сообщением и ID созданного плейлиста
    return jsonify({'message': 'playlist created', 'id': playlist.id}), 201

# Определяем маршрут для добавления песни в плейлист
@app.route('/playlists/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    # Получаем ID песни из запроса
    song_id = request.json.get('song_id')
    # Если ID не указан, возвращаем ошибку
    if song_id is None:
        abort(400, description="Song id is required")

    # Получаем песню по ID
    song = Song.query.get(song_id)
    # Если песни с таким ID нет, возвращаем ошибку
    if song is None:
        abort(404, description="Song not found")

    # Получаем плейлист по ID
    playlist = Playlist.query.get(playlist_id)
    # Если плейлиста с таким ID нет, возвращаем ошибку
    if playlist is None:
        abort(404, description="Playlist not found")

    # Создаем связь между плейлистом и песней
    playlist_song = PlaylistSong(song_id=song_id, playlist_id=playlist_id)
    # Добавляем связь в БД и сохраняем изменения
    db.session.add(playlist_song)
    db.session.commit()

    # Возвращаем ответ с сообщением и ID созданной связи
    return jsonify({'message': 'song added to playlist', 'id': playlist_song.id}), 201

# Определяем маршрут для получения всех песен из плейлиста
@app.route('/playlists/<int:playlist_id>/songs', methods=['GET'])
def get_songs_from_playlist(playlist_id):
    # Получаем плейлист по ID
    playlist = Playlist.query.get(playlist_id)
    # Если плейлиста с таким ID нет, возвращаем ошибку
    if playlist is None:
        abort(404, description="Playlist not found")

    # Получаем все песни из плейлиста
    songs = [playlist_song.song for playlist_song in playlist.songs]
    # Возвращаем список песен
    return jsonify([{
        'title': song.title,
        'artist': song.artist,
        'genre': song.genre,
        'duration': song.duration,
        'album': song.album,
        'rating': song.rating
    } for song in songs])

# Определяем маршрут для оценки песни
@app.route('/ratings', methods=['POST'])
def rate_song():
    # Получаем ID песни и оценку из запроса
    song_id = request.json.get('song_id')
    rating = request.json.get('rating')
    # Если одно из значений не указано, возвращаем ошибку
    if song_id is None or rating is None:
        abort(400, description="Song id and rating are required")

    # Получаем песню по ID
    song = Song.query.get(song_id)
    # Если песни с таким ID нет, возвращаем ошибку
    if song is None:
        abort(404, description="Song not found")

    # Проверяем, что оценка находится в допустимых пределах
    if rating < 0.0 or rating > 10.0:
        abort(400, description="Rating must be between 0 and 10")

    # Устанавливаем новую оценку песни и сохраняем изменения
    song.rating = rating
    db.session.commit()
    # Возвращаем ответ с сообщением, ID песни и новой оценкой
    return jsonify({'message': 'song rated', 'id': song_id, 'rating': rating}), 201

# Обработчик ошибок 404 (ресурс не найден)
@app.errorhandler(404)
def resource_not_found(e):
    # Возвращаем ошибку с описанием
    return jsonify(error=str(e)), 404

# Обработчик ошибок 400 (плохой запрос)
@app.errorhandler(400)
def bad_request(e):
    # Возвращаем ошибку с описанием
    return jsonify(error=str(e)), 400

# Запускаем наше приложение, если скрипт был запущен напрямую
if __name__ == "__main__":
    # Создаём все необходимые таблицы в БД
    with app.app_context():
        db.create_all()
    # Запускаем сервер
    app.run(debug=True, port=8800)
