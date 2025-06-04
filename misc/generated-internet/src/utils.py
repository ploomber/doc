def get_interaction_javascript() -> str:
    """Get the JavaScript code needed for continued interaction"""
    return """
    <div id="loading-toast" style="
        display: none;
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #ffff00;
        border: 2px solid #000000;
        padding: 20px 20px;
        font-family: 'VT323', monospace;
        font-size: 16px;
        z-index: 9999;
        box-shadow: 4px 4px 0px #000000;
    ">⏳ Loading next page...</div>

    <script>
    // Function to send interaction data to the server and replace entire page
    async function sendInteraction(actionType, elementId, elementText, inputValue = null, additionalData = null) {

        const toast = document.getElementById('loading-toast');
        toast.style.display = 'block';
        const interactionData = {
            action_type: actionType,
            element_id: elementId,
            element_text: elementText,
            input_value: inputValue,
            page_url: window.location.href,
            timestamp: new Date().toISOString(),
            additional_data: additionalData
        };
        
        try {
            const response = await fetch('/api/interact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(interactionData)
            });
            
            if (response.ok) {
                const htmlContent = await response.text();
                // Replace entire page content
                document.open();
                document.write(htmlContent);
                document.close();
            }
        } catch (error) {
            console.error('Error sending interaction:', error);
        }
    }
    
    // Function to attach event listeners
    function attachEventListeners() {
        // Handle clicks on elements with data-action attribute
        document.addEventListener('click', function(e) {
            if (e.target.hasAttribute('data-action')) {
                e.preventDefault();
                const action = e.target.getAttribute('data-action');
                const target = e.target.getAttribute('data-target');
                const text = e.target.textContent;
                const elementId = e.target.id || null;
                
                sendInteraction('click', elementId, text, null, { action: action, target: target });
            }
        });
        
        // Handle form submissions
        document.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            const formObject = Object.fromEntries(formData);
            
            sendInteraction('form_submit', form.id || null, 'Form Submission', JSON.stringify(formObject));
        });
        
        // Handle input fields with enter key
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && e.target.type === 'text') {
                const inputValue = e.target.value;
                const inputId = e.target.id || null;
                
                sendInteraction('input', inputId, 'Input Entry', inputValue);
            }
        });
        
        // Handle search button clicks specifically
        const searchBtns = document.querySelectorAll('.search-btn, [data-action="search"]');
        searchBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const searchInput = document.querySelector('input[type="text"], #search-input, .search-input');
                const searchValue = searchInput ? searchInput.value : '';
                sendInteraction('search', btn.id || 'search-btn', 'Search Button', searchValue);
            });
        });
    }
    
    // Initialize event listeners when page loads
    document.addEventListener('DOMContentLoaded', function() {
        attachEventListeners();
    });
    </script>
    """

error_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - Yahou!</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 50px; background-color: #f0f0f0; }}
        .error-box {{ background-color: #ffcccc; border: 2px solid #ff0000; padding: 20px; }}
        .back-btn {{ 
            background-color: #0066cc; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            margin-top: 10px; 
        }}
    </style>
</head>
<body>
    <div class="error-box">
        <h1>⚠️ Yahou! Error</h1>
        <p>Sorry, there was an error generating your page. Please try again!</p>
        <button class="back-btn" data-action="navigate" data-target="home">🏠 Return to Home</button>
    </div>
    {get_interaction_javascript()}
</body>
</html>'''


