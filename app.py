"""
QR Code Generator Pro
A modern, feature-rich Python QR Code Generator with CustomTkinter.
Supports Website/Links, Telephone numbers, Numeric IDs, Plain Text, and Wi-Fi networks.
Features two primary actions: 'Generate QR Code' and 'Save Img' with high-res export.
"""

import os
import sys
import re
import tempfile
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
import customtkinter as ctk

# Set appearance and default theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class QRCodeGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("QR Code Generator Pro")
        self.geometry("980x720")
        self.minsize(880, 640)
        
        # Center the window on screen
        self.center_window(980, 720)

        # State Variables
        self.current_mode = "Website / Link"
        self.current_qr_image = None       # High-res PIL Image
        self.current_preview_image = None  # CTkImage for display
        self.encoded_text = ""
        self.fg_color = "#000000"
        self.bg_color = "#FFFFFF"
        self.last_saved_path = None

        # Build UI Layout
        self.create_header()
        self.create_main_content()
        self.create_footer()

        # Keyboard Shortcut: Press Enter / Return to generate
        self.bind("<Return>", lambda event: self.generate_qr())

        # Generate a default initial QR code for a great first impression
        self.url_entry.insert(0, "https://www.google.com")
        self.generate_qr()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ================= UI CREATION =================
    def create_header(self):
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray90", "#181A20"), height=65)
        header_frame.pack(side="top", fill="x")
        header_frame.pack_propagate(False)

        # App Title & Icon badge
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=24, pady=10)

        icon_label = ctk.CTkLabel(
            title_box, 
            text="📱", 
            font=ctk.CTkFont(size=24)
        )
        icon_label.pack(side="left", padx=(0, 10))

        text_box = ctk.CTkFrame(title_box, fg_color="transparent")
        text_box.pack(side="left")

        app_title = ctk.CTkLabel(
            text_box, 
            text="QR Code Generator Pro", 
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=("gray15", "#FFFFFF")
        )
        app_title.pack(anchor="w")

        app_sub = ctk.CTkLabel(
            text_box, 
            text="Instant QR generation for websites, telephone numbers, codes & text", 
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#94A3B8")
        )
        app_sub.pack(anchor="w")

        # Top Right: Theme Switcher
        theme_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        theme_box.pack(side="right", padx=24, pady=10)

        theme_lbl = ctk.CTkLabel(theme_box, text="Theme:", font=ctk.CTkFont(size=12))
        theme_lbl.pack(side="left", padx=(0, 8))

        self.theme_switch = ctk.CTkOptionMenu(
            theme_box,
            values=["Dark", "Light", "System"],
            command=self.change_theme,
            width=90,
            height=28,
            font=ctk.CTkFont(size=12)
        )
        self.theme_switch.set("Dark")
        self.theme_switch.pack(side="left")

    def create_main_content(self):
        # Two-column container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=15)
        self.main_container.grid_columnconfigure(0, weight=6, minsize=420)
        self.main_container.grid_columnconfigure(1, weight=5, minsize=380)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Left Column: Configuration & Inputs
        self.left_panel = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("gray95", "#20232A"))
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)

        # Right Column: Live Preview & Save Actions
        self.right_panel = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color=("gray95", "#20232A"))
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)

        self.setup_left_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        pad = 20

        # Section 1: Type Selection
        type_lbl = ctk.CTkLabel(
            self.left_panel, 
            text="1. SELECT INPUT TYPE", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        type_lbl.pack(anchor="w", padx=pad, pady=(16, 8))

        self.mode_selector = ctk.CTkSegmentedButton(
            self.left_panel,
            values=["Website / Link", "Telephone", "Number", "Plain Text", "Wi-Fi"],
            command=self.on_mode_change,
            height=36,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.mode_selector.set("Website / Link")
        self.mode_selector.pack(fill="x", padx=pad, pady=(0, 14))

        # Section 2: Dynamic Input Container
        input_head = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        input_head.pack(fill="x", padx=pad, pady=(0, 4))

        self.input_label = ctk.CTkLabel(
            input_head, 
            text="Website URL:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.input_label.pack(side="left")

        # Paste & Clear quick buttons
        btn_box = ctk.CTkFrame(input_head, fg_color="transparent")
        btn_box.pack(side="right")

        paste_btn = ctk.CTkButton(
            btn_box, 
            text="📋 Paste", 
            width=65, 
            height=24, 
            font=ctk.CTkFont(size=11),
            fg_color=("gray85", "#2D3139"),
            text_color=("gray20", "#E2E8F0"),
            hover_color=("gray75", "#3A3F4B"),
            command=self.paste_from_clipboard
        )
        paste_btn.pack(side="left", padx=(0, 6))

        clear_btn = ctk.CTkButton(
            btn_box, 
            text="✕ Clear", 
            width=58, 
            height=24, 
            font=ctk.CTkFont(size=11),
            fg_color=("gray85", "#2D3139"),
            text_color=("gray20", "#E2E8F0"),
            hover_color=("gray75", "#3A3F4B"),
            command=self.clear_input
        )
        clear_btn.pack(side="left")

        # Container for different mode input fields
        self.input_card = ctk.CTkFrame(self.left_panel, fg_color=("white", "#181A20"), corner_radius=8)
        self.input_card.pack(fill="x", padx=pad, pady=(4, 12))

        # --- Sub-frames for each mode ---
        # Mode 1: URL / Website
        self.url_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            placeholder_text="Enter link (e.g., https://example.com or google.com)",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.url_entry.pack(fill="x", padx=12, pady=(12, 6))
        self.url_hint = ctk.CTkLabel(
            self.url_frame,
            text="💡 Tip: If you type 'example.com', 'https://' will be added automatically.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#94A3B8")
        )
        self.url_hint.pack(anchor="w", padx=12, pady=(0, 10))

        # Mode 2: Telephone
        self.tel_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.tel_entry = ctk.CTkEntry(
            self.tel_frame, 
            placeholder_text="Enter phone number (e.g., +1 234 567 8900 or 012345678)",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.tel_entry.pack(fill="x", padx=12, pady=(12, 6))
        self.tel_hint = ctk.CTkLabel(
            self.tel_frame,
            text="📞 Formatted as standard 'tel:' URI for one-tap calling when scanned.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#94A3B8")
        )
        self.tel_hint.pack(anchor="w", padx=12, pady=(0, 10))

        # Mode 3: Number
        self.num_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.num_entry = ctk.CTkEntry(
            self.num_frame, 
            placeholder_text="Enter numeric code, serial number, or ID (e.g., 9876543210)",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.num_entry.pack(fill="x", padx=12, pady=(12, 6))
        self.num_hint = ctk.CTkLabel(
            self.num_frame,
            text="🔢 Perfect for tracking numbers, account numbers, and barcode equivalents.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#94A3B8")
        )
        self.num_hint.pack(anchor="w", padx=12, pady=(0, 10))

        # Mode 4: Plain Text
        self.text_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.text_box = ctk.CTkTextbox(
            self.text_frame, 
            height=85,
            font=ctk.CTkFont(size=13)
        )
        self.text_box.pack(fill="x", padx=12, pady=(12, 6))
        self.text_hint = ctk.CTkLabel(
            self.text_frame,
            text="📝 Any text, secret message, contact card or note up to ~1,500 characters.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#94A3B8")
        )
        self.text_hint.pack(anchor="w", padx=12, pady=(0, 10))

        # Mode 5: Wi-Fi
        self.wifi_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        
        wifi_grid = ctk.CTkFrame(self.wifi_frame, fg_color="transparent")
        wifi_grid.pack(fill="x", padx=12, pady=(10, 4))
        wifi_grid.columnconfigure(0, weight=1)
        wifi_grid.columnconfigure(1, weight=1)

        ctk.CTkLabel(wifi_grid, text="Network Name (SSID):", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(wifi_grid, text="Security Type:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.wifi_ssid = ctk.CTkEntry(wifi_grid, placeholder_text="e.g., MyHomeWiFi", height=34)
        self.wifi_ssid.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(2, 8))

        self.wifi_security = ctk.CTkOptionMenu(wifi_grid, values=["WPA/WPA2", "WEP", "Open (None)"], height=34)
        self.wifi_security.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(2, 8))

        ctk.CTkLabel(wifi_grid, text="Network Password:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, columnspan=2, sticky="w")
        self.wifi_password = ctk.CTkEntry(wifi_grid, placeholder_text="Enter Wi-Fi password", show="*", height=34)
        self.wifi_password.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 4))

        self.wifi_hint = ctk.CTkLabel(
            self.wifi_frame,
            text="📶 Guests can scan this QR code with their camera to connect instantly!",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#94A3B8")
        )
        self.wifi_hint.pack(anchor="w", padx=12, pady=(0, 10))

        # Show initial URL frame
        self.url_frame.pack(fill="x")

        # Section 3: Customization Options
        opt_lbl = ctk.CTkLabel(
            self.left_panel, 
            text="2. CUSTOMIZE APPEARANCE", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        opt_lbl.pack(anchor="w", padx=pad, pady=(6, 6))

        opts_frame = ctk.CTkFrame(self.left_panel, fg_color=("white", "#181A20"), corner_radius=8)
        opts_frame.pack(fill="x", padx=pad, pady=(0, 14))

        opts_grid = ctk.CTkFrame(opts_frame, fg_color="transparent")
        opts_grid.pack(fill="x", padx=12, pady=10)
        opts_grid.columnconfigure(0, weight=1)
        opts_grid.columnconfigure(1, weight=1)

        # Foreground color
        ctk.CTkLabel(opts_grid, text="QR Color:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=0, sticky="w", padx=4)
        self.fg_color_menu = ctk.CTkOptionMenu(
            opts_grid, 
            values=["Classic Black", "Royal Blue (#1E3A8A)", "Emerald Green (#059669)", "Neon Purple (#7C3AED)", "Crimson Red (#DC2626)", "Custom..."],
            command=self.on_fg_color_select,
            height=32
        )
        self.fg_color_menu.set("Classic Black")
        self.fg_color_menu.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 8))

        # Background color
        ctk.CTkLabel(opts_grid, text="Background:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, sticky="w", padx=4)
        self.bg_color_menu = ctk.CTkOptionMenu(
            opts_grid, 
            values=["Pure White", "Soft Gray (#F3F4F6)", "Transparent", "Custom..."],
            command=self.on_bg_color_select,
            height=32
        )
        self.bg_color_menu.set("Pure White")
        self.bg_color_menu.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 8))

        # Error correction & Resolution
        ctk.CTkLabel(opts_grid, text="Error Correction:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=0, sticky="w", padx=4)
        self.ec_menu = ctk.CTkOptionMenu(
            opts_grid,
            values=["High (30% recovery)", "Quartile (25%)", "Medium (15%)", "Low (7%)"],
            height=32
        )
        self.ec_menu.set("High (30% recovery)")
        self.ec_menu.grid(row=3, column=0, sticky="ew", padx=4, pady=(2, 4))

        ctk.CTkLabel(opts_grid, text="Export Resolution:", font=ctk.CTkFont(size=11, weight="bold")).grid(row=2, column=1, sticky="w", padx=4)
        self.res_menu = ctk.CTkOptionMenu(
            opts_grid,
            values=["Ultra HD (2000 px)", "High Res (1000 px)", "Standard (500 px)"],
            height=32
        )
        self.res_menu.set("High Res (1000 px)")
        self.res_menu.grid(row=3, column=1, sticky="ew", padx=4, pady=(2, 4))

        # ================= HERO BUTTON 1: GENERATE QR CODE =================
        self.gen_button = ctk.CTkButton(
            self.left_panel,
            text="✨ Generate QR Code",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            height=46,
            corner_radius=8,
            fg_color=("#2563EB", "#3B82F6"),
            hover_color=("#1D4ED8", "#2563EB"),
            command=self.generate_qr
        )
        self.gen_button.pack(fill="x", padx=pad, pady=(6, 12))

    def setup_right_panel(self):
        pad = 20

        # Header for preview
        top_box = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        top_box.pack(fill="x", padx=pad, pady=(16, 6))

        preview_lbl = ctk.CTkLabel(
            top_box, 
            text="LIVE QR PREVIEW", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=("#2563EB", "#60A5FA")
        )
        preview_lbl.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            top_box,
            text="● Ready to Scan",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#10B981"
        )
        self.status_badge.pack(side="right")

        # Preview Display Box with elegant border and card background
        self.preview_card = ctk.CTkFrame(self.right_panel, fg_color=("white", "#181A20"), corner_radius=12)
        self.preview_card.pack(fill="both", expand=True, padx=pad, pady=(4, 12))

        # QR Image Display Label
        self.qr_display_label = ctk.CTkLabel(
            self.preview_card,
            text="Click 'Generate QR Code' to create preview",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "#94A3B8")
        )
        self.qr_display_label.pack(expand=True, fill="both", padx=16, pady=16)

        # Encoded Data Info Bar
        self.info_frame = ctk.CTkFrame(self.right_panel, fg_color=("white", "#181A20"), corner_radius=8, height=36)
        self.info_frame.pack(fill="x", padx=pad, pady=(0, 12))
        self.info_frame.pack_propagate(False)

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Encoded: None",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=("gray40", "#94A3B8")
        )
        self.info_label.pack(side="left", padx=12, pady=6)

        # ================= HERO BUTTON 2: SAVE IMG =================
        action_box = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        action_box.pack(fill="x", padx=pad, pady=(0, 16))
        action_box.columnconfigure(0, weight=6)
        action_box.columnconfigure(1, weight=4)

        self.save_button = ctk.CTkButton(
            action_box,
            text="💾 Save Img",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=46,
            corner_radius=8,
            fg_color=("#059669", "#10B981"),
            hover_color=("#047857", "#059669"),
            command=self.save_image
        )
        self.save_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        # Secondary action: Copy to Clipboard
        self.copy_btn = ctk.CTkButton(
            action_box,
            text="📋 Copy Image",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            height=46,
            corner_radius=8,
            fg_color=("gray85", "#2D3139"),
            text_color=("gray15", "#FFFFFF"),
            hover_color=("gray75", "#3A3F4B"),
            command=self.copy_image_to_clipboard
        )
        self.copy_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def create_footer(self):
        footer_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent", height=28)
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 6))

        self.footer_status = ctk.CTkLabel(
            footer_frame,
            text="Ready. Enter content and click 'Generate QR Code' or press Enter.",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#94A3B8")
        )
        self.footer_status.pack(side="left")

        shortcut_lbl = ctk.CTkLabel(
            footer_frame,
            text="Shortcut: Press [Enter] to Generate",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "#64748B")
        )
        shortcut_lbl.pack(side="right")

    # ================= LOGIC & EVENT HANDLERS =================
    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

    def on_mode_change(self, value):
        self.current_mode = value

        # Hide all input sub-frames
        for frame in (self.url_frame, self.tel_frame, self.num_frame, self.text_frame, self.wifi_frame):
            frame.pack_forget()

        # Update input label and show matching sub-frame
        if value == "Website / Link":
            self.input_label.configure(text="Website URL:")
            self.url_frame.pack(fill="x")
        elif value == "Telephone":
            self.input_label.configure(text="Telephone Number:")
            self.tel_frame.pack(fill="x")
        elif value == "Number":
            self.input_label.configure(text="Number / Code / ID:")
            self.num_frame.pack(fill="x")
        elif value == "Plain Text":
            self.input_label.configure(text="Plain Text Content:")
            self.text_frame.pack(fill="x")
        elif value == "Wi-Fi":
            self.input_label.configure(text="Wi-Fi Credentials:")
            self.wifi_frame.pack(fill="x")

    def paste_from_clipboard(self):
        try:
            clipboard_text = self.clipboard_get()
            if self.current_mode == "Website / Link":
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, clipboard_text.strip())
            elif self.current_mode == "Telephone":
                self.tel_entry.delete(0, "end")
                self.tel_entry.insert(0, clipboard_text.strip())
            elif self.current_mode == "Number":
                self.num_entry.delete(0, "end")
                self.num_entry.insert(0, clipboard_text.strip())
            elif self.current_mode == "Plain Text":
                self.text_box.delete("1.0", "end")
                self.text_box.insert("1.0", clipboard_text)
            elif self.current_mode == "Wi-Fi":
                self.wifi_password.delete(0, "end")
                self.wifi_password.insert(0, clipboard_text.strip())
            self.footer_status.configure(text="Pasted content from clipboard.", text_color=("gray40", "#94A3B8"))
        except Exception:
            self.footer_status.configure(text="Clipboard is empty or does not contain text.", text_color="#EF4444")

    def clear_input(self):
        if self.current_mode == "Website / Link":
            self.url_entry.delete(0, "end")
        elif self.current_mode == "Telephone":
            self.tel_entry.delete(0, "end")
        elif self.current_mode == "Number":
            self.num_entry.delete(0, "end")
        elif self.current_mode == "Plain Text":
            self.text_box.delete("1.0", "end")
        elif self.current_mode == "Wi-Fi":
            self.wifi_ssid.delete(0, "end")
            self.wifi_password.delete(0, "end")
        self.footer_status.configure(text="Input cleared.", text_color=("gray40", "#94A3B8"))

    def on_fg_color_select(self, choice):
        if choice == "Classic Black":
            self.fg_color = "#000000"
        elif "Royal Blue" in choice:
            self.fg_color = "#1E3A8A"
        elif "Emerald Green" in choice:
            self.fg_color = "#059669"
        elif "Neon Purple" in choice:
            self.fg_color = "#7C3AED"
        elif "Crimson Red" in choice:
            self.fg_color = "#DC2626"
        elif choice == "Custom...":
            chosen = colorchooser.askcolor(title="Choose QR Code Color", initialcolor=self.fg_color)
            if chosen and chosen[1]:
                self.fg_color = chosen[1]
                self.fg_color_menu.set(f"Custom ({self.fg_color})")
        if self.current_qr_image:
            self.generate_qr()

    def on_bg_color_select(self, choice):
        if choice == "Pure White":
            self.bg_color = "#FFFFFF"
        elif "Soft Gray" in choice:
            self.bg_color = "#F3F4F6"
        elif choice == "Transparent":
            self.bg_color = "transparent"
        elif choice == "Custom...":
            chosen = colorchooser.askcolor(title="Choose Background Color", initialcolor="#FFFFFF")
            if chosen and chosen[1]:
                self.bg_color = chosen[1]
                self.bg_color_menu.set(f"Custom ({self.bg_color})")
        if self.current_qr_image:
            self.generate_qr()

    def get_formatted_data(self):
        """Formats the input into proper QR standard formats based on active mode."""
        mode = self.current_mode
        if mode == "Website / Link":
            raw = self.url_entry.get().strip()
            if not raw:
                return None, "Please enter a website URL or link."
            # Automatically prepend https:// if missing
            if not re.match(r"^https?://", raw, re.IGNORECASE):
                raw = "https://" + raw
            return raw, None

        elif mode == "Telephone":
            raw = self.tel_entry.get().strip()
            if not raw:
                return None, "Please enter a telephone number."
            # Clean telephone: standard tel: protocol for instant smartphone calling
            cleaned = re.sub(r"[^\d+]", "", raw)
            tel_uri = f"tel:{cleaned}"
            return tel_uri, None

        elif mode == "Number":
            raw = self.num_entry.get().strip()
            if not raw:
                return None, "Please enter a number or numeric code."
            return raw, None

        elif mode == "Plain Text":
            raw = self.text_box.get("1.0", "end").strip()
            if not raw:
                return None, "Please enter some text content."
            return raw, None

        elif mode == "Wi-Fi":
            ssid = self.wifi_ssid.get().strip()
            if not ssid:
                return None, "Please enter the Wi-Fi Network Name (SSID)."
            pwd = self.wifi_password.get()
            sec_choice = self.wifi_security.get()
            sec_type = "WPA"
            if "WEP" in sec_choice:
                sec_type = "WEP"
            elif "Open" in sec_choice:
                sec_type = "nopass"
            # Standard WiFi QR code format: WIFI:T:WPA;S:MyNetwork;P:MyPassword;;
            wifi_str = f"WIFI:T:{sec_type};S:{ssid};P:{pwd};;"
            return wifi_str, None

        return None, "Unknown mode selected."

    def get_error_correction_level(self):
        choice = self.ec_menu.get()
        if "Low" in choice:
            return ERROR_CORRECT_L
        elif "Medium" in choice:
            return ERROR_CORRECT_M
        elif "Quartile" in choice:
            return ERROR_CORRECT_Q
        return ERROR_CORRECT_H

    # ================= HERO ACTION 1: GENERATE QR CODE =================
    def generate_qr(self):
        data, err = self.get_formatted_data()
        if err:
            self.status_badge.configure(text="● Input Required", text_color="#EF4444")
            self.footer_status.configure(text=f"⚠️ {err}", text_color="#EF4444")
            return

        self.encoded_text = data

        try:
            ec_level = self.get_error_correction_level()
            qr = qrcode.QRCode(
                version=None,
                error_correction=ec_level,
                box_size=12,
                border=3
            )
            qr.add_data(data)
            qr.make(fit=True)

            # Handle transparent background or solid color
            is_transparent = (self.bg_color == "transparent")
            actual_bg = "#FFFFFF" if is_transparent else self.bg_color

            img = qr.make_image(
                fill_color=self.fg_color,
                back_color=actual_bg
            ).convert("RGBA")

            if is_transparent:
                # Convert the white background to transparent
                datas = img.getdata()
                new_data = []
                for item in datas:
                    # If pixel matches background color (white), make alpha 0
                    if item[0] > 240 and item[1] > 240 and item[2] > 240:
                        new_data.append((255, 255, 255, 0))
                    else:
                        new_data.append(item)
                img.putdata(new_data)

            # Store high-res generated image
            self.current_qr_image = img

            # Create scaled preview (280x280) for the UI
            preview_img = img.copy()
            preview_img = preview_img.resize((280, 280), Image.Resampling.LANCZOS)
            self.current_preview_image = ctk.CTkImage(
                light_image=preview_img,
                dark_image=preview_img,
                size=(280, 280)
            )

            # Update Preview Display
            self.qr_display_label.configure(image=self.current_preview_image, text="")
            self.status_badge.configure(text="● Ready to Scan", text_color="#10B981")

            # Update Info Label with truncated display
            display_text = data
            if len(display_text) > 42:
                display_text = display_text[:39] + "..."
            self.info_label.configure(text=f"Encoded ({self.current_mode}): {display_text}")

            self.footer_status.configure(
                text=f"✓ QR Code successfully generated! Click 'Save Img' to export.",
                text_color=("#059669", "#34D399")
            )

        except Exception as e:
            self.status_badge.configure(text="● Generation Error", text_color="#EF4444")
            self.footer_status.configure(text=f"Error generating QR code: {str(e)}", text_color="#EF4444")

    # ================= HERO ACTION 2: SAVE IMG =================
    def save_image(self):
        if not self.current_qr_image:
            messagebox.showwarning("No QR Code", "Please click 'Generate QR Code' first before saving.")
            return

        # Prepare default filename based on active mode
        clean_mode = self.current_mode.lower().replace(" / ", "_").replace(" ", "_")
        default_name = f"qr_code_{clean_mode}.png"

        # Open native Windows file save dialog
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save QR Code Image",
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[
                ("PNG Image (*.png)", "*.png"),
                ("JPEG Image (*.jpg;*.jpeg)", "*.jpg;*.jpeg"),
                ("Bitmap (*.bmp)", "*.bmp"),
                ("All Files (*.*)", "*.*")
            ]
        )

        if not file_path:
            return  # User cancelled

        try:
            # Determine target resolution
            res_choice = self.res_menu.get()
            target_size = 1000
            if "2000" in res_choice:
                target_size = 2000
            elif "500" in res_choice:
                target_size = 500

            # High-quality resize
            export_img = self.current_qr_image.resize(
                (target_size, target_size), 
                Image.Resampling.NEAREST  # NEAREST preserves razor-sharp QR pixels!
            )

            # Handle format conversions if user selected JPEG
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                # JPEG doesn't support alpha, composite onto white background
                if export_img.mode == "RGBA":
                    bg = Image.new("RGB", export_img.size, (255, 255, 255))
                    bg.paste(export_img, mask=export_img.split()[3])
                    export_img = bg
                else:
                    export_img = export_img.convert("RGB")
                export_img.save(file_path, "JPEG", quality=95)
            elif ext == ".bmp":
                export_img = export_img.convert("RGB")
                export_img.save(file_path, "BMP")
            else:
                # Default PNG
                export_img.save(file_path, "PNG")

            self.last_saved_path = file_path
            self.footer_status.configure(
                text=f"✓ Saved image: {os.path.basename(file_path)} ({target_size}x{target_size}px)",
                text_color=("#059669", "#34D399")
            )

            # Prompt with option to view file in Windows Explorer
            answer = messagebox.askyesno(
                "Image Saved Successfully",
                f"Your QR code has been saved to:\n\n{file_path}\n\nWould you like to open the folder now?"
            )
            if answer:
                # Open Windows Explorer and select the saved file
                subprocess.run(f'explorer /select,"{os.path.abspath(file_path)}"', shell=True)

        except Exception as e:
            messagebox.showerror("Save Failed", f"Failed to save image:\n{str(e)}")

    def copy_image_to_clipboard(self):
        """Copies the generated QR code image directly to the Windows clipboard."""
        if not self.current_qr_image:
            messagebox.showwarning("No QR Code", "Please generate a QR code first.")
            return

        try:
            # Save temporary BMP for Windows clipboard
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_filename = tmp.name
                
            # Composite onto white if transparent
            img = self.current_qr_image.copy()
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg
            else:
                img = img.convert("RGB")
                
            img.save(temp_filename, "PNG")

            # Use PowerShell to put image on Windows clipboard
            ps_script = (
                f"Add-Type -AssemblyName System.Windows.Forms; "
                f"$img = [System.Drawing.Image]::FromFile('{temp_filename}'); "
                f"[System.Windows.Forms.Clipboard]::SetImage($img); "
                f"$img.Dispose()"
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                check=True
            )

            try:
                os.unlink(temp_filename)
            except Exception:
                pass

            self.footer_status.configure(
                text="✓ QR Code image copied to clipboard! You can paste it (Ctrl+V) anywhere.",
                text_color=("#059669", "#34D399")
            )
            messagebox.showinfo("Copied!", "QR Code image has been copied to your clipboard!\nYou can paste it directly into Word, WhatsApp, Discord, Photoshop, etc.")

        except Exception as e:
            self.footer_status.configure(text=f"Failed to copy to clipboard: {str(e)}", text_color="#EF4444")


if __name__ == "__main__":
    app = QRCodeGeneratorApp()
    app.mainloop()
