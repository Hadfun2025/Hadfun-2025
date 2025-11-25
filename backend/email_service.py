import os
import resend
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via Resend"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.sender_email = os.environ.get('SENDER_EMAIL', 'noreply@hadfun.app')
        if self.api_key:
            resend.api_key = self.api_key
        else:
            logger.warning("RESEND_API_KEY not found in environment variables")
    
    async def send_team_invitation(
        self,
        recipient_email: str,
        team_name: str,
        team_code: str,
        inviter_name: str,
        app_url: str
    ) -> Dict[str, any]:
        """
        Send a team invitation email
        
        Args:
            recipient_email: Email address of the invitee
            team_name: Name of the team
            team_code: Team join code
            inviter_name: Name of person sending invite
            app_url: Base URL of the application
        
        Returns:
            Dict with status and message/error
        """
        try:
            join_link = f"{app_url}/team-management?join={team_code}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        color: #2c3e50;
                        margin-bottom: 30px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #3498db;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .team-code {{
                        background-color: #ecf0f1;
                        padding: 15px;
                        border-radius: 5px;
                        text-align: center;
                        font-size: 24px;
                        font-weight: bold;
                        letter-spacing: 2px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        color: #7f8c8d;
                        font-size: 12px;
                        margin-top: 30px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="content">
                        <div class="header">
                            <h1>⚽ Team Invitation</h1>
                        </div>
                        
                        <p>Hi there!</p>
                        
                        <p><strong>{inviter_name}</strong> has invited you to join their team on <strong>HadFun Predictor</strong>!</p>
                        
                        <p><strong>Team Name:</strong> {team_name}</p>
                        
                        <p>You can join the team by clicking the button below or using the team code:</p>
                        
                        <div class="team-code">{team_code}</div>
                        
                        <div style="text-align: center;">
                            <a href="{join_link}" class="button">Join Team Now</a>
                        </div>
                        
                        <p>Join your team to:</p>
                        <ul>
                            <li>Make weekly football predictions</li>
                            <li>Compete in the weekly pot</li>
                            <li>Track your performance on the leaderboard</li>
                            <li>Chat with team members</li>
                        </ul>
                        
                        <p>Good luck and have fun!</p>
                        
                        <div class="footer">
                            <p>HadFun Predictor - Where football predictions meet friendly competition</p>
                            <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": f"HadFun Predictor <{self.sender_email}>",
                "to": [recipient_email],
                "subject": f"🎯 You're invited to join {team_name} on HadFun Predictor!",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Team invitation email sent to {recipient_email}")
            
            return {
                "status": "success",
                "message": "Invitation email sent successfully",
                "email_id": response.get('id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send team invitation email: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def send_welcome_email(
        self,
        recipient_email: str,
        user_name: str,
        team_name: str
    ) -> Dict[str, any]:
        """
        Send a welcome email when user joins a team
        
        Args:
            recipient_email: Email address of the new member
            user_name: Name of the user
            team_name: Name of the team they joined
        
        Returns:
            Dict with status and message/error
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    .content {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        color: #27ae60;
                        margin-bottom: 30px;
                    }}
                    .welcome-badge {{
                        background-color: #27ae60;
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="content">
                        <div class="header">
                            <h1>🎉 Welcome to the Team!</h1>
                        </div>
                        
                        <div class="welcome-badge">
                            <h2>You've joined {team_name}</h2>
                        </div>
                        
                        <p>Hi {user_name},</p>
                        
                        <p>Welcome to <strong>{team_name}</strong> on HadFun Predictor! You're now part of the action.</p>
                        
                        <p><strong>What's next?</strong></p>
                        <ul>
                            <li>Check the weekly fixtures and make your predictions</li>
                            <li>Join the weekly pot for a chance to win</li>
                            <li>Climb the leaderboard</li>
                            <li>Connect with your teammates</li>
                        </ul>
                        
                        <p>Remember: Predictions must be submitted before Wednesday 11:59 PM each week!</p>
                        
                        <p>Good luck and may the best predictor win! ⚽</p>
                        
                        <p>Cheers,<br>The HadFun Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": f"HadFun Predictor <{self.sender_email}>",
                "to": [recipient_email],
                "subject": f"🎉 Welcome to {team_name}!",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Welcome email sent to {recipient_email}")
            
            return {
                "status": "success",
                "message": "Welcome email sent successfully",
                "email_id": response.get('id')
            }
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
