import csv
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import Request, urlopen


def to_datetime_str(ts):
    """Convert unix timestamp to readable string."""
    try:
        if not ts or ts in ["0", 0]:
            return "NA"
        return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "NA"


def process_row(row):
    host = row.get("host", "").rstrip("/")
    username = row.get("username", "")
    password = row.get("password", "")

    base_api = f"{host}/player_api.php?username={quote(username)}&password={quote(password)}"

    # Default result
    result = dict(row)
    result.update({
        "status": "invalid",
        "created_at": "NA",
        "exp_date": "NA",
        "active_cons": "NA",
        "max_connections": "NA"
    })

    try:
        req = Request(base_api, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=2) as response:
            import json
            data = json.loads(response.read().decode())

        user = data.get("user_info", {})
        status = user.get("status")

        if not status:
            return result

        result["status"] = str(status)
        result["created_at"] = to_datetime_str(user.get("created_at"))
        result["exp_date"] = to_datetime_str(user.get("exp_date"))
        result["active_cons"] = str(user.get("active_cons") or "NA")
        result["max_connections"] = str(user.get("max_connections") or "NA")
        return result
    except:
        return result


# Fetch CSV data using standard library
csv_url = "https://raw.githubusercontent.com/lamtung16/HashFunction/refs/heads/main/sources.csv"
req = Request(csv_url, headers={"User-Agent": "Mozilla/5.0"})

results = []
try:
    with urlopen(req) as response:
        lines = [line.decode("utf-8") for line in response.readlines()]
        reader = csv.DictReader(lines)
        for row in reader:
            try:
                processed = process_row(row)
                results.append(processed)
            except Exception as e:
                print(f"Error processing row: {e}")
except Exception as e:
    print(f"Error fetching CSV: {e}")

# ---------------- BEAUTIFIED TABLE PRINTING ----------------
if results:
    # Define columns to exclude (case-insensitive check)
    exclude_columns = {"url_format", "created_at"}
    
    # Filter out excluded keys from available columns
    all_keys = [k for k in results[0].keys() if k.lower() not in exclude_columns]
    
    # Calculate column widths dynamically based on content
    col_widths = {}
    for key in all_keys:
        max_len = max(len(str(key)), max(len(str(r.get(key, ""))) for r in results))
        col_widths[key] = min(max_len, 30)  # Cap width at 30 to prevent overflow

    # Build header row
    header = " | ".join(f"{str(key).upper():<{col_widths[key]}}" for key in all_keys)
    separator = "-+-".join("-" * col_widths[key] for key in all_keys)

    print(header)
    print(separator)

    # Print rows
    for res in results:
        row_str = " | ".join(f"{str(res.get(key, '')):<{col_widths[key]}}" for key in all_keys)
        print(row_str)
else:
    print("No results to display.")