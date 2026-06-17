
## Project Overview

Django GitHub SSO is a Django app that adds GitHub OAuth 2.0 authentication to Django Admin and/or regular pages. Users can log in using their GitHub account, with optional org/repo/domain-based access control. Supports multiple SSO providers simultaneously (Google, Microsoft).

## Architecture

- **views.py** — Entry point: `start_login` redirects to GitHub OAuth, `callback` handles the OAuth response.
- **main.py** — `GithubAuth` handles OAuth session/URL/token logic; `UserHelper` handles user lookup, creation, permissions and data sync.
- **conf.py** — Module-level settings class (`GitHubSSOSettings`) exposed via PEP 562 `__getattr__`.
- **hooks.py** — Default no-op callbacks for pre-validate, pre-create and pre-login customization.
- **models.py** — `GitHubSSOUser` model linking Django `User` to GitHub profile data.
- **Flow**: OAuth → callback → validate user/email/org/repo → pre-create hook → get_or_create user → pre-login hook → login.

## Key Patterns

- **Callable settings**: Many settings accept a callable `(request) -> value` for per-request dynamic configuration.
- **Callback hooks**: Three lifecycle hooks (`pre_validate`, `pre_create`, `pre_login`) let apps inject custom logic at each stage.
- **Dataclass helpers**: `GithubAuth` and `UserHelper` are `@dataclass` classes encapsulating request-specific state.
- **Module-level conf singleton**: `GitHubSSOSettings` is instantiated once and accessed via module `__getattr__`.
- **PEP 562**: Conf module uses `__getattr__` to delegate attribute access to the settings singleton.

## Commands

```bash
make install        # Install deps + pre-commit hooks
make lint           # Run pre-commit (black, flake8, isort)
make tests          # Run full pytest suite
make test <path>    # Run a single test, e.g.: make test megalus/tests/test_base_views.py::test_health_check
make update         # Update dependencies and pre-commit hooks
```

## Testing Conventions

- To run tests, use `make tests` to run all tests or `make test <test_path>` to run a single test.
- If you need to run using pytest command directly, set `STELA_ENV=test`
- Tests are always syncronous (no `async` tests) and should avoid external API calls (mock them instead). Use `pytest-mock` for mocking.
- When resolving tests, always resolve warnings too.

## Lint and Formatting

- Check lint using command `make lint`.
- The command `make lint` runs `pre-commit run --all` under the hood.
- This means when `ruff` and `bandit` runs, they will try to fix the issues automatically.
- When checking for lint, if the first `make lint` returns errors, run the command again before making any manual changes.


## Code Style

- Python 3.13, Django 6.0, Ruff for deps.
- Always use type hints. Use `TypedDict` for dicts with 5+ keys. Use `Enum`/`Literal` for fixed values. Use `X | None` not `Optional[X]`.
- Google-style docstrings for functions/classes >7 lines.
- f-strings, double quotes, triple quotes for multi-line.
- Prefer dataclasses over regular classes.
- Always use English in code, comments, tests, commits, and docs. If non-English content is needed, put it in a separate file and use `gettext` for translation.

## Commit Messages

One-line, semantic prefix based on changed files:
- `feat:` — changes in `django-github-sso/` and `docs/`
- `refactor:` — changes in `django-github-sso/` without test changes
- `ci:` — changes only in `.github/`, or `pyproject.toml`
- `chore:` — changes outside `django-github-sso/` and `example_github_app/`
- `docs:` — changes only in `docs/` or `README.md`
