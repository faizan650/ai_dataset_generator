from fastapi import FastAPI, Form, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from dataset_generator import generate_dataset_async, job_status, generate_dataset_preview
from database import queries_collection
from auth import router as auth_router
import os
import traceback
import re

app = FastAPI(title="Dataset AI Backend")

# ------------------------------------------------------
# CORRECT CORS FOR CLOUDFLARE PAGES + RENDER
# ------------------------------------------------------

def get_origin(request: Request):
    origin = request.headers.get("origin")
    if not origin:
        return None

    # Allow Cloudflare Pages: https://<random>.ai-dataset-generator.pages.dev
    if re.match(r"https://.*\.ai-dataset-generator\.pages\.dev$", origin):
        return origin

    # Allow localhost
    if origin.startswith("http://localhost"):
        return origin

    return None


@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    response = await call_next(request)

    origin = get_origin(request)
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response


# Preflight support
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    origin = get_origin(request)
    headers = {
        "Access-Control-Allow-Origin": origin or "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }
    return JSONResponse({"status": "ok"}, headers=headers)


# ------------------------------------------------------
# ROUTERS
# ------------------------------------------------------
app.include_router(auth_router)

# ------------------------------------------------------
# GENERATE DATASET
# ------------------------------------------------------
@app.post("/generate/")
async def generate_dataset(
    request: Request,
    domain: str = Form(...),
    records: int = Form(...),
    batch_size: int = Form(...),
    user_email: str = Form(None),
):
    print("\n🟢 GENERATE REQUEST")
    print(f"domain={domain}, records={records}, batch={batch_size}, user={user_email}")

    try:
        os.makedirs("datasets", exist_ok=True)

        file_name = f"{domain.replace(' ', '_')}_dataset.jsonl"
        out_path = os.path.join("datasets", file_name)

        generate_dataset_async(domain, int(records), int(batch_size),
                               model="gpt-3.5-turbo", out_path=out_path)

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
        print("❌ ERROR:", e)
        print(traceback.format_exc())
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/status")
def get_status(file_name: str):
    return job_status(file_name)


@app.get("/preview")
def get_preview(file_name: str, lines: int = 8):
    path = os.path.join("datasets", file_name)
    if not os.path.exists(path):
        return {"preview": []}
    return {"preview": generate_dataset_preview(path, lines)}


@app.get("/download/{file_name}")
def download_dataset(file_name: str):
    path = os.path.join("datasets", file_name)
    if os.path.exists(path):
        return FileResponse(path, filename=file_name)
    return JSONResponse({"error": "File not found"}, status_code=404)


@app.get("/queries/user")
def get_user_queries(user_email: str = Query(...)):
    results = list(
        queries_collection.find({"user_email": user_email}, {"_id": 0})
    )
    return {"datasets": results}


@app.get("/")
def home():
    return {"message": "Backend running 🚀"}
