import json
import urllib
from string import punctuation
import nltk

from wikifier_util import get_wikipedia_url_from_wikidata_id

ENTITY_TYPES = [
    "human",
    "person",
    "company",
    "enterprise",
    "business",
    "geographic region",
    "human settlement",
    "geographic entity",
    "territorial entity type",
    "organization",
]


def wikifier(text, lang="en", threshold=0.8):
    """Function that fetches entity linking results from wikifier.com API"""
    # Prepare the URL.
    data = urllib.parse.urlencode(
        [
            ("text", text),
            ("lang", lang),
            ("userKey", "tgbdmkpmkluegqfbawcwjywieevmza"),
            ("pageRankSqThreshold", "%g" % threshold),
            ("applyPageRankSqThreshold", "true"),
            ("nTopDfValuesToIgnore", "100"),
            ("nWordsToIgnoreFromList", "100"),
            ("wikiDataClasses", "true"),
            ("wikiDataClassIds", "false"),
            ("support", "true"),
            ("ranges", "false"),
            ("minLinkFrequency", "2"),
            ("includeCosines", "false"),
            ("maxMentionEntropy", "3"),
        ]
    )
    url = "http://www.wikifier.org/annotate-article"
    # Call the Wikifier and read the response.
    req = urllib.request.Request(url, data=data.encode("utf8"), method="POST")
    with urllib.request.urlopen(req, timeout=60) as f:
        response = f.read()
        response = json.loads(response.decode("utf8"))
    # Output the annotations.
    results = list()
    for annotation in response["annotations"]:
        # Filter out desired entity classes
        if ("wikiDataClasses" in annotation) and (
            any([el["enLabel"] in ENTITY_TYPES for el in annotation["wikiDataClasses"]])
        ):

            # Specify entity label
            if any(
                [
                    el["enLabel"] in ["human", "person"]
                    for el in annotation["wikiDataClasses"]
                ]
            ):
                label = "Person"
            elif any(
                [
                    el["enLabel"]
                    in ["company", "enterprise", "business", "organization"]
                    for el in annotation["wikiDataClasses"]
                ]
            ):
                label = "Organization"
            elif any(
                [
                    el["enLabel"]
                    in [
                        "geographic region",
                        "human settlement",
                        "geographic entity",
                        "territorial entity type",
                    ]
                    for el in annotation["wikiDataClasses"]
                ]
            ):
                label = "Location"
            else:
                label = None

            results.append(
                {
                    "title": annotation["title"],
                    "wikiId": annotation["wikiDataItemId"],
                    "label": label,
                    "characters": [
                        (el["chFrom"], el["chTo"]) for el in annotation["support"]
                    ],
                }
            )
    return results


wikified = wikifier(
    "Secretary of State Antony J. Blinken and Secretary of Defense Lloyd J. Austin III will travel to Seoul, Republic of Korea (ROK), March 17–18 to reaffirm the United States’ commitment to strengthening our Alliance and to highlight cooperation that promotes peace, security, and prosperity in the Indo-Pacific and around the world."
)

wiki_page = get_wikipedia_url_from_wikidata_id(
    wikified[0]["wikiId"]
)  # wikidata id -> wikipedia page

import webbrowser

# MacOS
chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

# Windows
# chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

# Linux
# chrome_path = '/usr/bin/google-chrome %s'

webbrowser.get(chrome_path).open(wiki_page)


if __name__ == "__main__":
    pass
