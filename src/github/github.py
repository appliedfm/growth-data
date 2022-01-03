from config import *
from datetime import datetime, timezone
from time import sleep
import json
import requests
import urllib.parse
import sys

class GitHub:
    def __init__(self, disable_ratelimit=False, token=None):
        self.last_query = None
        self.last_search = None
        self.disable_ratelimit = disable_ratelimit
        self.token=token

    def ratelimit(self, is_search):
        ts = datetime.now(tz=timezone.utc)
        if self.disable_ratelimit:
            return ts

        last = self.last_search if is_search else self.last_query

        SEARCH_DELAY = GITHUB_SEARCH_DELAY_AUTHENTICATED if self.token is not None else GITHUB_SEARCH_DELAY

        if last is not None:
            delay = SEARCH_DELAY if is_search else GITHUB_QUERY_DELAY
            second_since_last = (ts - last).total_seconds()
            sleep_for = delay - second_since_last
            if sleep_for > 0:
                print(f"  ... rate limit: sleeping for {sleep_for} seconds ...", flush=True)
                sleep(sleep_for)

        ts = datetime.now(tz=timezone.utc)
        if is_search:
            self.last_search = ts
        else:
            self.last_query = ts
        return ts

    def do_request(self, api_url, is_search=False, retries=2):
        print(f"  ... do_request(\"{api_url}\")", flush=True)
        ts = self.ratelimit(is_search)
        headers = {
            'User-Agent': 'https://github.com/appliedfm/growth-data'
        }
        if self.token is not None:
            headers['Authorization'] = 'token ' + self.token
        response = requests.get(api_url, headers=headers)

        if 200 != response.status_code:
            print(f"  ... error: status={response.status_code}", file=sys.stderr, flush=True)
            print(f"      headers: {response.headers}", file=sys.stderr, flush=True)
            print(f"      response: {json.dumps(response.json())}", file=sys.stderr, flush=True)
            if 0 < retries:
                sleep_for = 120
                print(f"  ... sleeping for {sleep_for} seconds, then retrying ... ", file=sys.stderr, flush=True)
                sleep(sleep_for)
                return self.do_request(
                    api_url,
                    is_search=is_search,
                    retries=retries - 1
                )
            print(f"      exiting with failure (out of retries)", file=sys.stderr, flush=True)
            exit(-1)

        return response.status_code, response

    def do_search(self, search_type, q, fetch_all=False, sortby=None, page=1, per_page=100, items=[], retries=2):
        if not fetch_all:
            per_page = 1

        print(f"{search_type}_search(q={q}, fetch_all={fetch_all}, sortby={sortby}, page={page}, per_page={per_page})", flush=True)

        api_url = f"https://api.github.com/search/{search_type}?q={urllib.parse.quote(q)}&page={page}&per_page={per_page}"
        if sortby is not None:
            api_url = api_url + f"&sort={sortby}&order=desc"

        github_rest_status, github_rest_response = self.do_request(api_url, is_search=True)
        github_rest_data = github_rest_response.json()

        total_count = int(github_rest_data["total_count"])
        total_so_far = len(items) + len(github_rest_data["items"])
        print(f"  ... success: {total_so_far} of {total_count}", flush=True)

        if fetch_all:
            items = items + github_rest_data["items"]

            # Continue to the next page
            if total_so_far < total_count and total_so_far < GITHUB_SEARCH_MAX_RESULTS:
                return self.do_search(
                    search_type,
                    q,
                    fetch_all = fetch_all,
                    sortby = sortby,
                    page = page + 1,
                    per_page = per_page,
                    items = items,
                    retries = 2,
                )
        
        return github_rest_status, total_count, items
