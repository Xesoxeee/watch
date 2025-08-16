import requests
import json
import urllib.parse
import time

# Endpoint
BASE_URL = "https://scratch-earn-tma.fly.dev/api/v1/user"
WATCH_ENDPOINT = f"{BASE_URL}/watch"
SCRATCH_ENDPOINT = f"{BASE_URL}/scratch"
CLAIM_ENDPOINT = f"{BASE_URL}/scratch/claim"

HEADERS_BASE = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://tma.scratchearn.xyz",
    "referer": "https://tma.scratchearn.xyz/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

def parse_uid(initdata: str):
    parsed = urllib.parse.parse_qs(initdata)
    if "user" not in parsed:
        return None
    user_data = json.loads(parsed["user"][0])
    return user_data.get("id")

def login(initdata: str):
    uid = parse_uid(initdata)
    if not uid:
        print("❌ Gagal parse UID dari initData")
        return None

    payload = {"uid": uid, "referBy": ""}

    try:
        r = requests.post(BASE_URL, json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            token = data.get("token") or data.get("data", {}).get("token")
            if token:
                print(f"✅ Login sukses UID {uid}")
                return token
            else:
                print(f"⚠️ Respon login tanpa token: {data}")
                return None
        else:
            print(f"❌ Login gagal {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print(f"❌ Error login: {e}")
        return None

def watch_ads(token):
    headers = HEADERS_BASE.copy()
    headers["token"] = token

    # Aturan watch
    watch_plan = {
        "richads": 8,
        "adextra": 50,
        "gigapub": 50,
        "monetag": 50
    }

    for name, count in watch_plan.items():
        for i in range(count):
            try:
                r = requests.post(WATCH_ENDPOINT, headers=headers, json={"name": name})
                print(f"▶️ Watch {name} [{i+1}/{count}]: {r.text}")
                time.sleep(1)  # jeda 1 detik antar watch
            except Exception as e:
                print(f"⚠️ Gagal watch {name} [{i+1}/{count}]: {e}")

def scratch(token):
    headers = HEADERS_BASE.copy()
    headers["token"] = token
    try:
        r = requests.post(SCRATCH_ENDPOINT, headers=headers)
        print(f"🎯 Scratch: {r.text}")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Gagal scratch: {e}")

    try:
        r = requests.post(CLAIM_ENDPOINT, headers=headers)
        print(f"💰 Claim: {r.text}")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Gagal claim: {e}")

def main():
    try:
        with open("watch.txt", "r") as f:
            initdatas = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ File watch.txt tidak ditemukan")
        return

    for i, initdata in enumerate(initdatas, start=1):
        print(f"\n============== Akun {i} ==============")
        token = login(initdata)
        if not token:
            print("⛔ Skip akun ini karena login gagal")
            continue

        watch_ads(token)
        scratch(token)

    print("\n✅ Selesai semua akun")

if __name__ == "__main__":
    main()
              
