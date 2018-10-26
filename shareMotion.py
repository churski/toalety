from flask import Flask
from flask import send_file

app = Flask(__name__)

if __name__ == '__main__':
	app.run(host='0.0.0.0')

@app.route("/")
def hello():
	file = open("motion.state", "r")
	state = file.read()
	file.close()
	if state == "1":
		return send_file('occ.png', mimetype='image/png')
	else:
		return send_file('vac.png', mimetype='image/png')
	return 1;
