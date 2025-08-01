#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module kiểm tra và validation dữ liệu xổ số
Đảm bảo tính chính xác và toàn vẹn của dữ liệu
"""

import json
import csv
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import structlog
from pathlib import Path

logger = structlog.get_logger()


class DataValidator:
    """Kiểm tra và validation dữ liệu xổ số"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.json_file = self.data_dir / "lottery-results.json"
        self.csv_file = self.data_dir / "lottery-results.csv"
        
        # Quy tắc validation cho xổ số miền Bắc
        self.validation_rules = {
            'Giải Đặc Biệt': {'count': 1, 'digits': 5},
            'Giải Nhất': {'count': 1, 'digits': 5},
            'Giải Nhì': {'count': 2, 'digits': 5},
            'Giải Ba': {'count': 6, 'digits': 5},
            'Giải Tư': {'count': 4, 'digits': 4},
            'Giải Năm': {'count': 6, 'digits': 4},
            'Giải Sáu': {'count': 3, 'digits': 3},
            'Giải Bảy': {'count': 4, 'digits': 2}
        }
    
    def validate_number_format(self, number: str, expected_digits: int) -> bool:
        """Kiểm tra format của một số"""
        if not isinstance(number, str):
            number = str(number)
        
        # Kiểm tra chỉ chứa số
        if not re.match(r'^\d+$', number):
            return False
        
        # Kiểm tra số chữ số
        if len(number) != expected_digits:
            return False
        
        return True
    
    def validate_prize_numbers(self, prize_name: str, numbers: List[str]) -> Tuple[bool, List[str]]:
        """Kiểm tra số lượng và format của các số trong một giải"""
        errors = []
        
        if prize_name not in self.validation_rules:
            errors.append(f"Giải thưởng không hợp lệ: {prize_name}")
            return False, errors
        
        rule = self.validation_rules[prize_name]
        expected_count = rule['count']
        expected_digits = rule['digits']
        
        # Kiểm tra số lượng
        if len(numbers) != expected_count:
            errors.append(
                f"{prize_name}: Số lượng không đúng. "
                f"Mong đợi {expected_count}, nhận được {len(numbers)}"
            )
        
        # Kiểm tra format từng số
        for i, number in enumerate(numbers):
            if not self.validate_number_format(number, expected_digits):
                errors.append(
                    f"{prize_name}: Số thứ {i+1} không hợp lệ: {number}. "
                    f"Mong đợi {expected_digits} chữ số"
                )
        
        return len(errors) == 0, errors
    
    def validate_single_record(self, record: Dict) -> Tuple[bool, List[str]]:
        """Kiểm tra một bản ghi dữ liệu"""
        errors = []
        
        # Kiểm tra các trường bắt buộc
        required_fields = ['date', 'source', 'results', 'collected_at']
        for field in required_fields:
            if field not in record:
                errors.append(f"Thiếu trường bắt buộc: {field}")
        
        # Kiểm tra format ngày
        if 'date' in record:
            try:
                datetime.strptime(record['date'], '%d/%m/%Y')
            except ValueError:
                errors.append(f"Format ngày không hợp lệ: {record['date']}")
        
        # Kiểm tra kết quả xổ số
        if 'results' in record:
            results = record['results']
            if not isinstance(results, dict):
                errors.append("Trường 'results' phải là dictionary")
            else:
                for prize_name, numbers in results.items():
                    if not isinstance(numbers, list):
                        errors.append(f"{prize_name}: Danh sách số phải là array")
                        continue
                    
                    is_valid, prize_errors = self.validate_prize_numbers(
                        prize_name, numbers
                    )
                    errors.extend(prize_errors)
        
        return len(errors) == 0, errors
    
    def validate_json_file(self) -> Tuple[bool, List[str]]:
        """Kiểm tra file JSON"""
        errors = []
        
        if not self.json_file.exists():
            errors.append(f"File JSON không tồn tại: {self.json_file}")
            return False, errors
        
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                errors.append("Dữ liệu JSON phải là array")
                return False, errors
            
            logger.info("Bắt đầu kiểm tra JSON", total_records=len(data))
            
            for i, record in enumerate(data):
                is_valid, record_errors = self.validate_single_record(record)
                if not is_valid:
                    errors.extend([f"Bản ghi {i+1}: {error}" for error in record_errors])
            
            if errors:
                logger.error("Tìm thấy lỗi trong JSON", error_count=len(errors))
            else:
                logger.info("JSON hợp lệ", total_records=len(data))
            
        except json.JSONDecodeError as e:
            errors.append(f"Lỗi parse JSON: {e}")
        except Exception as e:
            errors.append(f"Lỗi đọc file JSON: {e}")
        
        return len(errors) == 0, errors
    
    def validate_csv_file(self) -> Tuple[bool, List[str]]:
        """Kiểm tra file CSV"""
        errors = []
        
        if not self.csv_file.exists():
            errors.append(f"File CSV không tồn tại: {self.csv_file}")
            return False, errors
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Kiểm tra headers
                expected_headers = [
                    'date', 'source', 'collected_at',
                    'giai_dac_biet', 'giai_nhat', 'giai_nhi',
                    'giai_ba', 'giai_tu', 'giai_nam', 'giai_sau', 'giai_bay'
                ]
                
                if reader.fieldnames != expected_headers:
                    errors.append("Headers CSV không đúng format")
                
                # Kiểm tra từng dòng
                row_count = 0
                for i, row in enumerate(reader, 1):
                    row_count = i
                    
                    # Kiểm tra ngày
                    if row.get('date'):
                        try:
                            datetime.strptime(row['date'], '%d/%m/%Y')
                        except ValueError:
                            errors.append(f"Dòng {i}: Format ngày không hợp lệ: {row['date']}")
                    
                    # Kiểm tra các giải thưởng
                    prize_checks = [
                        ('giai_dac_biet', 1, 5),
                        ('giai_nhat', 1, 5),
                        ('giai_nhi', 2, 5),
                        ('giai_ba', 6, 5),
                        ('giai_tu', 4, 4),
                        ('giai_nam', 6, 4),
                        ('giai_sau', 3, 3),
                        ('giai_bay', 4, 2)
                    ]
                    
                    for prize_col, expected_count, expected_digits in prize_checks:
                        if row.get(prize_col):
                            numbers = row[prize_col].split(',')
                            numbers = [n.strip() for n in numbers if n.strip()]
                            
                            if len(numbers) != expected_count:
                                errors.append(
                                    f"Dòng {i}, {prize_col}: Số lượng không đúng. "
                                    f"Mong đợi {expected_count}, có {len(numbers)}"
                                )
                            
                            for number in numbers:
                                if not self.validate_number_format(number, expected_digits):
                                    errors.append(
                                        f"Dòng {i}, {prize_col}: Số không hợp lệ: {number}"
                                    )
                
                if errors:
                    logger.error("Tìm thấy lỗi trong CSV", error_count=len(errors))
                else:
                    logger.info("CSV hợp lệ", total_rows=row_count)
                
        except Exception as e:
            errors.append(f"Lỗi đọc file CSV: {e}")
        
        return len(errors) == 0, errors
    
    def validate_all(self) -> bool:
        """Kiểm tra tất cả dữ liệu"""
        logger.info("Bắt đầu validation toàn bộ dữ liệu")
        
        json_valid, json_errors = self.validate_json_file()
        csv_valid, csv_errors = self.validate_csv_file()
        
        all_errors = json_errors + csv_errors
        
        if all_errors:
            logger.error("Validation thất bại", total_errors=len(all_errors))
            for error in all_errors:
                logger.error("Validation error", error=error)
            return False
        else:
            logger.info("Validation thành công - Tất cả dữ liệu hợp lệ")
            return True


def main():
    """Hàm main để chạy validation"""
    validator = DataValidator()
    success = validator.validate_all()
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
