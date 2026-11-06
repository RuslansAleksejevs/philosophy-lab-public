[Home](../README.md) · [Submitted edition](submitted-edition.md) · [Citing the work](citing.md)

# Keep a verifiable copy

The competition-facing edition is **submitted-2026-11-01**. Its six PDFs are frozen at the exact bytes downloaded from OpenReview. The public and private repositories retain different commit histories but the same content tree for this edition.

## Read offline

Download the repository at the desired commit, or keep the [submission ZIP](../submission/20261101/Submission-Package-E050-E012-E051.zip) for just the three essays, reports, abstracts, form templates and LaTeX sources. The wider repository contains all candidates and their history. OpenReview access is not required to read the local PDFs.

## Verify the edition

From the repository root, with Python 3.10 or newer:

```sh
python3 -B tools/verify_submission_edition.py
```

The verifier uses only the standard library. It checks the frozen file inventory, the six submitted hashes, all 107 candidate biographies, the package manifest, navigation, and preservation of every preceding file. It restores the previous edition in a temporary view and runs that edition's existing checks too. It does not access the network, call a model or change research files.

For a quick check of just the six PDFs:

```sh
cd submission/20261101
shasum -a 256 -c SHA256SUMS.txt
```

A checksum detects changes relative to the recorded value; it does not by itself establish trust in the record. Cite a Git commit with the edition so that a reader can retrieve the same snapshot.

## Rebuild a PDF without replacing the submission

Each [LaTeX project](../submission/20261101/latex) contains `main.tex` and `body.tex`. Compile with Tectonic or XeLaTeX to a separate output directory. Rebuilding may change PDF metadata, font subsets or compiler output even when the text is identical. The committed PDF—not a later rebuild—is the submitted byte sequence.

## Continue without overwriting history

Keep the submitted files fixed. Put any erratum, revised essay or competition outcome in a dated addition and name its predecessor. Preserve the original wording alongside any corrected account. Existing past reviews should remain attached to the version they actually assessed.

The log export has a fixed, documented cutoff. Local collection may continue; that does not mean later conversations are already included here. [Coverage and limits](provenance.md).
