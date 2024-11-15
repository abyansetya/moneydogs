import requests
import json
import time
from colorama import Fore, Style
from urllib.parse import unquote
import re
from datetime import datetime

RED = Fore.RED + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT

def get_formatted_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
            response.raise_for_status()
            if response.status_code == 200:
                return response.json().get('token')
        except (requests.RequestException, ValueError) as e:
            print(f"{RED}Error getting token: {e}", flush=True)
            if attempt < retries - 1:
                print(f"{YELLOW}Retrying... ({attempt + 1}/{retries})", end="\r", flush=True)
                time.sleep(delay)
            else:
                return None

def get_username(query_id):
    timestamp = Fore.MAGENTA + get_formatted_time() + Fore.RESET
    try:
        found = re.search('user=([^&]*)', query_id).group(1)
        decoded_user_part = unquote(found)
        user_obj = json.loads(decoded_user_part)
        username = user_obj['username']
        print(f"[{timestamp}] - Username: {Fore.GREEN}@{username}{Fore.RESET}")
        return username
    except Exception as e:
        print(f"[{timestamp}] - {Fore.RED}Error: Failed to extract username: {e}{Fore.RESET}")
        return None

def check_in(token):
    timestamp = Fore.MAGENTA + get_formatted_time() + Fore.RESET
    url = "https://api.moneydogs-ton.com/daily-check-in"
    headers = get_headers(token)

    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            print(f"[{timestamp}] - {Fore.GREEN}Check-in successful{Fore.RESET}")
        elif response.status_code == 400:
            print(f"[{timestamp}] - {Fore.YELLOW}already check-in{Fore.RESET}")
        else:
            print(f"[{timestamp}] - {Fore.RED}Unexpected status: {response.status_code}{Fore.RESET}")
    except requests.RequestException as e:
        print(f"[{timestamp}] - {Fore.RED}Error during check-in: {e}{Fore.RESET}")


def get_tasks(token, url):
    headers = get_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def complete_tasks(token, task):
    url = f"https://api.moneydogs-ton.com/tasks/{task['id']}/verify"
    headers = get_headers(token)
    headers.update({"content-type": "application/json"})
    timestamp = Fore.MAGENTA + get_formatted_time() + Fore.RESET

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        if response.status_code in [200, 201]:
            print(f"[{timestamp}] - {task['title']}: {Fore.GREEN}Completed!{Fore.RESET}")
        else:
            print(f"[{timestamp}] - {task['title']}: {Fore.RED}Manual task only!{Fore.RESET}")
        return response.status_code
    except (requests.RequestException, ValueError) as e:
        print(f"[{timestamp}] - {task['title']}: {Fore.RED}Manual task only!{Fore.RESET}")
        return None

def run_account(encoded_message):
    try:
        token = auth(encoded_message)
        if not token:
            return (None, 0)

        username = get_username(encoded_message)
        tasks = get_tasks(token, "https://api.moneydogs-ton.com/tasks")
        tasks_featured = get_tasks(token, "https://api.moneydogs-ton.com/tasks?isFeatured=true")
        checkin = check_in(token)

        for task in tasks + tasks_featured:
            complete_tasks(token, task)
            time.sleep(2)

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"An error occurred: {e}")
        return (None, 0)

def main():
    with open("query.txt", "r") as file:
        queries = file.read().splitlines()

    for query in queries:
        run_account(query)

    print("done")

if __name__ == "__main__":
    main()