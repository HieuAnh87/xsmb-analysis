#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium-based lottery collector cho các website JavaScript-heavy
"""

import os
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import structlog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logger = structlog.get_logger()


class SeleniumLotteryCollector:
    """Thu thập dữ liệu xổ số sử dụng Selenium cho JavaScript sites"""
    
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
        # JavaScript-heavy sources
        self.js_sources = [
            {
                'name': 'XoSo123',
                'url': 'https://xoso123.com/xsmb',
                'wait_selector': '.kqxs-table',
                'parser': self._parse_xoso123
            },
            {
                'name': 'SoiCauMB',
                'url': 'https://soicaumb.com/xsmb-hom-nay',
                'wait_selector': '.result-table',
                'parser': self._parse_soicaumb
            }
        ]
    
    def setup_driver(self):
        """Cấu hình Chrome driver cho Selenium"""
        try:
            chrome_options = Options()
            
            # Headless mode cho GitHub Actions
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Anti-detection options
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User agent
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Install ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize Selenium WebDriver", error=str(e))
            self.driver = None
    
    def fetch_with_selenium(self, target_date: Optional[datetime] = None) -> Optional[Dict]:
        """Thu thập dữ liệu sử dụng Selenium"""
        if not self.driver:
            logger.error("Selenium WebDriver not available")
            return None
        
        if target_date is None:
            from lottery_collector import LotteryCollector
            collector = LotteryCollector()
            target_date = collector.get_vietnam_date()
        
        date_str = target_date.strftime('%d/%m/%Y')
        logger.info("Starting Selenium data collection", date=date_str)
        
        for source in self.js_sources:
            try:
                logger.info("Trying Selenium source", source_name=source['name'])
                
                # Navigate to page
                self.driver.get(source['url'])
                
                # Wait for page to load
                wait = WebDriverWait(self.driver, 20)
                
                # Wait for specific element
                if source.get('wait_selector'):
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, source['wait_selector'])))
                    except:
                        logger.warning("Wait selector not found, continuing anyway", selector=source['wait_selector'])
                
                # Additional wait for JavaScript to execute
                time.sleep(5)
                
                # Get page source and parse
                page_source = self.driver.page_source
                result = source['parser'](page_source, date_str)
                
                if result:
                    logger.info("Selenium collection successful", source=source['name'])
                    return result
                    
            except Exception as e:
                logger.error("Selenium source failed", source=source['name'], error=str(e))
                continue
        
        logger.error("All Selenium sources failed")
        return None
    
    def _parse_xoso123(self, page_source: str, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ XoSo123"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            results = {}
            
            # Tìm bảng kết quả
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        prize_text = cells[0].get_text(strip=True)
                        numbers_text = cells[1].get_text(strip=True)
                        
                        # Map prize names
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
                        
                        prize_name = prize_mapping.get(prize_text, None)
                        if prize_name:
                            numbers = re.findall(r'\d{2,5}', numbers_text)
                            if numbers:
                                results[prize_name] = numbers
            
            if len(results) >= 3:
                return {
                    'date': date_str,
                    'source': 'XoSo123 (Selenium)',
                    'results': results,
                    'collected_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error("Error parsing XoSo123", error=str(e))
            
        return None
    
    def _parse_soicaumb(self, page_source: str, date_str: str) -> Optional[Dict]:
        """Parse dữ liệu từ SoiCauMB"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            results = {}
            
            # Tìm các element chứa kết quả
            result_divs = soup.find_all('div', class_=lambda x: x and 'result' in x.lower())
            
            for div in result_divs:
                text = div.get_text()
                
                # Extract numbers using regex patterns
                if 'đặc biệt' in text.lower():
                    db_numbers = re.findall(r'đặc biệt[:\s]*(\d{5})', text, re.IGNORECASE)
                    if db_numbers:
                        results['Giải Đặc Biệt'] = [db_numbers[0]]
                
                if 'giải nhất' in text.lower():
                    g1_numbers = re.findall(r'giải nhất[:\s]*(\d{5})', text, re.IGNORECASE)
                    if g1_numbers:
                        results['Giải Nhất'] = [g1_numbers[0]]
            
            # Fallback: extract all numbers and categorize
            if len(results) < 2:
                all_numbers = re.findall(r'\b\d{2,5}\b', soup.get_text())
                five_digit = [n for n in all_numbers if len(n) == 5]
                
                if len(five_digit) >= 8:
                    results['Giải Đặc Biệt'] = five_digit[:1]
                    results['Giải Nhất'] = five_digit[1:2]
                    results['Giải Nhì'] = five_digit[2:4]
                    results['Giải Ba'] = five_digit[4:10] if len(five_digit) >= 10 else five_digit[4:]
            
            if len(results) >= 2:
                return {
                    'date': date_str,
                    'source': 'SoiCauMB (Selenium)',
                    'results': results,
                    'collected_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error("Error parsing SoiCauMB", error=str(e))
            
        return None
    
    def cleanup(self):
        """Đóng WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver closed")
            except Exception as e:
                logger.error("Error closing WebDriver", error=str(e))


def main():
    """Test Selenium collector"""
    collector = SeleniumLotteryCollector()
    
    try:
        result = collector.fetch_with_selenium()
        if result:
            print("✅ Selenium collection successful!")
            print(f"Source: {result['source']}")
            print(f"Date: {result['date']}")
            print(f"Prizes: {len(result.get('results', {}))}")
        else:
            print("❌ Selenium collection failed")
    finally:
        collector.cleanup()


if __name__ == "__main__":
    main()
