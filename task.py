import os
import requests
from typing import Dict
import os
import csv
import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Report
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()  

REPORTS_DIR = "weather_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


class WeatherService:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def get_weather_data(self, city: str) -> Dict:
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Weather API error: {str(e)}")

weather_service = WeatherService()

async def send_report_email(
    email_to: str,
    username: str,
    report_id: int,
    download_url: str,
    city: str
) -> bool:
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    sender_email = os.getenv("EMAIL_FROM")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    msg = EmailMessage()
    msg['Subject'] = f"Weather Report for {city} (ID: {report_id})"
    msg['From'] = sender_email
    msg['To'] = email_to
    
    body = f"""Hello {username},

Your weather report for {city} is ready.

Download link: {download_url}

This report contains current weather conditions for {city}.

The link will expire in 24 hours.

Thank you,
Weather Report Service
"""
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls() 
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False



def generate_report_file(report_id: int, city: str) -> str:
    filename = f"weather_report_{report_id}_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    try:
        weather_data = weather_service.get_weather_data(city)
        
        with open(filepath, mode='w', newline='') as report_file:
            writer = csv.writer(report_file)
            
            writer.writerow([
                "Report ID", "City", "Date", "Temperature (°C)", 
                "Conditions", "Humidity (%)", "Wind Speed (m/s)",
                "Pressure (hPa)", "Visibility (m)"
            ])
            
            writer.writerow([
                report_id,
                city,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                weather_data['main']['temp'],
                weather_data['weather'][0]['description'],
                weather_data['main']['humidity'],
                weather_data['wind']['speed'],
                weather_data['main']['pressure'],
                weather_data.get('visibility', 'N/A')
            ])
        
        return filepath
        
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate weather report: {str(e)}"
        )

async def generate_report(
    report_id: int,
    user_email: str,
    username: str,
    city: str,
    db: Session
):
    try:
        file_path = generate_report_file(report_id, city)
        db_report = db.query(Report).filter(Report.report_id == report_id).first()
        if db_report:
            db_report.status = "completed"
            db_report.file_path = file_path
            db.commit()
            db.refresh(db_report)
            
            download_url = f"http://localhost:8000/reports/{report_id}/download"
            
            await send_report_email(
                email_to=user_email,
                username=username,
                report_id=report_id,
                download_url=download_url,
                city=city
            )
            
    except Exception as e:
        print(f"Error generating report: {str(e)}") 
        db_report = db.query(Report).filter(Report.report_id == report_id).first()
        if db_report:
            db_report.status = "failed"
            db.commit()
 