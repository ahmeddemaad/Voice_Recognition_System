from Voice_Recognition import app
from flask import render_template

@app.route('/')
def main():
    return render_template('Index.html')