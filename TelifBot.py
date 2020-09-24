import json
import pywikibot
from pywikibot import pagegenerators
from urllib import parse
from urllib.error import HTTPError, URLError
import requests
import sys
import logging

language = 'tr'
project = 'wikipedia'

def get_html(query_url):
    # Queries the website
    # We handle 500-502-503 etc server-side errors as HTTPError so the code do not crash
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        }
        response = requests.get(query_url, headers=headers)
        data = response.content
        return data
    except HTTPError as e:
        logging.error("EXCEPTION: get_html The server couldn't fulfill the request.")
        logging.error("Error code: ", e.code)
        return None
    except URLError as e:
        logging.error("EXCEPTION: get_html We failed to reach a server.")
        logging.error("Reason: ", e.reason)
        return None
    except MemoryError:
        logging.error('EXCEPTION: get_html Memory error')
        return None
    except:
        logging.error('EXCEPTION: get_html Other error')
        logging.error(str(sys.exc_info()))
        return None


def copyvios_score_printer(item):
    message = "Violation?\t"
    message += str(item["best"]["violation"])
    message += "\t("
    message += str(100 * item["best"]["confidence"])[0:5]
    message += "%)\t"
    message += str(item["best"]["url"])
    logging.info(message)


def json_violation(item):
    best = item["best"]
    if best["violation"] == "none":
        return None
    elif best["violation"] == "possible":
        return best
    elif best["violation"] == "suspected":
        return best
    else:
        return best


def make_template(json_data):
    probability = round(100 * json_data["best"]["confidence"], 2)
    url = json_data["best"]["url"]
    template_text = '''{{{{telifihlal
 | adres     = {0}
 | olasılık  = {1}
}}}}
'''.format(url, probability)
    return template_text


def controller(page):
    # Checks the page, only analyzes the page if it is NEW, in MAIN namespace, and longer than 500 bytes
    result = None
    if page._rcinfo["type"] == "new":
        if page._rcinfo["namespace"] == 0:
            if page._rcinfo["length"]["new"] > 500:
                result = True
    return result


def get_exceptions():
    try:
        # Loads the exceptions list from user page
        wiki = pywikibot.Site(language, project)
        exception_json = pywikibot.Page(wiki, 'User:%(username)s/Telif' % {'username': wiki.username()})
        json_data = str(exception_json.text)
        json_data = json_data.replace("\n", "")
        json_data = json.loads(json_data)
        return json_data["exception_list"]
    except:
        return []


def check_exceptions(page):
    # See if the page has a string/link that is in the exceptions list:
    match = False
    # Get the most recent exceptions list
    exception_list = get_exceptions()
    for item in exception_list:
        if item in page:
            match = True
            logging.info("EXCEPTION MATCH, PASSING!")
            logging.info(item)
    return match


def main():
    try:
        logging.info(page._link.title)
        analyze = controller(page)
        if analyze:
            page_to_analyze = parse.quote(page._link.title)
            copyvios_query = copyright_query + page_to_analyze
            if verbose == 1: logging.info(copyvios_query)
            copyvios_scores = get_html(copyvios_query)
            copyvios_json_scores = json.loads(copyvios_scores)
            if verbose == 1: copyvios_score_printer(copyvios_json_scores)
            copy_violation = json_violation(copyvios_json_scores)

            if copy_violation:
                copy_prob = "Olasılık: %" + str(round(100 * copy_violation["confidence"], 2))
                human_readable = human_query.format(page_to_analyze)
                summary = "Bot: Olası telif ihlali - " + copy_prob + " ([[Kullanıcı Mesaj:Khutuck|Hata bildir]])"

                template = make_template(copyvios_json_scores)
                page.text = template + page.text

                logging.info(page._link.title)
                logging.info(template)
                logging.info(summary)
                logging.info(human_readable)

                if not check_exceptions(page.text):
                    page.save(summary)

    except pywikibot.exceptions.NoPage:
        logging.error("No Page, pass")
        pass

    except:
        logging.error(sys.exc_info())
        pass


if __name__ == "__main__":
    # Global Settings
    verbose = 1
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
    copyright_query = "https://copyvios.toolforge.org/api.json?version=1&action=search&project=" + project + "&lang=" + language + "&title="
    human_query = "https://copyvios.toolforge.org/?lang=" + language + "&project=" + project + "&title={0}&oldid=&action=search&use_engine=1&use_links=1&turnitin=0"

    # Generators
    # generator = pagegenerators.TextfilePageGenerator(filename='TestPages.txt') # Offline testing
    generator = pagegenerators.LiveRCPageGenerator(site)  # Live RC

    logging.info("Telif Bot starting up...")
    for page in generator:
        main()
