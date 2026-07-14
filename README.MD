# Task CRUD API

Task CRUD API adalah REST API sederhana untuk mengelola daftar tugas. API ini dibangun menggunakan Python dan FastAPI.

Data disimpan secara in-memory sehingga task baru akan hilang ketika server dihentikan atau dijalankan ulang.

## Features

- Create a task
- Read all tasks
- Read one task
- Update a task
- Delete a task
- Input validation
- JSON error responses
- Swagger UI documentation

## Requirements

- Python 3.10 or newer
- Git

## Installation

Clone the repository:

```bash
git clone https://github.com/USERNAME/task-crud-api-fastapi.git
cd task-crud-api-fastapi
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the API

```bash
fastapi dev main.py
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

| Method | Endpoint           | Description         | Success status |
| ------ | ------------------ | ------------------- | -------------: |
| GET    | `/`                | Get API information |            200 |
| GET    | `/health`          | Check server health |            200 |
| GET    | `/tasks`           | List all tasks      |            200 |
| GET    | `/tasks/{task_id}` | Get one task        |            200 |
| POST   | `/tasks`           | Create a task       |            201 |
| PUT    | `/tasks/{task_id}` | Update a task       |            200 |
| DELETE | `/tasks/{task_id}` | Delete a task       |            204 |

## Create a Task

Request:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
-H "Content-Type: application/json" \
-d "{\"title\":\"Buy milk\"}"
```

Example response:

```text
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Error Response

Requesting an unknown task:

```bash
curl -i http://127.0.0.1:8000/tasks/99
```

Response:

```json
{
  "error": "Task 99 not found"
}
```

## Swagger UI

![Swagger UI](docs/swagger-ui.png)

## In-Memory Storage

This project does not use a database. All tasks are stored inside a Python list while the server is running.

When the server restarts, tasks created through POST requests disappear and the original three example tasks are restored.
