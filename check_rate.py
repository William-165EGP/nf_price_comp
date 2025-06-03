import requests, json, os, subprocess

API_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/twd.json"
CACHE_FILE = "twd.json"

def get_twd_exchange_rate():
    try:
        response = requests.get(API_URL, timeout=5)
        return response.json().get("twd", {})
    except:
        return {}

def load_last_rates():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return data.get("twd", {})
    return {}

def save_current_rates():
    response = requests.get(API_URL, timeout=5)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        f.write(response.text)

def has_significant_change(new_rates, old_rates, using_currency, threshold=0.1):
    for k in new_rates:
        if k not in using_currency:
#            print(k)
            continue
        elif k in old_rates and old_rates[k] > 0:
            change = abs(new_rates[k] - old_rates[k]) / old_rates[k]
            if change > threshold:
                print(f"{k.upper()} changed {change*100:.2f}%")
                return True
    return False

def commit_and_push():
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", CACHE_FILE], check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode != 0:
        subprocess.run(["git", "commit", "-m", "Update twd.json via check_rate"], check=True)
        repo = os.environ.get("GITHUB_REPOSITORY")
        token = os.environ.get("GH_PAT")
        subprocess.run([
            "git", "push",
            f"https://x-access-token:{token}@github.com/{repo}.git"
        ], check=True)

def load_using_currency():
    with open('static.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    using_currency = set()
    for key, value in data.items():
#        print(key, value)
        using_currency.add(value['currency'].lower())
#    print(using_currency)
    return using_currency

if __name__ == "__main__":
    current = get_twd_exchange_rate()
    last = load_last_rates()
    using_currency = load_using_currency()

    if has_significant_change(current, last, using_currency):
        print("Significant rate change detected, committing new data")
        save_current_rates()
        commit_and_push()
    else:
        print("No significant change in exchange rates")