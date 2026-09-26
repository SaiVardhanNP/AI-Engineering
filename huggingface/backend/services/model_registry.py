import os
import re
import time

import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

LOCAL_ID = "local:gemma-3-1b-it"
CATALOG_TTL_SECONDS = 600

GEMINI_CHAT = re.compile(r"^gemini-(\d+(?:\.\d+)?)-(flash|pro)(-lite)?(-preview)?$")
GROQ_SKIP = re.compile(r"whisper|orpheus|guard|safeguard|tts|allam")

SPECIAL_WORDS = {"gpt": "GPT", "oss": "OSS"}

PROVIDERS = [
    {"id": "local", "label": "On this machine", "cloud": False, "key": None},
    {"id": "gemini", "label": "Google Gemini", "cloud": True, "key": "GEMINI_API_KEY"},
    {"id": "groq", "label": "Groq", "cloud": True, "key": "GROQ_API_KEY"},
]


class UnknownModel(Exception):
    pass


def prettify(name):
    words = []

    for token in name.split("/")[-1].split("-"):
        lowered = token.lower()

        if lowered in SPECIAL_WORDS:
            words.append(SPECIAL_WORDS[lowered])
        elif re.fullmatch(r"\d+(\.\d+)?b", lowered):
            words.append(lowered.upper())
        elif re.fullmatch(r"[\d.]+", lowered):
            words.append(lowered)
        else:
            words.append(token.capitalize())

    return " ".join(words)


def entry(provider, name, label, note=None):
    return {
        "id": f"{provider}:{name}",
        "label": label,
        "provider": provider,
        "cloud": provider != "local",
        "note": note,
    }


def fetch_gemini(key):
    response = httpx.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"pageSize": 200},
        headers={"x-goog-api-key": key},
        timeout=15,
    )
    response.raise_for_status()

    names = [
        model["name"].split("/")[-1]
        for model in response.json().get("models", [])
        if "generateContent" in model.get("supportedGenerationMethods", [])
    ]

    best = {}

    for name in names:
        match = GEMINI_CHAT.match(name)

        if not match:
            continue

        version = float(match.group(1))
        tier = "lite" if match.group(3) else match.group(2)
        preview = bool(match.group(4))
        rank = (version, not preview)

        if tier not in best or rank > best[tier][0]:
            best[tier] = (rank, name, preview)

    return [
        entry("gemini", name, prettify(name).removesuffix(" Preview"), "Preview" if preview else None)
        for tier in ("flash", "pro", "lite")
        if tier in best
        for _, name, preview in [best[tier]]
    ]


def fetch_groq(key):
    response = httpx.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=15,
    )
    response.raise_for_status()

    names = [
        model["id"]
        for model in response.json().get("data", [])
        if not GROQ_SKIP.search(model["id"])
    ]

    def size(name):
        match = re.search(r"(\d+)b", name)
        return int(match.group(1)) if match else 0

    return [
        entry("groq", name, prettify(name))
        for name in sorted(names, key=size, reverse=True)
    ]


class ModelRegistry:
    def __init__(self, local_factory):
        self.local_factory = local_factory
        self.instances = {}
        self.catalog_cache = None
        self.catalog_time = 0.0

    def catalog(self):
        if self.catalog_cache and time.time() - self.catalog_time < CATALOG_TTL_SECONDS:
            return self.catalog_cache

        models = [entry("local", "gemma-3-1b-it", "Gemma 3 1B", "Runs offline")]
        providers = []

        for provider in PROVIDERS:
            key = os.getenv(provider["key"]) if provider["key"] else "local"
            status = "ready" if key else "no_key"

            if key and provider["id"] != "local":
                try:
                    fetch = fetch_gemini if provider["id"] == "gemini" else fetch_groq
                    models.extend(fetch(key))
                except httpx.HTTPError:
                    status = "unreachable"

            providers.append(
                {
                    "id": provider["id"],
                    "label": provider["label"],
                    "cloud": provider["cloud"],
                    "env": provider["key"],
                    "status": status,
                }
            )

        self.catalog_cache = {"default": LOCAL_ID, "models": models, "providers": providers}
        self.catalog_time = time.time()

        return self.catalog_cache

    def describe(self, model_id):
        model_id = model_id or LOCAL_ID

        for item in self.catalog()["models"]:
            if item["id"] == model_id:
                return item

        raise UnknownModel(model_id)

    def get(self, model_id):
        item = self.describe(model_id)

        if item["id"] in self.instances:
            return self.instances[item["id"]]

        name = item["id"].split(":", 1)[1]

        if item["provider"] == "local":
            llm = self.local_factory()
        elif item["provider"] == "gemini":
            llm = ChatGoogleGenerativeAI(
                model=name,
                google_api_key=os.environ["GEMINI_API_KEY"],
                temperature=0.2,
                max_output_tokens=2048,
            )
        else:
            llm = ChatGroq(
                model=name,
                api_key=os.environ["GROQ_API_KEY"],
                temperature=0.2,
                max_tokens=2048,
            )

        self.instances[item["id"]] = llm

        return llm
