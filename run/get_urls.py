#!/usr/bin/env python


import pandas as pd
import requests
import re
import random
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote


def main():

    dfcompany = pd.read_csv('data/fortune/f500_firm_sample.csv')

    dfcompany_sample = dfcompany.loc[lambda x: (x['include']==True) & (x['ranking']<=300)].copy()
    privacy_policy_url = {}
    full_sequence = 0

    useragents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:70.0) Gecko/20100101 Firefox/70.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148 Safari/604.1"
    ]

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,en;q=0.8",
      }

    current_sequence = 0

    while len(privacy_policy_url) < len(dfcompany_sample):

        dfcompany_sample_remaining = dfcompany_sample.loc[lambda x: ~x['firm'].isin(privacy_policy_url.keys())]
        companies = dfcompany_sample_remaining['firm'].values
        urls = dfcompany_sample_remaining['url'].values

        for c, u in zip(companies, urls):

            if full_sequence == 0:
                max_sequence = random.randint(2, 4)
                next_agent_row = random.randint(0, len(useragents)-1)
                headers["User-Agent"] = useragents[next_agent_row]
            elif current_sequence <= max_sequence:
                pass
            else:
                current_sequence = 0
                max_sequence = random.randint(2, 4)
                next_agent_row = random.randint(0, len(useragents)-1)
                headers["User-Agent"] = useragents[next_agent_row]

            urlbase = urlparse(u).netloc.split('.', 1)[1]
            searchurl = f'https://www.google.dz/search?q=privacy+policy+{urlbase}'

            response = requests.get(searchurl, headers=headers)
            if response.status_code != 200:
                print(f'Response code: {response.status_code}')
                wait = random.randint(60, 150)
                print(f'Sleeping for {wait} seconds')
                time.sleep(wait)
                print('Continue')
                current_sequence = 0
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            search_url_results = []
            for h in soup.findAll('a'):
                href = h.get('href')
                if href != None:
                    href_checked = re.search("(?P<url>https?://[^\s]+)", href)
                    if href_checked != None:
                        href_checked = href_checked.group()
                        href_cleaned = unquote(href_checked.split('&')[0])
                        href_domain = urlparse(href_cleaned)
                        href_domain_base = href_domain.netloc
                        if re.search('google.', href_domain_base):
                            pass
                        elif re.search(urlbase, href_domain_base):
                            search_url_results.append(href_cleaned)
                        else:
                            pass

            try:
                privacy_policy_url[c] = {"ppurl": search_url_results[0]}
                print(f'=> {len(privacy_policy_url)} / {len(dfcompany_sample)}')
                print(f'{c} - founded url: {search_url_results[0]}')
            except:
                privacy_policy_url[c] = {"ppurl": "unknown"}
                print(f'=> {len(privacy_policy_url)} / {len(dfcompany_sample)}')
                print(f'{c} - founded url: unknown')

            current_sequence += 1
            time.sleep(random.randint(30, 120) / 10)
            full_sequence += 1

            if full_sequence % random.randint(5, 40) == 0:
                time.sleep(random.randint(60, 180))

    with open('data/policies/urls/privacy_policy_urls.json', 'w') as outfile:
        json.dump(privacy_policy_url, outfile)


if __name__ == '__main__':
    main()
