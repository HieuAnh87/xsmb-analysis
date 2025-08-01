#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hệ thống thông báo và monitoring cho việc thu thập dữ liệu xổ số
"""

import json
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import structlog
from pathlib import Path

logger = structlog.get_logger()


class NotificationSystem:
    """Hệ thống thông báo và monitoring"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.log_file = self.data_dir / "system.log"
        self.status_file = self.data_dir / "last_run_status.json"
        
        # Cấu hình email (từ environment variables)
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_emails': os.getenv('RECIPIENT_EMAILS', '').split(',')
        }
        
        # Webhook URLs (Discord, Slack, etc.)
        self.webhook_urls = {
            'discord': os.getenv('DISCORD_WEBHOOK_URL'),
            'slack': os.getenv('SLACK_WEBHOOK_URL')
        }
    
    def log_status(self, status: str, message: str, details: Optional[Dict] = None):
        """Ghi log trạng thái hệ thống"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': message,
            'details': details or {}
        }
        
        # Ghi vào file log
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error("Lỗi ghi log", error=str(e))
        
        # Ghi vào status file
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Lỗi ghi status", error=str(e))
        
        logger.info("Đã ghi log", status=status, message=message)
    
    def send_email_notification(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Gửi thông báo qua email"""
        if not self.email_config['sender_email'] or not self.email_config['sender_password']:
            logger.warning("Chưa cấu hình email, bỏ qua gửi thông báo")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = ', '.join(self.email_config['recipient_emails'])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(
                self.email_config['sender_email'],
                self.email_config['recipient_emails'],
                text
            )
            server.quit()
            
            logger.info("Đã gửi email thông báo")
            return True
            
        except Exception as e:
            logger.error("Lỗi gửi email", error=str(e))
            return False
    
    def send_webhook_notification(self, message: str, webhook_type: str = 'discord') -> bool:
        """Gửi thông báo qua webhook (Discord, Slack)"""
        webhook_url = self.webhook_urls.get(webhook_type)
        
        if not webhook_url:
            logger.warning(f"Chưa cấu hình {webhook_type} webhook")
            return False
        
        try:
            import requests
            
            if webhook_type == 'discord':
                payload = {'content': message}
            elif webhook_type == 'slack':
                payload = {'text': message}
            else:
                payload = {'message': message}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Đã gửi {webhook_type} notification")
            return True
            
        except Exception as e:
            logger.error(f"Lỗi gửi {webhook_type} notification", error=str(e))
            return False
    
    def notify_success(self, data: Dict):
        """Thông báo khi thu thập dữ liệu thành công"""
        date = data.get('date', 'N/A')
        source = data.get('source', 'N/A')
        
        # Log status
        self.log_status(
            'SUCCESS',
            f'Thu thập dữ liệu thành công cho ngày {date}',
            {'date': date, 'source': source}
        )
        
        # Tạo thông báo
        subject = f"✅ Thu thập xổ số thành công - {date}"
        message = f"""
🎲 **Báo cáo thu thập dữ liệu xổ số miền Bắc**

✅ **Trạng thái:** Thành công
📅 **Ngày:** {date}
🌐 **Nguồn:** {source}
⏰ **Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Dữ liệu đã được lưu trữ thành công vào hệ thống.
        """.strip()
        
        # Gửi thông báo qua các kênh
        self.send_webhook_notification(message, 'discord')
        
        # Email chi tiết hơn
        email_body = f"""
        <h2>🎲 Báo cáo thu thập dữ liệu xổ số miền Bắc</h2>
        
        <p><strong>✅ Trạng thái:</strong> Thành công</p>
        <p><strong>📅 Ngày:</strong> {date}</p>
        <p><strong>🌐 Nguồn:</strong> {source}</p>
        <p><strong>⏰ Thời gian:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        
        <h3>Chi tiết kết quả:</h3>
        <ul>
        """
        
        results = data.get('results', {})
        for prize, numbers in results.items():
            if isinstance(numbers, list):
                numbers_str = ', '.join(map(str, numbers))
                email_body += f"<li><strong>{prize}:</strong> {numbers_str}</li>"
        
        email_body += """
        </ul>
        
        <p>Dữ liệu đã được lưu trữ thành công vào hệ thống và sẵn sàng cho phân tích.</p>
        """
        
        self.send_email_notification(subject, email_body, is_html=True)
    
    def notify_failure(self, error_message: str, details: Optional[Dict] = None):
        """Thông báo khi thu thập dữ liệu thất bại"""
        # Log status
        self.log_status(
            'FAILURE',
            f'Thu thập dữ liệu thất bại: {error_message}',
            details
        )
        
        # Tạo thông báo
        subject = f"❌ Thu thập xổ số thất bại - {datetime.now().strftime('%d/%m/%Y')}"
        message = f"""
🚨 **Cảnh báo: Thu thập dữ liệu xổ số thất bại**

❌ **Trạng thái:** Thất bại
📅 **Ngày:** {datetime.now().strftime('%d/%m/%Y')}
⏰ **Thời gian:** {datetime.now().strftime('%H:%M:%S')}
🔍 **Lỗi:** {error_message}

Vui lòng kiểm tra hệ thống và thử lại.
        """.strip()
        
        # Gửi thông báo khẩn cấp
        self.send_webhook_notification(message, 'discord')
        
        # Email chi tiết
        email_body = f"""
        <h2>🚨 Cảnh báo: Thu thập dữ liệu xổ số thất bại</h2>
        
        <p><strong>❌ Trạng thái:</strong> Thất bại</p>
        <p><strong>📅 Ngày:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
        <p><strong>⏰ Thời gian:</strong> {datetime.now().strftime('%H:%M:%S')}</p>
        <p><strong>🔍 Lỗi:</strong> {error_message}</p>
        
        <h3>Chi tiết lỗi:</h3>
        <pre>{json.dumps(details, ensure_ascii=False, indent=2) if details else 'Không có chi tiết'}</pre>
        
        <p><strong>Hành động cần thiết:</strong></p>
        <ul>
            <li>Kiểm tra kết nối internet</li>
            <li>Kiểm tra trạng thái website nguồn</li>
            <li>Xem logs chi tiết trong GitHub Actions</li>
            <li>Thử chạy lại workflow thủ công</li>
        </ul>
        """
        
        self.send_email_notification(subject, email_body, is_html=True)
    
    def notify_validation_error(self, errors: List[str]):
        """Thông báo khi có lỗi validation dữ liệu"""
        error_count = len(errors)
        
        # Log status
        self.log_status(
            'VALIDATION_ERROR',
            f'Phát hiện {error_count} lỗi validation',
            {'errors': errors}
        )
        
        subject = f"⚠️ Lỗi validation dữ liệu - {datetime.now().strftime('%d/%m/%Y')}"
        message = f"""
⚠️ **Cảnh báo: Lỗi validation dữ liệu**

📊 **Số lỗi:** {error_count}
📅 **Ngày:** {datetime.now().strftime('%d/%m/%Y')}
⏰ **Thời gian:** {datetime.now().strftime('%H:%M:%S')}

Dữ liệu có thể không chính xác, cần kiểm tra thủ công.
        """.strip()
        
        self.send_webhook_notification(message, 'discord')
    
    def get_system_health(self) -> Dict:
        """Lấy thông tin sức khỏe hệ thống"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    last_status = json.load(f)
            else:
                last_status = None
            
            # Kiểm tra file dữ liệu
            json_file = self.data_dir / "lottery-results.json"
            csv_file = self.data_dir / "lottery-results.csv"
            
            health = {
                'last_run': last_status,
                'data_files': {
                    'json_exists': json_file.exists(),
                    'csv_exists': csv_file.exists(),
                    'json_size': json_file.stat().st_size if json_file.exists() else 0,
                    'csv_size': csv_file.stat().st_size if csv_file.exists() else 0
                },
                'system_status': 'healthy' if last_status and last_status.get('status') == 'SUCCESS' else 'warning'
            }
            
            return health
            
        except Exception as e:
            logger.error("Lỗi lấy system health", error=str(e))
            return {'error': str(e)}


def main():
    """Test notification system"""
    notifier = NotificationSystem()
    
    # Test thông báo thành công
    test_data = {
        'date': '08/01/2025',
        'source': 'Test Source',
        'results': {
            'Giải Đặc Biệt': ['12345'],
            'Giải Nhất': ['67890']
        }
    }
    
    notifier.notify_success(test_data)
    
    # Hiển thị system health
    health = notifier.get_system_health()
    logger.info("System health", health=health)


if __name__ == "__main__":
    main()
