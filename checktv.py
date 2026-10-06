import pandas as pd
import requests
from datetime import datetime, UTC
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Tivimate 5.1.6"
}

# ---------------- HELPERS ----------------
def to_datetime_str(ts):
    """Convert unix timestamp to readable string."""
    try:
        if not ts or ts in ["0", 0]:
            return "NA"
        return datetime.fromtimestamp(int(ts), UTC).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "NA"


# ---------------- CORE ----------------

def process_row(row):
    host = str(row["host"]).rstrip("/")
    username = row["username"]
    password = row["password"]

    base_api = f"{host}/player_api.php?username={quote(username)}&password={quote(password)}"

    session = requests.Session()
    session.headers.update(HEADERS)

    # Default result (ensures row is always returned)
    result = row.copy()
    result.update({
        "status": "invalid",
        "created_at": "NA",
        "exp_date": "NA",
        "active_cons": "NA",
        "max_connections": "NA"
    })

    try:
        response = session.get(base_api, timeout=2)
        data = response.json()

        user = data.get("user_info", {})
        status = user.get("status")

        # If no status → keep defaults
        if not status:
            return result

        result["status"] = status
        result["created_at"] = to_datetime_str(user.get("created_at"))
        result["exp_date"] = to_datetime_str(user.get("exp_date"))
        result["active_cons"] = user.get("active_cons") or "NA"
        result["max_connections"] = user.get("max_connections") or "NA"
        return result
    except:
        return result

df = pd.read_csv("https://raw.githubusercontent.com/lamtung16/HashFunction/refs/heads/main/sources.csv", dtype=str)

results = []

for _, row in df.iterrows():
    try:
        processed = process_row(row)
        results.append(processed)  # always append
    except Exception as e:
        print(f"Error processing row: {e}")

out_df = pd.DataFrame(results)

# Convert back to string
out_df["created_at"] = out_df["created_at"].astype(str)
out_df["exp_date"] = out_df["exp_date"].astype(str)
print(out_df)