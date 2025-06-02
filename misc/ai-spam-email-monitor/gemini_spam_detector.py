#!/usr/bin/env python3
import os
import json
import google.generativeai as genai
from typing import Dict, Tuple, Any, Optional, List, Set

# Constants
GEMINI_CONFIG_FILE = "gemini_config.json"
SPAM_THREADS_FILE = "spam_threads.json"
DEFAULT_MODEL = "gemini-2.0-flash-lite"  # You can change this to another model if needed

class GeminiSpamDetector:
    """Class to handle Google Gemini integration for spam detection"""
    
    def __init__(self, config_path: str = GEMINI_CONFIG_FILE, spam_threads_path: str = SPAM_THREADS_FILE):
        """Initialize the Gemini client"""
        self.config_path = config_path
        self.spam_threads_path = spam_threads_path
        self.api_key = None
        self.model = DEFAULT_MODEL
        self.is_configured = False
        self.spam_threads = set()
        self._load_config()
        self._load_spam_threads()
        
    def _load_config(self) -> None:
        """Load Gemini API configuration from file if it exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                self.api_key = config.get('api_key')
                self.model = config.get('model', DEFAULT_MODEL)
                
                if self.api_key:
                    genai.configure(api_key=self.api_key)
                    self.is_configured = True
            except Exception as e:
                print(f"Error loading Gemini configuration: {e}")
    
    def _load_spam_threads(self) -> None:
        """Load spam thread IDs from file if it exists"""
        if os.path.exists(self.spam_threads_path):
            try:
                with open(self.spam_threads_path, 'r') as f:
                    thread_data = json.load(f)
                self.spam_threads = set(thread_data.get('spam_threads', []))
            except Exception as e:
                print(f"Error loading spam threads: {e}")
                self.spam_threads = set()
    
    def _save_spam_threads(self) -> None:
        """Save spam thread IDs to file"""
        try:
            with open(self.spam_threads_path, 'w') as f:
                json.dump({
                    'spam_threads': list(self.spam_threads)
                }, f)
        except Exception as e:
            print(f"Error saving spam threads: {e}")
    
    def mark_thread_as_spam(self, thread_id: str) -> None:
        """Mark a thread as spam to ensure all future replies use AI generation"""
        if thread_id and thread_id not in self.spam_threads:
            self.spam_threads.add(thread_id)
            self._save_spam_threads()
            print(f"Thread {thread_id} marked as spam for continued AI responses")
    
    def is_spam_thread(self, thread_id: str) -> bool:
        """Check if a thread has been previously marked as spam"""
        return thread_id in self.spam_threads
    
    def configure(self, api_key: str, model: str = DEFAULT_MODEL) -> Tuple[bool, str]:
        """Configure the Gemini client with API key and save to config file"""
        try:
            # Set the API key in the SDK
            genai.configure(api_key=api_key)
            
            # Save configuration
            self.api_key = api_key
            self.model = model
            self.is_configured = True
            
            # Test connection
            models = genai.list_models()
            model_exists = any(m.name.endswith(model) for m in models)
            
            if not model_exists:
                return False, f"API key valid but model '{model}' not found. Using default model."
                
            # Save to config file
            with open(self.config_path, 'w') as f:
                json.dump({
                    'api_key': api_key,
                    'model': model
                }, f)
                
            return True, "Gemini API configured successfully"
        except Exception as e:
            self.is_configured = False
            return False, f"Error configuring Gemini API: {str(e)}"
    
    def is_ready(self) -> bool:
        """Check if the Gemini client is properly configured"""
        return self.is_configured
    
    def analyze_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an email to determine if it's spam
        
        Args:
            email_data: Dictionary containing email data with at least:
                        - sender: The email sender
                        - subject: The email subject
                        - body: The email body content
                        - thread_id: The email thread ID (optional)
                        
        Returns:
            Dictionary with analysis results:
                - is_spam: Boolean indicating if email is spam
                - confidence: Confidence score (0-1)
                - reasoning: Explanation of the decision
        """
        # Check if this is part of a known spam thread
        thread_id = email_data.get('thread_id', '')
        if thread_id and self.is_spam_thread(thread_id):
            # If it's in a spam thread, treat it as spam automatically
            return {
                'is_spam': True,
                'confidence': 1.0,
                'reasoning': "This email is part of a previously identified spam conversation thread.",
                'from_spam_thread': True  # Flag to indicate this wasn't newly analyzed
            }
        
        if not self.is_ready():
            return {
                'is_spam': False,
                'confidence': 0,
                'reasoning': "Gemini API not configured",
                'error': "API not configured"
            }
        
        try:
            # Prepare email content for analysis
            sender = email_data.get('sender', 'Unknown Sender')
            subject = email_data.get('subject', 'No Subject')
            body = email_data.get('body', 'No Content')
            
            # Truncate body if too long
            if len(body) > 5000:
                body = body[:5000] + "..."
            
            # Create prompt for the model
            prompt = f"""
            Analyze this email and determine if it's spam or legitimate.
            
            FROM: {sender}
            SUBJECT: {subject}
            BODY: 
            {body}
            
            Provide your analysis in the following format:
            IS_SPAM: [Yes/No]
            CONFIDENCE: [0-100]
            REASONING: [Brief explanation of your decision]
            """
            
            # Get Gemini model
            model = genai.GenerativeModel(self.model)
            
            # Generate response
            response = model.generate_content(prompt)
            
            # Parse response
            result_text = response.text
            is_spam = "YES" in result_text.upper().split("IS_SPAM:")[1].split("\n")[0]
            
            # Extract confidence
            confidence_line = result_text.upper().split("CONFIDENCE:")[1].split("\n")[0].strip()
            try:
                # Handle percentage or decimal format
                confidence = float(confidence_line.replace("%", "").strip())
                if confidence > 1:  # If it's a percentage (0-100)
                    confidence /= 100
            except:
                confidence = 0.5  # Default if parsing fails
                
            # Extract reasoning
            reasoning = "No reasoning provided"
            if "REASONING:" in result_text.upper():
                reasoning = result_text.split("REASONING:")[1].strip()
            
            # If this is spam and we have a thread ID, mark the thread
            if is_spam and thread_id:
                self.mark_thread_as_spam(thread_id)
            
            return {
                'is_spam': is_spam,
                'confidence': confidence,
                'reasoning': reasoning
            }
            
        except Exception as e:
            return {
                'is_spam': False,
                'confidence': 0,
                'reasoning': "Error analyzing email",
                'error': str(e)
            }
    
    def generate_email_reply(self, email_data: Dict[str, Any], is_continuation: bool = False) -> str:
        """
        Generate a reply for an email - either a time-wasting reply for spam or a contextual follow-up
        
        Args:
            email_data: Dictionary containing email data
            is_continuation: Whether this is a continuation of a spam thread
                        
        Returns:
            A string containing the generated reply
        """
        if not self.is_ready():
            return "Unable to generate reply - Gemini API not configured"
        
        try:
            # Extract email content
            sender = email_data.get('sender', 'Unknown Sender')
            subject = email_data.get('subject', 'No Subject')
            body = email_data.get('body', 'No Content')
            
            # Try to extract sender's name for personalized greeting
            sender_name = ""
            if '<' in sender:
                # Format typically like: "John Doe <john@example.com>"
                sender_name = sender.split('<')[0].strip()
                # If there are quotes, remove them
                sender_name = sender_name.replace('"', '').replace("'", '')
                # Get first name only
                sender_name = sender_name.split()[0] if sender_name else ""
            
            # Truncate body if too long
            if len(body) > 5000:
                body = body[:5000] + "..."
            
            # Adjust prompt based on whether this is a continuation or initial contact
            if is_continuation:
                prompt_intro = """
                You're continuing a conversation with a spammer. You need to craft a follow-up response that 
                continues to waste their time by showing interest while revealing no actual valuable information.
                
                This is part of an ongoing conversation where you're pretending to be interested in their offer.
                """
            else:
                prompt_intro = """
                You're going to help me craft a response to a spam email. The goal is to waste the spammer's time by 
                showing just enough interest to keep them engaged, but without revealing any real personal information.
                """
            
            # Create prompt for the model with VERY clear formatting instructions
            prompt = f"""
            {prompt_intro}

            Here's the email you're responding to:
            
            FROM: {sender}
            SUBJECT: {subject}
            BODY: 
            {body}
            
            Create a reply that:
            1. Shows interest but remains vague
            2. Asks questions that will require lengthy responses
            3. Pretends to be slightly confused or naive
            4. Hints at potential value to the scammer without committing to anything
            5. NEVER provides any real personal information, financial details, or anything valuable
            6. Maintains a friendly, slightly eager tone
            7. Is brief (maximum 8-10 sentences) to appear genuine
            8. Uses SHORT paragraphs (1-2 sentences per paragraph maximum)
            9. Includes 3-5 paragraphs with good spacing between them
            10. Does NOT include any subject line (this will be handled automatically)
            11. Does NOT artificially split sentences into multiple lines - let each sentence flow naturally regardless of length
            12. Only use line breaks to separate paragraphs, not within paragraphs
            
            IMPORTANT FORMATTING INSTRUCTIONS:
            - Each paragraph should be written as continuous text with NO line breaks inside it
            - Only use line breaks to separate different paragraphs
            - Do not split sentences across multiple lines
            - Do not try to limit the width of text
            - Do not use any artificial text wrapping
            
            Write ONLY the email body text with proper paragraph formatting. Don't include any additional explanations or commentary.
            """
            
            # Get Gemini model
            model = genai.GenerativeModel(self.model)
            
            # Generate response with very specific formatting requirements
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Clean up and format the response
            reply_text = response.text.strip()
            
            # Remove any subject line if present (looking for patterns like "Subject:" or "Re:")
            if reply_text.lower().startswith("subject:") or reply_text.lower().startswith("re:"):
                lines = reply_text.split('\n')
                reply_text = '\n'.join(lines[1:]).strip()
            
            return reply_text
            
        except Exception as e:
            return f"Unable to generate reply: {str(e)}"
    
    # Keeping the original method name for backward compatibility
    def generate_spam_reply(self, email_data: Dict[str, Any]) -> str:
        """Alias for generate_email_reply for backward compatibility"""
        return self.generate_email_reply(email_data)

def setup_gemini() -> GeminiSpamDetector:
    """Helper function to create and return a configured GeminiSpamDetector instance"""
    detector = GeminiSpamDetector()
    
    if not detector.is_ready():
        print("\nGoogle Gemini API is not configured.")
        print("You need to set up your API key to use spam detection features.")
        print("Go to https://makersuite.google.com/app/apikey to get your API key")
        
        api_key = input("\nEnter your Gemini API key: ").strip()
        
        if api_key:
            success, message = detector.configure(api_key)
            print(message)
        else:
            print("No API key provided. Gemini features will be disabled.")
    
    return detector

if __name__ == "__main__":
    """Run this file directly to configure Gemini API"""
    print("Google Gemini Spam Detector Setup")
    print("=================================")
    print("This tool will help you configure Google Gemini for spam detection.")
    
    detector = setup_gemini()
    
    if detector.is_ready():
        print("\nTesting Gemini connection...")
        
        # Simple test with a sample email
        test_email = {
            'sender': 'test@example.com',
            'subject': 'Hello, this is a test email',
            'body': 'This is a test email to verify the spam detection functionality.'
        }
        
        result = detector.analyze_email(test_email)
        
        print("\nTest Analysis Results:")
        print(f"Is Spam: {result['is_spam']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
        
        print("\nSetup complete! You can now use the spam detection functionality.")
    else:
        print("\nSetup incomplete. Please run this script again to configure Gemini API.") 