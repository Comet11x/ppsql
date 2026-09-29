# ppsql

`ppsql` is a preprocessor for SQL files. It expands variables, inlines included files
and strips comments before the result is handed over to a database client.

-----

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Directives](#directives)
- [Python API](#python-api)
- [Development](#development)
- [License](#license)

## Installation

```console
pip install ppsql
```

## Usage

```console
ppsql -i path/to/main.sql -o path/to/out.sql
```

| Option              | Description                                    | Default       |
| ------------------- | ---------------------------------------------- | ------------- |
| `-i`, `--input`     | entry point of the build (required)            | -             |
| `-s`, `--source`    | source directory                               | current dir   |
| `-o`, `--out`       | output file                                    | `./out.sql`   |
| `-e`, `--env`       | file or directory holding a `.env` file        | current dir   |
| `-c`, `--credential`| directory holding a `.password` file           | home dir      |
| `-d`, `--debug`     | verbose logging                                | off           |

The module can also be executed directly:

```console
python -m ppsql -i path/to/main.sql -o path/to/out.sql
```

## Directives

Every directive is written on its own line and is removed from the output.

| Directive              | Description                                     |
| ---------------------- | ----------------------------------------------- |
| `@set name = value`    | sets a variable in the scope of the file         |
| `@set global name = v` | sets a variable in the global scope              |
| `@unset name =`        | removes a variable                               |
| `@include path`        | inlines a file, or `index.sql` of a directory    |

A variable is referenced as `$name` or, when the name touches other characters,
as `${name}`. Write `\$name` to keep a dollar sign as it is. Values are looked up in
the scope of the file, then in the global scope, which is initialised from the
environment and extended by `--env` and `--credential` files.

```sql
@set table = users

@include queries/columns.sql

select * from ${table};
```

```console
$ ppsql -i main.sql -o out.sql && cat out.sql
select id, name from users;
select * from users;
```

## Python API

```python
from ppsql import Builder

sql = Builder(entry="main.sql", variables={"table": "users"}).build()
```

| Object                  | Responsibility                                |
| ----------------------- | --------------------------------------------- |
| `Builder`               | builds an entry point, resolves includes       |
| `Context` / `Line`      | the content of a file and a cursor over it     |
| `VariableScope`         | local and global variables                     |
| `Loader`                | reads a file and creates a `Context`           |
| `Writer`                | writes the result into a file                  |
| `actions`               | the directive handlers and the `Action` protocol|
| `cli`                   | argument reader, `load_env`, `load_password`   |

## Development

The project is managed by [hatch](https://hatch.pypa.io/latest/):

```console
hatch run test          # run the test suite
hatch run test-cov      # run the test suite with coverage
hatch run lint:check    # check formatting and lint rules
hatch run lint:fix      # fix formatting and lint rules
hatch run types:check   # run mypy
hatch build             # build the sdist and the wheel
```

## License

`ppsql` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
