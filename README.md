## Create virtual env
python -m venv venv

## Activate venv
source venv/bin/activate

## Intsall Requirements
pip install -r requirements.txt
        
## Start server
cd app
fastapi dev main.py

# Or use uv

brew install uv/pip install uv

uv lock

uv sync

cd app
uv run fastapi dev main.py