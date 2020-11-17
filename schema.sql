drop table if exists users;
drop table if exists games;

create table users
(
    username varchar(16),
    password varchar(128),
    primary key (username)
);

create table games
(
    game_id      int,
    title        varchar(32),
    years        int,
    min_players  int,
    max_players  int,
    min_playtime int,
    image        varchar(256),
    primary key (game_id)
)