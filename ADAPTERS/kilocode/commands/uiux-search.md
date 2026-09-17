---
description: Search the UIUX ENGINE reference library for a concept and return the token-efficient context pack.
---
# UIUX Reference Search

Search the local reference index for: $ARGUMENTS

Steps:

1. Locate the engine root (`UIUX_ENGINE_HOME` env var or ask; default
   `C:\Users\SRS\Desktop\UIUX_ENGINE` on this machine — verify it exists).
2. Run the search (do NOT read the index JSON files into context):

   `uiux search "<arguments>" --context-pack -n 8`
   (or `python -m uiux search ... ` with PYTHONPATH=<engine>\CLI if no shim)

3. Read the returned JSON. It contains generated names, ui_category,
   layout, style, motion, palette hexes, and matched patterns — nothing
   else is authorized context.
4. If the index is empty, tell the user to run `uiux ingest` and stop.
5. Summarize the 3 most relevant references as PRINCIPLES (what they solve
   and how), never as instructions to copy a design. Cite generated names.

Do not open image/video files. Do not read INDEX/*.json. Do not load more
knowledge cards than the orchestrator routes to.
