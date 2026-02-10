import sqlite3
import re
from config import DATABASE_CONVENTIONS, ROUTING_CONFIG

# Cache for performance
_TABLE_CACHE = {}
_FK_CACHE = {}

def get_table_names(db_path='ecommerce.db'):
    """Get all table names from database (cached)"""
    if db_path not in _TABLE_CACHE:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        _TABLE_CACHE[db_path] = [row[0] for row in cursor.fetchall()]
        conn.close()
    
    return _TABLE_CACHE[db_path]

def get_foreign_key_graph(db_path='ecommerce.db'):
    """Build foreign key relationship graph (cached)"""
    if db_path not in _FK_CACHE:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        graph = {}
        
        for table in get_table_names(db_path):
            related = set()
            
            # Get FKs from this table
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()
            for fk in fks:
                related.add(fk[2])
            
            # Get FKs pointing TO this table
            for other_table in get_table_names(db_path):
                if other_table != table:
                    cursor.execute(f"PRAGMA foreign_key_list({other_table})")
                    other_fks = cursor.fetchall()
                    for fk in other_fks:
                        if fk[2] == table:
                            related.add(other_table)
            
            graph[table] = list(related)
        
        conn.close()
        _FK_CACHE[db_path] = graph
    
    return _FK_CACHE[db_path]

def normalize_table_name(table_name):
    """Strip common prefixes/suffixes using config"""
    name = table_name.lower()
    
    # Remove prefixes from config
    for prefix in DATABASE_CONVENTIONS['prefixes']:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break
    
    # Remove suffixes from config
    for suffix in DATABASE_CONVENTIONS['suffixes']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    
    return name

def classify_complexity(question, db_path='ecommerce.db'):
    """Phase 1: Fast complexity classification"""
    
    question_lower = question.lower()
    weights = ROUTING_CONFIG['weights']
    
    # Feature extraction
    features = {
        'query_length': len(question.split()),
        'entity_count': count_entities(question_lower, db_path),
        'has_aggregation': has_keywords(question_lower, ['top', 'total', 'average', 'sum', 'count', 'most', 'least', 'max', 'min']),
        'has_comparison': has_keywords(question_lower, ['more than', 'less than', 'between', 'greater', 'higher', 'lower', 'above', 'below']),
        'has_time': has_keywords(question_lower, ['last', 'since', 'between', 'before', 'after', 'during', 'recent', 'latest']),
        'has_multiple_conditions': question_lower.count('and') + question_lower.count('or'),
        'has_grouping_hint': has_keywords(question_lower, ['each', 'per', 'by', 'group', 'category', 'type'])
    }
    
    # Scoring system using config weights
    score = (
        (features['query_length'] / weights['query_length_divisor']) +
        (features['entity_count'] * weights['entity_count']) +
        (features['has_aggregation'] * weights['aggregation']) +
        (features['has_comparison'] * weights['comparison']) +
        (features['has_time'] * weights['time']) +
        (features['has_multiple_conditions'] * weights['multiple_conditions']) +
        (features['has_grouping_hint'] * weights['grouping_hint'])
    )
    
    threshold = ROUTING_CONFIG['threshold']
    tier = 'tier2' if score >= threshold else 'tier1'
    
    return tier, score, features

def count_entities(question_lower, db_path='ecommerce.db'):
    """Count database tables mentioned in question (dynamic)"""
    tables = get_table_names(db_path)
    count = 0
    
    for table in tables:
        normalized = normalize_table_name(table)
        
        # Check normalized name
        if normalized in question_lower:
            count += 1
            continue
        
        # Check singular form
        singular = normalized.rstrip('s')
        if singular != normalized and singular in question_lower:
            count += 1
    
    return count

def has_keywords(text, keywords):
    """Check if any keyword exists"""
    return any(keyword in text for keyword in keywords)

def extract_relevant_tables(question, db_path='ecommerce.db'):
    """Phase 2: Identify relevant tables with layered approach"""
    
    question_lower = question.lower()
    question_words = set(re.findall(r'\w+', question_lower))
    
    all_tables = get_table_names(db_path)
    matched_tables = set()
    
    # LAYER 1: Smart Preprocessing & Matching
    for table in all_tables:
        normalized = normalize_table_name(table)
        
        # Strategy 1: Exact normalized match
        if normalized in question_lower:
            matched_tables.add(table)
            continue
        
        # Strategy 2: Singular form (customers → customer)
        singular = normalized.rstrip('s')
        if singular != normalized and singular in question_lower:
            matched_tables.add(table)
            continue
        
        # Strategy 3: Compound tables (order_items → "order" or "item")
        table_parts = re.split(r'[_\-]', normalized)
        for part in table_parts:
            if part in question_words and len(part) > 3:
                matched_tables.add(table)
                break
    
    # LAYER 2: Foreign Key Expansion (include related tables)
    if matched_tables:
        fk_graph = get_foreign_key_graph(db_path)
        expanded_tables = set(matched_tables)
        
        for table in matched_tables:
            if table in fk_graph:
                expanded_tables.update(fk_graph[table])
        
        matched_tables = expanded_tables
    
    # Convert to list and preserve order
    relevant_tables = [t for t in all_tables if t in matched_tables]
    
    # LAYER 3: Safety Fallback
    if not relevant_tables:
        relevant_tables = all_tables
    
    return relevant_tables

def get_focused_schema(tables, db_path='ecommerce.db'):
    """Get schema for specific tables only"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = ""
    for table in tables:
        # Get columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        schema += f"\nTable: {table}\n"
        schema += "Columns: " + ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        if fks:
            fk_info = []
            for fk in fks:
                fk_info.append(f"{fk[3]} → {fk[2]}.{fk[4]}")
            schema += "\nForeign Keys: " + ", ".join(fk_info)
        
        schema += "\n"
    
    conn.close()
    return schema

def clear_cache():
    """Clear all caches (useful if database changes)"""
    global _TABLE_CACHE, _FK_CACHE
    _TABLE_CACHE = {}
    _FK_CACHE = {}
