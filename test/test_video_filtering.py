#!/usr/bin/env python3
"""Test script for video filtering functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from doj_research_agent.scraping.scraper import DOJScraper
from doj_research_agent.core.models import ScrapingConfig

def test_video_filtering():
    """Test video filtering functionality."""
    print("🧪 Testing Video Filtering...")
    
    # Test URLs that should be filtered out
    video_urls = [
        "https://www.justice.gov/news/videos/some-video",
        "https://www.justice.gov/video/another-video",
        "https://www.justice.gov/media/video/test.mp4",
        "https://www.justice.gov/news/video-player",
        "https://www.justice.gov/opa/pr/test.mp4",
        "https://www.justice.gov/opa/pr/test?video=true",
        "https://youtube.com/watch?v=test",
        "https://www.justice.gov/embed/vimeo.com/test"
    ]
    
    # Test URLs that should be allowed
    valid_urls = [
        "https://www.justice.gov/opa/pr/valid-press-release",
        "https://www.justice.gov/news/press-release",
        "https://www.justice.gov/opa/pr/another-valid-release"
    ]
    
    config = ScrapingConfig()
    scraper = DOJScraper(config)
    
    print("\n📹 Testing video URL filtering:")
    for url in video_urls:
        is_valid = scraper._is_press_release_url(url)
        status = "❌ BLOCKED" if not is_valid else "✅ ALLOWED"
        print(f"  {status}: {url}")
        if is_valid:
            print(f"    ⚠️  This video URL was NOT filtered - potential issue!")
    
    print("\n📄 Testing valid URL filtering:")
    for url in valid_urls:
        is_valid = scraper._is_press_release_url(url)
        status = "✅ ALLOWED" if is_valid else "❌ BLOCKED"
        print(f"  {status}: {url}")
        if not is_valid:
            print(f"    ⚠️  This valid URL was filtered - potential issue!")
    
    print("\n🎯 Video filtering test completed!")
    print("💡 Video content filtering is enabled by default in ScrapingConfig")

if __name__ == "__main__":
    test_video_filtering() 