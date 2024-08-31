# Contributing

Thank you for your interest in contributing to _nigeria_geodata_. If you're a developer, you can skip to the [development](#development) section.

## General

If you're not a developer or you don't have the time to contribute, here are other easy ways to support the project:

- Star the project.
- Tweet about it or promote it on social media.
- Use it in your project.
- Mention the project at your organization, conference, articles, or tell your friends/colleagues about it.

## Development

### Clone the project

```bash
   # clone the repo
   git clone https://github.com/jeafreezy/nigeria_geodata.git

   # enter the project directory
   cd nigeria_geodata
```

### Python

This project is developed with **Python 3.8.1** and uses [Poetry](https://python-poetry.org/) to manage Python dependencies.

After cloning the project and installing Poetry, run:

```bash
   poetry install
```

to install all dependencies.

### Pre-commit

This repo is set to use pre-commit to run the following hooks: check-yaml, end-of-file-fixer, trailing-whitespace, [Ruff](https://docs.astral.sh/ruff/) ("An extremely fast Python linter and code formatter, written in Rust.") when committing new code.

Run:

```bash
   pre-commit install
```
to install the pre-commit hooks.

In case you run into errors, it is likely that you haven't installed the dev dependencies. In this case, you can run the command below to install them, then you can retry the command above again.

```bash
   poetry install --with dev
```

### Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/) for testing. Run the command below to run the tests:

```python
   pytest
```


In case you run into errors, it is likely that you haven't installed the dev dependencies. In this case, you can run the command below to install them, then you can retry the command above again.

```bash
   poetry install --with dev
```

### Documentation

The documentation website is generated with [mkdocs-material](https://squidfunk.github.io/mkdocs-material/). After poetry install, you can serve the docs website locally with:

```bash
   poetry run mkdocs serve
```

In case you run into errors, it is likely that you haven't installed the docs dependencies. In this case, you can run the command below to install them, then you can retry the command above again.

```bash
   poetry install --with docs
```

### CI-CD & Publishing

This project uses GitHub Actions for automated tests and deployment. The `.github/workflows` folder comprise of three major workflows:
1. `deploy-mkdocs.yml` : It handles the automated deployment of the documentation site. It is triggered on every push to the main branch.
2. `release.yml`: It handles the release of the package to [PyPI](https://pypi.org/). It happens when a tag with `v*` is set and pushed to the main branch.
3. `tests.yml`: It runs on every pull requests and push to the main branch. It runs the test suites across major Python versions (3.8, 3.9, 3.10, 3.11).


## Helpful Links

Issues and pull requests are more than welcome:

- [Project Documentation](https://jeafreezy.github.io/nigeria_geodata/)
- [Issue Tracker](https://github.com/jeafreezy/nigeria_geodata/issues)
- [Pull Requests](https://github.com/jeafreezy/nigeria_geodata/pulls)
- [Code of Conduct](https://github.com/jeafreezy/nigeria_geodata/blob/main/CODE_OF_CONDUCT.md)
