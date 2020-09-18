[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# TelifBot
A bot to check copyright violations on Wikipedia

- Listens the recent changes feed of Wikipedia for new pages
- For all new pages in the main (article) namespace, checks the copyright status via https://copyvios.toolforge.org tool
- If a copyright violation is detected, adds a copyright violation template to the page
