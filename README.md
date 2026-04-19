# 🧾 SmartBill Pro v2.0

A comprehensive **Restaurant Billing & Management System** built with Python, Tkinter, and SQLite.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-59%20Passed-brightgreen)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Login System** | Admin/staff authentication with role tracking |
| 📊 **Dashboard** | Real-time revenue stats, recent orders, quick actions |
| 🛒 **POS / Billing** | Table-based ordering, menu search, cart with +/− controls |
| 💰 **Discount & Tax** | Configurable discount %, persistent tax rate |
| 💳 **Payment Methods** | Cash / Card / UPI selection per order |
| 🧾 **Receipts** | Formatted receipts with save-to-file option |
| 📋 **Order History** | Date & table filters, double-click for details |
| 📝 **Menu Manager** | Add, edit, soft-delete menu items |
| 📈 **Analytics** | 4 embedded charts (top items, monthly, category, hourly) |
| ⚙️ **Settings** | Restaurant name, tax rate, tables, currency |
| 📤 **CSV Export** | Export all order data to CSV |
| ⌨️ **Keyboard Shortcuts** | F1-F6 navigation, Ctrl+N, Ctrl+E, Ctrl+Q |
| 💾 **Backup & Restore** | Database backup, restore, and cleanup CLI |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/prasanna-gowd/SmartBill.git
cd SmartBill

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

**Login with:** `admin` / `admin123`

---

## 📁 Project Structure

```
SmartBill/
├── main.py                      # Main application (SmartBillApp class)
├── modules/
│   ├── __init__.py              # Package exports
│   ├── config.py                # Colors, fonts, constants
│   ├── db_manager.py            # Database operations
│   ├── validators.py            # Input validation
│   ├── report_generator.py      # Report generation
│   └── backup_manager.py        # Backup & restore
├── tests/
│   └── test_smartbill.py        # 59 unit tests
├── database/                    # SQLite database (auto-created)
├── reports/                     # Saved receipts & reports
├── setup_guide.html             # Step-by-step setup guide
├── project_documentation.html   # Full project documentation
├── analytics.py                 # Standalone top-items chart
├── monthly_sales.py             # Standalone monthly sales chart
└── datewise_analysis.py         # Date-range analysis GUI
```

---

## 🗄️ Database Schema

| Table | Purpose |
|-------|---------|
| **Users** | Login credentials and roles |
| **Menu** | Items with name, price, category, soft-delete |
| **Orders** | Full order details with discount/tax breakdown |
| **OrderItems** | Individual items per order |
| **Settings** | Key-value configuration store |

---

## 📊 Tech Stack

- **Language:** Python 3.8+
- **GUI:** Tkinter (built-in)
- **Database:** SQLite 3 (built-in)
- **Charts:** Matplotlib (embedded via TkAgg)
- **Export:** CSV module (built-in)

---

## 📖 Documentation

- 📖 **[Setup Guide](setup_guide.html)** — Step-by-step terminal commands to run the project
- 📚 **[Project Documentation](project_documentation.html)** — Complete explanation with architecture, DB schema, and code walkthrough

---

## 📦 Dependencies

| Package | Required? | Purpose |
|---------|-----------|---------|
| `tkinter` | ✅ Built-in | GUI framework |
| `sqlite3` | ✅ Built-in | Database |
| `matplotlib` | ⭐ Recommended | Analytics charts |
| `tkcalendar` | Optional | Date picker (legacy scripts) |

---

## 🧪 Running Tests

```bash
python -m unittest tests.test_smartbill -v
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

---

## 📜 License

This project is open source under the [MIT License](LICENSE).
