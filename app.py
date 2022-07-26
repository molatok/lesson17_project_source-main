from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from models import *
from schemas import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


api = Api(app)
movie_ns = api.namespace('movies')

@movie_ns.route('/')
class MovieView(Resource):

    def get(self):
        movies_with_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                      Genre.name.label('genre'), Director.name.label('director')).join(Genre).join(Director)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movies_with_genre_and_director = movies_with_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movies_with_genre_and_director = movies_with_genre_and_director.filter(Movie.genre_id == genre_id)
        all_movies = movies_with_genre_and_director.all()
        return movies_schema.dupm(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан, 201"

@movie_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid: int):
        movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer, Genre.name.label('genre'), Director.name.label('director')).join(Genre).join(Director).filter(Movie.id == mid).first()
        if movie:
            return movie_schema.dump(movie)
        return "Не нашли", 404

    def put(self, mid: int):
        movie = db.session.query(Movie).get(mid)

        if not movie:
            return 'не нашли', 404
        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f'Объект с id {mid} обновлен', 204

    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return 'не нашли', 404
        db.session.delete(movie)
        db.session.commit()
        return f'Объект с id {mid} удален', 204


if __name__ == '__main__':
    app.run(debug=True)
