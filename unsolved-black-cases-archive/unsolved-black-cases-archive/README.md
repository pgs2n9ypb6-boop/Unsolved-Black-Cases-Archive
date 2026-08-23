# Unsolved Black Cases Archive

A public-record research archive documenting unsolved cases involving Black victims.
Live site: https://unsolved-black-cases-archive-jet.vercel.app/

## How this site works

This is a fully static site — plain HTML, CSS, and JavaScript. There is no server
and no database. Every page in the repo is already the final, ready-to-serve file.

The entire site (all `.html` pages, `data/cases.json`, `js/cases-data.js`) is
**generated** from a single source of truth: `build.py`. That file contains the
`CASES` list — one Python dict per case — plus the templates for every page type
(dashboard, case board, document pages).

**Never hand-edit an `.html` file directly.** Any manual edit will be silently
overwritten the next time `build.py` runs. Always edit `build.py` (or hand new
case details to Claude to do it) and regenerate.

## Adding a new case

1. Add a new `dict(...)` entry to the `CASES` list in `build.py`, following the
   pattern of the existing entries — `caseNumber`, `name`, `status`, `year`,
   location fields, `summary`, `known` / `unknown` / `unanswered` lists, and
   `extraSources` with real, verified citation URLs only.
2. Set `dateAdded` to today's date if you want it featured on the homepage as
   the "Latest Case Added" — this is handled automatically per case in the
   post-processing loop near the top of the file; no other homepage edit is needed.
3. If you have a real, rights-cleared photo (e.g. an official FBI missing-persons
   or wanted listing, which is U.S. government work / public domain), add a
   `victimPhotos` list with `url`, `caption`, and `credit` — see the
   `diamond-and-tionda-bradley` or `alonzo-brooks` entries for the pattern.
   Never guess at or fabricate a photo source.
4. Run the build:
   ```
   python3 build.py
   ```
5. Commit and push (or upload the changed files via GitHub's web UI). If this
   repo is connected to Vercel, it redeploys automatically on push.

## Local preview

Just open `index.html` in a browser — no server needed. (Search, the case
timeline, and the map view all read from `js/cases-data.js`, which is loaded
via `<script src>`, so they work even opened directly from disk.)

## Content standards

See `research.html` on the live site for the full sourcing standards this
archive follows: public record only, no accusations without official basis,
every case traceable to a cited source, "NOT AVAILABLE IN CURRENT RECORD"
instead of guessing at missing facts.
