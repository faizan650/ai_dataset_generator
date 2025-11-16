import os
import json
import time
import math
import threading
import random
import traceback
from openai import OpenAI
from dotenv import load_dotenv
from domain_classifier import classify_domain

# ---------------------------------------------------------
# LOAD ENV + CLIENT
# ---------------------------------------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory progress tracker
JOBS = {}
STRICT_MODE = False

# ---------------------------------------------------------
# SUBTOPIC MAPPING
# ---------------------------------------------------------
DOMAIN_SUBTOPICS = {
    "sports": ["training", "nutrition", "psychology", "performance", "injury", "recovery", "motivation"],
    "finance": ["investment", "budgeting", "markets", "loans", "insurance", "savings", "taxation"],
    "education": ["learning strategies", "assessment", "pedagogy", "technology", "motivation", "policy"],
    "health": ["diet", "exercise", "mental health", "disease prevention", "wellness", "treatment"],
    "law": ["contracts", "intellectual property", "criminal law", "corporate law", "civil rights"],
    "code_generation": ["python", "javascript", "data structures", "algorithms", "debugging", "API design"],
    "text_to_sql": ["joins", "filters", "aggregations", "grouping", "ordering", "subqueries"],
    "consulting": ["strategy", "operations", "marketing", "finance", "management", "technology"],
    "generic": ["common knowledge", "decision-making", "analysis", "reasoning", "language", "logic"],
}

# ---------------------------------------------------------
# PROMPT TEMPLATE
# ---------------------------------------------------------
def get_prompt_template(domain_name: str, domain_type: str, batch_size: int, subtopic: str) -> str:
    """Generates domain-specific prompt enforcing structured JSON output."""
    base_rules = f"""
You are generating realistic fine-tuning examples for a large language model (LLM).

Focus this batch on the subtopic "{subtopic}" under "{domain_name}".
Each record must be a valid JSON line with *non-empty* fields:
- instruction
- input
- output
- tags (must include "{subtopic}")

No markdown, no explanations. Return exactly {batch_size} JSON objects, one per line.
"""

    if domain_type == "text_to_sql":
        example = {
            "instruction": "Convert this to SQL.",
            "input": "List all employees older than 30.",
            "output": "SELECT * FROM employees WHERE age > 30;",
            "tags": ["sql", subtopic],
        }
    elif domain_type == "consulting":
        example = {
            "instruction": "Give business advice.",
            "input": "A startup wants to reduce operational costs.",
            "output": "Analyze spending categories and adopt automation tools for efficiency.",
            "tags": ["consulting", subtopic],
        }
    elif domain_type == "code_generation":
        example = {
            "instruction": "Write a Python function to reverse a string.",
            "input": "The function should take a single argument s.",
            "output": "def reverse_string(s): return s[::-1]",
            "tags": ["code", "python", subtopic],
        }
    else:
        example = {
            "instruction": "Explain how to stay motivated in learning.",
            "input": "A student struggling with consistency.",
            "output": "Use spaced repetition and set achievable daily goals.",
            "tags": [domain_name, subtopic],
        }

    return f"{base_rules}\nExample:\n{json.dumps(example, ensure_ascii=False)}"

# ---------------------------------------------------------
# OPENAI HELPER (with retries + logs)
# ---------------------------------------------------------
def _call_model(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    for attempt in range(3):
        try:
            print(f"🔹 OpenAI call (attempt {attempt+1}) using {model}...")
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3000,
            )
            text = resp.choices[0].message.content
            print(f"🔹 Response received ({len(text)} chars)")
            return text
        except Exception as e:
            print(f"[WARN] OpenAI call failed ({attempt+1}/3): {e}")
            time.sleep(3)
    raise RuntimeError("OpenAI model failed after 3 retries.")

# ---------------------------------------------------------
# ASYNC GENERATION (background thread)
# ---------------------------------------------------------
def generate_dataset_async(domain, total_records=100, batch_size=20, model="gpt-3.5-turbo", out_path=None):
    """Launch dataset generation as a background thread."""
    thread = threading.Thread(
        target=_generate_and_track,
        args=(domain, total_records, batch_size, model, out_path),
        daemon=True,
    )
    thread.start()

# ---------------------------------------------------------
# CORE GENERATION FUNCTION
# ---------------------------------------------------------
def _generate_and_track(domain, total_records, batch_size, model, out_path):
    file_name = os.path.basename(out_path)
    JOBS[file_name] = {"status": "running", "progress": 0}

    try:
        domain_type = classify_domain(domain)
        subtopics = DOMAIN_SUBTOPICS.get(domain_type, DOMAIN_SUBTOPICS["generic"])
        random.shuffle(subtopics)

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        written = 0

        print(f"🧠 Generating dataset for '{domain}' → {out_path}")
        with open(out_path, "w", encoding="utf-8") as fo:
            while written < total_records:
                remaining = total_records - written
                current_batch = min(batch_size, remaining)
                subtopic = subtopics[written % len(subtopics)]
                prompt = get_prompt_template(domain, domain_type, current_batch, subtopic)

                print(f"[Batch] Generating {current_batch} records on '{subtopic}'")
                try:
                    text = _call_model(prompt, model)
                except Exception as e:
                    print(f"[ERROR] OpenAI failed: {e}")
                    traceback.print_exc()
                    JOBS[file_name]["status"] = f"error: {e}"
                    break

                valid = 0
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if not isinstance(obj, dict):
                            continue

                        instr = obj.get("instruction", "").strip()
                        inp = obj.get("input", "").strip()
                        outp = obj.get("output", "").strip()
                        tags = obj.get("tags", [])

                        if not instr or not outp:
                            continue
                        if not inp:
                            obj["input"] = f"Context: {instr}"
                        if not tags:
                            obj["tags"] = [domain_type, subtopic]

                        fo.write(json.dumps(obj, ensure_ascii=False) + "\n")
                        valid += 1
                        written += 1
                        if written >= total_records:
                            break
                    except json.JSONDecodeError:
                        continue

                JOBS[file_name]["progress"] = int((written / total_records) * 100)
                print(f"✅ Batch complete: {valid}/{current_batch} | Total: {written}/{total_records}")
                time.sleep(1)

        if written >= total_records:
            JOBS[file_name]["status"] = "completed"
            JOBS[file_name]["progress"] = 100
            print(f"🎉 Dataset completed: {written}/{total_records}")
        else:
            JOBS[file_name]["status"] = f"incomplete ({written}/{total_records})"
            print(f"[WARN] Incomplete dataset ({written}/{total_records})")

    except Exception as e:
        JOBS[file_name]["status"] = f"error: {e}"
        JOBS[file_name]["progress"] = 0
        print(f"[FATAL ERROR] {e}")
        traceback.print_exc()

# ---------------------------------------------------------
# JOB STATUS + PREVIEW
# ---------------------------------------------------------
def job_status(file_name: str):
    """Return current status of a dataset job."""
    return JOBS.get(file_name, {"status": "unknown", "progress": 0})

def generate_dataset_preview(path: str, lines: int = 5):
    """Return the first few lines of generated dataset."""
    data = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for _ in range(lines):
                line = f.readline()
                if not line:
                    break
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"[WARN] File not found: {path}")
    return data
