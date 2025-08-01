#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module quản lý lưu trữ dữ liệu xổ số
Hỗ trợ format JSON và CSV với khả năng append dữ liệu mới
"""

import json
import csv
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import structlog
from pathlib import Path

logger = structlog.get_logger()


class DataStorage:
    """Quản lý lưu trữ dữ liệu xổ số"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.json_file = self.data_dir / "lottery-results.json"
        self.csv_file = self.data_dir / "lottery-results.csv"
        
        # Khởi tạo files nếu chưa tồn tại
        self._initialize_files()
    
    def _initialize_files(self):
        """Khởi tạo các file dữ liệu nếu chưa tồn tại"""
        # Khởi tạo JSON file
        if not self.json_file.exists():
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info("Đã tạo file JSON mới", file=str(self.json_file))
        
        # Khởi tạo CSV file
        if not self.csv_file.exists():
            self._create_csv_header()
            logger.info("Đã tạo file CSV mới", file=str(self.csv_file))
    
    def _create_csv_header(self):
        """Tạo header cho file CSV"""
        headers = [
            'date', 'source', 'collected_at',
            'giai_dac_biet', 'giai_nhat', 'giai_nhi',
            'giai_ba', 'giai_tu', 'giai_nam', 'giai_sau', 'giai_bay'
        ]
        
        with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    
    def _load_existing_data(self) -> List[Dict]:
        """Tải dữ liệu hiện có từ file JSON"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning("Không thể tải dữ liệu hiện có", error=str(e))
            return []
    
    def _check_duplicate(self, new_data: Dict, existing_data: List[Dict]) -> bool:
        """Kiểm tra dữ liệu trùng lặp"""
        new_date = new_data.get('date')
        new_source = new_data.get('source')
        
        for existing in existing_data:
            if (existing.get('date') == new_date and 
                existing.get('source') == new_source):
                return True
        return False
    
    def save_to_json(self, data: Dict) -> bool:
        """Lưu dữ liệu vào file JSON"""
        try:
            existing_data = self._load_existing_data()
            
            # Kiểm tra trùng lặp
            if self._check_duplicate(data, existing_data):
                logger.info("Dữ liệu đã tồn tại, bỏ qua", 
                           date=data.get('date'), source=data.get('source'))
                return True
            
            # Thêm dữ liệu mới
            existing_data.append(data)
            
            # Sắp xếp theo ngày (mới nhất trước)
            existing_data.sort(
                key=lambda x: datetime.strptime(x.get('date', '01/01/1900'), '%d/%m/%Y'),
                reverse=True
            )
            
            # Lưu file
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            logger.info("Đã lưu dữ liệu vào JSON", 
                       file=str(self.json_file), total_records=len(existing_data))
            return True
            
        except Exception as e:
            logger.error("Lỗi lưu JSON", error=str(e))
            return False
    
    def _flatten_lottery_data(self, data: Dict) -> Dict:
        """Chuyển đổi dữ liệu xổ số thành format phẳng cho CSV"""
        flattened = {
            'date': data.get('date', ''),
            'source': data.get('source', ''),
            'collected_at': data.get('collected_at', ''),
        }
        
        results = data.get('results', {})
        
        # Mapping các giải thưởng
        prize_mapping = {
            'Giải Đặc Biệt': 'giai_dac_biet',
            'Giải Nhất': 'giai_nhat',
            'Giải Nhì': 'giai_nhi',
            'Giải Ba': 'giai_ba',
            'Giải Tư': 'giai_tu',
            'Giải Năm': 'giai_nam',
            'Giải Sáu': 'giai_sau',
            'Giải Bảy': 'giai_bay'
        }
        
        for prize_vn, prize_en in prize_mapping.items():
            numbers = results.get(prize_vn, [])
            flattened[prize_en] = ','.join(map(str, numbers)) if numbers else ''
        
        return flattened
    
    def save_to_csv(self, data: Dict) -> bool:
        """Lưu dữ liệu vào file CSV"""
        try:
            flattened_data = self._flatten_lottery_data(data)
            
            # Kiểm tra xem dữ liệu đã tồn tại chưa
            if self.csv_file.exists():
                df_existing = pd.read_csv(self.csv_file)
                
                # Kiểm tra trùng lặp
                duplicate_mask = (
                    (df_existing['date'] == flattened_data['date']) &
                    (df_existing['source'] == flattened_data['source'])
                )
                
                if duplicate_mask.any():
                    logger.info("Dữ liệu CSV đã tồn tại, bỏ qua",
                               date=flattened_data['date'],
                               source=flattened_data['source'])
                    return True
            
            # Append dữ liệu mới
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data.keys())
                writer.writerow(flattened_data)
            
            logger.info("Đã lưu dữ liệu vào CSV", file=str(self.csv_file))
            return True
            
        except Exception as e:
            logger.error("Lỗi lưu CSV", error=str(e))
            return False
    
    def save_data(self, data: Dict) -> bool:
        """Lưu dữ liệu vào cả JSON và CSV"""
        json_success = self.save_to_json(data)
        csv_success = self.save_to_csv(data)
        
        if json_success and csv_success:
            logger.info("Lưu dữ liệu thành công vào cả JSON và CSV")
            return True
        else:
            logger.error("Lỗi lưu dữ liệu", 
                        json_success=json_success, csv_success=csv_success)
            return False
    
    def get_statistics(self) -> Dict:
        """Lấy thống kê về dữ liệu đã lưu"""
        try:
            data = self._load_existing_data()
            
            if not data:
                return {'total_records': 0, 'date_range': None}
            
            dates = [item.get('date') for item in data if item.get('date')]
            date_objects = [
                datetime.strptime(date, '%d/%m/%Y') for date in dates
            ]
            
            return {
                'total_records': len(data),
                'date_range': {
                    'earliest': min(date_objects).strftime('%d/%m/%Y'),
                    'latest': max(date_objects).strftime('%d/%m/%Y')
                } if date_objects else None,
                'sources': list(set(item.get('source') for item in data))
            }
            
        except Exception as e:
            logger.error("Lỗi lấy thống kê", error=str(e))
            return {'error': str(e)}
