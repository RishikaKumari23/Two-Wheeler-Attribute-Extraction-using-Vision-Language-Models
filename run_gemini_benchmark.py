import os
import csv
import json
import time
import base64
import urllib.request
import urllib.error

# Configuration
# Read API key from environment variable for security
API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please export GEMINI_API_KEY='...'")
MODEL_NAME = "gemini-3.5-flash-lite"
IMG_DIR = "/Users/rishika/Downloads/Image/sampled_1080_dataset"
GT_CSV = "/Users/rishika/Downloads/Ground_Truth_Annotation_1080_Completed.csv"
OUT_CSV = "/Users/rishika/Downloads/Image/Gemini_Predictions_990.csv"
LOG_FILE = "/Users/rishika/Downloads/Image/gemini_run.log"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

PROMPT = """Analyze this traffic camera image of a two-wheeler vehicle.
Extract the following attributes strictly matching the given options:

1. vehicle_type: 'Motorcycle' or 'Scooter'
2. number_of_riders: '1' (solo driver), '2' (driver + 1 pillion), or '3+' (triple/more riding)
3. rider_gender: 'Male', 'Female', or 'Unclear'
4. rider_helmet: 'Yes' (helmet worn on head) or 'No' (no helmet or helmet merely hanging on bike/mirror)
5. pillion_helmet: 'N/A' (if only 1 rider), 'Yes', or 'No'
6. luggage: 'None' (no bags), 'Backpack' (personal, school, college, or laptop bag worn on body), or 'Cargo/Box' (delivery box, commercial sack, crate, or bulky cargo on footboard/rear)
7. is_valid_2w: true if a two-wheeler is visible. false if completely obscured by dense fog or not a two-wheeler (e.g. truck side).
"""

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "is_valid_2w": {"type": "BOOLEAN"},
        "vehicle_type": {"type": "STRING", "enum": ["Motorcycle", "Scooter"]},
        "number_of_riders": {"type": "STRING", "enum": ["1", "2", "3+"]},
        "rider_gender": {"type": "STRING", "enum": ["Male", "Female", "Unclear"]},
        "rider_helmet": {"type": "STRING", "enum": ["Yes", "No"]},
        "pillion_helmet": {"type": "STRING", "enum": ["Yes", "No", "N/A"]},
        "luggage": {"type": "STRING", "enum": ["None", "Backpack", "Cargo/Box"]}
    },
    "required": ["is_valid_2w", "vehicle_type", "number_of_riders", "rider_gender", "rider_helmet", "pillion_helmet", "luggage"]
}

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as lf:
        lf.write(line + "\n")

def call_gemini(img_path):
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "contents": [{
            "parts": [
                {"text": PROMPT},
                {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
            "response_schema": SCHEMA,
            "temperature": 0.0
        }
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    max_retries = 5
    backoff = 5
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in [429, 503]:
                log(f"HTTP {e.code} on attempt {attempt+1}/{max_retries}. Backing off for {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
            else:
                err_body = e.read().decode("utf-8", errors="ignore")
                log(f"HTTP Error {e.code}: {err_body}")
                return None
        except Exception as ex:
            log(f"Network error on attempt {attempt+1}: {ex}. Retrying in {backoff}s...")
            time.sleep(backoff)
            backoff *= 2

    return None

def main():
    log("=== Starting Gemini Automated Batch Pipeline (990 Images) ===")
    
    # 1. Read ground truth order
    if not os.path.exists(GT_CSV):
        log(f"Error: Ground truth file not found at {GT_CSV}")
        return

    with open(GT_CSV, "r", encoding="utf-8") as f:
        gt_rows = list(csv.DictReader(f))

    log(f"Loaded {len(gt_rows)} target images from Ground Truth file.")

    # 2. Check already completed images to support RESUME
    processed = set()
    file_exists = os.path.exists(OUT_CSV)
    if file_exists:
        with open(OUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if r.get("Image_File"):
                    processed.add(r["Image_File"])
        log(f"Found existing output CSV with {len(processed)} already processed images. Resuming...")

    fieldnames = [
        "Image_File",
        "Location",
        "Date",
        "Time",
        "Hour",
        "Recorded_Speed",
        "is_valid_2w",
        "Gemini_Vehicle_Type",
        "Gemini_Number_of_Riders",
        "Gemini_Rider_Gender",
        "Gemini_Rider_Helmet",
        "Gemini_Pillion_Helmet",
        "Gemini_Luggage",
        "Status"
    ]

    out_file = open(OUT_CSV, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(out_file, fieldnames=fieldnames)
    if not file_exists or len(processed) == 0:
        writer.writeheader()
        out_file.flush()

    total = len(gt_rows)
    for idx, row in enumerate(gt_rows, start=1):
        img_name = row["Image_File"]
        if img_name in processed:
            continue

        img_path = os.path.join(IMG_DIR, img_name)
        if not os.path.exists(img_path):
            log(f"[{idx}/{total}] Warning: Image file not found: {img_path}")
            continue

        pred = call_gemini(img_path)
        if pred:
            out_row = {
                "Image_File": img_name,
                "Location": row.get("Location", ""),
                "Date": row.get("Date", ""),
                "Time": row.get("Time", ""),
                "Hour": row.get("Hour", ""),
                "Recorded_Speed": row.get("Recorded_Speed", ""),
                "is_valid_2w": pred.get("is_valid_2w", True),
                "Gemini_Vehicle_Type": pred.get("vehicle_type", ""),
                "Gemini_Number_of_Riders": pred.get("number_of_riders", ""),
                "Gemini_Rider_Gender": pred.get("rider_gender", ""),
                "Gemini_Rider_Helmet": pred.get("rider_helmet", ""),
                "Gemini_Pillion_Helmet": pred.get("pillion_helmet", ""),
                "Gemini_Luggage": pred.get("luggage", ""),
                "Status": "Success"
            }
            log(f"[{idx}/{total}] ({idx/total*100:.1f}%) {img_name}: {pred.get('vehicle_type')} | {pred.get('number_of_riders')}R | Helmet:{pred.get('rider_helmet')} | Luggage:{pred.get('luggage')}")
        else:
            out_row = {
                "Image_File": img_name,
                "Location": row.get("Location", ""),
                "Date": row.get("Date", ""),
                "Time": row.get("Time", ""),
                "Hour": row.get("Hour", ""),
                "Recorded_Speed": row.get("Recorded_Speed", ""),
                "is_valid_2w": "",
                "Gemini_Vehicle_Type": "",
                "Gemini_Number_of_Riders": "",
                "Gemini_Rider_Gender": "",
                "Gemini_Rider_Helmet": "",
                "Gemini_Pillion_Helmet": "",
                "Gemini_Luggage": "",
                "Status": "Failed"
            }
            log(f"[{idx}/{total}] Failed to get response for {img_name}")

        writer.writerow(out_row)
        out_file.flush()
        processed.add(img_name)

        # 4.1-second delay to strictly stay under the 15 Requests Per Minute (RPM) free limit
        time.sleep(4.1)

    out_file.close()
    log("=== Completed All 990 Images! Predictions saved to CSV. ===")

if __name__ == "__main__":
    main()
