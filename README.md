# RetroAchievements Badge Dimensions Scanner

A Python tool to verify game badge dimensions on RetroAchievements.org. This script helps identify game badges that don't conform to the required 96x96 pixel dimensions by analyzing PNG metadata through the RetroAchievements Web API.

## Features

- Batch processing of multiple game IDs
- Built-in rate limiting to respect API constraints
- Progress tracking with real-time updates
- Detailed reporting of non-compliant images
- Error handling and recovery
- Support for interrupted execution

## Requirements

- Python 3.6 or higher
- RetroAchievements.org Web API key from `/settings`

## Installation

1. Clone this repository:

```bash
git clone https://github.com/RetroAchievements/badge-dimensions-scanner.git
cd badge-dimensions-scanner
```

2. No additional dependencies are required - the script uses only Python standard library modules.

## Usage

Run the script with your RetroAchievements API key and specify the range of game IDs to check:

```bash
python badge_dimensions_scanner.py --api-key YOUR_API_KEY --start-id 1 --end-id 28500
```

### Arguments

- `--api-key`: Your RetroAchievements Web API key from `/settings` (required)
- `--start-id`: First game ID to check (default: 1)
- `--end-id`: Last game ID to check (default: 100)

### Example Output

```
Checking games from ID 1 to 100...

Checking game ID 1...
✅ Icon dimensions correct: 96x96

Checking game ID 2...
❌ Icon dimensions incorrect: 98x96

Progress: 10/100 games checked

...

Results:
Total games processed: 100
Errors encountered: 5

Found 3 games with incorrect dimensions:
--------------------------------------------------------------------------------
Game ID: 2
Title: Some Game
Icon: /Images/123.png
Dimensions: 98x96
--------------------------------------------------------------------------------
```

## Rate Limiting

The script implements rate limiting to prevent overwhelming the RetroAchievements server. By default, it waits 0.5 seconds between requests. This can be adjusted by modifying the `request_delay` value in the `RAImageChecker` class.

## Error Handling

- Network errors are caught and reported
- Invalid PNG files are detected and skipped
- Missing icons are noted in the final report
- Keyboard interrupts (Ctrl+C) are handled gracefully with partial results displayed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
