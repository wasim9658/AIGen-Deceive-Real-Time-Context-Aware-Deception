import os
import chromadb

CHROMA_DIR = "/home/wasim/aigen_project/honey_chroma_db"

print("=== DECEPTION SYSTEM ACTIVE TOKEN LOGS ===")
if not os.path.exists(CHROMA_DIR):
    print("[-] No active database found. Trigger a bait file first!")
    exit(1)

client = chromadb.PersistentClient(path=CHROMA_DIR)

try:
    collection = client.get_collection(name="holographic_files")
    results = collection.get()
    
    if not results['ids']:
        print("[!] Database is initialized but no honey-tokens have been generated yet.")
    else:
        print(f"[+] Total Tracked Bait Files: {len(results['ids'])}\n")
        print(f"{'BAIT FILE':<25} | {'GENERATED CANARY TOKEN ID'}")
        print("-" * 60)
        
        for i in range(len(results['ids'])):
            file_name = results['ids'][i]
            # Extract the custom token metadata your script attached
            metadata = results['metadatas'][i]
            token_id = metadata.get('token_id', 'No Token Found')
            
            print(f"{file_name:<25} | {token_id}")
            
except Exception as e:
    print(f"[-] Database Error: {e}")