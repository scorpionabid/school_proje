# Məktəb Nəzarət Sistemi

Bu layihə məktəblərin idarə edilməsi üçün Django əsaslı veb tətbiqdir.

## Xüsusiyyətlər

- Şagird qeydiyyatı və idarə edilməsi
- Sinif idarəetməsi
- Müəllim idarəetməsi
- Davamiyyət izləmə
- Qiymətləndirmə sistemi
- Excel faylından şagird idxalı
- Çoxdilli dəstək (Azərbaycan dili)

## Tələblər

- Python 3.9+
- Django 4.2+
- PostgreSQL (tövsiyə olunur) və ya SQLite3

## Quraşdırma

1. Layihəni klonlayın:
```bash
git clone https://github.com/your-username/mekteb-nezaret.git
cd mekteb-nezaret
```

2. Virtual mühit yaradın və aktivləşdirin:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# və ya
venv\Scripts\activate  # Windows
```

3. Asılılıqları quraşdırın:
```bash
pip install -r requirements.txt
```

4. Mühit dəyişənlərini konfiqurasiya edin:
```bash
cp .env.example .env
# .env faylını redaktə edin
```

5. Verilənlər bazasını miqrasiya edin:
```bash
python manage.py migrate
```

6. Admin istifadəçi yaradın:
```bash
python manage.py createsuperuser
```

7. Serveri işə salın:
```bash
python manage.py runserver
```

## İstifadə

1. Admin panelə daxil olun: `http://localhost:8000/admin/`
2. Məktəb əlavə edin
3. Müəllim və şagirdləri əlavə edin
4. Sinifləri yaradın və şagirdləri siniflərə təyin edin

## Lisenziya

Bu layihə [MIT](LICENSE) lisenziyası altında lisenziyalanıb.

## Müəlliflər

- [Your Name](https://github.com/your-username)

## Töhfə vermək

1. Fork edin
2. Feature branch yaradın (`git checkout -b feature/amazing-feature`)
3. Dəyişiklikləri commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch-i push edin (`git push origin feature/amazing-feature`)
5. Pull Request yaradın
