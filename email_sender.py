"""
Email sender for flight deal notifications
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
from src.config import Config

logger = logging.getLogger(__name__)


class EmailSender:
    """Email notification system"""

    def __init__(self, config: Config):
        self.config = config
        self.sender = config.gmail_sender
        self.password = config.gmail_password
        self.recipient = config.email_recipient

    def send_deal_alert(self, offers: List[Dict[str, Any]]):
        """
        Send email alert for flight deals

        Args:
            offers: List of analyzed flight offers
        """
        if not offers:
            logger.info("No offers to send")
            return

        # Get best offer for subject line
        best_offer = offers[0]
        analysis = best_offer['analysis']

        # Create subject line
        subject = self._create_subject(best_offer, analysis)

        # Create email body
        html_body = self._create_html_body(offers)
        text_body = self._create_text_body(offers)

        # Send email
        self._send_email(subject, html_body, text_body)

    def _create_subject(self, offer: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create email subject line"""
        quality = analysis['deal_quality']
        price = offer['price']
        currency = offer['currency']
        discount = analysis.get('discount_percent', 0)

        emoji = {
            'amazing': '🔥',
            'great': '⭐',
            'good': '✓',
            'average': '📊'
        }.get(quality, '✈️')

        quality_text = quality.upper() + " DEAL" if quality != 'average' else "Flight Update"

        route_text = f"{offer['origin']} → {offer['destination']}"

        if discount and discount > 0:
            return f"{emoji} {quality_text}: {route_text} for {price:,.0f} {currency} ({discount:.0f}% off!)"
        else:
            return f"{emoji} {quality_text}: {route_text} for {price:,.0f} {currency}"

    def _create_html_body(self, offers: List[Dict[str, Any]]) -> str:
        """Create HTML email body"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px 10px 0 0; }
                .deal { background: #f8f9fa; border-left: 4px solid #667eea; 
                       padding: 15px; margin: 15px 0; border-radius: 5px; }
                .deal.amazing { border-left-color: #dc3545; background: #fff5f5; }
                .deal.great { border-left-color: #ffc107; background: #fffbf0; }
                .price { font-size: 32px; font-weight: bold; color: #667eea; }
                .discount { color: #28a745; font-weight: bold; }
                .flight-details { margin: 10px 0; padding: 10px; background: white; border-radius: 5px; }
                .button { display: inline-block; padding: 12px 24px; background: #667eea; 
                         color: white; text-decoration: none; border-radius: 5px; margin: 10px 5px; }
                .stats { background: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; }
                .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; 
                         font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✈️ Flight Deal Alert</h1>
                    <p>Warsaw → Brazil</p>
                </div>
        """

        for i, offer in enumerate(offers):
            analysis = offer['analysis']
            quality = analysis['deal_quality']

            html += f"""
                <div class="deal {quality}">
                    <h2>{i + 1}. {offer['origin']} → {offer['destination']}</h2>

                    <div class="price">
                        {offer['price']:,.0f} {offer['currency']}
            """

            if analysis.get('discount_percent') and analysis['discount_percent'] > 0:
                html += f"""
                        <span class="discount">({analysis['discount_percent']:.0f}% below average!)</span>
                """

            html += """
                    </div>
            """

            # Trip details
            outbound = offer.get('outbound', {})
            inbound = offer.get('inbound', {})

            if outbound:
                html += f"""
                    <div class="flight-details">
                        <strong>✈️ OUTBOUND:</strong><br>
                        {outbound.get('departure_time', '')[:10]}: 
                        {outbound.get('departure_airport')} → {outbound.get('arrival_airport')}
                        ({outbound.get('stops', 0)} stop{'s' if outbound.get('stops', 0) != 1 else ''})
                """

                if outbound.get('connections'):
                    html += f"<br>via {', '.join(outbound['connections'])}"

                html += """
                    </div>
                """

            if inbound:
                html += f"""
                    <div class="flight-details">
                        <strong>✈️ RETURN:</strong><br>
                        {inbound.get('departure_time', '')[:10]}: 
                        {inbound.get('departure_airport')} → {inbound.get('arrival_airport')}
                        ({inbound.get('stops', 0)} stop{'s' if inbound.get('stops', 0) != 1 else ''})
                """

                if inbound.get('connections'):
                    html += f"<br>via {', '.join(inbound['connections'])}"

                html += """
                    </div>
                """

            # Statistics
            stats_30d = analysis.get('stats_30d', {})
            if stats_30d.get('avg'):
                html += f"""
                    <div class="stats">
                        <strong>📊 Price Analysis:</strong><br>
                        30-day average: {stats_30d['avg']:,.0f} {offer['currency']}<br>
                        30-day low: {stats_30d.get('min', 'N/A'):,.0f} {offer['currency']}<br>
                        Checks in last 30 days: {stats_30d.get('count', 0)}
                    </div>
                """

            # Booking link
            booking_link = offer.get('booking_link', 'https://www.google.com/flights')
            html += f"""
                    <a href="{booking_link}" class="button">🔗 Book Now</a>
                </div>
            """

        html += f"""
                <div class="footer">
                    <p>This alert was sent because the deal meets your criteria:</p>
                    <ul>
                        <li>Price threshold or discount percentage met</li>
                        <li>Alert frequency: {self.config.get('email.alert_frequency', 'major_deals_only')}</li>
                    </ul>
                    <p>Alert generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><small>Flight Deal Bot • Powered by Amadeus API</small></p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _create_text_body(self, offers: List[Dict[str, Any]]) -> str:
        """Create plain text email body"""
        text = "✈️ FLIGHT DEAL ALERT - Warsaw → Brazil\n"
        text += "=" * 60 + "\n\n"

        for i, offer in enumerate(offers):
            analysis = offer['analysis']
            quality = analysis['deal_quality'].upper()

            text += f"{i + 1}. {quality} DEAL: {offer['origin']} → {offer['destination']}\n"
            text += f"Price: {offer['price']:,.0f} {offer['currency']}"

            if analysis.get('discount_percent') and analysis['discount_percent'] > 0:
                text += f" ({analysis['discount_percent']:.0f}% below average!)"

            text += "\n\n"

            # Flight details
            outbound = offer.get('outbound', {})
            inbound = offer.get('inbound', {})

            if outbound:
                text += f"✈️ OUTBOUND: {outbound.get('departure_time', '')[:10]}\n"
                text += f"   {outbound.get('departure_airport')} → {outbound.get('arrival_airport')}\n"
                text += f"   {outbound.get('stops', 0)} stop(s)"
                if outbound.get('connections'):
                    text += f" via {', '.join(outbound['connections'])}"
                text += "\n\n"

            if inbound:
                text += f"✈️ RETURN: {inbound.get('departure_time', '')[:10]}\n"
                text += f"   {inbound.get('departure_airport')} → {inbound.get('arrival_airport')}\n"
                text += f"   {inbound.get('stops', 0)} stop(s)"
                if inbound.get('connections'):
                    text += f" via {', '.join(inbound['connections'])}"
                text += "\n\n"

            # Statistics
            stats_30d = analysis.get('stats_30d', {})
            if stats_30d.get('avg'):
                text += f"📊 Price Analysis:\n"
                text += f"   30-day average: {stats_30d['avg']:,.0f} {offer['currency']}\n"
                text += f"   30-day low: {stats_30d.get('min', 'N/A'):,.0f} {offer['currency']}\n"
                text += f"   Recent checks: {stats_30d.get('count', 0)}\n"

            text += f"\n🔗 Book: {offer.get('booking_link', 'https://www.google.com/flights')}\n"
            text += "\n" + "-" * 60 + "\n\n"

        text += f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "Flight Deal Bot\n"

        return text

    def _send_email(self, subject: str, html_body: str, text_body: str):
        """Send email via Gmail SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = self.recipient

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {self.recipient}")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

    def test_email(self):
        """Send a test email to verify configuration"""
        try:
            subject = "✈️ Flight Deal Bot - Test Email"

            html_body = """
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>🎉 Flight Deal Bot Test Email</h2>
                <p>Congratulations! Your email configuration is working correctly.</p>
                <p>The bot is ready to send you flight deal alerts.</p>
                <hr>
                <p><small>If you receive this, your setup is complete!</small></p>
            </body>
            </html>
            """

            text_body = """
            🎉 Flight Deal Bot - Test Email

            Congratulations! Your email configuration is working correctly.
            The bot is ready to send you flight deal alerts.

            If you receive this, your setup is complete!
            """

            self._send_email(subject, html_body, text_body)
            logger.info("Test email sent successfully!")
            return True

        except Exception as e:
            logger.error(f"Test email failed: {e}")
            return False