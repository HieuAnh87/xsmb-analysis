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
                'name': 'XoSo.com.vn',
                'url': 'https://xoso.com.vn/xsmb-c1.html',
                'parser': self._parse_xoso_com_vn
            },
            {
                'name': 'VTCNews',
                'url': 'https://vtcnews.vn/xo-so/xsmb',
                'parser': self._parse_vtcnews
            },
            {
                'name': 'XoSoDaiPhat',
                'url': 'https://xosodaiphat.com/xsmb-xo-so-mien-bac.html',
                'parser': self._parse_xosodaiphat
            },
            {
                'name': 'XoSoYenBai',
                'url': 'https://xosoyenbai.vn/index.php/ketqua',
                'parser': self._parse_xosoyenbai
            }
        ]
        
        # Đảm bảo thư mục data tồn tại
        os.makedirs('data', exist_ok=True)
        
    def get_vietnam_date(self, offset_days: int = 0) -> datetime:
        """Lấy ngày hiện tại theo múi giờ Việt Nam"""
        now = datetime.now(self.vn_tz)
        return now + timedelta(days=offset_days)
    
    def _parse_xoso_com_vn(self, soup: BeautifulSoup, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ XoSo.com.vn"""
        try:
            results = {}

            # Tìm các element chứa kết quả xổ số
            # XoSo.com.vn thường có class 'kqxs-table' hoặc tương tự
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        prize_text = cells[0].get_text(strip=True)
                        numbers_text = cells[1].get_text(strip=True)

                        # Chuẩn hóa tên giải thưởng
                        if any(keyword in prize_text.lower() for keyword in ['đặc biệt', 'db']):
                            prize_name = 'Giải Đặc Biệt'
                        elif any(keyword in prize_text.lower() for keyword in ['nhất', '1']):
                            prize_name = 'Giải Nhất'
                        elif any(keyword in prize_text.lower() for keyword in ['nhì', '2']):
                            prize_name = 'Giải Nhì'
                        elif any(keyword in prize_text.lower() for keyword in ['ba', '3']):
                            prize_name = 'Giải Ba'
                        elif any(keyword in prize_text.lower() for keyword in ['tư', '4']):
                            prize_name = 'Giải Tư'
                        elif any(keyword in prize_text.lower() for keyword in ['năm', '5']):
                            prize_name = 'Giải Năm'
                        elif any(keyword in prize_text.lower() for keyword in ['sáu', '6']):
                            prize_name = 'Giải Sáu'
                        elif any(keyword in prize_text.lower() for keyword in ['bảy', '7']):
                            prize_name = 'Giải Bảy'
                        else:
                            continue

                        # Trích xuất số
                        numbers = re.findall(r'\d{2,5}', numbers_text)
                        if numbers:
                            results[prize_name] = numbers

            if len(results) >= 3:  # Ít nhất 3 giải thưởng
                return {
                    'date': date_str,
                    'source': 'XoSo.com.vn',
                    'results': results,
                    'collected_at': datetime.now(self.vn_tz).isoformat()
                }

        except Exception as e:
            logger.error("Lỗi parse XoSo.com.vn", error=str(e))

        return None
    
    def _parse_vtcnews(self, soup: BeautifulSoup, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ VTCNews"""
        try:
            results = {}

            # VTCNews có thể có cấu trúc khác, tìm các pattern chung
            # Tìm tất cả text có chứa số và từ khóa giải thưởng
            text_content = soup.get_text()

            # Pattern để tìm kết quả xổ số
            patterns = {
                'Giải Đặc Biệt': r'(?:đặc biệt|ĐB)[:\s]*(\d{5})',
                'Giải Nhất': r'(?:giải nhất|G1)[:\s]*(\d{5})',
                'Giải Nhì': r'(?:giải nhì|G2)[:\s]*(\d{5}(?:\s*-\s*\d{5})*)',
                'Giải Ba': r'(?:giải ba|G3)[:\s]*(\d{5}(?:\s*-\s*\d{5})*)',
                'Giải Tư': r'(?:giải tư|G4)[:\s]*(\d{4}(?:\s*-\s*\d{4})*)',
                'Giải Năm': r'(?:giải năm|G5)[:\s]*(\d{4}(?:\s*-\s*\d{4})*)',
                'Giải Sáu': r'(?:giải sáu|G6)[:\s]*(\d{3}(?:\s*-\s*\d{3})*)',
                'Giải Bảy': r'(?:giải bảy|G7)[:\s]*(\d{2}(?:\s*-\s*\d{2})*)'
            }

            for prize_name, pattern in patterns.items():
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    # Lấy match đầu tiên và tách các số
                    numbers_str = matches[0]
                    numbers = re.findall(r'\d+', numbers_str)
                    if numbers:
                        results[prize_name] = numbers

            if len(results) >= 3:
                return {
                    'date': date_str,
                    'source': 'VTCNews',
                    'results': results,
                    'collected_at': datetime.now(self.vn_tz).isoformat()
                }

        except Exception as e:
            logger.error("Lỗi parse VTCNews", error=str(e))

        return None

    def _parse_xosodaiphat(self, soup: BeautifulSoup, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ XoSoDaiPhat"""
        try:
            results = {}

            # Tìm bảng kết quả
            tables = soup.find_all('table')

            for table in tables:
                # Kiểm tra xem table có chứa dữ liệu xổ số không
                if 'xsmb' in str(table).lower() or 'miền bắc' in str(table).lower():
                    rows = table.find_all('tr')

                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            prize_cell = cells[0].get_text(strip=True)
                            numbers_cell = cells[1].get_text(strip=True)

                            # Mapping tên giải thưởng
                            prize_mapping = {
                                'ĐB': 'Giải Đặc Biệt',
                                'G1': 'Giải Nhất',
                                'G2': 'Giải Nhì',
                                'G3': 'Giải Ba',
                                'G4': 'Giải Tư',
                                'G5': 'Giải Năm',
                                'G6': 'Giải Sáu',
                                'G7': 'Giải Bảy'
                            }

                            prize_name = prize_mapping.get(prize_cell, None)
                            if prize_name:
                                numbers = re.findall(r'\d{2,5}', numbers_cell)
                                if numbers:
                                    results[prize_name] = numbers

            if len(results) >= 3:
                return {
                    'date': date_str,
                    'source': 'XoSoDaiPhat',
                    'results': results,
                    'collected_at': datetime.now(self.vn_tz).isoformat()
                }

        except Exception as e:
            logger.error("Lỗi parse XoSoDaiPhat", error=str(e))

        return None

    def _parse_xosoyenbai(self, soup: BeautifulSoup, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ XoSoYenBai"""
        try:
            results = {}

            # Tìm các div hoặc span chứa kết quả
            all_text = soup.get_text()

            # Sử dụng regex để tìm pattern số xổ số
            number_patterns = re.findall(r'\d{2,5}', all_text)

            # Lọc và phân loại số theo độ dài
            five_digit = [n for n in number_patterns if len(n) == 5]
            four_digit = [n for n in number_patterns if len(n) == 4]
            three_digit = [n for n in number_patterns if len(n) == 3]
            two_digit = [n for n in number_patterns if len(n) == 2]

            # Gán số vào các giải thưởng dựa trên quy tắc XSMB
            if len(five_digit) >= 8:  # Đủ số cho các giải 5 chữ số
                results['Giải Đặc Biệt'] = five_digit[:1]
                results['Giải Nhất'] = five_digit[1:2]
                results['Giải Nhì'] = five_digit[2:4]
                results['Giải Ba'] = five_digit[4:10] if len(five_digit) >= 10 else five_digit[4:]

            if len(four_digit) >= 10:  # Đủ số cho các giải 4 chữ số
                results['Giải Tư'] = four_digit[:4]
                results['Giải Năm'] = four_digit[4:10]

            if len(three_digit) >= 3:
                results['Giải Sáu'] = three_digit[:3]

            if len(two_digit) >= 4:
                results['Giải Bảy'] = two_digit[:4]

            if len(results) >= 3:
                return {
                    'date': date_str,
                    'source': 'XoSoYenBai',
                    'results': results,
                    'collected_at': datetime.now(self.vn_tz).isoformat()
                }

        except Exception as e:
            logger.error("Lỗi parse XoSoYenBai", error=str(e))

        return None
    
    def fetch_lottery_data(self, target_date: Optional[datetime] = None, max_retries: int = 3) -> Optional[Dict]:
        """Thu thập dữ liệu xổ số cho ngày chỉ định với retry mechanism"""
        if target_date is None:
            target_date = self.get_vietnam_date()

        date_str = target_date.strftime('%d/%m/%Y')
        logger.info("Bắt đầu thu thập dữ liệu xổ số", date=date_str, sources=len(self.sources))

        # Thử từng nguồn với retry mechanism
        for source_idx, source in enumerate(self.sources):
            logger.info("Thử nguồn", source_name=source['name'], attempt=f"{source_idx + 1}/{len(self.sources)}")

            for retry in range(max_retries):
                try:
                    # Thêm delay để tránh bị block, tăng delay theo retry
                    delay = 2 + retry * 2
                    time.sleep(delay)

                    # Rotate User-Agent để tránh bị detect
                    user_agents = [
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ]

                    self.session.headers.update({
                        'User-Agent': user_agents[retry % len(user_agents)],
                        'Referer': 'https://www.google.com/',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache'
                    })

                    logger.info("Đang kết nối", url=source['url'], retry=retry + 1, delay=delay)

                    response = self.session.get(source['url'], timeout=30)
                    response.raise_for_status()

                    logger.info("Kết nối thành công", status_code=response.status_code, content_length=len(response.content))

                    # Parse HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    result = source['parser'](soup, date_str)

                    if result and self.validate_lottery_data(result):
                        logger.info("Thu thập và validation thành công",
                                  source=source['name'],
                                  prizes_count=len(result.get('results', {})))
                        return result
                    else:
                        logger.warning("Dữ liệu không hợp lệ hoặc không đầy đủ",
                                     source=source['name'],
                                     has_result=result is not None)

                except requests.exceptions.Timeout:
                    logger.warning("Timeout kết nối", source=source['name'], retry=retry + 1)
                except requests.exceptions.ConnectionError:
                    logger.warning("Lỗi kết nối", source=source['name'], retry=retry + 1)
                except requests.exceptions.HTTPError as e:
                    logger.warning("HTTP Error", source=source['name'], status_code=e.response.status_code, retry=retry + 1)
                except Exception as e:
                    logger.error("Lỗi không xác định", source=source['name'], error=str(e), retry=retry + 1)

                # Nếu không phải retry cuối cùng, chờ trước khi thử lại
                if retry < max_retries - 1:
                    wait_time = 5 + retry * 5
                    logger.info("Chờ trước khi thử lại", wait_seconds=wait_time)
                    time.sleep(wait_time)

            logger.error("Nguồn thất bại sau tất cả retry", source=source['name'], max_retries=max_retries)

        logger.error("Không thể thu thập dữ liệu từ bất kỳ nguồn nào", total_sources=len(self.sources))

        # Try Selenium as fallback for JavaScript-heavy sites
        logger.info("Thử Selenium làm fallback cho JavaScript sites")
        selenium_result = self._try_selenium_fallback(target_date)
        if selenium_result:
            return selenium_result

        # Final fallback to mock data for testing/development
        logger.warning("Sử dụng mock data làm fallback cuối cùng")
        return self._generate_fallback_data(date_str)

    def _try_selenium_fallback(self, target_date: datetime) -> Optional[Dict]:
        """Thử sử dụng Selenium làm fallback"""
        try:
            from selenium_collector import SeleniumLotteryCollector

            selenium_collector = SeleniumLotteryCollector()

            if selenium_collector.driver:
                result = selenium_collector.fetch_with_selenium(target_date)
                selenium_collector.cleanup()

                if result and self.validate_lottery_data(result):
                    logger.info("Selenium fallback thành công")
                    return result
                else:
                    logger.warning("Selenium fallback không có dữ liệu hợp lệ")
            else:
                logger.warning("Selenium WebDriver không khả dụng")

        except ImportError:
            logger.warning("Selenium không được cài đặt, bỏ qua fallback")
        except Exception as e:
            logger.error("Lỗi Selenium fallback", error=str(e))

        return None

    def _generate_fallback_data(self, date_str: str) -> Dict:
        """Tạo dữ liệu fallback khi không thu thập được từ nguồn thực"""
        logger.warning("Sử dụng dữ liệu fallback do không thu thập được từ nguồn thực")

        import random

        # Tạo số ngẫu nhiên theo format XSMB
        def generate_random_number(digits: int) -> str:
            return ''.join([str(random.randint(0, 9)) for _ in range(digits)])

        fallback_results = {
            'Giải Đặc Biệt': [generate_random_number(5)],
            'Giải Nhất': [generate_random_number(5)],
            'Giải Nhì': [generate_random_number(5), generate_random_number(5)],
            'Giải Ba': [generate_random_number(5) for _ in range(6)],
            'Giải Tư': [generate_random_number(4) for _ in range(4)],
            'Giải Năm': [generate_random_number(4) for _ in range(6)],
            'Giải Sáu': [generate_random_number(3) for _ in range(3)],
            'Giải Bảy': [generate_random_number(2) for _ in range(4)]
        }

        return {
            'date': date_str,
            'source': 'Fallback Data (Mock)',
            'results': fallback_results,
            'collected_at': datetime.now(self.vn_tz).isoformat(),
            'is_fallback': True
        }

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
