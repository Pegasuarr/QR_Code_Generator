# 📱 QR Code Generator Pro

A sleek, modern QR code generator built with Python. Features both a desktop GUI powered by **CustomTkinter** and a local **Web application**.

---

## ✨ Features

- **Multiple Data Types**:
  - 🌐 **Websites & Links** (auto-appends `https://`)
  - 📞 **Telephone Numbers** (formats with `tel:` for one-tap calling)
  - 🔢 **Numeric IDs & Codes**
  - 📝 **Plain Text** (multiline notes, messages)
  - 📶 **Wi-Fi Networks** (one-scan connect for WPA/WPA2, WEP, or Open networks)
- **Customization**:
  - Color palettes (Classic Black, Royal Blue, Emerald Green, Neon Purple, Crimson, or custom hex)
  - Background choices (Pure White, Soft Gray, Transparent background)
  - Configurable error correction levels (Low, Medium, Quartile, High)
- **Export Options**:
  - 💾 **Save Image**: Export high-resolution images (`.png`, `.jpg`, `.webp`)
  - 📋 **Copy to Clipboard**: One-click copy directly to system clipboard for pasting into Word, Photoshop, WhatsApp, or Discord

---

## 🚀 Quick Start

### 1. Requirements
Make sure you have Python 3.10+ installed along with the required libraries:

```bash
pip install customtkinter pillow qrcode
```

### 2. Run the Desktop App
```bash
python app.py
```
*Or simply double-click [run.bat](run.bat) / run `.\run.ps1`.*

### 3. Run the Web App (Optional)
```bash
python web_app.py
```
*Opens an interactive browser-based generator at `http://127.0.0.1:5000`.*

---

## 📂 Project Structure

```text
Qr_code_generator/
├── app.py             # Desktop application (CustomTkinter)
├── web_app.py         # Browser/web interface (HTTP server)
├── run.bat            # Quick launcher for Windows Command Prompt
├── run.ps1            # Quick launcher for PowerShell
└── lib/               # Supporting assets & libraries
```

---

## ⌨️ Shortcuts
- <kbd>Enter</kbd> : Instantly generates the QR code.
- <kbd>Paste</kbd> / <kbd>Clear</kbd> : Quick input helper buttons.
