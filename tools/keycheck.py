"""Check .env has the 4 X keys. Prints names and lengths only, never the values.

Exit code 1 if any key is missing, so the workflow stops with a clear message.
"""
import sys
from pathlib import Path

NEEDED = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
env = Path(__file__).resolve().parent.parent / ".env"
text = env.read_text() if env.exists() else ""
found = {}
for n, line in enumerate(text.splitlines(), 1):
    line = line.strip().replace("\r", "")
    if not line or line.startswith("#"):
        continue
    if "=" not in line:
        print(f"line {n}: no '=' sign ({len(line)} characters)")
        continue
    name, value = line.split("=", 1)
    found[name.strip()] = value.strip()
    print(f"line {n}: {name.strip()} = <{len(value.strip())} characters>")
print(f".env has {len(text.splitlines())} lines, {len(text)} characters")
missing = [k for k in NEEDED if not found.get(k)]
if missing:
    print("MISSING:", ", ".join(missing))
    sys.exit(1)
print("All 4 X keys present.")
