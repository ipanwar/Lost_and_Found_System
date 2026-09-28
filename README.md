# 🎓 College Lost & Found System API

A lightweight, robust **FastAPI-based REST API** for managing lost and found item reports on a college campus. Built with **SQLite** and **SQLModel** (Pydantic + SQLAlchemy) with full data validation and automatic OpenAPI documentation via Swagger UI.

---

## 🛠 Features

- **Relational Database**: Persistent storage in SQLite using SQLModel ORM (`lost_and_found.db`).
- **Automatic Table Initialization**: Database tables are created automatically on startup via FastAPI `lifespan`.
- **Strict Data Validation**:
  - `title`, `description`, `category`, `location`, and `reported_by` must not be empty or contain only whitespace.
  - `status` only accepts strictly allowed values: `"Lost"`, `"Found"`, `"Returned"`.
- **Comprehensive Error Handling**: Returns appropriate HTTP status codes (`201`, `200`, `404`, `422`).
- **Interactive API Documentation**: Built-in Swagger UI at `/docs` and ReDoc at `/redoc`.

---

## 📂 Project Structure

```text
Lost_&_Found_System/
├── .venv/               # Python virtual environment (isolated dependencies)
├── proof of work/       # Proof of work directory
├── database.py          # SQLite engine and session dependency
├── models.py            # SQLModel entity definitions and Pydantic schemas
├── main.py              # FastAPI application and route handlers
├── test_main.py         # Pytest automated test suite
├── requirements.txt     # Project dependencies
├── .gitignore           # Git ignore rules
└── README.md            # API documentation
```

---

## 🚀 Setup & Execution (Virtual Environment)

### 1. Create & Activate Virtual Environment

A virtual environment (`.venv`) is already configured in this repository. To create or re-create it:

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt - CMD):**
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 2. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

---

### 3. Run the API Server

Start the development server with live reload:

```bash
uvicorn main:app --reload
```

The API will be available at: **`http://127.0.0.1:8000`**

---

## 📖 Swagger UI

You can test, inspect, and execute all API requests directly through the interactive Swagger UI:

👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

*(Alternative ReDoc documentation is available at [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc))*

---

## 📌 API Endpoints

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| **POST** | `/items` | Create a new lost/found item report | `201 Created` |
| **GET** | `/items` | Retrieve all reported items | `200 OK` |
| **GET** | `/items/{item_id}` | Retrieve a specific item by its ID | `200 OK` / `404 Not Found` |
| **PUT** | `/items/{item_id}` | Update details or status of an existing item | `200 OK` / `404 Not Found` |
| **DELETE** | `/items/{item_id}` | Delete an item report | `200 OK` / `404 Not Found` |
| **GET** | `/items/status/{status}` | Filter items by status (`Lost`, `Found`, `Returned`) | `200 OK` / `422 Validation Error` |
| **GET** | `/items/category/{category}` | Filter items by category (case-insensitive) | `200 OK` |

---

## 💡 Example Request Payloads

### 1. Create an Item (`POST /items`)
```json
{
  "title": "Dell Inspiron 15 Laptop",
  "description": "Black laptop with a GitHub sticker on the cover, left in the 2nd floor library reading room.",
  "category": "Electronics",
  "location": "Central Library Floor 2",
  "reported_by": "Alex Johnson",
  "status": "Lost"
}
```

### 2. Update an Item (`PUT /items/1`)
```json
{
  "status": "Returned",
  "location": "Security Office Desk"
}
```

---

## 🧪 Running Automated Tests

Run the automated test suite within the virtual environment:

```bash
pytest -v
```
