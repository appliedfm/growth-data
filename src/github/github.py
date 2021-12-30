from config import *
from datetime import datetime, timezone
from time import sleep
import requests
import urllib.parse

class GitHub:
    def __init__(self, disable_ratelimit=False):
        self.last_query = None
        self.last_search = None
        self.disable_ratelimit = disable_ratelimit

    def ratelimit(self, is_search):
        ts = datetime.now(tz=timezone.utc)
        if self.disable_ratelimit:
            return ts

        last = self.last_search if is_search else self.last_query

        if last is not None:
            delay = GITHUB_SEARCH_DELAY if is_search else GITHUB_QUERY_DELAY
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

    def do_request(self, api_url, is_search=False):
        print(f"  ... do_request(\"{api_url}\")", flush=True)
        ts = self.ratelimit(is_search)
        response = requests.get(api_url)        
        return response.status_code, response.json()

    def do_search(self, search_type, q, fetch_all=False, sortby=None, page=1, per_page=100, items=[]):
        if not fetch_all:
            per_page = 1

        print(f"{search_type}_search(q={q}, fetch_all={fetch_all}, sortby={sortby}, page={page}, per_page={per_page})", flush=True)

        api_url = f"https://api.github.com/search/{search_type}?q={urllib.parse.quote(q)}&page={page}&per_page={per_page}"
        if sortby is not None:
            api_url = api_url + f"&sort={sortby}"

        github_rest_status, github_rest_data = self.do_request(api_url, is_search=True)

        if 200 != github_rest_status:
            return github_rest_status, 0, items

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
                )
        
        return github_rest_status, total_count, items
