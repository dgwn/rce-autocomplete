## Create virtual env
python -m venv venv

## Activate venv
source venv/bin/activate

## Intsall Requirements
pip install -r requirements.txt

## OPENAI KEY
Add a `.env` file and add the following line:
`OPENAI_API_KEY=**SOMETHING**`
        
## Start server
cd app
fastapi dev main.py

# Or use uv

brew install uv/pip install uv

uv lock

uv sync

cd app
uv run fastapi dev main.py

# Env variables

OPENAI_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_KEY=
AWS_REGION=us-east-1
YOUTUBE_API_KEY=

# Note on default values

Since there are a lot of optional parameters, there are many default values.

Please store all default values in the completion.py schema for consistency