INSERT INTO users (id, name, email, age) VALUES
    (1, 'Anna', 'anna@example.com', 25),
    (2, 'Max', 'max@example.com', 28),
    (3, 'Olga', 'olga@example.com', 24),
    (4, 'Ivan', 'ivan@example.com', 30),
    (5, 'Maria', 'maria@example.com', 27);

INSERT INTO profiles (id, user_id, city, bio) VALUES
    (1, 1, 'Moscow', 'Coffee and walks.'),
    (2, 2, 'Saint Petersburg', 'Guitar and music.'),
    (3, 3, 'Kazan', 'Books and movies.'),
    (4, 4, 'Moscow', 'Gym and sport.'),
    (5, 5, 'Sochi', 'Sea and travel.');

SELECT setval('users_id_seq', 5, true);
SELECT setval('profiles_id_seq', 5, true);
