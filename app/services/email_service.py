from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_password_reset_email(to_email, username, reset_token):
    """Send password reset email to user."""
    try:
        reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:5000')}/auth/reset-password?token={reset_token}"
        
        msg = Message(
            subject="Password Reset Request",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[to_email]
        )
        
        msg.body = f"""
Hi {username},

You requested a password reset for your account.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this, please ignore this email.

Best regards,
Flask Auth Service
        """
        
        msg.html = f"""
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Hi <strong>{username}</strong>,</p>
    <p>You requested a password reset for your account.</p>
    <p>Click the button below to reset your password:</p>
    <a href="{reset_url}" style="
        background-color: #4CAF50;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 4px;
        display: inline-block;
        margin: 16px 0;
    ">Reset Password</a>
    <p>Or copy this link: <a href="{reset_url}">{reset_url}</a></p>
    <p><strong>This link will expire in 1 hour.</strong></p>
    <p>If you did not request this, please ignore this email.</p>
    <br>
    <p>Best regards,<br>Flask Auth Service</p>
</body>
</html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def send_welcome_email(to_email, username):
    """Send welcome email to newly registered user."""
    try:
        msg = Message(
            subject="Welcome to Flask Auth Service!",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[to_email]
        )
        
        msg.body = f"""
Hi {username},

Welcome to Flask Auth Service! Your account has been created successfully.

Best regards,
Flask Auth Service
        """
        
        msg.html = f"""
<html>
<body>
    <h2>Welcome to Flask Auth Service!</h2>
    <p>Hi <strong>{username}</strong>,</p>
    <p>Your account has been created successfully.</p>
    <br>
    <p>Best regards,<br>Flask Auth Service</p>
</body>
</html>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {to_email}: {str(e)}")
        return False