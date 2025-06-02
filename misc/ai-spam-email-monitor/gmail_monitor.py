#!/usr/bin/env python3
import os
import time
import json
import base64
import email
import argparse
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from auth import get_gmail_service, sign_out
from gemini_spam_detector import GeminiSpamDetector, setup_gemini

def get_unread_emails(service):
    """
    Fetches unread emails from the primary inbox only
    Returns a list of unread messages, excluding Promotions, Updates, Social, etc.
    """
    try:
        # Search for unread messages in the primary inbox only
        # The 'category:primary' filter ensures we only get messages from the primary tab
        results = service.users().messages().list(
            userId='me',
            q='is:unread in:inbox category:primary',
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f"Error fetching unread emails: {e}")
        return []

def mark_as_read(message_id, service):
    """
    Marks an email as read by removing the UNREAD label
    """
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error marking email {message_id} as read: {e}")
        return False

def send_reply(service, message_id, thread_id, to_email, subject, message_text):
    """
    Send a reply to an email using the Gmail API, ensuring it's in the same thread
    """
    try:
        # Create a MIMEText object for the email content
        message = MIMEText(message_text)
        message['to'] = to_email
        message['from'] = 'me'  # 'me' refers to the authenticated user
        
        # Make sure subject has Re: prefix if it doesn't already
        if not subject.lower().startswith('re:'):
            message['subject'] = f"Re: {subject}"
        else:
            message['subject'] = subject
            
        # These headers are critical for threading
        message['In-Reply-To'] = message_id
        message['References'] = message_id
        
        # Encode the message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Create the message body with thread ID
        body = {
            'raw': raw,
            'threadId': thread_id
        }
        
        # Send the message as part of the thread
        sent_message = service.users().messages().send(
            userId='me', 
            body=body
        ).execute()
        
        print("\n" + "-"*80)
        print("✓ Reply sent successfully!")
        print(f"To: {to_email}")
        print(f"Subject: {message['subject']}")
        print(f"Message: {message_text}")
        print(f"Thread ID: {thread_id}")
        print("-"*80)
        
        return True
    except Exception as e:
        print(f"Error sending reply: {e}")
        return False

def extract_email_content(msg):
    """
    Extract the full body content from an email message
    """
    body = ""
    
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body_data = part['body'].get('data', '')
                if body_data:
                    body += base64.urlsafe_b64decode(body_data).decode('utf-8')
    elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
        body_data = msg['payload']['body'].get('data', '')
        if body_data:
            body += base64.urlsafe_b64decode(body_data).decode('utf-8')
    
    return body or "No body content"

def display_email_info(message, service, spam_detector=None):
    """
    Displays relevant information about an email message,
    marks it as read, and sends an automatic reply
    """
    try:
        # Get the full message details
        msg = service.users().messages().get(
            userId='me', 
            id=message['id'],
            format='full'
        ).execute()
        
        # Extract headers
        headers = msg['payload']['headers']
        subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown Sender')
        reply_to = next((header['value'] for header in headers if header['name'].lower() == 'reply-to'), sender)
        date = next((header['value'] for header in headers if header['name'].lower() == 'date'), 'Unknown Date')
        
        # Get Message-ID for proper threading
        message_id = next((header['value'] for header in headers if header['name'].lower() == 'message-id'), message['id'])
        thread_id = msg['threadId']
        
        # Extract email address from sender format "Name <email@example.com>"
        reply_email = reply_to
        if '<' in reply_to and '>' in reply_to:
            reply_email = reply_to.split('<')[1].split('>')[0]
        
        # Get full body for spam detection
        full_body = extract_email_content(msg)
        
        # Get truncated body for display
        display_body = full_body[:100] + "..." if len(full_body) > 100 else full_body
        
        # Print formatted email info
        print("\n" + "="*80)
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Thread ID: {thread_id}")
        print("-"*80)
        print(f"Preview: {display_body}")
        
        # Check if this is from a known spam thread first
        is_spam_thread = False
        if spam_detector and spam_detector.is_ready():
            is_spam_thread = spam_detector.is_spam_thread(thread_id)
            if is_spam_thread:
                print("\n🔄 This is a continuation of a previously identified spam thread")
        
        # Analyze for spam if detector is available and it's not already a known spam thread
        spam_analysis = None
        if spam_detector and spam_detector.is_ready():
            if not is_spam_thread:
                print("\nAnalyzing email for spam...")
                email_data = {
                    'sender': sender,
                    'subject': subject,
                    'body': full_body,
                    'thread_id': thread_id
                }
                
                spam_analysis = spam_detector.analyze_email(email_data)
                
                print(f"Spam Analysis:")
                print(f"  Is Spam: {'Yes' if spam_analysis['is_spam'] else 'No'}")
                print(f"  Confidence: {spam_analysis['confidence']:.2f}")
                # print(f"  Reasoning: {spam_analysis['reasoning'][:150]}...")
            else:
                # Create a synthetic spam analysis result for known spam threads
                spam_analysis = {
                    'is_spam': True,
                    'confidence': 1.0,
                    'reasoning': "This email is part of a previously identified spam conversation thread."
                }
        
        print("="*80)
        
        # Mark the email as read after displaying it
        if mark_as_read(message['id'], service):
            print("✓ Marked as read")
        else:
            print("✗ Failed to mark as read")
        
        # Prepare and send the reply based on spam detection
        reply_text = ""
        
        # If it's spam (either new spam or part of a spam thread)
        if spam_analysis and spam_analysis['is_spam']:
            email_data = {
                'sender': sender,
                'subject': subject,
                'body': full_body,
                'thread_id': thread_id
            }
            
            # Check if this is a continuation of a spam thread
            if is_spam_thread:
                print("\n🎣 Generating follow-up reply for spam conversation...")
                reply_text = spam_detector.generate_email_reply(email_data, is_continuation=True)
            else:
                print("\n🎣 Generating initial time-wasting reply for spam email...")
                reply_text = spam_detector.generate_email_reply(email_data, is_continuation=False)
                
            print(f"Generated reply:\n{'-'*40}\n{reply_text}\n{'-'*40}")
        elif spam_analysis:
            # If it's not spam but we analyzed it
            spam_status = "NOT SPAM"
            confidence = f"{spam_analysis['confidence'] * 100:.1f}%"
            
            reply_text = (
                "Thank you for your email. This is an automated response.\n\n"
                "I've received your message and will get back to you as soon as possible.\n\n"
                f"[AI SPAM ANALYSIS: This email has been analyzed and is classified as {spam_status} "
                f"with {confidence} confidence.]\n\n"
                "Best regards,\nAutomated Gmail Monitor"
            )
        else:
            # No spam analysis was performed
            reply_text = (
                "Thank you for your email. This is an automated response.\n\n"
                "I've received your message and will get back to you as soon as possible.\n\n"
                "Best regards,\nAutomated Gmail Monitor"
            )
        
        send_reply(
            service, 
            message_id,  # Use actual Message-ID instead of Gmail's internal ID
            thread_id, 
            reply_email, 
            subject, 
            reply_text
        )
        
        return True
    except Exception as e:
        print(f"Error displaying email {message['id']}: {e}")
        return False

def main():
    """
    Main function that monitors the inbox for unread emails
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Gmail Inbox Monitor')
    parser.add_argument('--signout', action='store_true', help='Sign out and remove saved credentials')
    parser.add_argument('--setup-gemini', action='store_true', help='Configure Google Gemini API')
    args = parser.parse_args()
    
    # Handle sign out request
    if args.signout:
        success, message = sign_out()
        print(message)
        return
    
    # Set up Gmail API service
    service = get_gmail_service()
    
    # Set up Gemini spam detector
    spam_detector = None
    if args.setup_gemini:
        print("Setting up Google Gemini for spam detection...")
        spam_detector = setup_gemini()
    else:
        spam_detector = GeminiSpamDetector()
        
    if not spam_detector.is_ready():
        print("\nWARNING: Google Gemini API is not configured.")
        print("Spam detection features will be disabled.")
        print("Run with --setup-gemini to configure Gemini API")
    else:
        print("\nSpam detection is enabled.")
    
    print("Starting Gmail inbox monitor. Press Ctrl+C to stop.")
    print("Emails will be automatically marked as read and replied to after displaying.")
    
    try:
        while True:
            # Get unread emails
            unread_emails = get_unread_emails(service)
            
            # Display info for each unread email
            if unread_emails:
                print(f"\nFound {len(unread_emails)} unread email(s).")
                for email in unread_emails:
                    display_email_info(email, service, spam_detector)
            else:
                print("\nNo unread emails found.", end="\r")
            
            # Wait for 5 seconds before checking again
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\nExiting Gmail monitor.")

if __name__ == "__main__":
    main() 