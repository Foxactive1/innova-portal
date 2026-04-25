from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Voce precisa fazer login para acessar esta pagina."
login_manager.login_message_category = "warning"
limiter = Limiter(key_func=get_remote_address, default_limits=[])
