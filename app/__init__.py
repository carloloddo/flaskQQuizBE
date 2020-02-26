from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restplus import Api
import traceback

app = Flask(__name__)

# Benchè il db sia stato creato nell'altra app, dobbiamo
# accedervi anche da questa.
# Perciò anche qui è necessaria la sua configurazione.

db = SQLAlchemy(app)
# L'url deve indicare esattamente il punto dove abbiamo creato il db
# tramite l'app Users.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../site.db'
migrate = Migrate(app, db)
api = Api(app, version='1.0', title='Sample Questionari_Insert API',
    description='API')

# Le configurazioni sono le stesse del dell'app Users,
# cambia solo il nome del namespace da registrare.

from app.controllers import quizs

api.add_namespace(quizs)
