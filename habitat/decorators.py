from functools import wraps
from flask import session, request, redirect, url_for

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'admin' in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function
