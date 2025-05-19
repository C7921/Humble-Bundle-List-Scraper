# Humble-Bundle-List-Scraper
Gets a list of the bundle items available on Humble Bundle. Does not get the actual items, just stores a list for reference. 

Always recommend donating and this is not meant to get around that. I just wanted a list of the items in the bundles for reference or as ones to research later as options. Getting all item in the bundles just isn't feasible at times.

## Usage
1. Change URL in `main()` to whatever bundle link. Works with books, games, and software but was designed for books. Also add/remove the list of charity names in `main()` they are just there so not to appear in the list of items in the bundle. No easy way I could be bothered to find to remove them.

2. Run with `python humble-bundle-list-scraper.py`. You will need to install BeautifulSoup4 ([Here](https://beautiful-soup-4.readthedocs.io/en/latest/))

3. Get a nicely formatted list created in the same directory.

### Note

This is definitely not necessary in any way and is 100% overenginerred. But, sometimes its fun to build a tank where a bicycle would work, this could be done in 20 lines of simple (and more elegant code). There is no reason for recursive calls, JSON exports, and multiple fallback strategies. In does handle some weird edge cases (sort of) but don't expect perfection.

This info is already on the webpage anyway, why scrap it? Why not just take a screenshot like a normal person? Hell even print the page and save it as a PDF or just print the page.

I can't wait for a small change in their site to break this thing. Although if the site was simplier then it wouldn't really be a problem.
