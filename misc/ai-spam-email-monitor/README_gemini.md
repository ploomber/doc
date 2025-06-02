# Gmail Spam Detection with Google Gemini

This extension adds AI-powered spam detection to the Gmail Inbox Monitor using Google's Gemini API.

## Getting Started with Gemini Spam Detection

### Prerequisites

- All the requirements from the original Gmail Inbox Monitor
- Google Gemini API key

### Setting Up Google Gemini

1. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **Get a Google Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a Google account if you don't have one
   - Create a new API key (You may need to enter payment information, but Google offers free credits)
   - Save your API key in a secure place

3. **Configure Gemini for Spam Detection**:
   ```
   python gemini_spam_detector.py
   ```
   - This will prompt you to enter your API key
   - It will test the connection and save your configuration

### Using Spam Detection

Once set up, you can use the spam detection functionality in two ways:

1. **Run the example spam detection monitor**:
   ```
   python spam_detector_example.py
   ```
   
   This script will:
   - Monitor your inbox for new emails
   - Analyze each email using Google Gemini
   - Identify potential spam emails
   - Handle legitimate emails normally

2. **Configure Gemini directly**:
   ```
   python spam_detector_example.py --setup-gemini
   ```
   
   This will guide you through the Gemini setup process if you haven't done it yet.

## How It Works

The spam detection system uses Google's Gemini AI to analyze incoming emails by:

1. Extracting the sender, subject, and body of each email
2. Sending this information to the Gemini API for analysis
3. Processing the AI's response to determine if the email is spam
4. Handling the email differently based on the spam determination

## Customization

You can modify the spam detection behavior by:

- Changing the Gemini model in `gemini_spam_detector.py` (default is "gemini-2.0-flash-lite")
- Editing the prompt template in the `analyze_email` method
- Adding custom handling for detected spam emails in `handle_email_with_spam_detection`

## Integration

The spam detection functionality is designed to work alongside the existing Gmail Inbox Monitor, not replace it. You can:

- Use just the original inbox monitor without spam detection
- Use the new spam detection example that builds on the original functionality
- Create your own custom integration using the `GeminiSpamDetector` class

## Troubleshooting

If you encounter issues:

- Ensure your API key is correct and active
- Check that you have internet connectivity
- Verify you have sufficient API quota/credits with Google
- Look for any error messages in the console output

## Notes

- The Gemini API may have usage limits based on your account
- Processing very large emails may consume more API resources
- Your API key is stored locally in `gemini_config.json` 