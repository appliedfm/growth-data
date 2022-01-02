GitHub Overview
===============

Data is collected from GitHub on a weekly basis. Most of our data concerns repositories, although we do track some limited information about user population size and popular `topics <https://github.com/topics>`_.

For each language and various time windows (defined as "time since most recent push"), we perform a series of GitHub searches. We then compute various aggregated statistics about the search results.

* For privacy reasons, we do not retain the raw search results.
* We retain the aggregated statistics to facilitate time-series analysis.

Our corpus consists exclusively of "non-fork" repositories. We do this to avoid "double-counting" popular projects.

GitHub search data is limited to the top 1,000 results. Many of the languages we study have fewer than 1,000 non-fork public repositories; for those languages, our data is comprehensive. For languages with more responsitories, we fetch the top 1,000 results ordered by stars (descending).
