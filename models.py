# Импорт SQLAlchemy для работы с базой данных
from flask_sqlalchemy import SQLAlchemy

# Создание экземпляра SQLAlchemy
db = SQLAlchemy()

# Определение модели Song, которая представляет собой песню
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор песни
    title = db.Column(db.String(100), nullable=False)  # Название песни
    artist = db.Column(db.String(100), nullable=False)  # Артист, исполнивший песню
    genre = db.Column(db.String(50), nullable=False)  # Жанр песни
    duration = db.Column(db.Float, nullable=False)  # Продолжительность песни
    album = db.Column(db.String(100), nullable=False)  # Альбом, в который входит песня
    rating = db.Column(db.Float)  # Рейтинг песни

# Определение модели Playlist, которая представляет собой плейлист
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор плейлиста
    title = db.Column(db.String(100), nullable=False)  # Название плейлиста
    # Связь между плейлистом и песнями в нем через вспомогательную таблицу PlaylistSong
    songs = db.relationship('PlaylistSong', backref='playlist', lazy=True)

# Вспомогательная модель PlaylistSong, которая представляет связь между песнями и плейлистами
class PlaylistSong(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор связи
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)  # ID плейлиста
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)  # ID песни
    # Связь с песней, которая позволяет получить доступ к информации о песне напрямую из связи
    song = db.relationship('Song', backref='playlist_songs')
