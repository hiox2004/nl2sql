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

# Database Configuration
DATABASE_PATH = 'ecommerce.db'

# Table Naming Conventions (configurable per database)
DATABASE_CONVENTIONS = {
    'prefixes': [
        'tbl_',      # Common: tbl_customers
        'dim_',      # Data warehouse: dim_customers
        'fact_',     # Data warehouse: fact_sales
        'stg_',      # Staging: stg_customers
        't_',        # Short prefix: t_customers
        'v_',        # Views: v_customers
    ],
    'suffixes': [
        '_tbl',      # customers_tbl
        '_table',    # customers_table
        '_v1',       # customers_v1
        '_v2',       # customers_v2
        '_view',     # customers_view
        '_archive',  # customers_archive
        '_temp',     # customers_temp
        '_hist',     # customers_hist
    ]
}

# Routing Configuration
ROUTING_CONFIG = {
    'threshold': 4,  # Complexity score threshold for tier selection
    'weights': {
        'query_length_divisor': 10,
        'entity_count': 2,
        'aggregation': 2.5,
        'comparison': 1.5,
        'time': 1,
        'multiple_conditions': 1.5,
        'grouping_hint': 2
    }
}