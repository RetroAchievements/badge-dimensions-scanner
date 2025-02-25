"""
RetroAchievements Game Badge Dimensions Scanner
===============================================

A tool to verify game badge dimensions on RetroAchievements.org. This script checks if game badges
conform to the required 96x96 pixel dimensions by querying the RetroAchievements Web API and 
analyzing PNG metadata.

Features:
- Batch processing of game IDs
- Rate limiting to respect API constraints
- Progress tracking and error handling
- Detailed reporting of non-compliant images

Requirements:
- Python 3.6+
- RetroAchievements.org API key

Usage:
    python badge_dimensions_scanner.py --api-key YOUR_API_KEY --start-id 1 --end-id 100
"""

from urllib.request import urlopen, Request, HTTPError
from urllib.parse import urlencode
import json
import time
import argparse
import struct
import sys

class RAImageChecker:
    """RetroAchievements image dimension checker.
    
    This class provides functionality to check game icon dimensions using the RetroAchievements API.
    It includes rate limiting to prevent overloading the API server.
    
    Attributes:
        api_key (str): RetroAchievements API key for authentication.
        base_url (str): Base URL for the RetroAchievements API.
        media_url (str): Base URL for RetroAchievements media assets.
        request_delay (float): Minimum time between API requests in seconds.
        last_request (float): Timestamp of the last API request.
        headers (dict): HTTP headers used for API requests.
    """
    
    def __init__(self, api_key):
        """Initialize the checker with API credentials and configuration.
        
        Args:
            api_key (str): RetroAchievements API key for authentication.
        """
        self.api_key = api_key
        self.base_url = "https://retroachievements.org/API"
        self.media_url = "https://media.retroachievements.org"
        self.request_delay = 0.5  # Time between requests in seconds.
        self.last_request = 0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
    
    def _wait_for_rate_limit(self):
        """Implement rate limiting by waiting between requests.
        
        Ensures that subsequent API requests are spaced by at least request_delay seconds.
        """
        now = time.time()
        time_since_last = now - self.last_request
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request = time.time()
    
    def get_game(self, game_id):
        """Fetch game data from the RetroAchievements API.
        
        Args:
            game_id (int): The ID of the game to fetch.
            
        Returns:
            dict: Game data if successful, None if the request fails.
        """
        self._wait_for_rate_limit()
        
        try:
            params = urlencode({
                'y': self.api_key,
                'i': game_id
            })
            url = f"{self.base_url}/API_GetGame.php?{params}"
            
            request = Request(url, headers=self.headers)
            with urlopen(request) as response:
                return json.loads(response.read())
        except Exception as e:
            print(f"Failed to fetch game {game_id}: {str(e)}")
            return None
    
    def get_png_dimensions(self, data):
        """Extract width and height from PNG image data.
        
        Args:
            data (bytes): Raw PNG image data.
            
        Returns:
            tuple: (width, height) if successful, None if parsing fails.
        """
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            try:
                w, h = struct.unpack('>LL', data[16:24])
                return int(w), int(h)
            except struct.error:
                return None
        return None
    
    def check_image_dimensions(self, image_path):
        """Check dimensions of a game icon from its URL.
        
        Args:
            image_path (str): Path component of the image URL.
            
        Returns:
            tuple: (width, height) if successful, None if check fails.
        """
        try:
            full_url = self.media_url + image_path
            request = Request(full_url, headers=self.headers)
            with urlopen(request) as response:
                data = response.read()
                return self.get_png_dimensions(data)
        except Exception as e:
            print(f"Failed to check dimensions for {image_path}")
            return None

def main():
    """Main execution function.
    
    Processes command line arguments and runs the dimension checker on the specified range
    of game IDs. Provides progress updates and generates a final report.
    """
    parser = argparse.ArgumentParser(description='Check RetroAchievements game icon dimensions.')
    parser.add_argument('--api-key', required=True, help='Your RetroAchievements Web API key.')
    parser.add_argument('--start-id', type=int, default=1, help='Starting game ID to check.')
    parser.add_argument('--end-id', type=int, default=100, help='Ending game ID to check.')
    
    args = parser.parse_args()
    
    checker = RAImageChecker(args.api_key)
    incorrect_dimensions = []
    processed = 0
    errors = 0
    
    print(f"Checking games from ID {args.start_id} to {args.end_id}...")
    
    try:
        for game_id in range(args.start_id, args.end_id + 1):
            print(f"\nChecking game ID {game_id}...")
            game_data = checker.get_game(game_id)
            
            if not game_data:
                print(f"Failed to fetch game {game_id}")
                errors += 1
                continue
                
            if 'ImageIcon' in game_data and game_data['ImageIcon']:
                dimensions = checker.check_image_dimensions(game_data['ImageIcon'])
                
                if dimensions:
                    if dimensions[0] != 96 or dimensions[1] != 96:
                        print(f"❌ Icon dimensions incorrect: {dimensions[0]}x{dimensions[1]}")
                        incorrect_dimensions.append({
                            'id': game_id,
                            'title': game_data.get('Title', 'Unknown'),
                            'path': game_data['ImageIcon'],
                            'dimensions': dimensions
                        })
                    else:
                        print(f"✅ Icon dimensions correct: 96x96")
                else:
                    print(f"⚠️  Could not determine dimensions")
                    errors += 1
            else:
                print(f"⚠️  No icon found")
                errors += 1
            
            processed += 1
            if processed % 10 == 0:
                print(f"\nProgress: {processed}/{args.end_id - args.start_id + 1} games checked")
        
        print("\nResults:")
        print(f"Total games processed: {processed}")
        print(f"Errors encountered: {errors}")
        
        if incorrect_dimensions:
            print(f"\nFound {len(incorrect_dimensions)} games with incorrect dimensions:")
            print("-" * 80)
            for game in incorrect_dimensions:
                print(f"Game ID: {game['id']}")
                print(f"Title: {game['title']}")
                print(f"Icon: {game['path']}")
                print(f"Dimensions: {game['dimensions'][0]}x{game['dimensions'][1]}")
                print("-" * 80)
        else:
            print("\nAll checked icons have correct dimensions (96x96).")
            
    except KeyboardInterrupt:
        print("\nScript interrupted. Showing partial results...")
        print(f"\nProcessed {processed} games, encountered {errors} errors")
        if incorrect_dimensions:
            print(f"\nFound {len(incorrect_dimensions)} games with incorrect dimensions:")
            print("-" * 80)
            for game in incorrect_dimensions:
                print(f"Game ID: {game['id']}")
                print(f"Title: {game['title']}")
                print(f"Icon: {game['path']}")
                print(f"Dimensions: {game['dimensions'][0]}x{game['dimensions'][1]}")
                print("-" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()