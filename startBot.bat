
if not exist env (
    python -m venv create env
	call .\env\Scripts\activate
	pip install -r requirements.txt
) else (
	call .\env\Scripts\activate
)


python bot.py
pause
