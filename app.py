'''main app '''
from os import getenv
from flask import Flask

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

import routes
import users
import plan

plan.gen_default_places()
plan.gen_default_skills()
plan.gen_default_disturbances()
