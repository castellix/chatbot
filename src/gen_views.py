"""Generate the ArchiMate views (PlantUML, stdlib convention) from the version 2 model."""
import json, os, sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)

CAP = {c["id"]: c for c in data["caps"]}
DEP = {d["id"]: d for d in data["deps"]}
CON = {k["id"]: k for k in data["cons"]}
L1 = {l["id"]: l for l in data["l1"]}
BANDS = data["bands"]

WP = {
    "D3": "Register the chatbot’s purposes and consents",
    "D4": "Include chatbot data in data subject requests",
    "D5": "Add the chat to communication recording",
    "D6": "Extend complaint management to the chat channel",
    "D7": "Accept vulnerability handovers from the chat",
    "D8": "Exchange scam patterns and signals with the chat",
    "D9": "Feed chat signals into market abuse surveillance",
    "D11": "Add the conversation as an order channel",
    "D13": "Bring AI providers under third-party risk management",
}
DRIVERS = [
    ("drvMifid", "MiFID II", ["MiFID II", "2017/565"]),
    ("drvAiAct", "EU AI Act", ["AI Act"]),
    ("drvGdpr", "GDPR", ["GDPR"]),
    ("drvPsd2", "PSD2", ["PSD2"]),
    ("drvCredit", "Consumer and mortgage credit rules", ["Consumer Credit", "Mortgage Credit", "Belgian Code"]),
    ("drvMar", "Market Abuse Regulation", ["Market Abuse"]),
    ("drvPriips", "PRIIPs Regulation", ["PRIIPs"]),
    ("drvSfdr", "SFDR and ESMA fund-name guidelines", ["Sustainable Finance", "fund names"]),
    ("drvComplaints", "ESMA and EBA complaints guidelines", ["complaints handling"]),
    ("drvPolicy", "Bank policy", ["policy"]),
]
# Requirement = an obligation to do something; Constraint = a restriction on the solution
REQUIREMENTS = {"C1", "C7", "C8", "C12", "C13", "C15", "C17", "C18"}


def ca(cid):
    return "cap" + cid.replace(".", "_")


def short(s):
    return s.replace('"', "'")


def drivers_of(k):
    out = []
    for alias, name, keys in DRIVERS:
        if any(key.lower() in src.lower() for src in k["sources"] for key in keys):
            out.append(alias)
    return out


def header(title, lr=False):
    h = ["@startuml", "!include <archimate/Archimate>", f"title {title}"]
    if lr:
        h.append("left to right direction")
    return h


views = []

# ---------------------------------------------------------------- 1 capability map
L = header("AI chatbot capability model – capability map")
L.append("' Nesting means composition: Level 2 inside Level 1, Level 3 inside Level 2.")
top, bottom = {}, {}
for b in BANDS:
    L.append("")
    L.append(f'Grouping(grp_{b["key"]}, "{b["name"]}") {{')
    for n in reversed(b["l1"]):  # PlantUML places sibling containers right to left
        L.append(f'  Strategy_Capability(cap{n}, "{n} {short(L1[n]["name"])}") {{')
        caps = [c for c in data["caps"] if c["l1"] == n]
        for c in caps:
            if c["l3"]:
                L.append(f'    Strategy_Capability({ca(c["id"])}, "{c["id"]} {short(c["name"])}") {{')
                for i, r in enumerate(c["l3"], 1):
                    L.append(f'      Strategy_Capability({ca(c["id"])}_{i}, "{short(r[0])}")')
                L.append("    }")
            else:
                L.append(f'    Strategy_Capability({ca(c["id"])}, "{c["id"]} {short(c["name"])}")')
        L.append("  }")
    L.append("}")
lay = []
for n in L1:
    caps = [c for c in data["caps"] if c["l1"] == n]
    nodes = []
    for c in caps:
        if c["l3"]:
            kids = [f'{ca(c["id"])}_{i}' for i in range(1, len(c["l3"]) + 1)]
            for x, y in zip(kids, kids[1:]):
                lay.append(f"Lay_D({x}, {y})")
            nodes.append((kids[0], kids[-1]))
        else:
            nodes.append((ca(c["id"]), ca(c["id"])))
    for (t1, b1), (t2, b2) in zip(nodes, nodes[1:]):
        lay.append(f"Lay_D({b1}, {t2})")
    top[n], bottom[n] = nodes[0][0], nodes[-1][1]
depth = {n: sum(len(c["l3"]) or 1 for c in data["caps"] if c["l1"] == n) for n in L1}
for b1, b2 in zip(BANDS, BANDS[1:]):
    deepest = max(b1["l1"], key=lambda n: depth[n])
    for n in b2["l1"]:
        lay.append(f"Lay_D({bottom[deepest]}, {top[n]})")
L.append("")
L.append("' layout only")
L += lay
L.append("@enduml")
views.append(("01-capability-map", "Capability map", "Level 1, Level 2 and Level 3 capabilities, nested to show composition.", L))

# ---------------------------------------------------------------- 2 dependencies
L = header("AI chatbot capability model – enterprise dependencies", lr=True)
L.append("' Serving: the enterprise capability serves the chatbot capability that needs it.")
L.append("' Extends: the enterprise capability must change; the work package carries that change.")
ext = [d for d in data["deps"] if d["relation"] == "extends"]
use = [d for d in data["deps"] if d["relation"] == "uses"]
needed = sorted({c for d in data["deps"] for c in d["usedBy"]}, key=lambda s: [int(x) for x in s.split(".")])
L.append("")
L.append('Grouping(grpWork, "Changes to enterprise capabilities") {')
for d in ext:
    L.append(f'  Implementation_WorkPackage(wp{d["id"]}, "{short(WP[d["id"]])}")')
L.append("}")
L.append('Grouping(grpExtended, "Enterprise capabilities the chatbot extends") {')
for d in ext:
    L.append(f'  Strategy_Capability({d["id"].lower()}, "{d["id"]} {short(d["name"])}")')
L.append("}")
L.append('Grouping(grpUsed, "Enterprise capabilities the chatbot uses") {')
for d in use:
    L.append(f'  Strategy_Capability({d["id"].lower()}, "{d["id"]} {short(d["name"])}")')
L.append("}")
L.append('Grouping(grpChatbot, "AI chatbot capabilities") {')
for c in needed:
    L.append(f'  Strategy_Capability({ca(c)}, "{c} {short(CAP[c]["name"])}")')
L.append("}")
L.append("")
for d in ext:
    L.append(f'Rel_Association(wp{d["id"]}, {d["id"].lower()}, "changes")')
for d in data["deps"]:
    label = d["relation"] + (", agentic" if d["agentic"] else "")
    for c in d["usedBy"]:
        L.append(f'Rel_Serving({d["id"].lower()}, {ca(c)}, "{label}")')
L.append("@enduml")
views.append(("02-enterprise-dependencies", "Enterprise dependencies", "Enterprise capabilities serving the chatbot capabilities that need them, with a work package for each one that must be extended.", L))


# ---------------------------------------------------------------- 3 drivers and rules
def rule_macro(k):
    return "Motivation_Requirement" if k["id"] in REQUIREMENTS else "Motivation_Constraint"


L = header("AI chatbot capability model – drivers and rules", lr=True)
L.append("' Drivers influence the rules. Requirements oblige the chatbot to do something;")
L.append("' constraints restrict what it may do.")
L.append("")
L.append('Grouping(grpDrivers, "Drivers") {')
used = [d for d in DRIVERS if any(d[0] in drivers_of(k) for k in data["cons"])]
for alias, name, _ in used:
    L.append(f'  Motivation_Driver({alias}, "{name}")')
L.append("}")
L.append('Grouping(grpRules, "Requirements and constraints") {')
for k in data["cons"]:
    L.append(f'  {rule_macro(k)}({k["id"].lower()}, "{k["id"]} {short(k["title"])}")')
L.append("}")
L.append("")
for k in data["cons"]:
    for alias in drivers_of(k):
        L.append(f"Rel_Influence({alias}, {k['id'].lower()})")
L.append("@enduml")
views.append(("03-drivers-and-rules", "Drivers and rules", "Every requirement and constraint, traced to the regulation or policy that drives it.", L))


# ---------------------------------------------------------------- 4-6 realisation of the rules
def constraint_view(key, title, desc, ids):
    cons = [CON[i] for i in ids]
    caps = sorted({c for k in cons for c in k["enforcedBy"]}, key=lambda s: [int(x) for x in s.split(".")])
    deps = sorted({d for k in cons for d in k["dependsOn"]}, key=lambda s: int(s[1:]))
    L = header(f"AI chatbot capability model – {title[0].lower() + title[1:]}", lr=True)
    L.append("' Capabilities realise the rules. A rule that relies on an enterprise capability")
    L.append("' is realised by the chatbot and that enterprise capability together.")
    L.append("")
    L.append('Grouping(grpChatbot, "AI chatbot capabilities") {')
    for c in caps:
        L.append(f'  Strategy_Capability({ca(c)}, "{c} {short(CAP[c]["name"])}")')
    L.append("}")
    L.append(f'Grouping(grpRules, "{title}") {{')
    for k in cons:
        L.append(f'  {rule_macro(k)}({k["id"].lower()}, "{k["id"]} {short(k["title"])}")')
    L.append("}")
    if deps:
        L.append('Grouping(grpEnterprise, "Enterprise capabilities") {')
        for d in deps:
            L.append(f'  Strategy_Capability({d.lower()}, "{d} {short(DEP[d]["name"])}")')
        L.append("}")
    L.append("")
    for k in cons:
        for c in k["enforcedBy"]:
            L.append(f"Rel_Realization({ca(c)}, {k['id'].lower()})")
    for k in cons:
        for d in k["dependsOn"]:
            L.append(f"Rel_Realization({d.lower()}, {k['id'].lower()})")
    L.append("@enduml")
    views.append((key, title, desc, L))


constraint_view("04-rules-bank-wide-credit-payments", "Bank-wide, credit and payment rules",
                "Which capabilities realise the bank-wide rules and the credit and daily banking rules.",
                [k["id"] for k in data["cons"] if not k["domains"] or "credit" in k["domains"] or "payments" in k["domains"]])
constraint_view("05-rules-investment-conduct", "Investment conduct rules",
                "Which capabilities realise the rules on advice, initiative and steering for execution-only investments.",
                ["C2", "C3", "C4", "C15", "C16", "C19", "C20", "C21"])
constraint_view("06-rules-investment-information", "Investment information and record rules",
                "Which capabilities realise the rules on instrument scope, information, records and market abuse.",
                ["C11", "C12", "C14", "C17", "C18", "C23"])

meta = []
for key, title, desc, lines in views:
    open(os.path.join(outdir, f"{key}.puml"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    meta.append({"key": key, "title": title, "desc": desc})
json.dump(meta, open(os.path.join(outdir, "views.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for key, title, desc, lines in views:
    print(key, len(lines), "lines")
