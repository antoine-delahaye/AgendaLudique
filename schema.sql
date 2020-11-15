drop table if exists user;

create table user
(
    username  varchar(42),
    password  varchar(128),
    primary key (username)
);