"""
Database Models for Multi-User Support

This module defines the User model for storing user accounts and their Kindle email addresses.
Users authenticate via Google OAuth, and we store their email to look up their Kindle address
when they send articles via the inbound email webhook.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for storing authenticated users and their Kindle settings.
    
    Attributes:
        id: Primary key
        email: User's Google email (used for login and sender identification)
        name: User's display name from Google
        kindle_email: User's Kindle email address (e.g., user_123@kindle.com)
        created_at: When the account was created
        updated_at: When the account was last modified
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255))
    kindle_email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @classmethod
    def get_by_email(cls, email):
        """Look up a user by their email address."""
        return cls.query.filter_by(email=email.lower()).first()
    
    @classmethod
    def create_or_update(cls, email, name):
        """
        Create a new user or update existing user's name.
        Used during OAuth login.
        """
        user = cls.get_by_email(email)
        if user:
            user.name = name
            user.updated_at = datetime.utcnow()
        else:
            user = cls(email=email.lower(), name=name)
            db.session.add(user)
        db.session.commit()
        return user
