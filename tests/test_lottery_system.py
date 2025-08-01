#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite cho hệ thống xổ số miền Bắc
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path
import sys

# Thêm src vào Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lottery_collector import LotteryCollector
from data_storage import DataStorage
from data_validator import DataValidator
from analytics import LotteryAnalytics
from notification_system import NotificationSystem


class TestLotteryCollector:
    """Test module thu thập dữ liệu"""
    
    def setup_method(self):
        self.collector = LotteryCollector()
    
    def test_vietnam_timezone(self):
        """Test múi giờ Việt Nam"""
        vn_date = self.collector.get_vietnam_date()
        assert vn_date.tzinfo.zone == 'Asia/Ho_Chi_Minh'
    
    def test_validate_lottery_data_valid(self):
        """Test validation dữ liệu hợp lệ"""
        valid_data = {
            'date': '08/01/2025',
            'source': 'Test',
            'results': {
                'Giải Đặc Biệt': ['12345'],
                'Giải Nhất': ['67890'],
                'Giải Nhì': ['11111', '22222']
            },
            'collected_at': datetime.now().isoformat()
        }
        
        assert self.collector.validate_lottery_data(valid_data) == True
    
    def test_validate_lottery_data_invalid(self):
        """Test validation dữ liệu không hợp lệ"""
        invalid_data = {
            'date': '08/01/2025',
            'source': 'Test',
            'results': {
                'Giải Đặc Biệt': ['abc']  # Không phải số
            }
        }
        
        assert self.collector.validate_lottery_data(invalid_data) == False


class TestDataStorage:
    """Test module lưu trữ dữ liệu"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = DataStorage(self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialize_files(self):
        """Test khởi tạo files"""
        assert self.storage.json_file.exists()
        assert self.storage.csv_file.exists()
    
    def test_save_data(self):
        """Test lưu dữ liệu"""
        test_data = {
            'date': '08/01/2025',
            'source': 'Test',
            'results': {
                'Giải Đặc Biệt': ['12345'],
                'Giải Nhất': ['67890']
            },
            'collected_at': datetime.now().isoformat()
        }
        
        result = self.storage.save_data(test_data)
        assert result == True
        
        # Kiểm tra dữ liệu đã được lưu
        with open(self.storage.json_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1
        assert saved_data[0]['date'] == '08/01/2025'
    
    def test_duplicate_prevention(self):
        """Test ngăn chặn dữ liệu trùng lặp"""
        test_data = {
            'date': '08/01/2025',
            'source': 'Test',
            'results': {'Giải Đặc Biệt': ['12345']},
            'collected_at': datetime.now().isoformat()
        }
        
        # Lưu lần đầu
        self.storage.save_data(test_data)
        
        # Lưu lần thứ hai (trùng lặp)
        self.storage.save_data(test_data)
        
        # Kiểm tra chỉ có 1 bản ghi
        with open(self.storage.json_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert len(saved_data) == 1


class TestDataValidator:
    """Test module validation"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.validator = DataValidator(self.temp_dir)
        
        # Tạo dữ liệu test
        test_data = [{
            'date': '08/01/2025',
            'source': 'Test',
            'results': {
                'Giải Đặc Biệt': ['12345'],
                'Giải Nhất': ['67890'],
                'Giải Nhì': ['11111', '22222'],
                'Giải Ba': ['33333', '44444', '55555', '66666', '77777', '88888'],
                'Giải Tư': ['1234', '5678', '9012', '3456'],
                'Giải Năm': ['7890', '1234', '5678', '9012', '3456', '7890'],
                'Giải Sáu': ['123', '456', '789'],
                'Giải Bảy': ['12', '34', '56', '78']
            },
            'collected_at': datetime.now().isoformat()
        }]
        
        with open(self.validator.json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_number_format(self):
        """Test validation format số"""
        assert self.validator.validate_number_format('12345', 5) == True
        assert self.validator.validate_number_format('123', 5) == False
        assert self.validator.validate_number_format('abc', 3) == False
    
    def test_validate_json_file(self):
        """Test validation file JSON"""
        is_valid, errors = self.validator.validate_json_file()
        assert is_valid == True
        assert len(errors) == 0


class TestLotteryAnalytics:
    """Test module phân tích"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.analytics = LotteryAnalytics(self.temp_dir)
        
        # Tạo dữ liệu test
        test_data = [
            {
                'date': '08/01/2025',
                'source': 'Test',
                'results': {
                    'Giải Đặc Biệt': ['12345'],
                    'Giải Nhất': ['67890']
                },
                'collected_at': datetime.now().isoformat()
            },
            {
                'date': '07/01/2025',
                'source': 'Test',
                'results': {
                    'Giải Đặc Biệt': ['54321'],
                    'Giải Nhất': ['09876']
                },
                'collected_at': datetime.now().isoformat()
            }
        ]
        
        with open(self.analytics.json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_data(self):
        """Test tải dữ liệu"""
        data = self.analytics.load_data()
        assert len(data) == 2
        assert data[0]['date'] == '08/01/2025'
    
    def test_extract_all_numbers(self):
        """Test trích xuất tất cả số"""
        data = self.analytics.load_data()
        numbers = self.analytics.extract_all_numbers(data)
        assert '12345' in numbers
        assert '67890' in numbers
        assert len(numbers) == 4
    
    def test_analyze_frequency(self):
        """Test phân tích tần suất"""
        data = self.analytics.load_data()
        result = self.analytics.analyze_frequency(data)
        
        assert 'total_numbers_drawn' in result
        assert 'unique_numbers' in result
        assert 'most_common' in result
        assert result['total_numbers_drawn'] == 4


class TestNotificationSystem:
    """Test hệ thống thông báo"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.notifier = NotificationSystem(self.temp_dir)
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_log_status(self):
        """Test ghi log trạng thái"""
        self.notifier.log_status('SUCCESS', 'Test message', {'key': 'value'})
        
        assert self.notifier.log_file.exists()
        assert self.notifier.status_file.exists()
    
    def test_get_system_health(self):
        """Test lấy thông tin sức khỏe hệ thống"""
        # Tạo status file
        self.notifier.log_status('SUCCESS', 'Test')
        
        health = self.notifier.get_system_health()
        assert 'last_run' in health
        assert 'data_files' in health
        assert 'system_status' in health


def test_integration():
    """Test tích hợp toàn bộ hệ thống"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test data
        test_data = {
            'date': '08/01/2025',
            'source': 'Integration Test',
            'results': {
                'Giải Đặc Biệt': ['12345'],
                'Giải Nhất': ['67890'],
                'Giải Nhì': ['11111', '22222']
            },
            'collected_at': datetime.now().isoformat()
        }
        
        # Test storage
        storage = DataStorage(temp_dir)
        assert storage.save_data(test_data) == True
        
        # Test validation
        validator = DataValidator(temp_dir)
        is_valid, errors = validator.validate_json_file()
        assert is_valid == True
        
        # Test analytics
        analytics = LotteryAnalytics(temp_dir)
        report = analytics.generate_report()
        assert 'frequency_analysis' in report
        
        # Test notification
        notifier = NotificationSystem(temp_dir)
        notifier.notify_success(test_data)
        assert notifier.status_file.exists()
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
