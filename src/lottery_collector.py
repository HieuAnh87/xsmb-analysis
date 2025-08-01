#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thu thập kết quả xổ số miền Bắc từ website chính thức
Tác giả: GitHub Actions Bot
Ngày tạo: 2025-01-08
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import logging
from datetime import datetime, timedelta
import pytz
import time
import re
from typing import Dict, List, Optional, Tuple
import structlog

# Cấu hình logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class LotteryCollector:
    """Thu thập dữ liệu xổ số miền Bắc"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Múi giờ Việt Nam
        self.vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        
        # URLs để scrape (sử dụng nhiều nguồn để đảm bảo độ tin cậy)
        self.sources = [
            {
                'name': 'XSMB.com.vn',
                'url': 'https://xsmb.com.vn/',
                'parser': self._parse_xsmb_com_vn
            },
            {
                'name': 'KetQua.net',
                'url': 'https://ketqua.net/xo-so-mien-bac.html',
                'parser': self._parse_ketqua_net
            }
        ]
        
        # Đảm bảo thư mục data tồn tại
        os.makedirs('data', exist_ok=True)
        
    def get_vietnam_date(self, offset_days: int = 0) -> datetime:
        """Lấy ngày hiện tại theo múi giờ Việt Nam"""
        now = datetime.now(self.vn_tz)
        return now + timedelta(days=offset_days)
    
    def _parse_xsmb_com_vn(self, soup: BeautifulSoup, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ XSMB.com.vn"""
        try:
            results = {}
            
            # Tìm bảng kết quả
            table = soup.find('table', class_='table-result')
            if not table:
                logger.warning("Không tìm thấy bảng kết quả trên XSMB.com.vn")
                return None
            
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    prize_name = cells[0].get_text(strip=True)
                    numbers = cells[1].get_text(strip=True)
                    
                    if prize_name and numbers:
                        # Làm sạch và chuẩn hóa dữ liệu
                        numbers = re.findall(r'\d+', numbers)
                        if numbers:
                            results[prize_name] = numbers
            
            if results:
                return {
                    'date': date_str,
                    'source': 'XSMB.com.vn',
                    'results': results,
                    'collected_at': datetime.now(self.vn_tz).isoformat()
                }
                
        except Exception as e:
            logger.error("Lỗi parse XSMB.com.vn", error=str(e))
            
        return None
    
    def _parse_ketqua_net(self, soup: BeautifulSoup, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ KetQua.net"""
        try:
            results = {}
            
            # Tìm container kết quả
            result_div = soup.find('div', class_='kqxs-content')
            if not result_div:
                logger.warning("Không tìm thấy kết quả trên KetQua.net")
                return None
            
            # Parse các giải thưởng
            prize_rows = result_div.find_all('div', class_='row-prize')
            for row in prize_rows:
                prize_label = row.find('div', class_='prize-label')
                prize_numbers = row.find('div', class_='prize-numbers')
                
                if prize_label and prize_numbers:
                    prize_name = prize_label.get_text(strip=True)
                    numbers = re.findall(r'\d+', prize_numbers.get_text())
                    
                    if numbers:
                        results[prize_name] = numbers
            
            if results:
                return {
                    'date': date_str,
                    'source': 'KetQua.net',
                    'results': results,
                    'collected_at': datetime.now(self.vn_tz).isoformat()
                }
                
        except Exception as e:
            logger.error("Lỗi parse KetQua.net", error=str(e))
            
        return None
    
    def fetch_lottery_data(self, target_date: Optional[datetime] = None) -> Optional[Dict]:
        """Thu thập dữ liệu xổ số cho ngày chỉ định"""
        if target_date is None:
            target_date = self.get_vietnam_date()
        
        date_str = target_date.strftime('%d/%m/%Y')
        logger.info("Bắt đầu thu thập dữ liệu xổ số", date=date_str)
        
        for source in self.sources:
            try:
                logger.info("Thử nguồn", source_name=source['name'])
                
                # Thêm delay để tránh bị block
                time.sleep(2)
                
                response = self.session.get(source['url'], timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                result = source['parser'](soup, date_str)
                
                if result:
                    logger.info("Thu thập thành công", source=source['name'])
                    return result
                    
            except requests.RequestException as e:
                logger.error("Lỗi kết nối", source=source['name'], error=str(e))
            except Exception as e:
                logger.error("Lỗi không xác định", source=source['name'], error=str(e))
        
        logger.error("Không thể thu thập dữ liệu từ bất kỳ nguồn nào")
        return None

    def validate_lottery_data(self, data: Dict) -> bool:
        """Kiểm tra tính hợp lệ của dữ liệu xổ số"""
        if not data or 'results' not in data:
            return False

        results = data['results']

        # Kiểm tra các giải thưởng cơ bản
        required_prizes = ['Giải Đặc Biệt', 'Giải Nhất', 'Giải Nhì']
        for prize in required_prizes:
            if prize not in results:
                logger.warning("Thiếu giải thưởng", prize=prize)
                return False

        # Kiểm tra format số
        for prize, numbers in results.items():
            for number in numbers:
                if not re.match(r'^\d+$', str(number)):
                    logger.warning("Số không hợp lệ",
                                   prize=prize, number=number)
                    return False

        return True


def main():
    """Hàm main để chạy thu thập dữ liệu"""
    collector = LotteryCollector()

    # Thu thập dữ liệu cho ngày hôm nay
    data = collector.fetch_lottery_data()

    if data and collector.validate_lottery_data(data):
        # Import data storage module
        from data_storage import DataStorage
        storage = DataStorage()

        # Lưu dữ liệu
        storage.save_data(data)
        logger.info("Hoàn thành thu thập và lưu trữ dữ liệu")

        return True
    else:
        logger.error("Thu thập dữ liệu thất bại hoặc dữ liệu không hợp lệ")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
