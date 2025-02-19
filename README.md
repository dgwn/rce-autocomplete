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