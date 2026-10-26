"""
Python Web QR Code Generator
A modern web-based QR Code Generator powered by Python backend (http.server).
Supports Website/URL, Telephone numbers, Numeric IDs, Plain Text, and Wi-Fi.
Features 'Generate QR Code' and 'Save Img' with high-resolution output.
"""

import os
import sys
import json
import base64
import io
import re
import urllib.parse
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import Image

PORT = 5000
HOST = "127.0.0.1"


def format_qr_content(raw_data, mode):
    """Formats raw data according to QR code standards."""
    mode = mode.lower()
    raw = raw_data.strip()
    
    if "tel" in mode or "phone" in mode:
        # Standard tel: protocol
        cleaned = re.sub(r"[^\d+]", "", raw)
        return f"tel:{cleaned}"
    elif "web" in mode or "link" in mode or "url" in mode:
        if not re.match(r"^https?://", raw, re.IGNORECASE):
            return f"https://{raw}"
        return raw
    elif "wifi" in mode:
        # Expected raw: JSON or dict string or plain
        return raw
    return raw


def generate_qr_image(data, fg_color="#000000", bg_color="#FFFFFF", ec_level="H", target_size=1000):
    """Generates a PIL Image of the QR code using Python qrcode library."""
    ec_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H
    }
    ec = ec_map.get(ec_level.upper(), ERROR_CORRECT_H)
    
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec,
        box_size=10,
        border=3
    )
    qr.add_data(data)
    qr.make(fit=True)

    is_transparent = (bg_color.lower() in ["transparent", "none", "rgba(0,0,0,0)"])
    actual_bg = "#FFFFFF" if is_transparent else bg_color

    img = qr.make_image(fill_color=fg_color, back_color=actual_bg).convert("RGBA")

    if is_transparent:
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)

    # Resize to target export resolution (NEAREST preserves crisp vector-like pixels)
    img = img.resize((target_size, target_size), Image.Resampling.NEAREST)
    return img


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Python QR Code Generator Pro</title>
  <meta name="description" content="Generate and download custom QR codes for websites, telephone numbers, and numeric IDs using Python.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #0f172a;
      --card-bg: rgba(30, 41, 59, 0.7);
      --card-border: rgba(255, 255, 255, 0.1);
      --input-bg: #1e293b;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent-green: #10b981;
      --accent-green-hover: #059669;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --radius: 16px;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 50%, #020617 100%);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      padding: 24px;
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
      width: 100%;
      flex: 1;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 32px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--card-border);
    }

    .logo-area {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .logo-badge {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
    }

    h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }

    .subtitle {
      color: var(--text-muted);
      font-size: 13px;
    }

    .status-pill {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      font-size: 12px;
      font-weight: 600;
      padding: 6px 14px;
      border-radius: 999px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .grid-layout {
      display: grid;
      grid-template-columns: 1.15fr 0.85fr;
      gap: 28px;
    }

    @media (max-width: 860px) {
      .grid-layout {
        grid-template-columns: 1fr;
      }
    }

    .glass-card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 28px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }

    .section-title {
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #60a5fa;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 24px;
      background: rgba(15, 23, 42, 0.6);
      padding: 6px;
      border-radius: 12px;
      border: 1px solid var(--card-border);
    }

    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 10px;
      font-family: inherit;
      font-size: 13px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.05);
    }

    .tab-btn.active {
      background: var(--primary);
      color: #fff;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
    }

    .form-group {
      margin-bottom: 20px;
    }

    label {
      display: block;
      font-size: 13px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #e2e8f0;
    }

    .input-wrapper {
      position: relative;
    }

    input[type="text"], input[type="tel"], textarea, select {
      width: 100%;
      background: var(--input-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 14px 16px;
      color: #fff;
      font-family: inherit;
      font-size: 14px;
      outline: none;
      transition: all 0.2s ease;
    }

    input:focus, textarea:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
    }

    .hint {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 6px;
    }

    .options-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 24px;
    }

    .color-picker-row {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    input[type="color"] {
      -webkit-appearance: none;
      border: none;
      width: 38px;
      height: 38px;
      border-radius: 8px;
      cursor: pointer;
      background: transparent;
    }

    input[type="color"]::-webkit-color-swatch-wrapper {
      padding: 0;
    }

    input[type="color"]::-webkit-color-swatch {
      border: 1px solid var(--card-border);
      border-radius: 8px;
    }

    /* Hero Buttons */
    .btn-hero-generate {
      width: 100%;
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      color: white;
      border: none;
      padding: 16px 24px;
      font-family: inherit;
      font-size: 16px;
      font-weight: 700;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35);
    }

    .btn-hero-generate:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 28px rgba(59, 130, 246, 0.45);
    }

    .btn-hero-generate:active {
      transform: translateY(0);
    }

    .btn-hero-save {
      width: 100%;
      background: linear-gradient(135deg, #10b981, #059669);
      color: white;
      border: none;
      padding: 16px 24px;
      font-family: inherit;
      font-size: 16px;
      font-weight: 700;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      box-shadow: 0 8px 24px rgba(16, 185, 129, 0.35);
    }

    .btn-hero-save:hover {
      transform: translateY(-2px);
      box-shadow: 0 12px 28px rgba(16, 185, 129, 0.45);
    }

    .preview-box {
      background: #0f172a;
      border: 2px dashed rgba(255, 255, 255, 0.15);
      border-radius: 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      min-height: 330px;
      margin-bottom: 20px;
      position: relative;
    }

    .qr-image-container {
      background: #ffffff;
      padding: 16px;
      border-radius: 12px;
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
    }

    #qrPreviewImg {
      max-width: 240px;
      max-height: 240px;
      width: 100%;
      height: auto;
      display: block;
      image-rendering: pixelated;
    }

    .meta-box {
      width: 100%;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 20px;
      font-size: 12px;
      color: var(--text-muted);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .preview-actions {
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 12px;
    }

    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
      border: 1px solid var(--card-border);
      border-radius: 12px;
      font-family: inherit;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s ease;
    }

    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.14);
    }

    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: #fff;
      padding: 14px 22px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 14px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
      display: none;
      animation: slideUp 0.3s ease;
      z-index: 1000;
    }

    @keyframes slideUp {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-area">
        <div class="logo-badge">⚡</div>
        <div>
          <h1>Python QR Code Generator Pro</h1>
          <p class="subtitle">Generate & download QR codes for Websites, Telephones, and Numbers</p>
        </div>
      </div>
      <div class="status-pill">
        <span>●</span> Python Backend Connected
      </div>
    </header>

    <div class="grid-layout">
      <!-- Left Panel: Input & Options -->
      <div class="glass-card">
        <div class="section-title">1. Choose Content Type</div>
        <div class="tabs">
          <button class="tab-btn active" id="tab-web" onclick="switchTab('web')">🌐 Website</button>
          <button class="tab-btn" id="tab-tel" onclick="switchTab('tel')">📞 Telephone</button>
          <button class="tab-btn" id="tab-num" onclick="switchTab('num')">🔢 Number</button>
          <button class="tab-btn" id="tab-text" onclick="switchTab('text')">📝 Plain Text</button>
        </div>

        <div class="form-group">
          <label id="inputLabel" for="mainInput">Website or Link URL:</label>
          <div class="input-wrapper">
            <input type="text" id="mainInput" placeholder="e.g. https://google.com or example.com" value="https://www.google.com" onkeydown="if(event.key === 'Enter') generateQR()">
          </div>
          <p class="hint" id="inputHint">💡 If you type 'example.com', 'https://' will be prepended automatically.</p>
        </div>

        <div class="section-title">2. Styling Options</div>
        <div class="options-grid">
          <div class="form-group">
            <label>QR Code Color</label>
            <div class="color-picker-row">
              <input type="color" id="fgColor" value="#000000" onchange="generateQR()">
              <span id="fgColorHex" style="font-size: 13px; color: var(--text-muted);">#000000</span>
            </div>
          </div>
          <div class="form-group">
            <label>Background Color</label>
            <div class="color-picker-row">
              <input type="color" id="bgColor" value="#ffffff" onchange="generateQR()">
              <span id="bgColorHex" style="font-size: 13px; color: var(--text-muted);">#FFFFFF</span>
            </div>
          </div>
          <div class="form-group">
            <label for="ecSelect">Error Correction</label>
            <select id="ecSelect" onchange="generateQR()">
              <option value="H" selected>High (30% Recovery)</option>
              <option value="Q">Quartile (25%)</option>
              <option value="M">Medium (15%)</option>
              <option value="L">Low (7%)</option>
            </select>
          </div>
          <div class="form-group">
            <label for="resSelect">Export Resolution</label>
            <select id="resSelect">
              <option value="1200" selected>High Res (1200 x 1200 px)</option>
              <option value="2000">Ultra 4K (2000 x 2000 px)</option>
              <option value="600">Standard (600 x 600 px)</option>
            </select>
          </div>
        </div>

        <!-- HERO BUTTON 1: GENERATE QR CODE -->
        <button class="btn-hero-generate" id="btnGenerate" onclick="generateQR()">
          ✨ Generate QR Code
        </button>
      </div>

      <!-- Right Panel: Preview & Save Img -->
      <div class="glass-card">
        <div class="section-title">Live Preview</div>
        <div class="preview-box">
          <div class="qr-image-container">
            <img id="qrPreviewImg" src="" alt="Generated QR Code">
          </div>
        </div>

        <div class="meta-box" id="metaInfo">
          Encoded: https://www.google.com
        </div>

        <!-- HERO BUTTON 2: SAVE IMG -->
        <div class="preview-actions">
          <button class="btn-hero-save" id="btnSave" onclick="saveImage()">
            💾 Save Img
          </button>
          <button class="btn-secondary" id="btnCopy" onclick="copyImage()">
            📋 Copy
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="toast" id="toast">Message</div>

  <script>
    let activeMode = 'web';
    let currentBase64Image = '';

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 2600);
    }

    function switchTab(mode) {
      activeMode = mode;
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.getElementById('tab-' + mode).classList.add('active');

      const input = document.getElementById('mainInput');
      const label = document.getElementById('inputLabel');
      const hint = document.getElementById('inputHint');

      if (mode === 'web') {
        label.textContent = 'Website or Link URL:';
        input.placeholder = 'e.g., https://example.com or google.com';
        input.value = 'https://www.google.com';
        hint.textContent = "💡 If you type 'example.com', 'https://' will be prepended automatically.";
      } else if (mode === 'tel') {
        label.textContent = 'Telephone Number:';
        input.placeholder = 'e.g., +1 234 567 8900 or 012345678';
        input.value = '+1 234 567 8900';
        hint.textContent = "📞 Formatted as standard 'tel:' URI for one-tap calling when scanned.";
      } else if (mode === 'num') {
        label.textContent = 'Number / Numeric ID / Code:';
        input.placeholder = 'e.g., 9876543210 or Product #4582';
        input.value = '9876543210';
        hint.textContent = "🔢 Perfect for serial numbers, codes, or inventory tracking.";
      } else if (mode === 'text') {
        label.textContent = 'Plain Text Content:';
        input.placeholder = 'Type any text, message, or note...';
        input.value = 'Hello from Python QR Code Generator!';
        hint.textContent = "📝 Freeform text message or information.";
      }

      generateQR();
    }

    async function generateQR() {
      const raw = document.getElementById('mainInput').value.trim();
      if (!raw) {
        showToast('⚠️ Please enter content before generating.');
        return;
      }

      const fg = document.getElementById('fgColor').value;
      const bg = document.getElementById('bgColor').value;
      const ec = document.getElementById('ecSelect').value;
      const size = parseInt(document.getElementById('resSelect').value, 10);

      document.getElementById('fgColorHex').textContent = fg.toUpperCase();
      document.getElementById('bgColorHex').textContent = bg.toUpperCase();

      try {
        const res = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            data: raw,
            mode: activeMode,
            fg_color: fg,
            bg_color: bg,
            ec_level: ec,
            size: size
          })
        });

        const data = await res.json();
        if (data.success) {
          currentBase64Image = data.image;
          document.getElementById('qrPreviewImg').src = data.image;
          document.getElementById('metaInfo').textContent = 'Encoded (' + activeMode + '): ' + data.encoded;
          showToast('✓ QR Code Generated!');
        } else {
          showToast('Error: ' + data.error);
        }
      } catch (err) {
        console.error(err);
        showToast('Error contacting Python server.');
      }
    }

    function saveImage() {
      if (!currentBase64Image) {
        showToast('⚠️ Please generate a QR code first!');
        return;
      }

      // Create download trigger
      const link = document.createElement('a');
      link.href = currentBase64Image;
      link.download = 'qr_code_' + activeMode + '.png';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast('✓ Image downloaded: qr_code_' + activeMode + '.png');
    }

    async function copyImage() {
      if (!currentBase64Image) {
        showToast('⚠️ Generate QR code first!');
        return;
      }
      try {
        const response = await fetch(currentBase64Image);
        const blob = await response.blob();
        await navigator.clipboard.write([
          new ClipboardItem({ 'image/png': blob })
        ]);
        showToast('✓ QR Code copied to clipboard!');
      } catch (err) {
        showToast('Clipboard copy not supported in this browser.');
      }
    }

    // Auto-generate on initial load
    window.onload = () => {
      generateQR();
    };
  </script>
</body>
</html>
"""


class QRRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                payload = json.loads(body)
                raw_data = payload.get("data", "")
                mode = payload.get("mode", "web")
                fg = payload.get("fg_color", "#000000")
                bg = payload.get("bg_color", "#FFFFFF")
                ec = payload.get("ec_level", "H")
                size = payload.get("size", 1000)

                formatted = format_qr_content(raw_data, mode)
                pil_img = generate_qr_image(formatted, fg, bg, ec, size)

                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                b64 = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

                resp = {
                    "success": True,
                    "encoded": formatted,
                    "image": b64
                }
                data_bytes = json.dumps(resp).encode("utf-8")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data_bytes)))
                self.end_headers()
                self.wfile.write(data_bytes)

            except Exception as e:
                err_resp = json.dumps({"success": False, "error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err_resp)))
                self.end_headers()
                self.wfile.write(err_resp)
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, QRRequestHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"\\n==========================================")
    print(f" Python QR Code Generator Pro is running!")
    print(f" URL: {url}")
    print(f" Press Ctrl+C in terminal to stop.")
    print(f"==========================================\\n")
    
    # Automatically open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
