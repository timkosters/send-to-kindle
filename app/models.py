"""
Database Models for Multi-User Support

This module defines the User model for storing user accounts and their Kindle email addresses.
Users can authenticate via Google OAuth or email/password.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for storing authenticated users and their Kindle settings.
    
    Attributes:
        id: Primary key
        email: User's email (used for login and sender identification)
        name: User's display name
        password_hash: Hashed password (null for OAuth-only users)
        kindle_email: User's Kindle email address (e.g., user_123@kindle.com)
        created_at: When the account was created
        updated_at: When the account was last modified
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))  # Null for OAuth-only users
    kindle_email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and store the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_by_email(cls, email):
        """Look up a user by their email address."""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def create_or_update(cls, email, name, password=None):
        """
        Create a new user or update existing user's name.
        Used during OAuth login or email registration.
        """
        user = cls.get_by_email(email)
        if user:
            user.name = name
            user.updated_at = datetime.utcnow()
        else:
            user = cls(email=email.lower(), name=name)
            if password:
                user.set_password(password)
            db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def register(cls, email, name, password):
        """Register a new user with email and password."""
        if cls.get_by_email(email):
            return None  # User already exists
        user = cls(email=email.lower(), name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
