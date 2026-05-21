cd $PSScriptRoot
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn main:app --reload