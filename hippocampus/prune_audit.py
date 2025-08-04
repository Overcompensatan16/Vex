import json

def write_audit_entry():
    audit_path = r"E:\AI_Audit\MemoryLogs\prune_audit.jsonl"
    audit_entry = {"fact": "test", "score": 1.0}
    with open(audit_path, "a") as f:
        f.write(json.dumps(audit_entry) + "\n")
    print(f"✅ Successfully wrote to {audit_path}")

# Call the function
write_audit_entry()



