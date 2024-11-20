# Project Manager

Một ứng dụng web quản lý dự án được xây dựng với Django và React, cho phép người dùng quản lý và theo dõi các dự án và nhiệm vụ một cách hiệu quả.

## Tính năng

- 🔐 Xác thực và phân quyền người dùng
- 📊 Quản lý dự án và nhiệm vụ theo cấu trúc cây
- 👥 Quản lý thành viên và phân quyền chi tiết
- 📈 Theo dõi tiến độ tự động
- 📅 Quản lý thời gian và deadline
- 📨 Hệ thống thông báo và lời mời
- 🎨 Giao diện người dùng thân thiện
- 🌗 Hỗ trợ giao diện sáng/tối
- 📱 Responsive trên mọi thiết bị

## Công nghệ sử dụng

### Backend
- Django
- Django REST Framework
- Celery
- Redis
- JWT Authentication
- SQLite

### Frontend
- React
- Next.js
- TypeScript
- Tailwind CSS
- Zustand
- React Query

## Cài đặt

### Backend Requirements
```bash
# Clone repository
git clone https://github.com/your-username/project-manager-backend.git

# Tạo môi trường ảo
python -m venv env
source env/bin/activate  # Linux/Mac
env\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r [requirements.txt](http://_vscodecontentref_/1)

# Tạo database
python [manage.py](http://_vscodecontentref_/2) migrate

# Chạy development server
python [manage.py](http://_vscodecontentref_/3) runserver


git clone https://github.com/your-username/project-manager-frontend.git

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
