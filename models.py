from datetime import datetime

from flask import url_for
# from flask_login import UserMixin
# from flask_security import RoleMixin

from database import db
from sqlalchemy import Column, Integer, String
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declarative_base


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    face_image1 = db.Column(db.String(255), nullable=False)
    face_image2 = db.Column(db.String(255), nullable=False)
    face_image3 = db.Column(db.String(255), nullable=False)
