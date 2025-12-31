"""
Authentication Blueprint for Google OAuth

This module handles user authentication via Google OAuth 2.0.
Users click "Sign in with Google" and are redirected through the OAuth flow.
After successful authentication, we create/update their user record and log them in.
"""

from flask import Blueprint, redirect, url_for, session, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from .models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# OAuth will be initialized in init_oauth()
oauth = OAuth()


def init_oauth(app):
    """
    Initialize OAuth with the Flask app.
    Must be called after app is created with proper config.
    """
    oauth.init_app(app)
    
    # Register Google as OAuth provider
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )


@auth_bp.route('/login')
def login():
    """
    Initiate Google OAuth login.
    Redirects user to Google's login page.
    """
    # Build the callback URL
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """
    Handle OAuth callback from Google.
    Creates/updates user record and logs them in.
    """
    try:
        # Get the access token
        token = oauth.google.authorize_access_token()
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback: fetch from userinfo endpoint
            resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
            user_info = resp.json()
        
        email = user_info.get('email')
        name = user_info.get('name', email.split('@')[0])
        
        if not email:
            flash('Could not get email from Google. Please try again.', 'error')
            return redirect(url_for('index'))
        
        # Create or update user in database
        user = User.create_or_update(email=email, name=name)
        
        # Log the user in
        login_user(user)
        
        # Redirect to settings if they haven't set up Kindle email yet
        if not user.kindle_email:
            flash(f'Welcome, {name}! Please set up your Kindle email to get started.', 'info')
            return redirect(url_for('settings'))
        
        flash(f'Welcome back, {name}!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        current_app.logger.error(f'OAuth error: {e}')
        flash('Login failed. Please try again.', 'error')
        return redirect(url_for('login_page'))


@auth_bp.route('/logout')
@login_required
def logout():
    """Log the user out."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login_page'))
