[Home](../README.md) · [Essay evidence](../docs/essay-evidence.md) · [Search](../docs/archive-search.md)

# Original laboratory sources

This dated source collection supplies the files behind the essays and the programs used to run the lab. The [manifest](MANIFEST.json) binds every file to its original path and SHA-256 fingerprint. Files retain their exact bytes, including original Russian, historical instructions and past status statements.

| Material | Read |
| --- | --- |
| Histories, questions, criticism and author responses | [Routes for all 107 essays](../docs/essay-evidence.md) |
| Twenty original method files | [Methods](methods) |
| Six workflow documents | [Workflows](workflows) |
| Collector, provider bridges and research programs | [47 source files](scripts) |
| Original test suite | [46 test files](tests) |
| Schemas and task templates | [Schemas](schemas) · [Templates](templates) |
| Later completion receipts | [Dated run records](runs) |

## Read and reuse the code

The Python files, templates, tests, example configuration and original Makefile are preserved for inspection. They describe the actual local system, including its dependencies on provider state, the canonical archive and machine-specific paths. They are not a self-contained installation of the original runtime. Live configuration and provider databases are not included.

Start with [the example configuration](collector/config.example.json), [archive event schema](schemas/archive_event.schema.json), [collector](scripts/collector.py), [source parser](scripts/collector_source.py) and [round coordinator](scripts/philosophy_round.py). Reading or searching this collection does not start a collector or call a model. The independent [archive search](../docs/archive-search.md) and edition verifier run without the old runtime.

## Read the historical instructions as evidence

Assignments and workflow files record what a particular author, critic or coordinator was told. Their old instructions and statuses do not change the present submission edition. The submitted manuscripts and PDFs remain fixed.

The import includes 97 previously unexported history files for 88 essays, with additional histories and research artifacts where the recorded biographies identify them. It also preserves eight earlier completion or planning records. Some content had already appeared inside conversations; these files make its original form directly accessible.

Raw third-party downloads, native provider envelopes, live credentials and the deliberately excluded retrospective dossier retain their earlier local boundaries. [Publication policy](../PUBLICATION.md) · [Coverage](../docs/provenance.md).
