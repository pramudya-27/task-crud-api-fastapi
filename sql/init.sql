CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL
        CHECK (BTRIM(title) <> ''),
    done BOOLEAN NOT NULL DEFAULT FALSE
);


INSERT INTO tasks (title, done)
SELECT seed.title, seed.done
FROM (
    VALUES
        ('Learn FastAPI', FALSE),
        ('Connect the API to PostgreSQL', FALSE),
        ('Containerize the application', TRUE)
) AS seed(title, done)
WHERE NOT EXISTS (
    SELECT 1
    FROM tasks
);