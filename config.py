MODELS = {
    "tier1": "qwen2.5-coder:1.5b",
    "tier2": "qwen2.5-coder:7b",
    "tier3": "qwen2.5-coder:7b", # bigger model to be used for production, using this because of laptop limitations
}

DATABASE_URL = "sqlite:///schema/toy.db"

APP_MODE = "toy"

STANDARDS = {
    "naming": "snake_case",
    "pk_suffix": "_id",
}