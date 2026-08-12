import time
import os
import uuid
import chromadb
import ollama
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HONEY_DIR = "/tmp/honey"
CHROMA_DIR = "/home/wasim/aigen_project/honey_chroma_db"
MODEL_NAME = "qwen2.5:1.5b"

os.makedirs(HONEY_DIR, exist_ok=True)
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="holographic_files")

def generate_and_save(file_path):
    file_name = os.path.basename(file_path)
    
    # Check if we already cached this token
    results = collection.get(ids=[file_name])
    if results and results['ids']:
        token_id = results['metadatas'][0]['token_id']
        fake_chroma_root_id = results['metadatas'][0].get('fake_root_id', str(uuid.uuid4()))
    else:
        token_id = f"canary_{file_name.split('.')[0]}_{uuid.uuid4().hex[:6]}"
        fake_chroma_root_id = str(uuid.uuid4())
        collection.add(
            ids=[file_name],
            metadatas=[{"token_id": token_id, "fake_root_id": fake_chroma_root_id}],
            documents=["holographic_bait"]
        )

    tracking_url = f"https://httpbin.org/get?token_id={token_id}&chroma_root_id={fake_chroma_root_id}"
    
    print(f"\n[!] Access Detected on {file_name}!")
    print(f"[*] Generating Decoy with Fake Root ID: {fake_chroma_root_id}")

    prompt = (
        f"Generate a short database config for {file_name}.\n"
        f"Include 'chroma_db_root_id': '{fake_chroma_root_id}'\n"
        f"Include 'telemetry_url': '{tracking_url}'\n"
        f"Return raw JSON only."
    )

    try:
        response = ollama.generate(
            model=MODEL_NAME,
            prompt=prompt,
            options={"temperature": 0.1, "num_predict": 150}
        )
        content = response['response'].strip()
        
        # Explicitly write the generated content back into the bait file
        with open(file_path, "w") as f:
            f.write(content + "\n")
            
        print("[+] Decoy file successfully written to disk!")
    except Exception as e:
        print(f"[-] Error during generation: {e}")

class HoneyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_triggered = 0

    def on_accessed(self, event):
        if not event.is_directory:
            # Debounce to prevent infinite loop triggers
            if time.time() - self.last_triggered > 2:
                self.last_triggered = time.time()
                generate_and_save(event.src_path)

if __name__ == "__main__":
    # Ensure a target file exists
    target_file = os.path.join(HONEY_DIR, "db_connection.str")
    if not os.path.exists(target_file):
        with open(target_file, "w") as f:
            f.write("# Pending connection initialization...\n")

    event_handler = HoneyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=HONEY_DIR, recursive=False)
    observer.start()
    
    print(f"=== DECEPTION DAEMON ACTIVE ON {HONEY_DIR} ===")
    print("[*] Waiting for attacker file access...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()