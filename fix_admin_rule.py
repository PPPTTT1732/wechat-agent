import re

with open("apps/api/routers/auth.py", "r", encoding="utf-8") as f:
    content = f.read()

# On remplace la règle pour enlever Marie et se baser uniquement sur Malick
old_rule = 'default_role = "ADMIN" if "marie" in req.email.lower() or "malick" in req.email.lower() else "USER"'
new_rule = 'default_role = "ADMIN" if "malickteuw.devweb@gmail.com" in req.email.lower() else "USER"'

content = content.replace(old_rule, new_rule)

with open("apps/api/routers/auth.py", "w", encoding="utf-8") as f:
    f.write(content)
