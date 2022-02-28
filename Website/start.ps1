#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#.\environment\bin\Activate.ps1

python -m pip install -r requirements.txt

$env:FLASK_APP = "console:create_app"
$env:FLASK_ENV = "development"

python -m flask run --host 192.168.1.254