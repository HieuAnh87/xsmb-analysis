#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module phân tích dữ liệu xổ số miền Bắc
Cung cấp các thống kê và phân tích pattern
"""

import json
import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import structlog
from pathlib import Path

logger = structlog.get_logger()


class LotteryAnalytics:
    """Phân tích dữ liệu xổ số miền Bắc"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.json_file = self.data_dir / "lottery-results.json"
        self.analytics_file = self.data_dir / "analytics-report.json"
        
    def load_data(self) -> List[Dict]:
        """Tải dữ liệu từ file JSON"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning("Không thể tải dữ liệu", error=str(e))
            return []
    
    def extract_all_numbers(self, data: List[Dict]) -> List[str]:
        """Trích xuất tất cả các số từ dữ liệu"""
        all_numbers = []
        
        for record in data:
            results = record.get('results', {})
            for prize, numbers in results.items():
                if isinstance(numbers, list):
                    all_numbers.extend([str(num) for num in numbers])
        
        return all_numbers
    
    def analyze_frequency(self, data: List[Dict]) -> Dict:
        """Phân tích tần suất xuất hiện của các số"""
        all_numbers = self.extract_all_numbers(data)
        
        if not all_numbers:
            return {'error': 'Không có dữ liệu để phân tích'}
        
        # Đếm tần suất
        frequency = Counter(all_numbers)
        total_draws = len(all_numbers)
        
        # Tính phần trăm
        frequency_percent = {
            num: {
                'count': count,
                'percentage': round((count / total_draws) * 100, 2)
            }
            for num, count in frequency.items()
        }
        
        # Top 10 số xuất hiện nhiều nhất
        most_common = frequency.most_common(10)
        least_common = frequency.most_common()[-10:]
        
        return {
            'total_numbers_drawn': total_draws,
            'unique_numbers': len(frequency),
            'frequency_detail': frequency_percent,
            'most_common': [
                {'number': num, 'count': count, 
                 'percentage': round((count / total_draws) * 100, 2)}
                for num, count in most_common
            ],
            'least_common': [
                {'number': num, 'count': count,
                 'percentage': round((count / total_draws) * 100, 2)}
                for num, count in least_common
            ]
        }
    
    def analyze_by_prize(self, data: List[Dict]) -> Dict:
        """Phân tích theo từng loại giải"""
        prize_analysis = {}
        
        for record in data:
            results = record.get('results', {})
            for prize, numbers in results.items():
                if prize not in prize_analysis:
                    prize_analysis[prize] = []
                
                if isinstance(numbers, list):
                    prize_analysis[prize].extend([str(num) for num in numbers])
        
        # Phân tích tần suất cho từng giải
        result = {}
        for prize, numbers in prize_analysis.items():
            if numbers:
                frequency = Counter(numbers)
                total = len(numbers)
                
                result[prize] = {
                    'total_numbers': total,
                    'unique_numbers': len(frequency),
                    'most_common': [
                        {'number': num, 'count': count,
                         'percentage': round((count / total) * 100, 2)}
                        for num, count in frequency.most_common(5)
                    ],
                    'average_frequency': round(total / len(frequency), 2) if frequency else 0
                }
        
        return result
    
    def analyze_patterns(self, data: List[Dict]) -> Dict:
        """Phân tích các pattern trong số"""
        patterns = {
            'consecutive_numbers': 0,
            'same_ending_digits': defaultdict(int),
            'sum_analysis': [],
            'even_odd_ratio': {'even': 0, 'odd': 0}
        }
        
        all_numbers = self.extract_all_numbers(data)
        
        for num_str in all_numbers:
            try:
                num = int(num_str)
                
                # Phân tích chẵn lẻ
                if num % 2 == 0:
                    patterns['even_odd_ratio']['even'] += 1
                else:
                    patterns['even_odd_ratio']['odd'] += 1
                
                # Phân tích chữ số cuối
                last_digit = num % 10
                patterns['same_ending_digits'][last_digit] += 1
                
                # Tổng các chữ số
                digit_sum = sum(int(digit) for digit in num_str)
                patterns['sum_analysis'].append(digit_sum)
                
            except ValueError:
                continue
        
        # Tính toán thống kê tổng
        if patterns['sum_analysis']:
            patterns['sum_statistics'] = {
                'average': round(sum(patterns['sum_analysis']) / len(patterns['sum_analysis']), 2),
                'min': min(patterns['sum_analysis']),
                'max': max(patterns['sum_analysis']),
                'most_common_sum': Counter(patterns['sum_analysis']).most_common(5)
            }
        
        # Chuyển đổi defaultdict thành dict thường
        patterns['same_ending_digits'] = dict(patterns['same_ending_digits'])
        
        return patterns
    
    def analyze_time_trends(self, data: List[Dict]) -> Dict:
        """Phân tích xu hướng theo thời gian"""
        if not data:
            return {'error': 'Không có dữ liệu'}
        
        # Sắp xếp theo ngày
        sorted_data = sorted(
            data,
            key=lambda x: datetime.strptime(x.get('date', '01/01/1900'), '%d/%m/%Y')
        )
        
        # Phân tích theo tháng
        monthly_stats = defaultdict(lambda: {'count': 0, 'numbers': []})
        
        for record in sorted_data:
            try:
                date_obj = datetime.strptime(record['date'], '%d/%m/%Y')
                month_key = date_obj.strftime('%Y-%m')
                
                monthly_stats[month_key]['count'] += 1
                
                # Thu thập số cho tháng này
                results = record.get('results', {})
                for numbers in results.values():
                    if isinstance(numbers, list):
                        monthly_stats[month_key]['numbers'].extend([str(n) for n in numbers])
                        
            except ValueError:
                continue
        
        # Tính thống kê cho từng tháng
        monthly_analysis = {}
        for month, stats in monthly_stats.items():
            if stats['numbers']:
                frequency = Counter(stats['numbers'])
                monthly_analysis[month] = {
                    'draws_count': stats['count'],
                    'total_numbers': len(stats['numbers']),
                    'unique_numbers': len(frequency),
                    'most_common': frequency.most_common(3)
                }
        
        return {
            'date_range': {
                'earliest': sorted_data[0]['date'],
                'latest': sorted_data[-1]['date']
            },
            'total_draws': len(sorted_data),
            'monthly_analysis': monthly_analysis
        }
    
    def generate_report(self) -> Dict:
        """Tạo báo cáo phân tích tổng hợp"""
        logger.info("Bắt đầu tạo báo cáo phân tích")
        
        data = self.load_data()
        
        if not data:
            return {'error': 'Không có dữ liệu để phân tích'}
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'data_summary': {
                'total_records': len(data),
                'date_range': self.analyze_time_trends(data).get('date_range', {})
            },
            'frequency_analysis': self.analyze_frequency(data),
            'prize_analysis': self.analyze_by_prize(data),
            'pattern_analysis': self.analyze_patterns(data),
            'time_trends': self.analyze_time_trends(data)
        }
        
        # Lưu báo cáo
        try:
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info("Đã tạo báo cáo phân tích", file=str(self.analytics_file))
            
        except Exception as e:
            logger.error("Lỗi lưu báo cáo", error=str(e))
        
        return report
    
    def get_insights(self, report: Dict) -> List[str]:
        """Tạo các insight từ báo cáo phân tích"""
        insights = []
        
        # Insight về tần suất
        freq_analysis = report.get('frequency_analysis', {})
        if 'most_common' in freq_analysis and freq_analysis['most_common']:
            most_common = freq_analysis['most_common'][0]
            insights.append(
                f"Số xuất hiện nhiều nhất: {most_common['number']} "
                f"({most_common['count']} lần, {most_common['percentage']}%)"
            )
        
        # Insight về chẵn lẻ
        pattern_analysis = report.get('pattern_analysis', {})
        even_odd = pattern_analysis.get('even_odd_ratio', {})
        if even_odd:
            total = even_odd.get('even', 0) + even_odd.get('odd', 0)
            if total > 0:
                even_percent = round((even_odd.get('even', 0) / total) * 100, 1)
                insights.append(f"Tỷ lệ số chẵn: {even_percent}%, số lẻ: {100-even_percent}%")
        
        # Insight về xu hướng thời gian
        time_trends = report.get('time_trends', {})
        if 'total_draws' in time_trends:
            insights.append(f"Tổng số lần quay: {time_trends['total_draws']}")
        
        return insights


def main():
    """Hàm main để chạy phân tích"""
    analytics = LotteryAnalytics()
    
    # Tạo báo cáo
    report = analytics.generate_report()
    
    if 'error' in report:
        logger.error("Không thể tạo báo cáo", error=report['error'])
        return False
    
    # Tạo insights
    insights = analytics.get_insights(report)
    
    logger.info("Hoàn thành phân tích dữ liệu")
    for insight in insights:
        logger.info("Insight", message=insight)
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
