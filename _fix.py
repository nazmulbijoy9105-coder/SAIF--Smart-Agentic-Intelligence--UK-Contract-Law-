import base64
with open("backend/app/ilrmf/engine.py","wb") as f: f.write(base64.b64decode(open("_engine.b64").read()))
with open("frontend/app/result/page.tsx","wb") as f: f.write(base64.b64decode(open("_result.b64").read()))
print("Done")
