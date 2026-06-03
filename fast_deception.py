import os
import sys
import json
import time
import uuid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import ollama
import chromadb

HONEY_DIR = "/tmp/honey"
CHROMA_DIR = "./honey_chroma_db"
CANARY_WEBHOOK_BASE = "http://httpbin.org/get?token_id="
MODEL_NAME = "qwen2.5:1.5b"

print("[*] Phase 1: Initializing local persistent Vector DB (ChromaDB)...")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="holographic_files")

print(f"[*] Phase 2: Verifying connection to local Ollama '{MODEL_NAME}' engine...")
try:
    # Quick low-overhead handshake test to make sure model responds natively
    ollama.generate(model=MODEL_NAME, prompt="ping")
except Exception as e:
    print(f"[-] Native Ollama connection failed: {e}.\n[!] Ensure 'ollama serve' is active.")
    sys.exit(1)


def generate_holographic_content(file_path: str, tracking_url: str) -> str:
    """Uses native, direct streaming ollama API for zero-lag text output."""
    file_name = os.path.basename(file_path)
    
    prompt = (
        f"Generate a realistic production configuration dataset for a file named '{file_name}'.\n"
        f"You MUST include an active parameter line setting the remote endpoint, database URL, "
        f"or service URL to exactly this string: '{tracking_url}'.\n"
        f"Output ONLY raw text configuration. Do not write markdown blocks or explanations."
    )
    
    # We use ollama.generate but with stream=True
    stream = ollama.generate(
        model=MODEL_NAME, 
        prompt=prompt,
        stream=True,
        options={
            "temperature": 0.1,
            "num_predict": 150
        }
    )
    
    full_response = ""
    print("[*] Streaming tokens from local LLM matrix: ", end="", flush=True)
    for chunk in stream:
        token = chunk['response']
        print(token, end="", flush=True)  # This will print the text token-by-token on your screen instantly
        full_response += token
        
    print() # New line after stream ends
    return full_response.strip()

class FastDeceptionHandler(FileSystemEventHandler):
    def __init__(self):
        self.active_baits = ["aws_config.env", "kubeconfig.yaml", "shadow_passwords.bak", "db_connection.str"]

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type in ['modified', 'opened', 'accessed']:
            self.process_deception(event.src_path)

    def process_deception(self, file_path):
        file_name = os.path.basename(file_path)
        if file_name not in self.active_baits:
            return

        # Consistency Cache Check
        existing_record = collection.get(ids=[file_name])
        if existing_record and existing_record['documents']:
            if os.path.exists(file_path) and os.path.getsize(file_path) < 30:
                cached_payload = existing_record['documents'][0]
                with open(file_path, "w") as f:
                    f.write(cached_payload)
                print(f"[+] CACHE HIT: Restored consistent data for '{file_name}' from ChromaDB.")
            return

        # First-time access tracking generation
        print(f"\n[!] ALERT: Intrusion detected on path: {file_path}")
        print(f"[*] Manufacturing unique Honey-Token tracker...")
        
        token_id = f"canary_{file_name.split('.')[0]}_{uuid.uuid4().hex[:6]}"
        tracking_url = f"{CANARY_WEBHOOK_BASE}{token_id}"
        
        print(f"[*] Simulating real-time data payload via Native Qwen Client...")
        decoy_payload = generate_holographic_content(file_path, tracking_url)
        
        # Strip code formatting if the model slips up
        if decoy_payload.startswith("```"):
            decoy_payload = "\n".join(decoy_payload.split("\n")[1:-1])

        # Commit to databases
        collection.add(
            documents=[decoy_payload],
            metadatas=[{"file_path": file_path, "token_id": token_id}],
            ids=[file_name]
        )
        
        with open(file_path, "w") as f:
            f.write(decoy_payload)
            
        print("\n--- HOLOGRAPHIC DECOY DEPLOYED ---")
        print(decoy_payload)
        print("----------------------------------")

if __name__ == "__main__":
    os.makedirs(HONEY_DIR, exist_ok=True)
    
    # Refresh empty targets
    for bait in ["aws_config.env", "kubeconfig.yaml", "shadow_passwords.bak", "db_connection.str"]:
        with open(os.path.join(HONEY_DIR, bait), "w") as f:
            f.write("# Trapped resource node\n")

    event_handler = FastDeceptionHandler()
    observer = Observer()
    observer.schedule(event_handler, path=HONEY_DIR, recursive=False)
    
    print(f"\n[+] SUCCESS: Direct-Inference Deception System Operational!")
    print(f"[*] Actively monitoring: {HONEY_DIR}/*")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
