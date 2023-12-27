## Django Example App

## Start the Project

Please create a `.env.local` file with the following information:

```dotenv
GITHUB_SSO_CLIENT_ID="your Client ID here"
GITHUB_SSO_CLIENT_SECRET="your Client Secret  here"
GITHUB_SSO_NEEDED_REPOS=["my-org/example-repo","other-org/example-another-repo"]  # User needs to be a member of all repos listed
GITHUB_SSO_CALLBACK_DOMAIN=localhost:8000
```

Then run the following commands:

```shell
poetry install
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Open browser in `http://localhost:8000/secret`

## Django Admin skins

Please uncomment on `settings.py` the correct app for the skin you want to test, in `INSTALLED_APPS`.
