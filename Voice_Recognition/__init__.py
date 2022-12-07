from flask import Flask

app= Flask(__name__)

from Voice_Recognition import routes , index
