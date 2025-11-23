from fastapi import FastAPI, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from dataset_generator import generate_dataset_async, job_status, generate_dataset_preview
from database import queries_collection
from auth import router as auth_router
import os
import traceback

# ------------------------------------------------------
# FASTAPI APP
# ------------------------------------------------------
app = FastAPI(title="Dataset AI Backend")

# ------------------------------------------------------
# CORS CONFIG (Render + Cloudflare Pages fixed)
# ------------------------------------------------------
ORIGINS = [
    "https://9206f1a4.ai-dataset-generator.pages.dev",   # FRONTEND
    "http://localhost:5173",                    # LOCAL DEV
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ------------------------------------------------------
# GLOBAL OPTIONS HANDLER (Render needs this!)
# ------------------------------------------------------
@app.options("/{path:path}")
async def preflight_handler(path: str):
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "https://ai-dataset-generator.pages.dev",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# ------------------------------------------------------
# AUTH ROUTES
# ------------------------------------------------------
app.include_router(auth_router)

# ------------------------------------------------------
# DATASET GENERATION
# ------------------------------------------------------
@app.post("/generate/")
async def generate_dataset(
    request: Request,
    domain: str = Form(...),
    records: int = Form(...),
    batch_size: int = Form(...),
    user_email: str = Form(None),
):
    print("\n🟢 /generate/ triggered")
    print(f"Domain={domain}, Records={records}, Batch Size={batch_size}, User={user_email}")

    try:
        os.makedirs("datasets", exist_ok=True)

        file_name = f"{domain.replace(' ', '_')}_dataset.jsonl"
        out_path = os.path.join("datasets", file_name)

        generate_dataset_async(
            domain,
            int(records),
            int(batch_size),
            model="gpt-3.5-turbo",
            out_path=out_path
        )

        if user_email:
            queries_collection.insert_one({
                "user_email": user_email,
                "query": domain,
                "file_name": file_name
            })

        return {
            "message": "Generation started",
            "file_name": file_name,
            "download_url": f"/download/{file_name}",
        }

    except Exception as e:
        print("❌ ERROR /generate:", e)
        print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)

# ------------------------------------------------------
# STATUS
# ------------------------------------------------------
@app.get("/status")
def get_status(file_name: str):
    info = job_status(file_name)
    print(f"📊 Status → {file_name}: {info}")
    return info

# ------------------------------------------------------
# PREVIEW
# ------------------------------------------------------
@app.get("/preview")
def get_preview(file_name: str, lines: int = 8):
    path = os.path.join("datasets", file_name)

    if not os.path.exists(path):
        print("❌ File not found for preview:", path)
        return {"preview": []}

    data = generate_dataset_preview(path, lines)
    return {"preview": data}

# ------------------------------------------------------
# DOWNLOAD
# ------------------------------------------------------
@app.get("/download/{file_name}")
def download_dataset(file_name: str):
    path = os.path.join("datasets", file_name)
    if os.path.exists(path):
        return FileResponse(path, filename=file_name, media_type="application/json")
    return JSONResponse({"error": "File not found"}, status_code=404)

# ------------------------------------------------------
# USER QUERIES / HISTORY
# ------------------------------------------------------
@app.get("/queries/user")
def get_user_queries(user_email: str = Query(...)):
    print(f"📬 Fetching queries for {user_email}")

    results = list(
        queries_collection.find({"user_email": user_email}, {"_id": 0})
    )

    return {"datasets": results}

# ------------------------------------------------------
# ROOT
# ------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Backend running 🚀"}
