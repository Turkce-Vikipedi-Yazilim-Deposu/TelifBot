# TelifBot
A bot to check copyright violations on Wikipedia

- Listens the recent changes feed of Wikipedia for new pages
- For all new pages in the main (article) namespace, checks the copyright status via https://copyvios.toolforge.org tool
- If a copyright violation is detected, adds a copyright violation template to the page
