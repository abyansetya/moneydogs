import requests
import json
import time
from colorama import Fore, Style

RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT

def get_headers(access_token=None):
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Microsoft Edge\";v=\"128\", \"Microsoft Edge WebView2\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Referer": "https://app.moneydogs-ton.com/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    if access_token:
        headers["x-auth-token"] = f"{access_token}"
    return headers

def auth(encoded_message, retries=3, delay=2):
    url = "https://api.moneydogs-ton.com/sessions"
    headers = get_headers()
    headers.update({"content-type": "application/json"})
    body = {
        "encodedMessage": encoded_message
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            response.raise_for_status()  # Raise exception if HTTP status code is 4xx/5xx
            if response.status_code == 200:
                response_json = response.json()
                return response_json.get('token')  # Return the token
        except (requests.RequestException, ValueError) as e:
            print(f"{RED}Error getting token: {e}", flush=True)
            if attempt < retries - 1:
                print(f"{YELLOW}Retrying... ({attempt + 1}/{retries})", end="\r", flush=True)
                time.sleep(delay)
            else:
                return None
    
def get_tasks(token):
    url = "https://api.moneydogs-ton.com/tasks"
    headers = get_headers(token)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def complete_tasks(token, task_id):
    url = f"https://api.moneydogs-ton.com/tasks/{task_id}/verify"
    headers = get_headers(token)
    headers.update({"content-type": "application/json"})

    try:
        response = requests.post(url, headers=headers)  # Fixed typo here (was `requets`)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as e:
        print(Fore.RED + f"Failed to verify task {task_id}: {e}")
        return None

def run_account(encoded_message):
    try:
        token = auth(encoded_message)
        if not token:
            return (None, 0)

        tasks = get_tasks(token)
        for task in tasks:
            task_id = task.get('id')
            task_name = task.get("title")
            if task_id:
                print(Fore.YELLOW + f"\nTrying to complete task: {task_name}")
                result = complete_tasks(token, task_id)
                if result:
                    print(Fore.WHITE + f"Verification result for task {task_id}: {result}")
            time.sleep(5)

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred: {e}")
        return (None, 0)

def main():
    with open("query.txt", "r") as file:
        queries = file.read().splitlines()

    for query in queries:
        result = run_account(query)

if __name__ == "__main__":
    main()
