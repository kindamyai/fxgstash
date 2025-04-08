#!/usr/bin/env python3
import json
import sys
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT
}

# Helper functions
def debug_print(message):
    """Print debug messages to stderr"""
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()

def read_json_input():
    """Read JSON input from stdin"""
    input_data = sys.stdin.read()
    return json.loads(input_data)

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    # Replace HTML entities and normalize whitespace
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&#8211;', '-', text)
    text = re.sub(r'&#8217;', "'", text)
    text = re.sub(r'&#038;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_performers_from_title(title):
    """Extract performer names from title"""
    # Common patterns:
    # "Studio - Performer1 & Performer2 - Scene Name"
    # "Performer1, Performer2 – Scene Name"
    
    performers = []
    
    # Try to extract from patterns with " - " or " – "
    if " - " in title or " – " in title:
        separator = " - " if " - " in title else " – "
        parts = title.split(separator)
        
        # Check if first part contains performers
        if "&" in parts[0] or "," in parts[0]:
            performer_part = parts[0]
            if "&" in performer_part:
                performers = [p.strip() for p in performer_part.split("&")]
            elif "," in performer_part:
                performers = [p.strip() for p in performer_part.split(",")]
    
    # Clean performer names
    performers = [clean_text(p) for p in performers if p.strip()]
    return performers

def extract_scene_name_from_title(title):
    """Extract scene name from title"""
    # Common patterns:
    # "Studio - Performer1 & Performer2 - Scene Name"
    # "Performer1, Performer2 – Scene Name"
    
    scene_name = ""
    
    # Try to extract from patterns with " - " or " – "
    if " - " in title or " – " in title:
        separator = " - " if " - " in title else " – "
        parts = title.split(separator)
        
        # Last part is usually the scene name
        if len(parts) > 1:
            scene_name = parts[-1]
    
    # Clean scene name
    scene_name = clean_text(scene_name)
    return scene_name

def extract_studio_from_title(title):
    """Extract studio name from title"""
    # Common patterns:
    # "Studio - Performer1 & Performer2 - Scene Name"
    # "OnlyFans - Performer1 & Performer2"
    
    studio = ""
    
    # Try to extract from patterns with " - "
    if " - " in title:
        parts = title.split(" - ")
        # First part is usually the studio
        if len(parts) > 0:
            studio = parts[0]
    
    # Clean studio name
    studio = clean_text(studio)
    return studio

def normalize_url(url):
    """Normalize URL by removing query parameters and fragments"""
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

# Site-specific scrapers
def scrape_fxggxt(url):
    """Scrape scene data from fxggxt.com"""
    debug_print(f"Scraping fxggxt.com: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract JSON-LD data first (most reliable)
        json_ld = None
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@graph' in data:
                    json_ld = data
                    break
            except:
                continue
        
        scene = {}
        
        # Extract from JSON-LD if available
        if json_ld:
            debug_print("Found JSON-LD data")
            for item in json_ld.get('@graph', []):
                if item.get('@type') == 'Article':
                    scene['title'] = clean_text(item.get('headline', ''))
                    
                    # Extract studio from articleSection
                    article_sections = item.get('articleSection', [])
                    if article_sections and isinstance(article_sections, list) and len(article_sections) > 0:
                        scene['studio'] = {'name': article_sections[0]}
                    
                    # Extract tags/categories
                    if 'keywords' in item and isinstance(item['keywords'], list):
                        scene['tags'] = [{'name': k} for k in item['keywords']]
        
        # Fallback to title parsing if JSON-LD doesn't have all we need
        if not scene.get('title'):
            title = soup.title.string if soup.title else ""
            scene['title'] = extract_scene_name_from_title(title)
        
        # Extract performers from title
        title = soup.title.string if soup.title else ""
        
        # For fxggxt.com, the title format is usually "Studio - Performer1 & Performer2 - Scene Name"
        if "fxggxt.com" in url:
            parts = title.split(" - ")
            if len(parts) >= 2:
                performer_part = parts[1]
                if "&" in performer_part:
                    performers = [p.strip() for p in performer_part.split("&")]
                    scene['performers'] = [{'name': p} for p in performers if p]
        else:
            # For other sites
            performers = extract_performers_from_title(title)
            if performers:
                scene['performers'] = [{'name': p} for p in performers]
        
        # Extract studio if not already set
        if not scene.get('studio'):
            studio = extract_studio_from_title(title)
            if studio:
                scene['studio'] = {'name': studio}
        
        # Set URL
        scene['url'] = url
        
        return scene
        
    except Exception as e:
        debug_print(f"Error scraping fxggxt.com: {str(e)}")
        return {}

def scrape_likegay(url):
    """Scrape scene data from likegay.net"""
    debug_print(f"Scraping likegay.net: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scene = {}
        
        # Extract from title
        title = soup.title.string if soup.title else ""
        
        # Extract scene name
        scene_name = extract_scene_name_from_title(title)
        if scene_name:
            scene['title'] = scene_name
        
        # Extract performers
        performers = extract_performers_from_title(title)
        if performers:
            scene['performers'] = [{'name': p} for p in performers]
        
        # Try to extract studio from breadcrumbs
        breadcrumbs = soup.select('.breadcrumb a')
        if breadcrumbs and len(breadcrumbs) > 1:
            studio_name = clean_text(breadcrumbs[1].text)
            if studio_name:
                scene['studio'] = {'name': studio_name}
        
        # Set URL
        scene['url'] = url
        
        return scene
        
    except Exception as e:
        debug_print(f"Error scraping likegay.net: {str(e)}")
        return {}

def scrape_hutgay(url):
    """Scrape scene data from hutgay.com"""
    debug_print(f"Scraping hutgay.com: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scene = {}
        
        # Extract from title
        title = soup.title.string if soup.title else ""
        
        # Extract scene name
        scene_name = extract_scene_name_from_title(title)
        if scene_name:
            scene['title'] = scene_name
        
        # Extract performers
        performers = extract_performers_from_title(title)
        if performers:
            scene['performers'] = [{'name': p} for p in performers]
        
        # Try to extract studio from URL or content
        # Most hutgay URLs don't include studio info, so we'll try to infer from content
        h1_text = soup.h1.text if soup.h1 else ""
        if " - " in h1_text:
            studio_candidate = h1_text.split(" - ")[0].strip()
            if studio_candidate and studio_candidate not in [p['name'] for p in scene.get('performers', [])]:
                scene['studio'] = {'name': studio_candidate}
        
        # Set URL
        scene['url'] = url
        
        return scene
        
    except Exception as e:
        debug_print(f"Error scraping hutgay.com: {str(e)}")
        return {}

def scrape_scene_by_url(url):
    """Scrape scene data by URL"""
    normalized_url = normalize_url(url)
    
    if "fxggxt.com" in normalized_url:
        return scrape_fxggxt(normalized_url)
    elif "likegay.net" in normalized_url:
        return scrape_likegay(normalized_url)
    elif "hutgay.com" in normalized_url:
        return scrape_hutgay(normalized_url)
    else:
        debug_print(f"Unsupported URL: {normalized_url}")
        return {}

def scrape_scene_by_fragment(fragment):
    """Scrape scene data by fragment (filename)"""
    debug_print(f"Scraping by fragment: {fragment}")
    
    # Extract potential scene data from filename
    scene = {}
    
    # Try to extract scene name, performers, and studio from filename
    filename = fragment.get('title', '')
    
    # Pattern 1: "Studio - Scene Name Actor1, Actor2"
    pattern1 = re.compile(r'^(.+?)\s*-\s*(.+?)\s+(.+?)$')
    
    # Pattern 2: "STUDIO_-_SCENE_NAME_-_Actor1_-_Actor2_-_Actor3"
    pattern2 = re.compile(r'^(.+?)_-_(.+?)_-_(.+?)$')
    
    # Try pattern 1
    match = pattern1.match(filename)
    if match:
        studio, scene_name, performers_str = match.groups()
        scene['studio'] = {'name': clean_text(studio)}
        scene['title'] = clean_text(scene_name)
        
        # Extract performers
        performers = []
        if ',' in performers_str:
            performers = [clean_text(p) for p in performers_str.split(',')]
        else:
            performers = [clean_text(performers_str)]
        
        scene['performers'] = [{'name': p} for p in performers if p]
    
    # Try pattern 2
    if not scene and '_-_' in filename:
        parts = filename.split('_-_')
        if len(parts) >= 3:
            studio = parts[0]
            scene_name = parts[1]
            performers = parts[2:]
            
            scene['studio'] = {'name': clean_text(studio)}
            scene['title'] = clean_text(scene_name)
            scene['performers'] = [{'name': clean_text(p)} for p in performers if clean_text(p)]
    
    # If still no match, try more general extraction
    if not scene:
        # Try to extract studio and scene name if format is "Studio - Scene Name"
        if ' - ' in filename:
            parts = filename.split(' - ')
            if len(parts) >= 2:
                scene['studio'] = {'name': clean_text(parts[0])}
                scene['title'] = clean_text(parts[1])
        
        # Try to extract performers if they're in the filename
        performers = []
        # Look for common performer separator patterns
        for pattern in [', ', ' & ', '_-_']:
            if pattern in filename:
                potential_performers = filename.split(pattern)
                # Filter out likely non-performer parts (too short, contains numbers, etc.)
                performers = [p for p in potential_performers if len(p) > 2 and not p.isdigit()]
                if performers:
                    break
        
        if performers:
            scene['performers'] = [{'name': clean_text(p)} for p in performers if clean_text(p)]
    
    return scene

# Main execution
if __name__ == "__main__":
    if len(sys.argv) < 2:
        debug_print("Error: Missing command argument")
        sys.exit(1)
    
    command = sys.argv[1]
    input_data = read_json_input()
    
    if command == "scrapeURL":
        url = input_data.get('url', '')
        if not url:
            debug_print("Error: Missing URL in input")
            sys.exit(1)
        
        result = scrape_scene_by_url(url)
        print(json.dumps(result))
    
    elif command == "scrapeFragment":
        result = scrape_scene_by_fragment(input_data)
        print(json.dumps(result))
    
    else:
        debug_print(f"Error: Unknown command '{command}'")
        sys.exit(1)
