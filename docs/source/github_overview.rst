GitHub Overview
===============

Data is collected from GitHub on a weekly basis. Most of our data concerns repositories, although we do track some limited information about user population size and popular `topics <https://github.com/topics>`_.

For each language and various time windows (defined as "time since most recent push"), we perform a series of GitHub searches. We then compute various aggregated statistics about the search results.

* For privacy reasons, we do not retain the raw search results.
* We retain the aggregated statistics to facilitate time-series analysis.

Our corpus consists exclusively of "non-fork" repositories. We do this to avoid "double-counting" popular projects.

GitHub search data is limited to the top 1,000 results. Many of the languages we study have fewer than 1,000 non-fork public repositories; for those languages, our data is comprehensive. For languages with more responsitories, our statistics are computed using the top 1,000 results ordered by stars (descending).


Repo counts by language & activity
----------------------------------

These counts are gathered directly from GitHub. (In particular, they are not impacted by the "1,000 results limit" described above.)

* "Pushed" refers to the time since the repository was last pushed. We measure it in weeks. For example, ``pushed=013_3month`` refers to repositories that have been pushed sometime in the last 13 weeks (which is approximately 3 months). The only exception is ``pushed=alltime``, which considers *all* repositories regardless of when their last push occurred.

* Below, we show two charts: they contain the same data, but one is in *logarithmic scale* while the other is in *linear scale*.

.. raw:: html
   :file: _static/plots/repo-alltime-counts/repo_counts/repo_count-logscale.html

.. raw:: html
   :file: _static/plots/repo-alltime-counts/repo_counts/repo_count.html


Users by language & account age
-------------------------------

These counts are gathered directly from GitHub. (In particular, they are not impacted by the "1,000 results limit" described above.)

* "Created" refers to the time since the user account was created: in other words, the account's "age." We measure it in weeks. For example, ``created=013_3month`` refers to users who created their account sometime in the last 13 weeks (which is approximately 3 months). The only exception is ``created=alltime``, which considers *all* users regardless of when their account was created.

* These charts shed light on which languages are most popular among different "generations" of GitHub users.

* Below, we show two charts: they contain the same data, but one is in *logarithmic scale* while the other is in *linear scale*.

.. raw:: html
   :file: _static/plots/user-alltime-counts/user_counts/user_count-logscale.html

.. raw:: html
   :file: _static/plots/user-alltime-counts/user_counts/user_count.html

