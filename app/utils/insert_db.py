from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.models import Game, Note, Genre, Classification


class insertDB:
    def __init__(self):
        from app import config_app
        from instance.config import config
        import os
        with config_app(config.get(os.environ.get("FLASK_ENV"), 'default')) as app:
            url_db = app.config["SQLALCHEMY_DATABASE_URI"]

        self.__engine = create_engine(
            url_db,
            pool_size=5,  # default in SQLAlchemy
            max_overflow=10,  # default in SQLAlchemy
            pool_timeout=1,  # raise an error faster than default
        )
        self.__thread_safe_session_factory = scoped_session(sessionmaker(bind=self.__engine))
        self.__default_message = "Auto-generated note, the average rating of the game at boardgamegeek.com"
        self.__genres_dict = {}

    def insert(self, data):
        session = self.__thread_safe_session_factory()
        i_game = 1
        i_genres = 1

        for title, infos in data.items():

            if len(title) > 128:
                continue

            # Adding game
            session.add(Game(
                id=i_game,
                title=title,
                publication_year=infos["publication_year"],
                min_players=infos["min_players"],
                max_players=infos["max_players"],
                min_playtime=infos["min_playtime"],
                image=infos["images"]["original"])
            )

            # Adding note
            session.add(Note(
                note=round(infos["average_rating"]),
                message=self.__default_message,
                user_id=1,
                game_id=i_game)
            )

            for genre in infos["type"]:
                # Adding genre
                if genre not in self.__genres_dict:
                    self.__genres_dict[genre] = i_genres
                    session.add(Genre(id=i_genres, name=genre))
                    i_genres += 1

                # Adding classification
                session.add(Classification(game_id=i_game, genre_id=self.__genres_dict[genre]))

            i_game += 1

        session.commit()
        self.__thread_safe_session_factory.remove()
