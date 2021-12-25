from datetime import timedelta

GITHUB_WINDOWS = {
    "alltime": None,
    "001_1week": timedelta(weeks=1),
    "004_1month": timedelta(weeks=1*4),
    "012_3month": timedelta(weeks=3*4),
    "024_6month": timedelta(weeks=6*4),
    "052_1year": timedelta(weeks=1*52),
    "156_3year": timedelta(weeks=3*52),
    "260_5year": timedelta(weeks=5*52),
    "520_10year": timedelta(weeks=10*52),
}

GITHUB_FULL_LANGUAGES = [
    "ada",
    "agda",
    "coq",
    "idris",
    "isabelle",
    "lean",
    "tla"
]

GITHUB_DISCOVER_LANGUAGES = [
    "erlang",
    "haskell",
    "fortran",
    "go",
    "ocaml",
    "rust",
    "terraform",
    "verilog",
]

GITHUB_LIGHT_LANGUAGES = [
    "assembly",
    "c",
    "c++",
    "java",
    "prolog",
    "python",
    "r",
    "scala",
]

GITHUB_LANGUAGES = GITHUB_FULL_LANGUAGES + GITHUB_DISCOVER_LANGUAGES + GITHUB_LIGHT_LANGUAGES

GITHUB_DISCOVER_WINDOW="001_1week"
GITHUB_DISCOVER_STARS=5
GITHUB_DISCOVER_TOPICS=2

GITHUB_FETCH_ALL = [
    (language, window)
    for language in GITHUB_FULL_LANGUAGES
    for window in [
        "alltime",
        "004_1month",
        "024_6month",
        "052_1year",
        "156_3year",
    ]
]

GITHUB_USER_WINDOWS = [
    "alltime",
    "004_1month",
    "052_1year",
    "260_5year",
]

GITHUB_TOPIC_WINDOWS = [
    "alltime",
]
