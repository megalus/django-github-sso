# CHANGELOG


## v4.0.0 (2024-10-09)

### Breaking

* feat!: Add support to 3.13

This is a BREAKING CHANGE commit. Changes:

* Add support to Python 3.13
* Drop support to 3.10
* Update Github Actions ([`50e35f8`](https://github.com/megalus/django-github-sso/commit/50e35f84bcc884eae5f6a31e002b3c79e6d3ec13))

### Continuous Integration

* ci: fix github actions ([`eb4587c`](https://github.com/megalus/django-github-sso/commit/eb4587c7f491460281a28f89cf803886d433928a))

### Documentation

* docs: update docs ([`26b510a`](https://github.com/megalus/django-github-sso/commit/26b510aa2a6fd22132a9e14c0e507968736665f6))

### Unknown

* Merge pull request #3 from megalus/develop

Add support to 3.13 ([`1d32aea`](https://github.com/megalus/django-github-sso/commit/1d32aea409e23babdc7df9c7d5493ac12a78885a))


## v3.0.1 (2024-09-21)

### Continuous Integration

* ci: fix django example app in github actions ([`b2dc535`](https://github.com/megalus/django-github-sso/commit/b2dc53562580f041f9817678b708e6b7d7eb2ebf))

* ci: fix github action tests ([`444b0b9`](https://github.com/megalus/django-github-sso/commit/444b0b9fe5becc1cde867699153b9758b1d55425))

### Documentation

* docs: update docs ([`451e278`](https://github.com/megalus/django-github-sso/commit/451e2787f8307ece2dec26437f7bb3e45812ace9))

### Fixes

* fix: add missing GITHUB_SSO_ENABLE_MESSAGES option ([`0e88d47`](https://github.com/megalus/django-github-sso/commit/0e88d473eea8aa892bb627d88662a9e9b6b00c50))

### Unknown

* Merge pull request #2 from megalus/develop

Fix: Add missing GITHUB_SSO_ENABLE_MESSAGES option ([`b5ccd25`](https://github.com/megalus/django-github-sso/commit/b5ccd256cfea11c4f0c6e5d89d590b6dc3a33d6a))

* Merge pull request #1 from dqd/main

Usage without django_microsoft_sso installed ([`30e2f1e`](https://github.com/megalus/django-github-sso/commit/30e2f1e672d786a76f51072d1fc0c50cce157f07))

* Usage without django_microsoft_sso installed ([`6f3b50d`](https://github.com/megalus/django-github-sso/commit/6f3b50d71d26b16bcbb96192eae11cd40faa9262))


## v3.0.0 (2024-09-17)

### Breaking

* feat!: Update dependencies and add new options

This is a BREAKING CHANGE commit. Changes:

* Remove support to Django 4.1 and add support to Django 5.1
* Fix check W003 for Django 5.1
* Add new option: `GITHUB_SSO_PRE_VALIDATE_CALLBACK`. Use to add your custom logic to validate a user.
* Add new option: `GITHUB_SSO_SAVE_BASIC_GITHUB_INFO` to save basic github data in database. Default: True.
* Add new option: `GITHUB_SSO_SHOW_FAILED_LOGIN_MESSAGE`. Use to show failed attempted logins on browser. Default: False. ([`b73c8b1`](https://github.com/megalus/django-github-sso/commit/b73c8b17a41d41c753d255f94c1826a28de5bc5c))


## v2.2.0 (2024-07-31)

### Features

* feat: add option to include all created users as staff.

Also better handling lower and upper case emails and usernames saved on database. ([`56bbfbf`](https://github.com/megalus/django-github-sso/commit/56bbfbfa22b50647b698c3eb360f2eb45b20f571))


## v2.1.2 (2024-06-07)

### Fixes

* fix: add support to Django USERNAME_FIELD ([`427081b`](https://github.com/megalus/django-github-sso/commit/427081bcdc67c2d229bdcb88baaab5b8153631b4))


## v2.1.1 (2024-04-09)

### Fixes

* fix: add token in request before call pre-create callback ([`1ac1bba`](https://github.com/megalus/django-github-sso/commit/1ac1bbacbe0bb2b3b7120d0c148bbde229e0eadd))


## v2.1.0 (2024-04-09)

### Features

* feat: Add support to custom attributes in User model before creation.

    Use the `GITHUB_SSO_PRE_CREATE_CALLBACK` setting to define a custom function which can return a dictionary which will be used during user creation for the `defaults` value. ([`1ac0b47`](https://github.com/megalus/django-github-sso/commit/1ac0b47f0d457d2799cd4ad071ea871fea52fa65))


## v2.0.1 (2024-03-12)

### Fixes

* fix: error when create a user with empty username when a user with no username already exists on database ([`9332314`](https://github.com/megalus/django-github-sso/commit/933231467c468be3567c6c603a8f883840b83ba6))


## v2.0.0 (2024-03-12)

### Breaking

* feat!: Add basic support to custom login templates.

Rework the login.html and login_sso.html to simplify login template customization. The use case is the [Django Unfold](https://github.com/unfoldadmin/django-unfold) package. This is a BREAKING CHANGE for the static and html files.

Also:
* Remove pytest-lazy-fixture to upgrade pytest to latest version ([`286e763`](https://github.com/megalus/django-github-sso/commit/286e763a365c1ccf00eb5801d8f10cf495635ab5))

### Chores

* chore: Better Stela use

Also add missing tests in GitHub Actions ([`0192cd7`](https://github.com/megalus/django-github-sso/commit/0192cd73d346ae2e0b47e1243f18a886e07e949f))

### Unknown

* doc: fix link ([`9efe9cc`](https://github.com/megalus/django-github-sso/commit/9efe9cca74a0d0d97c264913e6e7cb408f9df1de))


## v1.0.0 (2023-12-20)

### Breaking

* feat!: First Public Version

BREAKING CHANGE: First public version ([`8681241`](https://github.com/megalus/django-github-sso/commit/8681241da113725d702ef3329e7990d1b5343372))

### Chores

* chore: fix version ([`e7f2433`](https://github.com/megalus/django-github-sso/commit/e7f243342d26f0e6cbe76c211091edabbcad50f1))

* chore: fix pre-commit issues ([`cca243b`](https://github.com/megalus/django-github-sso/commit/cca243b50c9bda41e21e94fc556be9c9708dcf24))

### Unknown

* Initial commit ([`6ddc2b7`](https://github.com/megalus/django-github-sso/commit/6ddc2b7fa1e6d293d654420e065c89d669adaa74))
