from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/section/<section>')
def index(section=None):
	return render_template('index.html', section=section)

if __name__ == '__main__':
	app.run(debug=True)
