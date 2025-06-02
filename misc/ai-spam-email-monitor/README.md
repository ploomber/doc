# Gmail Inbox Monitor

A simple Python application that monitors your Gmail inbox for unread emails and displays them in the terminal. The app refreshes every 5 seconds to show new unread emails and can analyze emails for spam using Google's Gemini AI.

## Prerequisites

- Python 3.6+
- Gmail account
- Google Cloud project with Gmail API enabled
- (Optional) Google Gemini API key for spam detection

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up Google API credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select an existing one)
   - Enable the Gmail API
   - Create OAuth credentials (Desktop application)
   - Download the credentials JSON file and save it as `credentials.json` in the project directory

4. (Optional) Set up Google Gemini for spam detection:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Run the setup command:
     ```
     python gmail_monitor.py --setup-gemini
     ```
   - Follow the prompts to enter your API key

## Usage

1. Run the authentication module to set up your credentials:
   ```
   python auth.py
   ```
   - This will open a browser window where you need to log in with your Google account and grant permissions
   - After successful authentication, a `token.json` file will be created

2. Run the main script to monitor your inbox:
   ```
   python gmail_monitor.py
   ```
   
3. Press Ctrl+C to stop the application

## Spam Detection and Response

When spam detection is enabled:

- Each email is analyzed by Google's Gemini AI
- If an email is identified as legitimate, a standard auto-reply is sent with the spam analysis result
- If an email is identified as spam, the system generates a clever time-wasting reply
  - The reply is designed to bait spammers by showing interest without revealing any valuable information
  - It asks questions that require lengthy responses and maintains a naive but interested tone
  - This helps waste spammers' time and resources while keeping you safe

### Conversation Tracking

The system tracks spam email threads persistently:

- Once an email is identified as spam, the entire conversation thread is marked for special handling
- All future replies in that thread will automatically receive AI-generated responses
- The system uses different prompts for initial spam emails versus follow-up messages
- Thread information is stored between sessions in `spam_threads.json`

To set up or reconfigure spam detection:
```
python gmail_monitor.py --setup-gemini
```

## Sign Out / Switch Accounts

You can sign out (remove saved credentials) in two ways:

1. Using the main script:
   ```
   python gmail_monitor.py --signout
   ```

2. Using the auth module directly:
   ```
   python auth.py --signout
   ```

After signing out, you'll need to re-authenticate the next time you run the application, allowing you to use a different Google account.

## Customization

You can modify the following aspects of the application:
- Change the refresh interval (default: 5 seconds)
- Adjust email display format
- Add filters for specific senders or subjects
- Modify the spam detection prompt in `gemini_spam_detector.py`
- Customize the spam-baiting reply generation by editing the prompt in the `generate_email_reply` function
