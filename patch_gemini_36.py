import re
with open("apps/api/routers/memory.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("gemini-flash-latest", "gemini-3.6-flash")

with open("apps/api/routers/memory.py", "w", encoding="utf-8") as f:
    f.write(content)
