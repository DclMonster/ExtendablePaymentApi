from ..app import configure_creditor
from flask import Flask

app = Flask(__name__)
configure_creditor(app)

client = app.test_client()

