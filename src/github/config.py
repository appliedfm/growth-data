from datetime import timedelta

GITHUB_QUERY_DELAY=3
GITHUB_SEARCH_DELAY=7
GITHUB_SEARCH_DELAY_AUTHENTICATED=3
GITHUB_SEARCH_MAX_RESULTS=1000

GITHUB_WINDOWS = {
    "alltime": None,
    "001_1week": timedelta(weeks=1),
    "004_1month": timedelta(weeks=1*4),
    "013_3month": timedelta(weeks=3*4 + 1),
    "026_6month": timedelta(weeks=6*4 + 2),
    "052_1year": timedelta(weeks=1*52),
    "156_3year": timedelta(weeks=3*52),
    "261_5year": timedelta(weeks=5*52 + 1),
    "522_10year": timedelta(weeks=10*52 + 2),
}

GITHUB_FULL_LANGUAGES = [
    "ada",
    "agda",
    "coq",
    "idris",
    "isabelle",
    "lean",
    "sml",
    "tla",
]

GITHUB_PARTIAL_LANGUAGES = [
    "elixir",
    "erlang",
    "go",
    "haskell",
    "ocaml",
    "rust",
]

GITHUB_OTHER_LANGUAGES = [
    "assembly",
    "c",
    "c++",
    "fortran",
    "java",
    "python",
    "r",
    "scala",
    "terraform",
    "verilog",
]

GITHUB_DATASETS = {
    "user-alltime-counts": {
        "type": "user",
        "args": {
            "language": GITHUB_FULL_LANGUAGES + GITHUB_PARTIAL_LANGUAGES + GITHUB_OTHER_LANGUAGES,
            "created": [
                "alltime",
                "004_1month",
                "013_3month",
                "052_1year",
                "261_5year",
            ]
        }
    },
    "repo-alltime-counts": {
        "type": "repo",
        "stats": False,
        "args": {
            "language": GITHUB_FULL_LANGUAGES + GITHUB_PARTIAL_LANGUAGES + GITHUB_OTHER_LANGUAGES,
            "sort-by": [None],
            "pushed": [
                "alltime",
                "001_1week",
                "004_1month",
                "013_3month",
                "026_6month",
                "052_1year",
                "156_3year",
            ],
        }
    },
    "repo-weekly-stats": {
        "type": "repo",
        "stats": True,
        "topics": True,
        "args": {
            "language": GITHUB_FULL_LANGUAGES + GITHUB_PARTIAL_LANGUAGES,
            "sort-by": ["stars"],
            "pushed": ["001_1week"],
        }
    },
    "repo-alltime-stats": {
        "type": "repo",
        "stats": True,
        "args": {
            "language": GITHUB_FULL_LANGUAGES,
            "sort-by": ["stars"],
            "pushed": [
                "alltime",
                "004_1month",
                "013_3month",
                "026_6month",
                "052_1year",
                "156_3year",
            ],
        }
    },
}
