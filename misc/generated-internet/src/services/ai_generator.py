from logging import Logger
from typing import Any
from datetime import datetime
import os
import re

from src.services.ai_provider import AIProvider, ClaudeClient, GeminiClient, OpenAIClient
from src.utils import get_interaction_javascript


class AIContentGenerator:
    """AI-powered HTML content generator for dynamic web interactions"""

    def __init__(self, api_key: str, provider: AIProvider, model: str):
        self.interaction_count = 0
        self.provider = provider
        
        # Initialize the appropriate AI client
        if provider == AIProvider.OPENAI:
            self.ai_client = OpenAIClient(
                api_key=api_key,
                model=model or "gpt-4o-mini"
            )
        elif provider == AIProvider.CLAUDE:
            self.ai_client = ClaudeClient(
                api_key=api_key,
                model=model or "claude-3-sonnet-20240229"
            )
        elif provider == AIProvider.GEMINI:
            self.ai_client = GeminiClient(
                api_key=api_key,
                model=model or "gemini-2.0-flash"
            )
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    

    def _inject_interaction_javascript(self, html_content: str) -> str:
        """Inject the interaction JavaScript into the HTML content"""
        interaction_js = get_interaction_javascript()
        
        # Try to inject before </body>
        if '</body>' in html_content:
            return html_content.replace('</body>', f'{interaction_js}</body>')
        
        # Try to inject before </html>
        elif '</html>' in html_content:
            return html_content.replace('</html>', f'{interaction_js}</html>')
        
        # If no proper structure, just append
        else:
            return html_content + interaction_js

    async def generate_content(self, interaction_data: dict[str, Any], logger: Logger) -> str:
        """Generate complete AI HTML page based on user interaction"""
        self.interaction_count += 1
        
        action_type = interaction_data.get('action_type', '')
        additional_data = interaction_data.get('additional_data', {})
        target = additional_data.get('target', '') if additional_data else ''
        input_value = interaction_data.get('input_value', '')
        
        # Generate complete HTML page
        logger.debug("Generating new page ..")
        html_content = await self._generate_complete_page(action_type, target, input_value)
        logger.debug("New page generated")
        
        cleaned_html = await self.clean_html(html_content)

        # Inject the interaction JavaScript to ensure continued functionality
        return self._inject_interaction_javascript(cleaned_html)
    
    async def clean_html(self, html_content: str) -> str:
        """Clean the HTML content to remove any unwanted elements"""
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        if html_content.endswith('```'):
            html_content = html_content[:-3]
        
        # Remove any other markdown code blocks
        html_content = re.sub(r'```.*?```', '', html_content, flags=re.DOTALL)
        
        return html_content

    async def _generate_complete_page(self, action_type: str, target: str, input_value: str) -> str:
        """Generate a complete HTML page with dynamic content"""
        
        # Create a descriptive prompt for the AI
        prompt = self._create_prompt(action_type, target, input_value)
        
        # Generate HTML using the selected AI provider
        return await self.ai_client.generate_html(prompt)

    def _create_prompt(self, action_type: str, target: str, input_value: str) -> str:
        """Create a descriptive prompt for AI content generation"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get specific prompt based on target/action
        specific_prompt = self._get_specific_prompt(action_type, target, input_value)
        
        if specific_prompt:
            return specific_prompt
        
        # Fallback to generic prompt
        base_prompt = f"""Create a modern, interactive HTML page for interaction #{self.interaction_count}.
        
        User performed: {action_type}
        Target element: {target}
        Input/Context: {input_value}
        Timestamp: {timestamp}
        
        Generate a creative, functional webpage that:
        1. Reflects the user's action and context
        2. Has beautiful, modern styling
        3. Includes interactive elements with proper data-action attributes
        4. Is fully responsive
        5. Has engaging content related to the interaction
        6. Includes navigation or "back" buttons for user flow
        
        CRITICAL: All clickable elements MUST have data-action and data-target attributes:
        - Links: <a href="#" data-action="navigate" data-target="page_name">
        - Buttons: <button data-action="action_type" data-target="target_name">
        - Forms: Include proper form elements and submit buttons
        - Search: Include search inputs and search buttons
        
        Make it unique and interesting based on the action type and context provided.
        """
        
        # Add specific guidance based on action type
        if action_type == "click":
            base_prompt += "\nFocus on creating an interactive page with clickable elements and animations."
        elif action_type == "input" or action_type == "form_submit" or action_type == "search":
            base_prompt += "\nCreate a page showing results of the search/input, with forms and input validation."
        elif action_type == "navigation" or action_type == "navigate":
            base_prompt += "\nBuild a page with navigation elements and menu systems."
        else:
            base_prompt += "\nCreate an engaging page that responds to the user's action."
        
        return base_prompt

    def _get_specific_prompt(self, action_type: str, target: str, input_value: str) -> str:
        """Get specific, tailored prompts for different targets/categories"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Base structure for all specific prompts
        base_structure = f"""
        CRITICAL REQUIREMENTS:
        - All clickable elements MUST have data-action and data-target attributes
        - Include navigation: <button data-action="navigate" data-target="home">🏠 Back to CyberHub</button>
        - Add interactive elements with proper data attributes
        - Make it fully responsive and visually appealing
        - Interaction #{self.interaction_count} • {timestamp}
        """
        
        # Category-specific prompts
        category_prompts = {
            # Main Categories
            "tech": f"""Create an immersive TECH ZONE website with a cyberpunk/hacker aesthetic.
            
            Include:
            - Latest tech news and breakthrough announcements
            - Interactive coding playground with syntax highlighting
            - Virtual computer specs comparison tool
            - Tech forums with active discussions
            - Software download sections
            - Hardware benchmarking tools
            - Programming tutorials and resources
            - AI/ML demos and experiments
            
            Style: Dark theme with neon green/blue accents, terminal-like fonts, glitch effects, animated code snippets
            {base_structure}""",
            
            "games": f"""Create an epic GAMES CENTRAL hub with retro gaming vibes.
            
            Include:
            - Game reviews and ratings system
            - Retro arcade with playable mini-games
            - Gaming news and announcements
            - Leaderboards and high scores
            - Game recommendation engine
            - Cheat codes and walkthroughs
            - Gaming forums and communities
            - Virtual game store
            
            Style: Retro 8-bit/16-bit aesthetic with pixel art, vibrant colors, arcade-style animations
            {base_structure}""",
            
            "music": f"""Create a vibrant MUSIC HUB with audio-visual elements.
            
            Include:
            - Music streaming interface with playlists
            - Artist profiles and discographies
            - Music creation tools and synthesizers
            - Concert listings and events
            - Music charts and trending tracks
            - Lyrics database and karaoke
            - Music forums and discussions
            - Vinyl collection showcase
            
            Style: Rich gradients, waveform visualizations, music-themed icons, vibrant colors
            {base_structure}""",
            
            "art": f"""Create an inspiring DIGITAL ART gallery and creation space.
            
            Include:
            - Digital art gallery with categories
            - Interactive drawing/painting tools
            - Artist portfolios and profiles
            - Art tutorials and techniques
            - NFT showcase and marketplace
            - Color palette generators
            - Art challenges and contests
            - Community feedback system
            
            Style: Creative, colorful, gallery-like with clean layouts, artistic typography
            {base_structure}""",
            
            "chat": f"""Create dynamic CHAT ROOMS with retro internet vibes.
            
            Include:
            - Multiple themed chat rooms
            - User profiles and avatars
            - Emoticon and emoji picker
            - Private messaging system
            - Chat history and logs
            - User status indicators
            - Moderation tools
            - Voice chat options
            
            Style: Classic IRC/MSN Messenger feel with chat bubbles, user lists, retro UI elements
            {base_structure}""",
            
            "news": f"""Create a comprehensive NEWS FEED platform.
            
            Include:
            - Breaking news ticker
            - Categorized news sections
            - Search and filtering options
            - Trending topics sidebar
            - Social sharing buttons
            - Comments and discussions
            - News archive
            - Weather and stock tickers
            
            Style: Clean newspaper layout with columns, headlines, professional typography
            {base_structure}""",
            
            "shop": f"""Create an exciting CYBER MALL shopping experience.
            
            Include:
            - Product categories and showcases
            - Shopping cart and wishlist
            - Product reviews and ratings
            - Search and filtering tools
            - Daily deals and discounts
            - User accounts and orders
            - Payment processing mockup
            - Store directory
            
            Style: E-commerce with product grids, shopping elements, promotional banners
            {base_structure}""",
            
            "forums": f"""Create classic BBS FORUMS with old-school internet charm.
            
            Include:
            - Multiple forum categories
            - Thread listings with post counts
            - User profiles and signatures
            - Search functionality
            - Sticky posts and announcements
            - Moderation tools
            - User reputation system
            - Recent activity feed
            
            Style: Classic forum layout with tables, user avatars, post threading
            {base_structure}""",
            
            "downloads": f"""Create a comprehensive DOWNLOADS center.
            
            Include:
            - Software categories and search
            - File information and screenshots
            - Download counters and ratings
            - User reviews and comments
            - Virus scan results
            - Mirror links and checksums
            - Popular/trending downloads
            - Upload interface
            
            Style: Clean file browser with icons, progress bars, download statistics
            {base_structure}""",
            
            "webmail": f"""Create a functional WEBMAIL interface.
            
            Include:
            - Inbox with email list
            - Compose new email form
            - Folder organization
            - Search and filtering
            - Attachment handling
            - Spam/junk filters
            - Settings and preferences
            - Address book
            
            Style: Clean email client interface with familiar email layouts
            {base_structure}""",
            
            "personal": f"""Create charming PERSONAL PAGES showcase.
            
            Include:
            - Personal website gallery
            - Profile creation tools
            - Blog/journal sections
            - Photo albums and galleries
            - Guestbook functionality
            - Link exchanges
            - Website building tools
            - Statistics and counters
            
            Style: Nostalgic 90s/early 2000s web design with geocities-style elements
            {base_structure}""",
            
            "links": f"""Create an awesome COOL LINKS directory.
            
            Include:
            - Categorized link collections
            - Link ratings and descriptions
            - User submissions
            - Random link generator
            - Search functionality
            - Recently added links
            - Popular/trending links
            - Link validation status
            
            Style: Simple directory layout with organized categories and descriptions
            {base_structure}""",
            
            # Hot Picks
            "vr": f"""Create an immersive VIRTUAL REALITY CENTRAL experience.
            
            Include:
            - VR game showcases with 360° previews
            - VR headset comparisons and reviews
            - Virtual worlds directory
            - VR development tools
            - Social VR spaces
            - VR fitness and education apps
            - Hardware setup guides
            - VR news and updates
            
            Style: Futuristic UI with 3D elements, immersive visuals, spatial design
            {base_structure}""",
            
            "ai": f"""Create an advanced AI PLAYGROUND with interactive demos.
            
            Include:
            - AI chatbot conversations
            - Image generation tools
            - Text analysis and processing
            - Machine learning demos
            - AI news and research
            - Model comparisons
            - Code generation tools
            - AI ethics discussions
            
            Style: Clean, modern tech interface with AI-themed elements, neural network visuals
            {base_structure}""",
            
            "cyber": f"""Create a comprehensive CYBERSPACE EXPLORER.
            
            Include:
            - Network visualization tools
            - Cybersecurity resources
            - Hacking challenges and CTFs
            - Digital privacy guides
            - Cryptocurrency tracking
            - Darknet exploration (educational)
            - Security tools directory
            - Cyber threat monitoring
            
            Style: Matrix-inspired design with green terminals, network graphs, hacker aesthetics
            {base_structure}""",
            
            "retro": f"""Create an authentic RETRO GAMING ZONE.
            
            Include:
            - Classic game emulators
            - Retro console showcases
            - High score leaderboards
            - Gaming history timeline
            - Retro game reviews
            - Arcade cabinet gallery
            - Chiptune music player
            - Vintage gaming forums
            
            Style: Authentic retro design with pixel fonts, CRT effects, classic gaming colors
            {base_structure}""",
            
            "digital": f"""Create extensive DIGITAL ARCHIVES.
            
            Include:
            - Historical document collections
            - Digital preservation tools
            - Archive search functionality
            - Timeline visualizations
            - Metadata management
            - Download and sharing options
            - Contribution system
            - Educational resources
            
            Style: Library-like interface with organized sections, clean typography
            {base_structure}""",
            
            # Featured Sites
            "portal": f"""Create GITPLACE - a developer's code sharing platform.
            
            Include:
            - Repository listings and search
            - Code viewer with syntax highlighting
            - User profiles and contributions
            - Issue tracking system
            - Pull request interface
            - Project documentation
            - Collaboration tools
            - Code statistics and insights
            
            Style: GitHub-inspired clean interface with code-focused layout
            {base_structure}""",
            
            "community": f"""Create ORANGEDIT - a vibrant discussion platform.
            
            Include:
            - Subreddit-style communities
            - Upvoting and downvoting system
            - Comment threading
            - User karma and profiles
            - Post filtering and sorting
            - Trending topics
            - Community moderation
            - Award system
            
            Style: Reddit-inspired layout with community focus, voting elements
            {base_structure}""",
            
            "library": f"""Create INSTAPICTURE - a photo sharing social network.
            
            Include:
            - Photo feed with filters
            - Story and highlights system
            - User profiles and followers
            - Photo editing tools
            - Hashtag system
            - Direct messaging
            - Explore and discover
            - Shopping integration
            
            Style: Instagram-inspired visual design with photo grids, stories layout
            {base_structure}""",
            
            "lab": f"""Create YALOUMAIL - a comprehensive email service.
            
            Include:
            - Modern inbox interface
            - Email composition with rich text
            - Folder organization
            - Advanced search and filters
            - Calendar integration
            - Contact management
            - Security features
            - Mobile-responsive design
            
            Style: Yahoo Mail inspired interface with modern email design patterns
            {base_structure}""",
            
            "market": f"""Create AMAXON SHOP - a massive online marketplace.
            
            Include:
            - Product search and categories
            - Shopping cart and checkout
            - Product reviews and Q&A
            - Seller profiles and stores
            - Recommendation engine
            - Order tracking
            - Prime/subscription services
            - Customer service chat
            
            Style: Amazon-inspired e-commerce layout with product focus
            {base_structure}""",
            
            # Navigation elements
            "home": f"""Create an enhanced CYBERHUB homepage.
            
            Include:
            - Welcome dashboard with user stats
            - Quick access to favorite sections
            - Recent activity feed
            - Trending content across categories
            - Search functionality
            - User profile panel
            - Notification center
            - Personalized recommendations
            
            Style: Maintain the retro-futuristic cyberpunk aesthetic with improved UX
            {base_structure}""",
            
            "back": f"""Create a NAVIGATION HISTORY page.
            
            Include:
            - Browsing history with timestamps
            - Bookmarked pages
            - Recently visited sections
            - Quick navigation shortcuts
            - Search through history
            - Clear history options
            - Export/import bookmarks
            - Browsing statistics
            
            Style: Clean, organized interface with history elements
            {base_structure}""",
            
            # Menu bar items
            "file": f"""Create a FILE MANAGER interface.
            
            Include:
            - File browser with folder navigation
            - Upload and download functionality
            - File operations (copy, move, delete)
            - File sharing and permissions
            - Cloud storage integration
            - File preview capabilities
            - Search and filtering
            - Storage usage statistics
            
            Style: Explorer/Finder-like interface with file icons, tree view
            {base_structure}""",
            
            "edit": f"""Create an EDIT/PREFERENCES center.
            
            Include:
            - User profile settings
            - Theme and appearance options
            - Privacy and security settings
            - Notification preferences
            - Language and region settings
            - Accessibility options
            - Account management
            - Data export/import tools
            
            Style: Settings panel with tabs, toggles, and form elements
            {base_structure}""",
            
            "view": f"""Create a VIEW CUSTOMIZATION panel.
            
            Include:
            - Display mode toggles (grid, list, details)
            - Zoom and scaling options
            - Column visibility controls
            - Sorting and grouping options
            - Filter and search visibility
            - Toolbar customization
            - Layout preferences
            - Window management
            
            Style: Control panel with preview options and live updates
            {base_structure}""",
            
            "go": f"""Create a GO/NAVIGATION quick access page.
            
            Include:
            - Quick navigation shortcuts
            - Bookmarked locations
            - Recent destinations
            - Popular/trending pages
            - Navigation shortcuts
            - Address bar with autocomplete
            - Tab management
            - Session restore options
            
            Style: Navigation-focused with quick access buttons and shortcuts
            {base_structure}""",
            
            "bookmarks": f"""Create a BOOKMARKS MANAGER.
            
            Include:
            - Organized bookmark folders
            - Search and filtering
            - Import/export functionality
            - Bookmark sharing
            - Tags and categories
            - Recently bookmarked
            - Duplicate detection
            - Bookmark validation
            
            Style: Organized library interface with folders and tags
            {base_structure}""",
            
            "help": f"""Create a comprehensive HELP CENTER.
            
            Include:
            - FAQ sections and answers
            - Tutorial videos and guides
            - Troubleshooting tools
            - Contact support options
            - Community forums
            - Documentation library
            - System status page
            - Feedback submission
            
            Style: Support center with search, categories, and helpful resources
            {base_structure}""",
            
            "forward": f"""Create a FORWARD NAVIGATION interface.
            
            Include:
            - Recently visited forward pages
            - Navigation prediction
            - Page preview thumbnails
            - Forward history timeline
            - Quick jump options
            - Session continuation
            - Tab restoration
            - Navigation analytics
            
            Style: Forward-focused navigation with previews and quick access
            {base_structure}""",
            
            "reload": f"""Create a REFRESH/RELOAD status page.
            
            Include:
            - Page refresh options
            - Cache management tools
            - Loading progress indicators
            - Refresh history
            - Auto-refresh settings
            - Force reload options
            - Performance metrics
            - Sync status indicators
            
            Style: Status page with progress indicators and refresh controls
            {base_structure}"""
        }
        
        # Handle search specifically
        if action_type == "search" and input_value:
            return f"""Create comprehensive SEARCH RESULTS for query: "{input_value}"
            
            Include:
            - Relevant search results with snippets
            - Filter options (web, images, news, etc.)
            - Related searches and suggestions
            - Search statistics and timing
            - Advanced search options
            - Safe search settings
            - Search history
            - Did you mean corrections
            
            Generate realistic, varied results that match the search query context.
            Style: Search engine results page with familiar layout patterns
            {base_structure}"""
        
        # Return specific prompt if target matches
        return category_prompts.get(target, "")
