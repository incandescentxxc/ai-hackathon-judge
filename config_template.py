"""
Configuration template for AI-Judge

Copy this file to config.py and update with your own authentication values.
DO NOT commit your config.py file to version control!
"""

# Headers for HTTP requests
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
}

# Cookies for authentication
# Replace with your own cookies after logging in to Devpost
COOKIES = {
    'jwt': 'your_jwt_token_here',
    'remember_user_token': 'your_remember_user_token_here',
    '_devpost': 'your_devpost_cookie_here',
    # Add other necessary cookies
}

# Base URL for the Devpost hackathon
BASE_URL = 'https://hackatopia.devpost.com' 