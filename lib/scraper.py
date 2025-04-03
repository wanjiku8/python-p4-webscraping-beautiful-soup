from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import time
import random

class FlatironScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        self.base_url = "https://flatironschool.com/"
        
    def _make_request(self, url):
        """Helper method to make requests with retries and delays"""
        try:
            time.sleep(random.uniform(1, 2))  # Polite delay
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def scrape_main_heading(self):
        """Scrape the main heading from homepage"""
        soup = self._make_request(self.base_url)
        if not soup:
            return "Failed to load homepage"
            
        # Current working selector for main heading
        heading = soup.find('h1')
        return heading.get_text(strip=True) if heading else "Main heading not found"

    def scrape_courses(self):
        """Scrape course information from the website"""
        soup = self._make_request(self.base_url)
        if not soup:
            return []
            
        courses = []
        
        # Try different approaches to find courses
        # Method 1: Look for program cards
        program_cards = soup.select('.program-card')
        for card in program_cards:
            title = card.select_one('h3')
            if title:
                courses.append(title.get_text(strip=True))
        
        # Method 2: Look for course links in navigation
        if not courses:
            nav_links = soup.select('nav a[href*="courses"]')
            for link in nav_links:
                if len(link.get_text(strip=True)) > 3:  # Filter out short texts
                    courses.append(link.get_text(strip=True))
        
        # Method 3: Fallback to any h3 elements that look like courses
        if not courses:
            all_h3 = soup.find_all('h3')
            for h3 in all_h3:
                text = h3.get_text(strip=True)
                if len(text.split()) > 1 and 'course' in text.lower():
                    courses.append(text)
        
        return list(set(courses))[:8]  # Remove duplicates and limit

    def scrape_all_links(self):
        """Extract all links from homepage"""
        soup = self._make_request(self.base_url)
        if not soup:
            return []
            
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('javascript:'):
                continue
            if href.startswith('http'):
                links.add(href)
            else:
                links.add(urljoin(self.base_url, href))
        return sorted(links)

    def run(self):
        """Execute all scraping functions and display results"""
        print("=== Flatiron School Scraper ===")
        
        print("\n[1] Main Heading:")
        print(self.scrape_main_heading())
        
        print("\n[2] Courses Offered:")
        courses = self.scrape_courses()
        if courses:
            for i, course in enumerate(courses, 1):
                print(f"{i}. {course}")
        else:
            print("No courses found - trying alternative approach...")
            # Try scraping from courses page directly
            courses_url = urljoin(self.base_url, "our-courses/")
            soup = self._make_request(courses_url)
            if soup:
                course_titles = soup.select('.program-title')
                if course_titles:
                    for i, title in enumerate(course_titles, 1):
                        print(f"{i}. {title.get_text(strip=True)}")
                else:
                    print("Still couldn't find courses. Website structure may have changed significantly.")
        
        print("\n[3] Sample Links (First 5):")
        links = self.scrape_all_links()
        for link in links[:5]:
            print(link)
        
        print("\nScraping complete!")

if __name__ == "__main__":
    scraper = FlatironScraper()
    scraper.run()