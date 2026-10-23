"""Build the version 2 page: model data plus the ArchiMate views (PlantUML source and SVG)."""
import base64, json, os

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)
data = json.load(open(os.path.join(here, "v2data.json"), encoding="utf-8"))
meta = json.load(open(os.path.join(root, "views", "views.json"), encoding="utf-8"))
data["views"] = []
for v in meta:
    base = os.path.join(root, "views", v["key"])
    puml = open(base + ".puml", encoding="utf-8").read()
    svg = open(base + ".svg", "rb").read()
    data["views"].append({**v, "puml": puml, "svg": base64.b64encode(svg).decode("ascii")})

tpl = open(os.path.join(here, "template.html"), encoding="utf-8").read()
js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
assert tpl.count("/*__DATA__*/null") == 1
out = tpl.replace("/*__DATA__*/null", js)
open(os.path.join(root, "ai-chatbot-capability-model.html"), "w", encoding="utf-8").write(out)
print("bytes", len(out.encode("utf-8")), "views", len(data["views"]))
