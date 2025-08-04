import glob
import os

for p in glob.glob("**/E:/AI_Memory_Stores/**/*.jsonl", recursive=True):
    print(os.path.abspath(p))
