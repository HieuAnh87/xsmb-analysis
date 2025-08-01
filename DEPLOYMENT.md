# 🚀 Hướng dẫn Triển khai - Northern Vietnam Lottery Analysis System

## 📋 **Bước 1: Tạo Repository trên GitHub**

1. **Đi tới GitHub và tạo repository mới:**
   - URL: https://github.com/new
   - Repository name: `xsmb-analysis` (hoặc tên bạn muốn)
   - Description: `🎲 Hệ thống Thu thập và Phân tích Xổ số Miền Bắc tự động`
   - Chọn **Public** (để sử dụng GitHub Actions miễn phí)
   - **KHÔNG** tích các option: Add README, .gitignore, license (chúng ta đã có)
   - Click **Create repository**

2. **Sao chép URL repository:**
   ```
   https://github.com/YOUR_USERNAME/xsmb-analysis.git
   ```

## 🔗 **Bước 2: Kết nối và Push Code**

Chạy các lệnh sau trong terminal (thay `YOUR_USERNAME` bằng username GitHub của bạn):

```bash
# Thêm remote origin
git remote add origin https://github.com/YOUR_USERNAME/xsmb-analysis.git

# Push code lên GitHub
git branch -M main
git push -u origin main
```

## ⚙️ **Bước 3: Cấu hình GitHub Actions**

### 3.1 Kích hoạt GitHub Actions
1. Vào repository trên GitHub
2. Click tab **Actions**
3. Click **I understand my workflows, go ahead and enable them**

### 3.2 Cấu hình GitHub Secrets (Tùy chọn - cho notifications)

Vào **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

#### Email Notifications:
- `SMTP_SERVER`: `smtp.gmail.com`
- `SMTP_PORT`: `587`
- `SENDER_EMAIL`: `your-email@gmail.com`
- `SENDER_PASSWORD`: `your-app-password` (không phải mật khẩu thường)
- `RECIPIENT_EMAILS`: `recipient1@gmail.com,recipient2@gmail.com`

#### Discord Webhook:
- `DISCORD_WEBHOOK_URL`: `https://discord.com/api/webhooks/...`

#### Slack Webhook:
- `SLACK_WEBHOOK_URL`: `https://hooks.slack.com/services/...`

## 🕐 **Bước 4: Kiểm tra Workflow**

### 4.1 Chạy thử thủ công
1. Vào tab **Actions**
2. Click workflow **"Thu thập kết quả xổ số miền Bắc hàng ngày"**
3. Click **Run workflow** → **Run workflow**

### 4.2 Xem kết quả
- Workflow sẽ chạy và tạo dữ liệu trong thư mục `data/`
- Kiểm tra logs để xem chi tiết quá trình

## 📅 **Bước 5: Lịch chạy tự động**

Workflow sẽ tự động chạy:
- **Thời gian**: 7:00 PM hàng ngày (giờ Việt Nam)
- **Cron**: `0 12 * * *` (12:00 PM UTC = 7:00 PM Vietnam)

## 📊 **Bước 6: Xem kết quả**

Sau khi workflow chạy thành công:

### Dữ liệu được tạo:
- `data/lottery-results.json` - Dữ liệu JSON
- `data/lottery-results.csv` - Dữ liệu CSV  
- `data/analytics-report.json` - Báo cáo phân tích
- `data/system.log` - Logs hệ thống

### Xem trên GitHub:
1. Vào repository
2. Browse thư mục `data/`
3. Click vào các file để xem nội dung

## 🔧 **Troubleshooting**

### Workflow không chạy:
- Kiểm tra tab Actions có được enable
- Kiểm tra syntax file `.github/workflows/lottery-collector.yml`
- Xem logs trong Actions để debug

### Không thu thập được dữ liệu:
- Website nguồn có thể thay đổi cấu trúc
- Cần implement Selenium cho JavaScript sites
- Kiểm tra logs để xem lỗi cụ thể

### Notifications không hoạt động:
- Kiểm tra GitHub Secrets đã được cấu hình đúng
- Verify webhook URLs và credentials

## 📈 **Nâng cấp sau triển khai**

### 1. Cải thiện thu thập dữ liệu:
```bash
# Thêm Selenium vào requirements.txt
echo "selenium==4.15.2" >> requirements.txt
echo "webdriver-manager==4.0.1" >> requirements.txt
```

### 2. Thêm website dashboard:
- Tạo GitHub Pages
- Sử dụng Chart.js để visualize data
- Tự động update từ JSON data

### 3. Database integration:
- Kết nối PostgreSQL/MongoDB
- Lưu trữ long-term data
- API endpoints cho external access

## 🎯 **Kết quả mong đợi**

Sau khi triển khai thành công:
- ✅ Workflow chạy tự động hàng ngày
- ✅ Dữ liệu được thu thập và lưu trữ
- ✅ Analytics reports được tạo
- ✅ Notifications hoạt động (nếu cấu hình)
- ✅ Historical data được maintain

## 📞 **Hỗ trợ**

Nếu gặp vấn đề:
1. Kiểm tra [Issues](../../issues) trong repository
2. Xem logs trong GitHub Actions
3. Tạo issue mới với mô tả chi tiết

---

**🎉 Chúc mừng! Hệ thống của bạn đã sẵn sàng hoạt động!** 🎲
