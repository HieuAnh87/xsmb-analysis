# 🎲 Hệ thống Thu thập và Phân tích Xổ số Miền Bắc

Công cụ tự động thu thập và phân tích kết quả xổ số miền Bắc hàng ngày sử dụng GitHub Actions.

## ✨ Tính năng chính

- 🕰️ **Tự động hóa hoàn toàn**: Chạy tự động lúc 19:00 hàng ngày (giờ Việt Nam)
- 🌐 **Thu thập đa nguồn**: Scrape từ nhiều website uy tín để đảm bảo độ chính xác
- 📊 **Lưu trữ đa định dạng**: Hỗ trợ JSON và CSV cho việc phân tích dễ dàng
- 🔍 **Validation dữ liệu**: Kiểm tra tính hợp lệ và toàn vẹn của dữ liệu
- 📈 **Phân tích thông minh**: Thống kê tần suất, pattern recognition, xu hướng
- 🔔 **Thông báo real-time**: Cảnh báo qua Discord, Slack, Email
- 🌏 **Hỗ trợ múi giờ**: Xử lý chính xác múi giờ Việt Nam (UTC+7)

## 🏗️ Cấu trúc dự án

```
xsmb-analysis/
├── .github/workflows/
│   └── lottery-collector.yml    # GitHub Actions workflow
├── src/
│   ├── lottery_collector.py     # Module thu thập dữ liệu
│   ├── data_storage.py         # Module lưu trữ dữ liệu
│   ├── data_validator.py       # Module validation
│   ├── analytics.py            # Module phân tích
│   └── notification_system.py  # Hệ thống thông báo
├── data/
│   ├── lottery-results.json    # Dữ liệu JSON
│   ├── lottery-results.csv     # Dữ liệu CSV
│   └── analytics-report.json   # Báo cáo phân tích
├── requirements.txt            # Dependencies Python
└── README.md                   # Tài liệu này
```

## 🚀 Cài đặt và Cấu hình

### 1. Fork Repository

1. Fork repository này về GitHub account của bạn
2. Clone về máy local (tùy chọn):

```bash
git clone https://github.com/your-username/xsmb-analysis.git
cd xsmb-analysis
```

### 2. Cấu hình GitHub Secrets (Tùy chọn)

Để sử dụng tính năng thông báo, thêm các secrets sau vào repository:

**Settings → Secrets and variables → Actions → New repository secret**

#### Email Notifications:
- `SMTP_SERVER`: smtp.gmail.com
- `SMTP_PORT`: 587
- `SENDER_EMAIL`: your-email@gmail.com
- `SENDER_PASSWORD`: your-app-password
- `RECIPIENT_EMAILS`: recipient1@gmail.com,recipient2@gmail.com

#### Discord Webhook:
- `DISCORD_WEBHOOK_URL`: https://discord.com/api/webhooks/...

#### Slack Webhook:
- `SLACK_WEBHOOK_URL`: https://hooks.slack.com/services/...

### 3. Kích hoạt GitHub Actions

1. Vào tab **Actions** trong repository
2. Kích hoạt workflows nếu chưa được bật
3. Workflow sẽ tự động chạy lúc 19:00 hàng ngày

## 📋 Cách sử dụng

### Chạy tự động
Workflow sẽ tự động chạy hàng ngày lúc 19:00 (giờ Việt Nam) và:
- Thu thập kết quả xổ số mới nhất
- Validation dữ liệu
- Lưu trữ vào file JSON và CSV
- Tạo báo cáo phân tích
- Gửi thông báo (nếu được cấu hình)

### Chạy thủ công
1. Vào tab **Actions**
2. Chọn workflow "Thu thập kết quả xổ số miền Bắc hàng ngày"
3. Click **Run workflow**

### Chạy local (Development)

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Thu thập dữ liệu
python src/lottery_collector.py

# Validation dữ liệu
python src/data_validator.py

# Tạo báo cáo phân tích
python src/analytics.py
```

## 📊 Format dữ liệu

### JSON Format
```json
[
  {
    "date": "08/01/2025",
    "source": "XSMB.com.vn",
    "collected_at": "2025-01-08T19:30:00+07:00",
    "results": {
      "Giải Đặc Biệt": ["12345"],
      "Giải Nhất": ["67890"],
      "Giải Nhì": ["11111", "22222"],
      "Giải Ba": ["33333", "44444", "55555", "66666", "77777", "88888"],
      "Giải Tư": ["1234", "5678", "9012", "3456"],
      "Giải Năm": ["7890", "1234", "5678", "9012", "3456", "7890"],
      "Giải Sáu": ["123", "456", "789"],
      "Giải Bảy": ["12", "34", "56", "78"]
    }
  }
]
```

### CSV Format
```csv
date,source,collected_at,giai_dac_biet,giai_nhat,giai_nhi,...
08/01/2025,XSMB.com.vn,2025-01-08T19:30:00+07:00,12345,67890,"11111,22222",...
```

## 📈 Báo cáo Phân tích

Hệ thống tự động tạo báo cáo phân tích bao gồm:

- **Thống kê tần suất**: Số xuất hiện nhiều/ít nhất
- **Phân tích theo giải**: Thống kê riêng cho từng loại giải
- **Pattern Recognition**: Phân tích số chẵn/lẻ, chữ số cuối, tổng các chữ số
- **Xu hướng thời gian**: Thống kê theo tháng, quý
- **Insights tự động**: Các nhận xét và đề xuất

## 🔧 Tùy chỉnh

### Thay đổi thời gian chạy
Sửa file `.github/workflows/lottery-collector.yml`:

```yaml
schedule:
  # Chạy lúc 20:00 giờ Việt Nam (13:00 UTC)
  - cron: '0 13 * * *'
```

### Thêm nguồn dữ liệu mới
Sửa file `src/lottery_collector.py`, thêm vào `self.sources`:

```python
{
    'name': 'Nguồn mới',
    'url': 'https://example.com',
    'parser': self._parse_new_source
}
```

### Tùy chỉnh thông báo
Sửa file `src/notification_system.py` để thay đổi format thông báo.

## 🛠️ Troubleshooting

### Workflow không chạy
- Kiểm tra tab Actions có được kích hoạt
- Đảm bảo repository không bị archived
- Kiểm tra syntax của cron expression

### Không thu thập được dữ liệu
- Kiểm tra logs trong GitHub Actions
- Website nguồn có thể thay đổi cấu trúc
- Cần cập nhật parser functions

### Lỗi validation
- Kiểm tra format dữ liệu thu thập
- Có thể website nguồn trả về dữ liệu không đầy đủ
- Xem chi tiết lỗi trong logs

## 📝 Logs và Monitoring

- **GitHub Actions logs**: Chi tiết quá trình chạy
- `data/system.log`: Log hệ thống
- `data/last_run_status.json`: Trạng thái lần chạy cuối
- **Issues tự động**: Tạo issue khi có lỗi

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

Dự án này được phân phối dưới MIT License. Xem file `LICENSE` để biết thêm chi tiết.

## ⚠️ Lưu ý quan trọng

- Dữ liệu chỉ mang tính chất tham khảo
- Không khuyến khích sử dụng cho mục đích cờ bạc
- Tuân thủ các quy định pháp luật về xổ số tại Việt Nam
- Tôn trọng robots.txt và terms of service của các website nguồn

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra [Issues](../../issues) hiện có
2. Tạo issue mới với mô tả chi tiết
3. Cung cấp logs và screenshots nếu có

---

**Được phát triển với ❤️ cho cộng đồng phân tích dữ liệu Việt Nam**
