[Home](../README.md) · [Essay evidence](essay-evidence.md) · [Conversation catalogue](../logs/catalogue.json)

# Search the published archive

Search essays, original histories, method files, reviews and visible conversations with one command. The search reads published tar/gzip and ZIP contents directly; you do not need to unpack each bundle. It uses Python 3.10 or newer with SQLite FTS5, normally included in Python distributions.

Download the repository, open a terminal in its folder, then try:

```sh
python3 -B tools/search_archive.py "holding" --kind essay
python3 -B tools/search_archive.py "возражения" --kind conversation
python3 -B tools/search_archive.py "photographs" --essay E012
```

The first search builds a local index. Later searches reuse it; adding or changing a source file triggers a rebuild. The index is disposable and ignored by Git. No provider account, model call or network connection is used.

## Read a result

Each result shows a title, location and excerpt. For example:

```text
bundle.tar.gz::sessions/example.json#source-line-42
```

This identifies the bundle, member and original message line. To read the complete matching message or file:

```sh
python3 -B tools/search_archive.py "keep Summer safe" --phrase --full --limit 1
```

Searches match all supplied words. Use `--phrase` for their exact order, `--json` for structured results, and `--limit 20` for a longer list. `--kind` accepts `essay`, `guide`, `source`, `conversation` or `record`. The essay filter follows recorded file and conversation associations; shared or unassigned material may require a search without that filter.

## What is indexed

Published UTF-8 text files and text inside their archives are searchable. Byte-identical files and repeated message identities are indexed once, preferring ordinary reading copies over archive members. PDF images and other binary contents are not OCRed; manuscript text and LaTeX sources provide searchable versions of the submitted essays.

The [unified conversation catalogue](../logs/catalogue.json) lists each session and every retained fragment location. The [bundle inventory](../logs/archive-inventory.json) covers all current log bundles. Both preserve the separate dates and scopes of the earlier exports.

To rebuild manually, run `python3 -B tools/search_archive.py --rebuild --index-only`. To check the search tool in isolated fixtures, run `python3 -B -m unittest discover -s tools -p test_search_archive.py`.
