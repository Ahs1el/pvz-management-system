from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="operator")

class StorageCell(db.Model):
    __tablename__ = "storage_cells"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    zone = db.Column(db.String(30), nullable=False, default="storage") # storage / returns
    is_active = db.Column(db.Boolean, nullable=False, default=True)

class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(100), unique=True, nullable=False)
    marketplace = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="awaiting_issue")
    cell_id = db.Column(db.Integer, db.ForeignKey("storage_cells.id"))
    accepted_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    accepted_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    note = db.Column(db.Text)
    cell = db.relationship("StorageCell")
    operator = db.relationship("User")

class OperationLog(db.Model):
    __tablename__ = "operation_log"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    operation = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    details = db.Column(db.Text)
