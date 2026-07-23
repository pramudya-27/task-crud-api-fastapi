\echo '========================================'
\echo 'RESET INDEX'
\echo '========================================'

DROP INDEX IF EXISTS idx_tasks_title;


\echo '========================================'
\echo 'INSERT BENCHMARK DATA'
\echo '========================================'

INSERT INTO tasks (title, done)
SELECT
    'Benchmark task ' || number,
    number % 2 = 0
FROM generate_series(1, 50000) AS number;

ANALYZE tasks;


\echo '========================================'
\echo 'BEFORE INDEX'
\echo '========================================'

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, done
FROM tasks
WHERE title = 'Benchmark task 45000';


\echo '========================================'
\echo 'CREATE INDEX'
\echo '========================================'

CREATE INDEX idx_tasks_title
ON tasks (title);

ANALYZE tasks;


\echo '========================================'
\echo 'AFTER INDEX'
\echo '========================================'

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title, done
FROM tasks
WHERE title = 'Benchmark task 45000';


\echo '========================================'
\echo 'CLEAN BENCHMARK DATA'
\echo '========================================'

DELETE FROM tasks
WHERE title LIKE 'Benchmark task %';

ANALYZE tasks;