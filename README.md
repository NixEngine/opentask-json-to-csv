# JSON array to CSV

A dependency-free Python 3.10+ command-line script that reads a UTF-8 JSON file containing an array of flat objects and writes UTF-8 CSV.

## Usage

```sh
python json_to_csv.py input.json output.csv
```

Example input:

```json
[
  {"name": "Ana", "age": 20},
  {"name": "Luís", "city": "Belo Horizonte"}
]
```

Output:

```csv
name,age,city
Ana,20,
Luís,,Belo Horizonte
```

The header contains the union of all object keys, in the order each key first appears. Missing keys and JSON `null` become empty fields. Booleans use `true`/`false`; numbers remain numbers represented as text. The standard-library CSV writer handles commas, quotes, embedded line breaks and Unicode without changing string contents. UTF-8 input with or without a BOM is accepted.

Input must be an array of flat objects. Nested objects/arrays, non-object rows and malformed JSON produce a clear error and exit status 1. An empty array, or records with no fields, produces an empty CSV because there is no header to infer. Input is read and validated before the output is opened; invalid input leaves an existing output untouched. Successful conversion overwrites the named output. Input and output cannot name the same file. The script reads the array into memory, so input must fit in available RAM.

## Tests

Only the tests require a third-party dependency:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover missing keys, the combined header, Unicode/BOM input, quotes and line breaks, nulls, booleans, empty input, invalid/nested records, CLI exit status and preserving an existing output on input errors.

## Scope and provenance

Prepared by Zero Px Core with AI assistance under Júnior's authorization as an implementation sample for [OpenTask's JSON-to-CSV task](https://opentask.ai/tasks/cmpupoqmm0027kw04351wcfhz). The task uses a hire-first process. Publication of this sample does not assert hiring, acceptance or payment. No buyer data, wallet credentials or marketplace secrets are included.

