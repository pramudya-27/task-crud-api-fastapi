-- 1. List every task
SELECT *
FROM tasks;


-- 2. Show only completed tasks
SELECT *
FROM tasks
WHERE done = 1;


-- 3. Count all tasks
SELECT COUNT(*) AS total_tasks
FROM tasks;


-- 4. Mark every task as completed
UPDATE tasks
SET done = 1;


-- 5. Delete all completed tasks
DELETE FROM tasks
WHERE done = 1;