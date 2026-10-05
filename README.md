# readpath-beta-texts

Texts for Read Path beta testers. The app fetches them from a link
(`https://leecommamark.github.io/readpath-beta-texts/`); nothing here is the app.

## Format

* One folder per bundle, named by theme: lowercase a-z, 0-9 and hyphens, up to
  40 characters (`everyday/`, `food/`). Other folders and root files are ignored.
* Each text is a `.txt` file directly in the folder: UTF-8, a short Chinese
  title on line 1, a blank line, then the body. Under 20,000 characters.
  Files are listed in filename order (`01-...`, `02-...`).
* Optional `bundle.md`: display name on line 1, one-line description on line 2.
* Optional `SOURCES.md`: where the texts came from (needed for CC texts).

Then run `python3 make_index.py`, then commit and push. The script checks every
text (valid UTF-8, has Chinese, within the length limit), warns about
duplicates, long titles and a non-blank line 2, writes each `<bundle>/index.json`
and `.nojekyll`. If anything fails it writes nothing.

## Links for testers

`https://leecommamark.github.io/readpath/?texts=<folder>`

On an iPhone, links open Safari, not the home-screen app. So testers copy the
link and use **Get texts from a link** in the app (it has a Paste button), or
just type the folder name.

## Rights

Own writing, public domain, or Creative Commons texts with attribution in the
bundle's `SOURCES.md`. No song lyrics or modern published texts. This repo is public.

## No pages

No `.html`, `.htm`, `.js`, `.mjs`, `.svg` or `.xml` files: this site shares an
origin with Read Path, which keeps testers' saved progress in that origin's
storage. The script refuses them.

## Known limit

An edited text comes in as a second copy for a tester who already has it; they
delete the old one.
