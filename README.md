# AI Chatbot Capability Model

A business capability model for a bank-wide AI chatbot covering daily banking, credit and execution-only investments. Version 2.2.

Open [`ai-chatbot-capability-model.html`](ai-chatbot-capability-model.html) in a browser. It is a single self-contained file with no external dependencies.

## What the model separates

| Layer | Count | What it is |
|---|---|---|
| Capabilities | 34 (8 Level 1) | What the chatbot itself must be able to do. Each has an owner and a maturity. |
| Enterprise dependencies | 16 | Capabilities the bank already has for every channel. The chatbot uses them as they are or needs them extended. |
| Constraints | 23 | Rules the chatbot complies with or not, each with a source, the capabilities that enforce it, and how to check it. |
| From version 1 | 60 rows | Where each capability of the first map went. |

## ArchiMate views

PlantUML, standard ArchiMate library (`!include <archimate/Archimate>`), rendered with PlantUML 1.2026.9. The SVG next to each `.puml` file is its rendering.

| File | View |
|---|---|
| [`views/01-capability-map.puml`](views/01-capability-map.puml) | Level 1, 2 and 3 capabilities, nested to show composition |
| [`views/02-enterprise-dependencies.puml`](views/02-enterprise-dependencies.puml) | Enterprise capabilities serving chatbot capabilities (uses or extends), with a work package for each extension |
| [`views/03-drivers-and-rules.puml`](views/03-drivers-and-rules.puml) | Requirements and constraints traced to the regulation or policy that drives them |
| [`views/04-rules-bank-wide-credit-payments.puml`](views/04-rules-bank-wide-credit-payments.puml) | Realisation of the bank-wide, credit and payment rules |
| [`views/05-rules-investment-conduct.puml`](views/05-rules-investment-conduct.puml) | Realisation of the investment conduct rules |
| [`views/06-rules-investment-information.puml`](views/06-rules-investment-information.puml) | Realisation of the investment information and record rules |

Conventions: nesting is composition; serving runs from the enterprise capability to the chatbot capability that needs it; capabilities realise rules; drivers influence rules; a work package is associated with the enterprise capability it changes.

## Rebuilding

The model data lives in [`src/v2data.json`](src/v2data.json).

```sh
python3 src/gen_views.py src/v2data.json views     # regenerate the .puml views
# render each views/*.puml to SVG with PlantUML 1.2026.9 or later (nested archimate elements need a recent version)
python3 src/build_page.py                          # rebuild ai-chatbot-capability-model.html
```
