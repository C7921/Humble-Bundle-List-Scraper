import requests
from bs4 import BeautifulSoup
import json
import re

def get_page_content(url):
    """Fetch and parse the HTML content of a webpage"""
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")

def extract_bundle_title(soup, url):
    """Extract bundle title from the page metadata"""
    # Try og:title meta tag first
    meta_tag = soup.find("meta", attrs={"property": "og:title"})
    if meta_tag and "content" in meta_tag.attrs:
        return meta_tag["content"]
    
    # Try title tag
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.text
    
    # Try bundle logo alt text
    img_tag = soup.find("img", class_="bundle-logo")
    if img_tag and "alt" in img_tag.attrs:
        return img_tag["alt"]
    
    # Fallback to URL
    path = url.split("/")[-1]
    return " ".join(word.capitalize() for word in path.split("-"))

def generate_filename(title):
    """Create a clean filename from the bundle title"""
    clean = re.sub(r'[^\w\s-]', '', title) # Remove special characters
    clean = re.sub(r'\s+', '_', clean).lower() # Replace spaces with underscores, convert to lowercase
    return f"{clean}_items.txt"

def extract_item_info(item_data, charity_names):
    """Extract items from the tier_item_data structure"""
    items = []
    
    for item_id, info in item_data.items():
        title = info.get("human_name", "Unknown Title")
        
        # Skip charity entries
        if any(charity.lower() in title.lower() for charity in charity_names):
            print(f"Skipping charity: {title}")
            continue
        
        # Extract authors/developers - Don't know why they mix the names
        authors = []
        if "developers" in info:
            for dev in info["developers"]:
                if "developer-name" in dev:
                    author = dev["developer-name"]
                    if not any(charity.lower() in author.lower() for charity in charity_names):
                        authors.append(author)
        
        # Extract publisher URL - Not all items have unique urls, might go to same places
        publisher_url = None
        if "publishers" in info:
            for publisher in info["publishers"]:
                if "publisher-url" in publisher:
                    publisher_url = publisher["publisher-url"]
                    break
        
        items.append((title, authors, publisher_url))
    
    return items

def find_items_recursive(data, charity_names):
    """Recursively search for items in the data structure"""
    items = []
    
    def search(obj):
        if isinstance(obj, dict):
            if "human_name" in obj and "developers" in obj:
                title = obj["human_name"]
                
                # Skip charity entries
                if any(charity.lower() in title.lower() for charity in charity_names):
                    return
                
                # Extract authors
                authors = []
                for dev in obj["developers"]:
                    if "developer-name" in dev:
                        author = dev["developer-name"]
                        if not any(charity.lower() in author.lower() for charity in charity_names):
                            authors.append(author)
                
                # Extract publisher URL - Don't know why they mix the names
                publisher_url = None
                if "publishers" in obj:
                    for publisher in obj["publishers"]:
                        if "publisher-url" in publisher:
                            publisher_url = publisher["publisher-url"]
                            break
                
                items.append((title, authors, publisher_url))
            
            # Keep searching
            for v in obj.values():
                search(v)
        elif isinstance(obj, list):
            for item in obj:
                search(item)
    
    search(data)
    return items

def save_item_list(items, filename, bundle_title):
    """Save the item list to a file and print to console"""
    heading = f"items in the {bundle_title}"
    print(heading)
    print("-" * len(heading))
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"{bundle_title}\n")
        file.write("=" * len(bundle_title) + "\n\n")
        
        for i, (title, authors, publisher_url) in enumerate(items, 1):
            # Console output (optional)
            print(f"{i}. {title}")
            if authors:
                print(f"   Author(s): {', '.join(authors)}")
            if publisher_url:
                print(f"   Link: {publisher_url}")
            print()
            
            # File output
            file.write(f"{i}. {title}")
            if authors:
                file.write(f" by {', '.join(authors)}")
            file.write("\n")
            if publisher_url:
                file.write(f"   Link: {publisher_url}\n")
            file.write("\n")
    
    print(f"Total items found: {len(items)}")
    print(f"item list saved to '{filename}'")

def main():
    """Main function to orchestrate the scraping process"""
    # URL of the Humble Bundle page
    url = "https://www.humblebundle.com/books/data-visualization-oreilly-books"
    # url = "" # Uncomment and set your own URL if needed
    
    # Charity names to exclude
    charity_names = ["Code for America", "CodeForAmerica", "codeforamerica", "GameHeads", "Gameheads", "gameheads"]
    # These are stored under the same tags/classes as the items, so we need to skip them. 
    # Please sugesst a cleaner way
    
    # Get the page content
    soup = get_page_content(url)
    
    # Extract title
    bundle_title = extract_bundle_title(soup, url)
    print(f"Bundle Title: {bundle_title}")
    
    
    filename = generate_filename(bundle_title)
    print(f"Filename: {filename}")
    
    # Find the script tag from JSON export
    script_tag = soup.find("script", id="webpack-bundle-page-data")
    
    if not script_tag:
        print("Could not find the webpack-bundle-page-data script tag.")
        return
    
    # Parse the JSON data
    data = json.loads(script_tag.string)
    
    # Try to extract items from tier_item_data
    items = []
    if "tier_item_data" in data:
        items = extract_item_info(data["tier_item_data"], charity_names)
    
    # If no items found, try recursive search
    if not items:
        print("tier_item_data not found or empty. Trying alternative method...")
        items = find_items_recursive(data, charity_names)
    
    # If still no items found, save data for debugging
    if not items:
        print("Could not find items in the data structure.")
        with open("data_structure.json", "w") as f:
            json.dump(data, f, indent=4)
        print("Saved data structure to 'data_structure.json' for inspection.")
        return
    
    # Save the item list
    save_item_list(items, filename, bundle_title)

if __name__ == "__main__":
    main()
