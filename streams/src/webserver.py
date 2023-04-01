import asyncio
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/twiml', methods=['POST'])
def return_twiml():
    print("POST TwiML")
    return render_template('streams.xml')
