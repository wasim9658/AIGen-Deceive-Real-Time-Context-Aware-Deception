import os
import chromadb

CHROMA_DIR = "/home/wasim/aigen_project/honey_chroma_db"

print("=== CHROMADB CORE ROOT INSPECTOR ===")
if not os.path.exists(CHROMA_DIR):
    print(f"[-] Database directory not found at {CHROMA_DIR}")
    print("[!] Run your main deception script first to generate the database.")
    exit(1)

client = chromadb.PersistentClient(path=CHROMA_DIR)

try:
    collection = client.get_collection(name="holographic_files")
    
    print(f"[+] Target Database Path : {os.path.abspath(CHROMA_DIR)}")
    print(f"[+] Collection Name      : {collection.name}")
    print(f"[+] Core Database Root ID: {collection.id}")
    print(f"[+] Total Active Records : {collection.count()}")
    print("====================================")
    
    if collection.count() > 0:
        data = collection.get()
        print("\n[ Active Decoy Mappings ]")
        for i, file_id in enumerate(data['ids']):
            metadata = data['metadatas'][i]
            print(f" -> File Name: {file_id} | Token ID: {metadata.get('token_id')}")

except Exception as e:
    print(f"[-] Error reading collection metadata: {e}")