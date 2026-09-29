#Module 5


**Repository SSH URL:** `git@github.com:Wanyiava/jhu_software_concepts.git`

## Setup

Use Python 3.12/3.13 and PostgreSQL 16. From the repository root:

cd module_4
python -m venv .venv
python -m pip install -r requirements.txt


Start an isolated development database (localhost only):


docker run --name gradcafe-dev -d -p 127.0.0.1:55432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -e POSTGRES_DB=gradcafe postgres:16-alpine


PowerShell:


$env:DATABASE_URL = "postgresql+psycopg2://postgres@127.0.0.1:55432/gradcafe"
$env:TEST_DATABASE_URL = $env:DATABASE_URL


macOS/Linux:

export DATABASE_URL='postgresql+psycopg2://postgres@127.0.0.1:55432/gradcafe'
export TEST_DATABASE_URL="$DATABASE_URL"

Trust authentication is for this disposable local container only. Shared databases should use authenticated URLs supplied through the environment. Tests require PostgreSQL schema-creation privileges and isolate each case in a temporary UUID schema.

## Pylint Check
To ensure the code complies with industry standards and to perform static code analysis, Pylint was run exclusively on the source code directory. 

The exact command used to run this check from the root of the `module_5` directory is:

```bash
pylint src/

##  fresh install
## Fresh Install
### Option 1: Standard Installation using pip
1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
2. install all dependencies and package the project in terminal
   pip install -r requirements.txt
   pip install -e .
### Option 2: Standard Installation using uv 
1. Create a virtual environment and sync dependencies in the terminal:
   uv venv
   source .venv/bin/activate
   uv pip sync requirements.txt
   uv pip install -e .