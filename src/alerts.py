import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json


class AlertSystem:
    def __init__(self, config_path='config/config.json'):
        with open(config_path) as f:
            self.config = json.load(f)

        self.thresholds = {
            'high_temp': self.config.get('temp_threshold', 35),
            'consecutive_checks': self.config.get('consecutive_checks', 2)
        }

        self.alert_history = {}

    def check_temperature_alert(self, city, temp, timestamp):
        if city not in self.alert_history:
            self.alert_history[city] = []

        history = self.alert_history[city]
        history.append({'temp': temp, 'timestamp': timestamp})

        if len(history) > self.thresholds['consecutive_checks']:
            history.pop(0)

        if (len(history) == self.thresholds['consecutive_checks'] and
                all(h['temp'] > self.thresholds['high_temp'] for h in history)):
            self.send_alert(city, temp, timestamp)
            return True
        return False

    def send_alert(self, city, temp, timestamp):
        if not self.config.get('enable_email_alerts', False):
            print(f"ALERT: High temperature in {city}: {temp}°C at {timestamp}")
            return

        email_config = self.config.get('email_config', {})
        if not email_config:
            return

        msg = MIMEMultipart()
        msg['From'] = email_config['from_email']
        msg['To'] = email_config['to_email']
        msg['Subject'] = f"Weather Alert: High Temperature in {city}"

        body = f"""
        Weather Alert!

        City: {city}
        Temperature: {temp}°C
        Time: {timestamp}

        Temperature has exceeded {self.thresholds['high_temp']}°C for 
        {self.thresholds['consecutive_checks']} consecutive checks.
        """

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")