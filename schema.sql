DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    timeEntry DATE DEFAULT (datetime('now', 'localtime')),
    user TEXT
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    displayName TEXT NOT NULL
);

INSERT INTO users (username, password, displayName) VALUES (
    'admin','password', 'System Admistator');