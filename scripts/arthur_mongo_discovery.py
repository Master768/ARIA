"""
Arthur (Source Discovery) & Silas (Extraction) Script for MongoDB
Target Database: pulse_db
"""
import os
import json
import pymongo
import dns.resolver
import pandas as pd
from datetime import datetime

# Set resilient public DNS nameservers for Atlas SRV resolution
try:
    dns.resolver.default_resolver = dns.resolver.Resolver()
    dns.resolver.default_resolver.nameservers = ['1.1.1.1', '8.8.8.8']
except Exception:
    pass

MONGO_URI = os.environ.get("MONGO_URI")

def main():
    global MONGO_URI
    if not MONGO_URI:
        import sys
        if len(sys.argv) > 1:
            MONGO_URI = sys.argv[1]
        else:
            print("[Arthur] Error: MONGO_URI environment variable is not set.")
            print("Please run: export MONGO_URI='your_connection_string' (or set $env:MONGO_URI in PowerShell)")
            print("Or pass as argument: python scripts/arthur_mongo_discovery.py '<connection_string>'")
            return

    print("--- [Arthur] Connecting to MongoDB to Discover pulse_db ---")
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
        # Force a connection verification
        client.admin.command('ping')
        print("Connected successfully to MongoDB Atlas cluster!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return

    # List databases
    dbs = client.list_database_names()
    print(f"Databases available on cluster: {dbs}")
    
    db_name = "pulse_db" if "pulse_db" in dbs else client.get_default_database().name
    print(f"Inspecting target database: {db_name}")
    db = client[db_name]
    
    collections = db.list_collection_names()
    print(f"Collections found in {db_name}: {collections}")
    
    catalog_info = []
    
    os.makedirs("data/raw", exist_ok=True)
    
    for coll_name in collections:
        coll = db[coll_name]
        doc_count = coll.count_documents({})
        sample_docs = list(coll.find().limit(5))
        
        # Analyze schema fields from sample
        field_types = {}
        for doc in sample_docs:
            for k, v in doc.items():
                if k not in field_types:
                    field_types[k] = type(v).__name__
                    
        catalog_info.append({
            "collection": coll_name,
            "count": doc_count,
            "fields": field_types,
            "sample": sample_docs[0] if sample_docs else {}
        })
        print(f"\nCollection: {coll_name} | Total Documents: {doc_count}")
        print(f"  Fields detected: {list(field_types.keys())}")
        
        # Silas extracts all documents to data/raw/
        if doc_count > 0:
            all_docs = list(coll.find())
            # Convert ObjectId and datetime to string for clean parquet serialization
            for d in all_docs:
                for k, v in d.items():
                    if isinstance(v, (datetime,)):
                        d[k] = v.isoformat()
                    elif not isinstance(v, (int, float, str, bool, list, dict, type(None))):
                        d[k] = str(v)
            df = pd.DataFrame(all_docs)
            if '_id' in df.columns:
                df['_id'] = df['_id'].astype(str)
                
            parquet_path = f"data/raw/pulse_{coll_name}.parquet"
            csv_path = f"data/raw/pulse_{coll_name}.csv"
            
            # Save CSV and Parquet
            df.to_csv(csv_path, index=False)
            try:
                df.to_parquet(parquet_path, index=False)
                print(f"  [Silas] Extracted {len(df)} records -> {parquet_path} & {csv_path}")
            except Exception as pe:
                print(f"  [Silas] Extracted {len(df)} records -> {csv_path} (Parquet note: {pe})")

    # Arthur compiles the discovery manifest
    manifest_content = f"""# Data Source Discovery Manifest: MongoDB `pulse_db`
**Agent:** Arthur (Principal Data Architect & Catalog Locator)  
**Data Source:** MongoDB Atlas (`cluster0.6jegcfk.mongodb.net`)  
**Database:** `{db_name}`  
**Discovered:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

---

## 1. Catalog & Entity Overview
Found **{len(collections)} collection(s)** in `{db_name}`.

| Collection Name | Document Count | Primary Key | Key Attributes | Extracted Path |
|---|---|---|---|---|
"""
    for item in catalog_info:
        field_list = ", ".join([f"`{k}` ({v})" for k, v in list(item['fields'].items())[:6]])
        manifest_content += f"| `{item['collection']}` | {item['count']:,} | `_id` (ObjectId) | {field_list} | `data/raw/pulse_{item['collection']}.csv` |\n"

    manifest_content += f"""
---

## 2. Detailed Schemas by Collection

"""
    for item in catalog_info:
        manifest_content += f"### Collection: `{item['collection']}`\n"
        manifest_content += f"- **Total Records:** {item['count']:,}\n"
        manifest_content += f"- **Schema Fields:**\n"
        for f_name, f_type in item['fields'].items():
            manifest_content += f"  - `{f_name}`: `{f_type}`\n"
        manifest_content += f"\n**Sample Document:**\n```json\n"
        sample_clean = {k: str(v) if not isinstance(v, (int, float, str, bool, list, dict, type(None))) else v for k, v in item['sample'].items()}
        manifest_content += json.dumps(sample_clean, indent=2, default=str)
        manifest_content += "\n```\n\n---\n"

    manifest_content += """
## 3. Downstream Handoff to Maya (Data Understanding)
- Extracted datasets are safely landed in `data/raw/pulse_*.csv` and `data/raw/pulse_*.parquet`.
- Maya can now profile distributions, missingness, and correlation across these collections!
"""
    with open("data/source_discovery_manifest.md", "w", encoding="utf-8") as f:
        f.write(manifest_content)

    print("\n--- [Arthur] Discovery Manifest written to data/source_discovery_manifest.md ---")
    print("--- [Silas] Raw datasets extracted to data/raw/ ---")

if __name__ == "__main__":
    main()
