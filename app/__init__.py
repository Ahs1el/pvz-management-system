from flask import Flask
from .models import db, User, StorageCell
from .routes import bp

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("DATABASE_URL", "sqlite:///pvz_dev.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or "dev-only-change-this"
    db.init_app(app); app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            db.session.add_all([User(full_name="Оператор ПВЗ", role="operator"), User(full_name="Управляющий", role="manager")])
        if StorageCell.query.count() == 0:
            db.session.add_all([StorageCell(code=f"A-{i:02d}") for i in range(1, 6)])
        db.session.commit()
    return app
