#!/usr/bin/env python3
"""
Release Notes Scraper
Scrapes release notes from documentation pages and outputs in various formats.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
import json
from urllib.parse import urlparse

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_packages = []
    
    try:
        import requests
    except ImportError:
        missing_packages.append('requests')
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_packages.append('beautifulsoup4')
    
    if missing_packages:
        print("Error: Required packages not installed.", file=sys.stderr)
        print(f"Missing packages: {', '.join(missing_packages)}", file=sys.stderr)
        print("Please install using uv:", file=sys.stderr)
        print(f"  uv pip install {' '.join(missing_packages)}", file=sys.stderr)
        print("\nOr install all requirements:", file=sys.stderr)
        print("  uv pip install -r requirements.txt", file=sys.stderr)
        print("\nIf you're using a virtual environment, make sure it's activated.", file=sys.stderr)
        sys.exit(1)
    
    return True

class ReleaseNotesScraper:
    """Scraper for release notes from various documentation sites."""
    
    # Common selectors for different documentation platforms
    PLATFORM_SELECTORS = {
        'google_cloud': {
            'container': ['main', 'article', '[role="main"]', '.devsite-article-body', 'div.release-notes-container'],
            'date_headers': ['h2', 'h3'],
            'content': ['p', 'ul', 'ol', 'div'],
            'date_patterns': [
                r'(\w+\s+\d{1,2},\s+\d{4})',  # January 15, 2024
                r'(\d{4}-\d{2}-\d{2})',       # 2024-01-15
                r'(\d{1,2}/\d{1,2}/\d{4})',    # 01/15/2024
            ]
        },
        'generic': {
            'container': ['main', 'article', '.content', '#content', '.release-notes'],
            'date_headers': ['h2', 'h3', 'h4'],
            'content': ['p', 'ul', 'li', 'div'],
            'date_patterns': [
                r'(\w+\s+\d{1,2},\s+\d{4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{1,2}/\d{1,2}/\d{4})',
            ]
        }
    }
    
    def __init__(self, url: str, months: int = 12):
        """Initialize the scraper with URL and time range."""
        # Import here after dependency check
        import requests
        from bs4 import BeautifulSoup
        
        self.requests = requests
        self.BeautifulSoup = BeautifulSoup
        
        self.url = url
        self.months = months
        self.cutoff_date = datetime.now() - timedelta(days=months * 30)
        self.releases = []
        self.platform = self._detect_platform(url)
        
    def _detect_platform(self, url: str) -> str:
        """Detect the documentation platform based on URL."""
        if 'cloud.google.com' in url:
            return 'google_cloud'
        return 'generic'
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats."""
        date_str = date_str.strip()
        
        # Try common date formats
        formats = [
            '%B %d, %Y',      # January 15, 2024
            '%b %d, %Y',      # Jan 15, 2024
            '%Y-%m-%d',       # 2024-01-15
            '%m/%d/%Y',       # 01/15/2024
            '%d/%m/%Y',       # 15/01/2024
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _categorize_item(self, element=None, text: str = None) -> str:
        """Categorize a release note item based on its element class or content."""
        
        # First check if we have an element with specific classes
        if element:
            element_classes = element.get('class', [])
            class_str = ' '.join(element_classes) if element_classes else ''
            
            # Check for specific div classes
            if 'release-feature' in class_str:
                element_text = element.get_text(strip=True) if hasattr(element, 'get_text') else str(element)
                if '(Preview)' in element_text or '(preview)' in element_text:
                    return 'public-preview'
                else:
                    return 'ga'
            elif 'release-changed' in class_str:
                return 'change'
            elif 'release-announcement' in class_str:
                return 'announcement'
            elif 'release-breaking' in class_str: # New breaking change class
                return 'breaking'
            elif 'release-issue' in class_str:
                return 'issue'
        
        # If no element or no matching class, fall back to text analysis
        if not text and element and hasattr(element, 'get_text'):
            text = element.get_text(strip=True)
        
        if not text:
            return 'update'
        
        text_lower = text.lower()
        
        # Check for specific patterns (most specific to least specific)
        
        # Security takes highest priority
        if any(keyword in text_lower for keyword in ['security', 'vulnerability', 'cve', 'patch']):
            return 'security'
        
        # Breaking changes
        if any(keyword in text_lower for keyword in ['breaking change', 'breaking change:', 'migration required', 'major version update']):
            return 'breaking'
        
        # Check for preview indicators (but only if not already categorized by div class)
        if any(keyword in text_lower for keyword in ['(preview)', 'public preview', 'in preview', 'preview)', 'early access', 'beta']):
            return 'public-preview'
        
        # GA/Generally Available
        if any(keyword in text_lower for keyword in ['generally available', 'general availability', '(ga)', 'is now ga', 'is in ga', 'in general availability']):
            return 'ga'
        
        # Deprecated
        if any(keyword in text_lower for keyword in ['deprecated', 'deprecation', 'obsolete', 'removed', 'discontinued']):
            return 'deprecated'
        
        # Fixed/Bug fixes
        if any(keyword in text_lower for keyword in ['fixed', 'fix:', 'resolved', 'bug']):
            return 'fixed'
        
        # Issue
        if any(keyword in text_lower for keyword in ['issue', 'known issue', 'workaround']):
            return 'issue'
        
        # Change (significant changes)
        if any(keyword in text_lower for keyword in ['changed:', 'migration required', 'version updates']):
            return 'change'
        
        # Announcements
        if any(keyword in text_lower for keyword in ['announced', 'announcement', 'introducing']):
            return 'announcement'
        
        # Libraries/SDKs
        if any(keyword in text_lower for keyword in ['library', 'sdk', 'api', 'client library', 'framework']):
            return 'libraries'
        
        # Default to update for everything else
        return 'update'
    
    def scrape(self) -> List[Dict]:
        """Main scraping method."""
        try:
            # Make request with appropriate headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.requests.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = self.BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get platform-specific selectors
            selectors = self.PLATFORM_SELECTORS[self.platform]
            
            # Find the main content area
            content_area = None
            for selector in selectors['container']:
                content_area = soup.select_one(selector)
                if content_area:
                    break
            
            if not content_area:
                content_area = soup.body or soup
            
            # Try multiple strategies to find release notes
            self._parse_structured_releases(content_area, selectors)
            
            if not self.releases:
                self._parse_unstructured_releases(content_area, selectors)
            
            # Filter by date
            filtered_releases = []
            for release in self.releases:
                if release['date'] and release['date'] >= self.cutoff_date:
                    filtered_releases.append(release)
            
            return filtered_releases
            
        except self.requests.RequestException as e:
            print(f"Error fetching URL: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error parsing content: {e}", file=sys.stderr)
            return []
    
    def _parse_structured_releases(self, content_area, selectors):
        """Parse releases with clear date headers."""
        for header_tag in selectors['date_headers']:
            headers = content_area.find_all(header_tag)
            
            for header in headers:
                header_text = header.get_text(strip=True)
                
                # Try to extract date from header
                for pattern in selectors['date_patterns']:
                    match = re.search(pattern, header_text)
                    if match:
                        date_str = match.group(1)
                        parsed_date = self._parse_date(date_str)
                        
                        if parsed_date:
                            # Get content after this header until next header
                            items = []
                            sibling = header.find_next_sibling()
                            
                            while sibling and sibling.name not in selectors['date_headers']:
                                # Check for specific release divs
                                div_classes = sibling.get('class', [])
                                if any(cls in ['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'] for cls in div_classes):
                                    text_content = str(sibling) # Get full HTML
                                    text = sibling.get_text(strip=True)
                                    links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
                                    if text and len(text) > 10:
                                        items.append({
                                            'text': text_content,
                                            'category': self._categorize_item(element=sibling, text=text),
                                            'urls': links
                                        })
                                
                                elif sibling.name in ['p', 'ul', 'ol', 'li', 'div']:
                                    if sibling.name in ['ul', 'ol']:
                                        for li in sibling.find_all('li'):
                                            text_content = str(li)
                                            li_text = li.get_text(strip=True)
                                            li_links = [a.get('href') for a in li.find_all('a') if a.get('href')]
                                            if li_text:
                                                items.append({
                                                    'text': text_content,
                                                    'category': self._categorize_item(element=li, text=li_text),
                                                    'urls': li_links
                                                })
                                    else:
                                        text_content = str(sibling)
                                        text = sibling.get_text(strip=True)
                                        links = [a.get('href') for a in sibling.find_all('a') if a.get('href')]
                                        if text and len(text) > 10:
                                            items.append({
                                                'text': text_content,
                                                'category': self._categorize_item(element=sibling, text=text),
                                                'urls': links
                                            })
                                sibling = sibling.find_next_sibling()
                            
                            if items:
                                self.releases.append({
                                    'date': parsed_date,
                                    'date_str': date_str,
                                    'items': items,
                                    'url': self.url
                                })
                            break
    
    def _parse_unstructured_releases(self, content_area, selectors):
        """Parse releases without clear structure."""
        # Look for specific release divs first
        release_divs = content_area.find_all('div', class_=['release-feature', 'release-changed', 'release-announcement', 'release-breaking', 'release-issue'])
        for div in release_divs:
            # Try to find a date near this div
            parent = div.parent
            date_found = None
            date_str = None
            
            # Look for date in parent or siblings
            for elem in [div.previous_sibling, parent, div.next_sibling]:
                if elem and hasattr(elem, 'get_text'):
                    text = elem.get_text(strip=True)
                    for pattern in selectors['date_patterns']:
                        match = re.search(pattern, text)
                        if match:
                            date_str = match.group(1)
                            date_found = self._parse_date(date_str)
                            break
                if date_found:
                    break
            
            if date_found and date_found >= self.cutoff_date:
                text_content = str(div)
                text = div.get_text(strip=True)
                links = [a.get('href') for a in div.find_all('a') if a.get('href')]
                if text and len(text) > 20:
                    # Check if we already have this content
                    is_duplicate = False
                    for release in self.releases:
                        for item in release.get('items', []):
                            if item['text'] == text_content:
                                is_duplicate = True
                                break
                    
                    if not is_duplicate:
                        self.releases.append({
                            'date': date_found,
                            'date_str': date_str,
                            'items': [{
                                'text': text_content,
                                'category': self._categorize_item(element=div, text=text),
                                'urls': links
                            }],
                            'url': self.url
                        })
    
        # Continue with existing text-based parsing
        all_text_elements = content_area.find_all(text=True)
        
        for text in all_text_elements:
            text = text.strip()
            if not text:
                continue
                
            for pattern in selectors['date_patterns']:
                matches = re.findall(pattern, text)
                for match in matches:
                    parsed_date = self._parse_date(match)
                    if parsed_date and parsed_date >= self.cutoff_date:
                        parent = text.parent
                        if parent and parent.name not in ['script', 'style']:
                            text_content = str(parent)
                            content = parent.get_text(strip=True)
                            links = [a.get('href') for a in parent.find_all('a') if a.get('href')]
                            if content and len(content) > 20:
                                is_duplicate = False
                                for release in self.releases:
                                    for item in release.get('items', []):
                                        if item['text'] == text_content:
                                            is_duplicate = True
                                            break
                                
                                if not is_duplicate:
                                    self.releases.append({
                                        'date': parsed_date,
                                        'date_str': match,
                                        'items': [{
                                            'text': text_content,
                                            'category': self._categorize_item(element=parent, text=content),
                                            'urls': links
                                        }],
                                        'url': self.url
                                    })
    
    def format_output(self, releases: List[Dict], format_type: str) -> str:
        """Format the scraped releases based on the specified format."""
        if format_type == 'json':
            return self._format_json(releases)
        elif format_type == 'markdown':
            return self._format_markdown(releases)
        elif format_type == 'html':
            return self._format_html(releases)
        else:
            return self._format_text(releases)
    
    def _format_text(self, releases: List[Dict]) -> str:
        """Format releases as plain text, extracting URLs from the text."""
        output = []
        output.append("=" * 80)
        output.append(f"RELEASE NOTES SUMMARY")
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Time range: Last {self.months} months")
        output.append("=" * 80)
        output.append("")
        
        if not releases:
            output.append("No releases found in the specified time range.")
            return "\n".join(output)
        
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        for release in releases:
            output.append(f"\n## {release['date_str']}")
            output.append("-" * 40)
            for item in release['items']:
                # The .get_text() method is used here to get plain text for the text output format.
                text = self.BeautifulSoup(item['text'], 'html.parser').get_text(strip=True)
                text = text.replace('https://cloud.google.com/run/docs/release-notes', '')
                output.append(f"  [{item['category'].upper()}] {text}")
                if item.get('urls'):
                    output.append("    Links:")
                    for url in item['urls']:
                        output.append(f"      - {url}")
                output.append("")
        
        # Add statistics
        output.append("\n" + "=" * 80)
        output.append("STATISTICS")
        output.append("-" * 40)
        output.append(f"Total releases: {len(releases)}")
        
        total_items = sum(len(r['items']) for r in releases)
        output.append(f"Total items: {total_items}")
        
        # Count by category
        category_counts = {}
        for release in releases:
            for item in release['items']:
                category = item['category']
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            output.append("\nItems by category:")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                output.append(f"  - {category}: {count}")
        
        return "\n".join(output)
    
    def _format_markdown(self, releases: List[Dict]) -> str:
        """Format releases as Markdown, extracting URLs from the text."""
        output = []
        output.append("# Release Notes Summary\n")
        output.append(f"**Source:** [{self.url}]({self.url})  ")
        output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        output.append(f"**Time range:** Last {self.months} months\n")
        output.append("---\n")
        
        if not releases:
            output.append("*No releases found in the specified time range.*")
            return "\n".join(output)
        
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        for release in releases:
            output.append(f"\n## {release['date_str']}\n")
            for item in release['items']:
                # Use BeautifulSoup to get plain text, and remove the specific URL
                text = self.BeautifulSoup(item['text'], 'html.parser').get_text(strip=True)
                text = text.replace('https://cloud.google.com/run/docs/release-notes', '')
                badge = f"`{item['category']}`"
                output.append(f"- {badge} {text}")
                if item.get('urls'):
                    for url in item['urls']:
                        output.append(f"  - [Link]({url})")
            output.append("")
        
        # Add statistics
        output.append("\n---\n")
        output.append("## Statistics\n")
        output.append(f"- **Total releases:** {len(releases)}")
        
        total_items = sum(len(r['items']) for r in releases)
        output.append(f"- **Total items:** {total_items}")
        
        # Count by category
        category_counts = {}
        for release in releases:
            for item in release['items']:
                category = item['category']
                category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            output.append("\n### Items by category\n")
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                output.append(f"- `{category}`: {count}")
        
        return "\n".join(output)
    
    def _format_json(self, releases: List[Dict]) -> str:
        """Format releases as JSON, extracting URLs from the text."""
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        # Convert datetime objects to strings for JSON serialization
        json_releases = []
        for release in releases:
            json_items = []
            for item in release['items']:
                # Use BeautifulSoup to get plain text for JSON, and remove the specific URL
                text = self.BeautifulSoup(item['text'], 'html.parser').get_text(strip=True)
                text = text.replace('https://cloud.google.com/run/docs/release-notes', '')
                json_item = {
                    'text': text,
                    'category': item['category'],
                    'urls': item.get('urls', [])
                }
                json_items.append(json_item)
                
            json_release = {
                'date': release['date'].isoformat() if release['date'] else None,
                'date_str': release['date_str'],
                'items': json_items,
                'url': release.get('url', self.url)
            }
            json_releases.append(json_release)
        
        output = {
            'metadata': {
                'source': self.url,
                'generated': datetime.now().isoformat(),
                'time_range_months': self.months,
                'cutoff_date': self.cutoff_date.isoformat()
            },
            'statistics': {
                'total_releases': len(releases),
                'total_items': sum(len(r['items']) for r in releases)
            },
            'releases': json_releases
        }
        
        return json.dumps(output, indent=2)
    
    def _format_html(self, releases: List[Dict]) -> str:
        """Format releases as HTML with URLs included."""
        # Sort releases by date (newest first)
        releases.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
        
        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html lang="en">')
        html.append('<head>')
        html.append('    <meta charset="UTF-8">')
        html.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html.append('    <title>Release Notes Summary</title>')
        html.append('    <style>')
        html.append('        body {')
        html.append('            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;')
        html.append('            line-height: 1.6;')
        html.append('            max-width: 1200px;')
        html.append('            margin: 0 auto;')
        html.append('            padding: 20px;')
        html.append('            background: #f5f5f5;')
        html.append('        }')
        html.append('        .header {')
        html.append('            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);')
        html.append('            color: white;')
        html.append('            padding: 30px;')
        html.append('            border-radius: 10px;')
        html.append('            margin-bottom: 30px;')
        html.append('        }')
        html.append('        .header h1 {')
        html.append('            margin: 0;')
        html.append('            font-size: 2em;')
        html.append('        }')
        html.append('        .meta {')
        html.append('            opacity: 0.9;')
        html.append('            margin-top: 10px;')
        html.append('        }')
        html.append('        .release-date {')
        html.append('            background: white;')
        html.append('            border-radius: 8px;')
        html.append('            padding: 20px;')
        html.append('            margin-bottom: 20px;')
        html.append('            box-shadow: 0 2px 4px rgba(0,0,0,0.1);')
        html.append('        }')
        html.append('        .release-date h2 {')
        html.append('            color: #333;')
        html.append('            margin-top: 0;')
        html.append('            border-bottom: 2px solid #667eea;')
        html.append('            padding-bottom: 10px;')
        html.append('        }')
        html.append('        .release-item {')
        html.append('            margin: 15px 0;')
        html.append('            padding: 10px;')
        html.append('            background: #f9f9f9;')
        html.append('            border-left: 4px solid #ccc;')
        html.append('            border-radius: 4px;')
        html.append('        }')
        html.append('        .release-item.ga { border-left-color: #4CAF50; }')
        html.append('        .release-item.publicpreview { border-left-color: #FF9800; }')
        html.append('        .release-item.change { border-left-color: #2196F3; }')
        html.append('        .release-item.announcement { border-left-color: #9C27B0; }')
        html.append('        .release-item.breaking { border-left-color: #f44336; }')
        html.append('        .release-item.deprecated { border-left-color: #f44336; }')
        html.append('        .release-item.fixed { border-left-color: #00BCD4; }')
        html.append('        .release-item.update { border-left-color: #795548; }')
        html.append('        .release-item.libraries { border-left-color: #607D8B; }')
        html.append('        .release-item.security { border-left-color: #E91E63; }')
        html.append('        .release-item.issue { border-left-color: #ffc107; }')
        html.append('        .category {')
        html.append('            display: inline-block;')
        html.append('            padding: 2px 8px;')
        html.append('            border-radius: 3px;')
        html.append('            font-size: 0.85em;')
        html.append('            font-weight: bold;')
        html.append('            margin-right: 10px;')
        html.append('        }')
        html.append('        .category.ga { background: #4CAF50; color: white; }')
        html.append('        .category.publicpreview { background: #FF9800; color: white; }')
        html.append('        .category.change { background: #2196F3; color: white; }')
        html.append('        .category.announcement { background: #9C27B0; color: white; }')
        html.append('        .category.breaking { background: #E91E63; color: white; }')
        html.append('        .category.deprecated { background: #f44336; color: white; }')
        html.append('        .category.fixed { background: #00BCD4; color: white; }')
        html.append('        .category.update { background: #795548; color: white; }')
        html.append('        .category.libraries { background: #607D8B; color: white; }')
        html.append('        .category.security { background: #E91E63; color: white; }')
        html.append('        .category.issue { background: #ffc107; color: white; }')
        html.append('        .stats {')
        html.append('            background: white;')
        html.append('            border-radius: 8px;')
        html.append('            padding: 20px;')
        html.append('            margin-top: 30px;')
        html.append('            box-shadow: 0 2px 4px rgba(0,0,0,0.1);')
        html.append('        }')
        html.append('        .stats h2 {')
        html.append('            color: #333;')
        html.append('            margin-top: 0;')
        html.append('        }')
        html.append('        a {')
        html.append('            color: #667eea;')
        html.append('            text-decoration: none;')
        html.append('        }')
        html.append('        a:hover {')
        html.append('            text-decoration: underline;')
        html.append('        }')
        html.append('        .source-link {')
        html.append('            margin-top: 20px;')
        html.append('            text-align: center;')
        html.append('        }')
        html.append('        .item-source {')
        html.append('            font-size: 0.8em;')
        html.append('            margin-top: 5px;')
        html.append('            opacity: 0.7;')
        html.append('        }')
        html.append('        .no-results {')
        html.append('            background: #fff3cd;')
        html.append('            border: 1px solid #ffc107;')
        html.append('            border-radius: 5px;')
        html.append('            padding: 20px;')
        html.append('            margin: 20px 0;')
        html.append('            text-align: center;')
        html.append('        }')
        html.append('    </style>')
        html.append('</head>')
        html.append('<body>')
        html.append('    <div class="header">')
        html.append('        <h1>Release Notes Summary</h1>')
        html.append('        <div class="meta">')
        html.append(f'            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>')
        html.append(f'            <p>Source: <a href="{self.url}" style="color: white; text-decoration: underline;">{self.url}</a></p>')
        html.append(f'            <p>Time range: Last {self.months} months</p>')
        html.append('        </div>')
        html.append('    </div>')
        
        if not releases:
            html.append('    <div class="no-results">')
            html.append('        <h2>No Release Notes Found</h2>')
            html.append('        <p>No release notes were found in the specified time range.</p>')
            html.append('        <p>This could be due to:</p>')
            html.append('        <ul style="text-align: left; display: inline-block;">')
            html.append('            <li>No releases in the past ' + str(self.months) + ' months</li>')
            html.append('            <li>Different page structure than expected</li>')
            html.append('            <li>Content loaded dynamically via JavaScript</li>')
            html.append('        </ul>')
            html.append('    </div>')
        else:
            # Add release notes with URLs
            for release in releases:
                html.append('    <div class="release-date">')
                html.append(f'        <h2>{release["date_str"]}</h2>')
                for item in release['items']:
                    category_class = item['category'].replace('-', '')
                    html.append(f'        <div class="release-item {category_class}">')
                    html.append(f'            <span class="category {category_class}">{item["category"].replace("-", " ").upper()}</span>')
                    html.append(f'            {item["text"]}') # Use the raw HTML content
                    html.append('        </div>')
                html.append('    </div>')
        
        # Add statistics
        html.append('    <div class="stats">')
        html.append('        <h2>Summary Statistics</h2>')
        html.append(f'        <p><strong>Total Releases:</strong> {len(releases)}</p>')
        
        total_items = sum(len(r['items']) for r in releases)
        html.append(f'        <p><strong>Total Items:</strong> {total_items}</p>')
        
        if releases:
            date_range_start = min(r['date'] for r in releases if r['date'])
            date_range_end = max(r['date'] for r in releases if r['date'])
            html.append(f'        <p><strong>Date Range:</strong> {date_range_start.strftime("%Y-%m-%d")} to {date_range_end.strftime("%Y-%m-%d")}</p>')
        else:
            cutoff = self.cutoff_date.strftime("%Y-%m-%d")
            today = datetime.now().strftime("%Y-%m-%d")
            html.append(f'        <p><strong>Search Range:</strong> {cutoff} to {today}</p>')
        
        # Category breakdown
        if releases:
            category_counts = {}
            for release in releases:
                for item in release['items']:
                    category = item['category']
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            if category_counts:
                html.append('        <h3>Items by Category</h3>')
                html.append('        <ul>')
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    display_name = category.replace('-', ' ').title()
                    if category == 'ga':
                        display_name = 'GA (Generally Available)'
                    elif category == 'public-preview':
                        display_name = 'Public Preview'
                    elif category == 'breaking':
                        display_name = 'Breaking'
                    html.append(f'            <li><strong>{display_name}:</strong> {count}</li>')
                html.append('        </ul>')
        
        html.append('    </div>')
        
        html.append('    <div class="source-link">')
        html.append(f'        <a href="{self.url}" target="_blank">View Full Release Notes</a>')
        html.append('    </div>')
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)

def main():
    """Main entry point for the script."""
    # Check dependencies before doing anything else
    check_dependencies()
    
    parser = argparse.ArgumentParser(
        description='Scrape release notes from documentation pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -u https://example.com/release-notes
  %(prog)s -u https://example.com/release-notes -m 6 -o json
  %(prog)s -u https://example.com/release-notes -o html -f output.html
  %(prog)s -u https://example.com/release-notes -m 3 -o markdown -f notes.md
        """
    )
    
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='URL of the release notes page to scrape'
    )
    
    parser.add_argument(
        '-m', '--months',
        type=int,
        default=12,
        help='Number of months to look back (default: 12)'
    )
    
    parser.add_argument(
        '-o', '--output',
        choices=['text', 'json', 'markdown', 'html'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Output file path (if not specified, prints to stdout)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Scraping: {args.url}", file=sys.stderr)
        print(f"Time range: Last {args.months} months", file=sys.stderr)
        print(f"Output format: {args.output}", file=sys.stderr)
    
    # Create scraper and run
    scraper = ReleaseNotesScraper(args.url, args.months)
    releases = scraper.scrape()
    
    if args.verbose:
        print(f"Found {len(releases)} releases", file=sys.stderr)
    
    # Format output
    output = scraper.format_output(releases, args.output)
    
    # Write output
    if args.file:
        try:
            with open(args.file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"{args.output.upper()} output saved to {args.file}", file=sys.stderr)
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

if __name__ == '__main__':
    main()

