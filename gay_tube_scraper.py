# Gay Tube Scraper for StashApp

This is a custom scraper for StashApp that works with the following gay tube sites:
- fxggxt.com
- likegay.net
- hutgay.com

## Features

- Scrapes scene information including title, performers, and studio
- Works with both URL matching and filename matching
- Handles various filename formats
- Extracts structured data when available (JSON-LD)
- Fallback to HTML parsing when structured data is not available
- Supports tags extraction when available

## Installation

### Method 1: Manual Installation

1. Copy `gay_tube_scraper.yml` and `gay_tube_scraper.py` to your StashApp scrapers directory
   - Default location: `~/.stash/scrapers/`
   - Windows location: `C:\Users\YourUsername\.stash\scrapers\`
   - Or the custom location you've configured in StashApp settings

2. Make sure the Python script is executable:
   ```
   chmod +x gay_tube_scraper.py  # Linux/Mac only
   ```

3. Ensure you have the required Python dependencies:
   ```
   pip install requests beautifulsoup4
   ```

4. Restart StashApp or reload scrapers from the UI (Scrape with... -> Reload scrapers)

### Method 2: Installation via StashApp UI (v0.24.0+)

1. In StashApp, go to Settings > Metadata Providers
2. Click "Add Source" and select "Custom"
3. Enter a name (e.g., "Gay Tube Scraper")
4. Upload the `gay_tube_scraper.yml` and `gay_tube_scraper.py` files
5. Click "Save"
6. Ensure you have Python installed and the required dependencies:
   ```
   pip install requests beautifulsoup4
   ```

## Python Configuration

Make sure you have Python 3.6+ installed on your system. If StashApp cannot find your Python installation, you can set the path in:
- Settings > System > Application Paths > Python executable path

For Windows users, we recommend installing Python from python.org and not from the Windows Store.

## Usage

### URL Scraping
1. In the scene edit page, paste a URL from one of the supported sites
2. Click the "Scrape" button next to the URL field
3. Select the fields you want to update
4. Click "Scrape" to apply the changes

### Filename Scraping
1. In the scene edit page, click "Scrape With..."
2. Select "GayTubeScraper" from the dropdown
3. Select the fields you want to update
4. Click "Scrape" to apply the changes

## Supported Filename Formats

The scraper attempts to extract information from various filename formats:

- `Studio - Scene Name Actor1, Actor2`
- `STUDIO_-_SCENE_NAME_-_Actor1_-_Actor2_-_Actor3`
- `Studio - Scene Name`
- Various other formats with performers separated by commas, ampersands, etc.

## Supported URL Formats

The scraper supports the following URL patterns:
- fxggxt.com: `https://fxggxt.com/[studio]-[scene-name]/`
- likegay.net: `https://likegay.net/[id]-[performers]-[scene-name].html`
- hutgay.com: `https://ww1.hutgay.com/[performers]-[scene-name]/`

## Extracted Metadata

The scraper extracts the following metadata:
- Scene title
- Performer names
- Studio name
- Tags (when available, primarily from fxggxt.com)

## Troubleshooting

If you encounter issues:

1. Check StashApp logs for error messages (Settings > Logs > Log Level Debug)
2. Ensure the Python script has execute permissions
3. Verify that all required Python dependencies are installed:
   ```
   pip install requests beautifulsoup4
   ```
4. Make sure the URL is from one of the supported sites
5. Try different filename formats if filename scraping isn't working
6. If you get "ModuleNotFoundError" errors, make sure you've installed the required Python packages
7. If you get "Permission denied" errors, make sure the script is executable (Linux/Mac)
8. If StashApp can't find Python, set the Python executable path in Settings > System > Application Paths

## License

This scraper is provided under the AGPL-3.0 license, consistent with StashApp's licensing.
