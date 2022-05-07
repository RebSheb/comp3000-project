sudo apt install -y tcpdump python3 python3-requests python3-netifaces python3-apt python3-flask python3-sqlalchemy
pip3 install -r requirements.txt

export FLASK_APP=console:create_app
export FLASK_ENV=development

flask run --host=0.0.0.0
