Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\environment\bin\Activate.ps1

pip3 install -r requirements.txt

$Env:FLASK_APP = console:create_app
$Env:FLASK_ENV = development

flask run