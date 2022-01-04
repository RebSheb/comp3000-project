source environment/bin/activate

pip3 install -r requirements.txt

export FLASK_APP=console:create_app
export FLASK_ENV=development

flask run --host=0.0.0.0
