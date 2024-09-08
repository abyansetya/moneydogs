# MoneyDogs Automation Script

This script automates tasks for the MoneyDogs-TON platform, including user authentication, retrieving tasks, and verifying task completion. The script reads encoded messages from a text file and processes them sequentially.

## Features

- **Authentication**: Authenticates the user and retrieves an access token using an encoded message.
- **Retrieve Tasks**: Fetches the list of available tasks associated with the user's account.
- **Complete Tasks**: Automatically attempts to verify and complete each task.
- **Retry Mechanism**: Retries requests in case of temporary errors.

## File Structure

```
├── moneydogs.py      # Main Python script for running the automation.
├── query.txt         # Text file that contains encoded messages (one per line).
└── README.md         # Documentation for the script.
```

### `main.py`

This is the main script that handles the logic for authentication, fetching tasks, and completing them. The script reads encoded messages from `query.txt`.

### `query.txt`

This file contains one or more encoded messages, each on a new line. Each message is used for user authentication.

Example `query.txt` content:

```
query_id=
query_id=
query_id=
```

## Usage

1. **Install Dependencies**  
   First, make sure you have the required Python libraries installed. You can install them via pip:

   ```bash
   pip install requests colorama
   ```

2. **Prepare `query.txt`**  
   Add your encoded messages (one per line) to the `query.txt` file. These messages are used to authenticate users.

3. **Run the Script**  
   Run the script using the following command:

   ```bash
   python moneydogs.py
   ```

   The script will:

   - Authenticate each user with the encoded messages.
   - Retrieve the list of tasks for each user.
   - Attempt to complete and verify each task.

   You will see task verification status and error messages (if any) printed in the console.

## Error Handling

- The script retries failed requests up to 3 times with a 2-second delay between attempts.
- If the token or tasks retrieval fails after all retries, an error message will be shown, and the script will continue processing the next user.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
