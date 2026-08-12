import os
import sys
import time
import uuid
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import chromadb

# Configuration Constants
HONEY_DIR = "/tmp/honey"
CHROMA_DIR = "./honey_chroma_db"
CANARY_WEBHOOK_BASE = "http://httpbin.org/get?token_id="

print("[*] Phase 1: Initializing local persistent Vector DB (ChromaDB)...")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name="holographic_files")

print("[*] Phase 2: Connecting to local Ollama 'qwen2.5:1.5b' engine...")
try:
    llm = OllamaLLM(model="qwen2.5:1.5b", temperature=0.1)
except Exception as e:
    print(f"[-] AI Initialization failed: {e}.\n[!] Fix: Run 'ollama run qwen2.5:1.5b' in another terminal.")
    sys.exit(1)

def generate_holographic_content(file_path: str, tracking_url: str) -> str:
    """Invokes the local LLM to generate bespoke fake data with embedded tokens."""
    file_name = os.path.basename(file_path)
    
    system_instruction = (
        "You are an automated Linux system simulation daemon. Your job is to output "
        "the exact raw text content of a requested production configuration file. "
        "Do not include any conversational text, introductions, markdown code block backticks (```), "
        "or explanations. Output ONLY valid, raw, realistic configuration data."
    )
    
    human_instruction = (
        f"The system detected an unauthorized read on file name: '{file_name}'.\n"
        f"Generate realistic, high-fidelity, syntactically perfect but completely FAKE file contents "
        f"matching what an attacker looking at a file named '{file_name}' would expect to find.\n"
        f"CRITICAL REQUIREMENT: You MUST naturally embed the following backend configuration URL "
        f"somewhere highly realistic inside the file (e.g., as a service_url, remote_endpoint, or base_url): "
        f"'{tracking_url}'"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", human_instruction)
    ])
    
    chain = prompt | llm
    return chain.invoke({}).strip()

class EnterpriseDeceptionHandler(FileSystemEventHandler):
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

        # Check ChromaDB for narrative consistency
        existing_record = collection.get(ids=[file_name])
        
        if existing_record and existing_record['documents']:
            # If the file was cleared out or truncated, restore it from cache
            if os.path.exists(file_path) and os.path.getsize(file_path) < 30:
                cached_payload = existing_record['documents'][0]
                with open(file_path, "w") as f:
                    f.write(cached_payload)
                print(f"[+] CACHE HIT: Restored identical consistent data for '{file_name}' from ChromaDB.")
            return

        # First-time access: Trigger LLM generation & Canary mapping
        print(f"\n[!] ALERT: Intrusion detected on bait path: {file_path}")
        print(f"[*] Manufacturing unique Honey-Token tracker...")
        
        token_id = f"canary_{file_name.split('.')[0]}_{uuid.uuid4().hex[:6]}"
        tracking_url = f"{CANARY_WEBHOOK_BASE}{token_id}"
        
        print(f"[*] Simulating real-time data payload via Qwen...")
        decoy_payload = generate_holographic_content(file_path, tracking_url)
        
        # Clean up code blocks if the LLM includes them
        if decoy_payload.startswith("```"):
            decoy_payload = "\n".join(decoy_payload.split("\n")[1:-1])

        # Commit to Vector Storage and Write to Disk
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
    
    # Initialize the canary targets on disk with a minimal tracking string
    baits = ["aws_config.env", "kubeconfig.yaml", "shadow_passwords.bak", "db_connection.str"]
    for bait in baits:
        path = os.path.join(HONEY_DIR, bait)
        with open(path, "w") as f:
            f.write("# Trapped resource node\n")

    event_handler = EnterpriseDeceptionHandler()
    observer = Observer()
    observer.schedule(event_handler, path=HONEY_DIR, recursive=False)
    
    print(f"\n[+] SUCCESS: Generative Deception Framework is fully operational!")
    print(f"[*] Actively monitoring: {HONEY_DIR}/*")
    print("[*] Press Ctrl+C to terminate system.")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[-] Deception framework safely shut down.")
    observer.join()
