"""
SmartBill Pro v2.0 - Restaurant Billing & Management System
A comprehensive Tkinter-based application for restaurant billing,
menu management, order tracking, and sales analytics.
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import sys
from datetime import datetime, timedelta

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from modules.db_manager import DatabaseManager

# Optional: Matplotlib for charts
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ========================================================================
# COLOR PALETTE
# ========================================================================

class Colors:
    """Modern design system color palette."""
    PRIMARY = "#0f172a"
    SECONDARY = "#1e293b"
    ACCENT = "#3b82f6"
    ACCENT_HOVER = "#2563eb"
    SURFACE = "#f8fafc"
    CARD = "#ffffff"
    ON_SURFACE = "#1e293b"
    TEXT_SECONDARY = "#64748b"
    SUCCESS = "#22c55e"
    SUCCESS_DARK = "#16a34a"
    WARNING = "#f59e0b"
    WARNING_DARK = "#d97706"
    ERROR = "#ef4444"
    ERROR_DARK = "#dc2626"
    WHITE = "#ffffff"
    LIGHT_GRAY = "#f1f5f9"
    MEDIUM_GRAY = "#e2e8f0"
    BORDER = "#cbd5e1"
    SIDEBAR_ACTIVE = "#334155"
    SIDEBAR_HOVER = "#1e293b"
    PURPLE = "#8b5cf6"
    PURPLE_DARK = "#7c3aed"
    TEAL = "#14b8a6"


# ========================================================================
# SMARTBILL APPLICATION
# ========================================================================

class SmartBillApp:
    """Main application class for SmartBill Pro."""

    def __init__(self):
        self.root = tk.Tk()
        self.db = DatabaseManager()

        # Application state
        self.current_user = None
        self.current_view = 'dashboard'
        self.current_table = None
        self.cart = {}
        self.discount_pct = tk.DoubleVar(value=0)
        self.tax_rate = float(self.db.get_setting('tax_rate', '5'))
        self.payment_method = tk.StringVar(value='Cash')

        # UI references
        self.sidebar_buttons = {}
        self.content_frame = None
        self.cart_frame_ref = None
        self.total_label_ref = None
        self.items_display_frame = None
        self.status_var = tk.StringVar(value="Ready")
        self._menu_loader = None

        # Window setup
        self.root.title("SmartBill Pro v2.0")
        self.root.geometry("1400x850")
        self.root.configure(bg=Colors.PRIMARY)
        self.root.minsize(1200, 700)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (850 // 2)
        self.root.geometry(f"1400x850+{x}+{y}")

        # Configure ttk styles
        self._configure_styles()

        # Show login
        self.show_login()
        self.root.mainloop()

    def _configure_styles(self):
        """Configure ttk widget styles for a modern look."""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Custom.Treeview',
                        background=Colors.WHITE,
                        foreground=Colors.ON_SURFACE,
                        rowheight=38,
                        fieldbackground=Colors.WHITE,
                        font=('Segoe UI', 10))
        style.configure('Custom.Treeview.Heading',
                        background=Colors.ACCENT,
                        foreground=Colors.WHITE,
                        font=('Segoe UI', 10, 'bold'),
                        relief='flat')
        style.map('Custom.Treeview',
                  background=[('selected', '#dbeafe')],
                  foreground=[('selected', Colors.ON_SURFACE)])

    # ================================================================
    # LOGIN SCREEN
    # ================================================================

    def show_login(self):
        """Display the login screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

        login_bg = tk.Frame(self.root, bg=Colors.PRIMARY)
        login_bg.pack(fill='both', expand=True)

        center = tk.Frame(login_bg, bg=Colors.PRIMARY)
        center.place(relx=0.5, rely=0.5, anchor='center')

        # Login card
        card = tk.Frame(center, bg=Colors.CARD, relief='flat', bd=0,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(padx=40, pady=40)

        inner = tk.Frame(card, bg=Colors.CARD)
        inner.pack(padx=50, pady=40)

        # Logo
        tk.Label(inner, text="🧾", font=('Segoe UI', 48), bg=Colors.CARD).pack()
        tk.Label(inner, text="SmartBill Pro", font=('Segoe UI', 28, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(pady=(5, 0))
        tk.Label(inner, text="Restaurant Billing System", font=('Segoe UI', 12),
                 bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(pady=(2, 30))

        # Username field
        tk.Label(inner, text="Username", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE, anchor='w').pack(fill='x')
        username_entry = tk.Entry(inner, font=('Segoe UI', 12), relief='flat',
                                  bd=8, bg=Colors.LIGHT_GRAY, width=30)
        username_entry.pack(fill='x', pady=(5, 15))
        username_entry.insert(0, "admin")

        # Password field
        tk.Label(inner, text="Password", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE, anchor='w').pack(fill='x')
        password_entry = tk.Entry(inner, font=('Segoe UI', 12), relief='flat',
                                   bd=8, bg=Colors.LIGHT_GRAY, show="●", width=30)
        password_entry.pack(fill='x', pady=(5, 25))
        password_entry.insert(0, "admin123")

        # Error message label
        error_label = tk.Label(inner, text="", font=('Segoe UI', 10),
                               bg=Colors.CARD, fg=Colors.ERROR)
        error_label.pack(pady=(0, 10))

        def do_login(event=None):
            user = username_entry.get().strip()
            pwd = password_entry.get().strip()
            if not user or not pwd:
                error_label.config(text="Please enter username and password")
                return
            result = self.db.authenticate(user, pwd)
            if result:
                self.current_user = result
                self.create_main_layout()
            else:
                error_label.config(text="Invalid username or password")
                password_entry.delete(0, 'end')

        login_btn = tk.Button(inner, text="Login", font=('Segoe UI', 12, 'bold'),
                              bg=Colors.ACCENT, fg=Colors.WHITE, relief='flat', bd=0,
                              padx=30, pady=12, cursor='hand2', command=do_login,
                              activebackground=Colors.ACCENT_HOVER,
                              activeforeground=Colors.WHITE)
        login_btn.pack(fill='x')
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=Colors.ACCENT_HOVER))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=Colors.ACCENT))

        # Key bindings
        password_entry.bind("<Return>", do_login)
        username_entry.bind("<Return>", lambda e: password_entry.focus_set())

        # Hint
        tk.Label(inner, text="Default: admin / admin123", font=('Segoe UI', 9),
                 bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(pady=(15, 0))

        username_entry.focus_set()

    # ================================================================
    # MAIN LAYOUT
    # ================================================================

    def create_main_layout(self):
        """Create the main application layout with sidebar and content area."""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_container = tk.Frame(self.root, bg=Colors.SURFACE)
        main_container.pack(fill='both', expand=True)

        # Sidebar
        sidebar = tk.Frame(main_container, bg=Colors.PRIMARY, width=250)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Right section
        right_section = tk.Frame(main_container, bg=Colors.SURFACE)
        right_section.pack(side='right', fill='both', expand=True)

        # Content area
        self.content_frame = tk.Frame(right_section, bg=Colors.SURFACE)
        self.content_frame.pack(fill='both', expand=True)

        # Status bar
        status_bar = tk.Frame(right_section, bg=Colors.MEDIUM_GRAY, height=30)
        status_bar.pack(fill='x', side='bottom')
        status_bar.pack_propagate(False)

        tk.Label(status_bar, textvariable=self.status_var, font=('Segoe UI', 9),
                 bg=Colors.MEDIUM_GRAY, fg=Colors.TEXT_SECONDARY, padx=15).pack(side='left', fill='y')

        time_label = tk.Label(status_bar, font=('Segoe UI', 9),
                              bg=Colors.MEDIUM_GRAY, fg=Colors.TEXT_SECONDARY, padx=15)
        time_label.pack(side='right', fill='y')

        def update_time():
            try:
                time_label.config(text=datetime.now().strftime("%d %b %Y  %I:%M:%S %p"))
                self.root.after(1000, update_time)
            except tk.TclError:
                pass  # Widget destroyed

        update_time()

        # Show dashboard by default
        self.switch_view('dashboard')

    def _build_sidebar(self, sidebar):
        """Build the sidebar navigation panel."""
        # App header
        header = tk.Frame(sidebar, bg=Colors.PRIMARY)
        header.pack(fill='x', padx=20, pady=(25, 30))

        tk.Label(header, text="🧾 SmartBill", font=('Segoe UI', 20, 'bold'),
                 bg=Colors.PRIMARY, fg=Colors.WHITE).pack(anchor='w')
        tk.Label(header, text="Pro v2.0", font=('Segoe UI', 10),
                 bg=Colors.PRIMARY, fg=Colors.TEXT_SECONDARY).pack(anchor='w')

        # Separator
        tk.Frame(sidebar, bg=Colors.SECONDARY, height=1).pack(fill='x', padx=15)

        # Navigation items
        nav_items = [
            ('📊', 'Dashboard', 'dashboard'),
            ('🛒', 'Billing / POS', 'pos'),
            ('📋', 'Order History', 'orders'),
            ('📝', 'Menu Manager', 'menu'),
            ('📈', 'Analytics', 'analytics'),
            ('⚙️', 'Settings', 'settings'),
        ]

        nav_frame = tk.Frame(sidebar, bg=Colors.PRIMARY)
        nav_frame.pack(fill='x', pady=(20, 0))

        for icon, label, view_name in nav_items:
            btn_frame = tk.Frame(nav_frame, bg=Colors.PRIMARY, cursor='hand2')
            btn_frame.pack(fill='x', padx=10, pady=2)

            btn_inner = tk.Frame(btn_frame, bg=Colors.PRIMARY)
            btn_inner.pack(fill='x', padx=5, pady=6)

            icon_lbl = tk.Label(btn_inner, text=icon, font=('Segoe UI', 14),
                                bg=Colors.PRIMARY, fg=Colors.WHITE)
            icon_lbl.pack(side='left', padx=(10, 10))

            text_lbl = tk.Label(btn_inner, text=label, font=('Segoe UI', 11),
                                bg=Colors.PRIMARY, fg=Colors.WHITE, anchor='w')
            text_lbl.pack(side='left', fill='x')

            self.sidebar_buttons[view_name] = btn_frame

            # Bind click and hover to all child widgets
            for widget in [btn_frame, btn_inner, icon_lbl, text_lbl]:
                widget.bind('<Button-1>', lambda e, v=view_name: self.switch_view(v))
                widget.bind('<Enter>',
                            lambda e, f=btn_frame, v=view_name: self._sidebar_hover(f, v, True))
                widget.bind('<Leave>',
                            lambda e, f=btn_frame, v=view_name: self._sidebar_hover(f, v, False))

        # Bottom section - user info and logout
        bottom = tk.Frame(sidebar, bg=Colors.PRIMARY)
        bottom.pack(side='bottom', fill='x', padx=15, pady=20)

        tk.Frame(bottom, bg=Colors.SECONDARY, height=1).pack(fill='x', pady=(0, 15))

        user_frame = tk.Frame(bottom, bg=Colors.PRIMARY)
        user_frame.pack(fill='x')

        tk.Label(user_frame, text="👤", font=('Segoe UI', 14),
                 bg=Colors.PRIMARY, fg=Colors.WHITE).pack(side='left')

        user_info = tk.Frame(user_frame, bg=Colors.PRIMARY)
        user_info.pack(side='left', padx=10)

        tk.Label(user_info, text=self.current_user.get('username', ''),
                 font=('Segoe UI', 11, 'bold'), bg=Colors.PRIMARY, fg=Colors.WHITE).pack(anchor='w')
        tk.Label(user_info, text=self.current_user.get('role', '').title(),
                 font=('Segoe UI', 9), bg=Colors.PRIMARY, fg=Colors.TEXT_SECONDARY).pack(anchor='w')

        logout_btn = tk.Button(bottom, text="🚪 Logout", font=('Segoe UI', 10),
                               bg=Colors.ERROR, fg=Colors.WHITE, relief='flat', bd=0,
                               padx=15, pady=8, cursor='hand2', command=self.logout)
        logout_btn.pack(fill='x', pady=(15, 0))
        logout_btn.bind("<Enter>", lambda e: logout_btn.config(bg=Colors.ERROR_DARK))
        logout_btn.bind("<Leave>", lambda e: logout_btn.config(bg=Colors.ERROR))

    def _sidebar_hover(self, frame, view_name, entering):
        """Handle sidebar button hover highlighting."""
        if view_name == self.current_view:
            return
        color = Colors.SIDEBAR_HOVER if entering else Colors.PRIMARY
        self._set_frame_bg(frame, color)

    @staticmethod
    def _set_frame_bg(frame, color):
        """Recursively set background color on a frame and its children."""
        try:
            frame.config(bg=color)
            for child in frame.winfo_children():
                SmartBillApp._set_frame_bg(child, color)
        except tk.TclError:
            pass

    def switch_view(self, view_name):
        """Switch to a different view."""
        self.current_view = view_name

        # Update sidebar active highlighting
        for name, btn in self.sidebar_buttons.items():
            color = Colors.SIDEBAR_ACTIVE if name == view_name else Colors.PRIMARY
            self._set_frame_bg(btn, color)

        # Clear content and show the requested view
        self.clear_content()

        views = {
            'dashboard': self.show_dashboard,
            'pos': self.show_pos,
            'orders': self.show_orders,
            'menu': self.show_menu,
            'analytics': self.show_analytics,
            'settings': self.show_settings,
        }

        view_func = views.get(view_name)
        if view_func:
            view_func()

        self.status_var.set(f"View: {view_name.replace('_', ' ').title()}")

    def clear_content(self):
        """Clear all widgets from the content area."""
        if self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    # ================================================================
    # REUSABLE UI COMPONENTS
    # ================================================================

    def _create_header(self, parent, title, subtitle=None):
        """Create a styled page header bar."""
        header = tk.Frame(parent, bg=Colors.SURFACE)
        header.pack(fill='x', padx=30, pady=(25, 20))

        tk.Label(header, text=title, font=('Segoe UI', 24, 'bold'),
                 bg=Colors.SURFACE, fg=Colors.ON_SURFACE).pack(side='left')

        if subtitle:
            tk.Label(header, text=f"  •  {subtitle}", font=('Segoe UI', 12),
                     bg=Colors.SURFACE, fg=Colors.TEXT_SECONDARY).pack(side='left', pady=(8, 0))

        return header

    def _create_stat_card(self, parent, icon, title, value, color):
        """Create a statistics card widget."""
        card = tk.Frame(parent, bg=Colors.CARD, relief='flat', bd=0,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(side='left', fill='both', expand=True, padx=8)

        inner = tk.Frame(card, bg=Colors.CARD)
        inner.pack(fill='both', padx=20, pady=18)

        tk.Label(inner, text=icon, font=('Segoe UI', 20), bg=Colors.CARD).pack(anchor='w')
        tk.Label(inner, text=str(value), font=('Segoe UI', 22, 'bold'),
                 bg=Colors.CARD, fg=color, anchor='w').pack(fill='x', pady=(8, 2))
        tk.Label(inner, text=title, font=('Segoe UI', 10),
                 bg=Colors.CARD, fg=Colors.TEXT_SECONDARY, anchor='w').pack(fill='x')

        return card

    def _create_button(self, parent, text, command, bg=None, fg=None, width=None):
        """Create a modern flat button with hover effect."""
        bg = bg or Colors.ACCENT
        fg = fg or Colors.WHITE

        btn = tk.Button(parent, text=text, command=command, font=('Segoe UI', 10, 'bold'),
                        bg=bg, fg=fg, relief='flat', bd=0, padx=18, pady=8,
                        cursor='hand2', activebackground=bg, activeforeground=fg)
        if width:
            btn.config(width=width)

        hover_map = {
            Colors.ACCENT: Colors.ACCENT_HOVER,
            Colors.SUCCESS: Colors.SUCCESS_DARK,
            Colors.ERROR: Colors.ERROR_DARK,
            Colors.WARNING: Colors.WARNING_DARK,
            Colors.PURPLE: Colors.PURPLE_DARK,
        }
        hover_bg = hover_map.get(bg, bg)

        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

        return btn

    # ================================================================
    # DASHBOARD VIEW
    # ================================================================

    def show_dashboard(self):
        """Display the dashboard with stats and recent orders."""
        self._create_header(self.content_frame, "Dashboard", "Overview")

        stats = self.db.get_dashboard_stats()

        # Stats cards row
        stats_frame = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        stats_frame.pack(fill='x', padx=30, pady=(0, 20))

        self._create_stat_card(stats_frame, "💰", "Today's Revenue",
                               f"₹{stats['today_revenue']:,.0f}", Colors.SUCCESS)
        self._create_stat_card(stats_frame, "📦", "Today's Orders",
                               stats['today_orders'], Colors.ACCENT)
        self._create_stat_card(stats_frame, "📊", "Avg Order Value",
                               f"₹{stats['avg_order']:,.0f}", Colors.PURPLE)
        self._create_stat_card(stats_frame, "🍽️", "Menu Items",
                               stats['menu_count'], Colors.TEAL)

        # Bottom section
        bottom = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        bottom.pack(fill='both', expand=True, padx=30, pady=(0, 20))

        # --- Recent orders card ---
        orders_card = tk.Frame(bottom, bg=Colors.CARD, relief='flat', bd=0,
                               highlightbackground=Colors.BORDER, highlightthickness=1)
        orders_card.pack(side='left', fill='both', expand=True, padx=(0, 10))

        tk.Label(orders_card, text="📋 Recent Orders", font=('Segoe UI', 14, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE, anchor='w').pack(
            fill='x', padx=20, pady=(18, 10))

        recent_orders = self.db.get_orders(limit=8)

        if recent_orders:
            for order in recent_orders:
                row = tk.Frame(orders_card, bg=Colors.CARD)
                row.pack(fill='x', padx=20, pady=4)

                tk.Label(row, text=f"#{order['id']}", font=('Segoe UI', 10, 'bold'),
                         bg=Colors.CARD, fg=Colors.ACCENT, width=6, anchor='w').pack(side='left')
                tk.Label(row, text=f"Table {order.get('table_number', '-')}",
                         font=('Segoe UI', 10),
                         bg=Colors.CARD, fg=Colors.ON_SURFACE, width=10,
                         anchor='w').pack(side='left')
                tk.Label(row, text=order.get('datetime', '')[:16], font=('Segoe UI', 9),
                         bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(side='left', padx=10)
                tk.Label(row, text=f"₹{order['total_amount']:,.0f}",
                         font=('Segoe UI', 10, 'bold'),
                         bg=Colors.CARD, fg=Colors.SUCCESS, anchor='e').pack(side='right')

                tk.Frame(orders_card, bg=Colors.LIGHT_GRAY, height=1).pack(fill='x', padx=20)
        else:
            tk.Label(orders_card, text="No orders yet.\nStart billing to see orders here!",
                     font=('Segoe UI', 11), bg=Colors.CARD, fg=Colors.TEXT_SECONDARY,
                     justify='center').pack(expand=True, pady=40)

        # --- Quick actions card ---
        actions_card = tk.Frame(bottom, bg=Colors.CARD, relief='flat', bd=0, width=300,
                                highlightbackground=Colors.BORDER, highlightthickness=1)
        actions_card.pack(side='right', fill='y', padx=(10, 0))
        actions_card.pack_propagate(False)

        tk.Label(actions_card, text="⚡ Quick Actions", font=('Segoe UI', 14, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE, anchor='w').pack(
            fill='x', padx=20, pady=(18, 15))

        actions = [
            ("🛒  New Order", Colors.SUCCESS, lambda: self.switch_view('pos')),
            ("📋  View Orders", Colors.ACCENT, lambda: self.switch_view('orders')),
            ("📝  Manage Menu", Colors.PURPLE, lambda: self.switch_view('menu')),
            ("📈  View Analytics", Colors.TEAL, lambda: self.switch_view('analytics')),
            ("📤  Export CSV", Colors.WARNING, self.export_orders),
        ]

        for text, color, cmd in actions:
            btn = self._create_button(actions_card, text, cmd, bg=color, width=22)
            btn.pack(padx=20, pady=5, fill='x')

    # ================================================================
    # POS / BILLING VIEW
    # ================================================================

    def show_pos(self):
        """Display the POS/Billing view."""
        if self.current_table is None:
            self._show_table_grid()
        else:
            self._show_billing_interface()

    def _show_table_grid(self):
        """Show the table selection grid."""
        self._create_header(self.content_frame, "Select Table",
                            "Choose a table to start billing")

        num_tables = int(self.db.get_setting('num_tables', '20'))
        cols = 5

        grid_frame = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        grid_frame.pack(fill='both', expand=True, padx=30, pady=(0, 20))

        for i in range(1, num_tables + 1):
            row = (i - 1) // cols
            col = (i - 1) % cols

            btn = tk.Button(grid_frame, text=f"🍽️\nTable {i}",
                            font=('Segoe UI', 13, 'bold'), bg=Colors.SUCCESS,
                            fg=Colors.WHITE, relief='flat', bd=0, width=14, height=4,
                            cursor='hand2', command=lambda t=i: self._select_table(t),
                            activebackground=Colors.SUCCESS_DARK,
                            activeforeground=Colors.WHITE)
            btn.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')

            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=Colors.ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=Colors.SUCCESS))

        for c in range(cols):
            grid_frame.columnconfigure(c, weight=1)

    def _select_table(self, table_num):
        """Select a table and launch the billing interface."""
        self.current_table = table_num
        self.cart = {}
        self.discount_pct.set(0)
        self.clear_content()
        self._show_billing_interface()

    def _show_billing_interface(self):
        """Show the full billing interface: menu on left, cart on right."""
        # Header with table info and back button
        header = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        header.pack(fill='x', padx=30, pady=(20, 15))

        back_btn = self._create_button(header, "← Tables",
                                       self._go_back_to_tables, bg=Colors.TEXT_SECONDARY)
        back_btn.pack(side='left')

        tk.Label(header, text=f"🍽️ Table {self.current_table}",
                 font=('Segoe UI', 22, 'bold'),
                 bg=Colors.SURFACE, fg=Colors.ON_SURFACE).pack(side='left', padx=20)

        # Main container: Menu (left) + Cart (right)
        main_area = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        main_area.pack(fill='both', expand=True, padx=30, pady=(0, 15))

        # ---- Left panel: Menu ----
        left = tk.Frame(main_area, bg=Colors.CARD, relief='flat', bd=0,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Search bar
        search_frame = tk.Frame(left, bg=Colors.CARD)
        search_frame.pack(fill='x', padx=15, pady=(15, 10))

        tk.Label(search_frame, text="🔍", font=('Segoe UI', 14), bg=Colors.CARD).pack(side='left')

        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=('Segoe UI', 11),
                                relief='flat', bd=5, bg=Colors.LIGHT_GRAY)
        search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        search_entry.insert(0, "Search menu items...")
        search_entry.config(fg=Colors.TEXT_SECONDARY)

        def on_search_focus(e):
            if search_entry.get() == "Search menu items...":
                search_entry.delete(0, 'end')
                search_entry.config(fg=Colors.ON_SURFACE)

        def on_search_blur(e):
            if not search_entry.get():
                search_entry.insert(0, "Search menu items...")
                search_entry.config(fg=Colors.TEXT_SECONDARY)

        def on_search(*args):
            query = search_var.get()
            if query and query != "Search menu items...":
                self._display_items(self.items_display_frame, category=None, search=query)

        search_entry.bind('<FocusIn>', on_search_focus)
        search_entry.bind('<FocusOut>', on_search_blur)
        search_var.trace_add('write', on_search)

        # Category buttons
        cats_frame = tk.Frame(left, bg=Colors.CARD)
        cats_frame.pack(fill='x', padx=15, pady=(0, 10))

        categories = self.db.get_categories()
        cat_inner = tk.Frame(cats_frame, bg=Colors.CARD)
        cat_inner.pack(fill='x')

        for idx, cat in enumerate(categories):
            btn = tk.Button(cat_inner, text=cat, font=('Segoe UI', 9, 'bold'),
                            bg=Colors.ACCENT, fg=Colors.WHITE, relief='flat', bd=0,
                            padx=12, pady=6, cursor='hand2',
                            command=lambda c=cat: self._display_items(
                                self.items_display_frame, c),
                            activebackground=Colors.ACCENT_HOVER,
                            activeforeground=Colors.WHITE)
            btn.grid(row=idx // 4, column=idx % 4, padx=3, pady=3, sticky='ew')
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=Colors.ACCENT_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=Colors.ACCENT))

        for c in range(min(4, len(categories))):
            cat_inner.columnconfigure(c, weight=1)

        # Scrollable items area
        items_container = tk.Frame(left, bg=Colors.CARD)
        items_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))

        items_canvas = tk.Canvas(items_container, bg=Colors.CARD, highlightthickness=0)
        items_scrollbar = ttk.Scrollbar(items_container, orient='vertical',
                                        command=items_canvas.yview)
        self.items_display_frame = tk.Frame(items_canvas, bg=Colors.CARD)

        self.items_display_frame.bind('<Configure>',
                                      lambda e: items_canvas.configure(
                                          scrollregion=items_canvas.bbox('all')))

        items_canvas.create_window((0, 0), window=self.items_display_frame, anchor='nw')
        items_canvas.configure(yscrollcommand=items_scrollbar.set)

        items_canvas.pack(side='left', fill='both', expand=True)
        items_scrollbar.pack(side='right', fill='y')

        # Mouse wheel support for items
        def _on_items_wheel(event):
            items_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        items_canvas.bind("<Enter>",
                          lambda e: items_canvas.bind_all("<MouseWheel>", _on_items_wheel))
        items_canvas.bind("<Leave>",
                          lambda e: items_canvas.unbind_all("<MouseWheel>"))

        # Show first category
        if categories:
            self._display_items(self.items_display_frame, categories[0])

        # ---- Right panel: Cart ----
        right = tk.Frame(main_area, bg=Colors.CARD, width=380, relief='flat', bd=0,
                         highlightbackground=Colors.BORDER, highlightthickness=1)
        right.pack(side='right', fill='y', padx=(10, 0))
        right.pack_propagate(False)

        self._build_cart_panel(right)

    def _display_items(self, items_frame, category=None, search=None):
        """Display menu items for a category or search query."""
        for widget in items_frame.winfo_children():
            widget.destroy()

        items = self.db.get_menu_items(category=category, search=search)

        if not items:
            tk.Label(items_frame, text="No items found", font=('Segoe UI', 12),
                     bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(pady=30)
            return

        for item in items:
            item_row = tk.Frame(items_frame, bg=Colors.LIGHT_GRAY, relief='flat', bd=0)
            item_row.pack(fill='x', padx=5, pady=3)

            content = tk.Frame(item_row, bg=Colors.LIGHT_GRAY)
            content.pack(fill='x', padx=12, pady=10)

            tk.Label(content, text=item['name'], font=('Segoe UI', 11, 'bold'),
                     bg=Colors.LIGHT_GRAY, fg=Colors.ON_SURFACE,
                     anchor='w').pack(side='left')

            add_btn = tk.Button(content, text="+ Add", font=('Segoe UI', 9, 'bold'),
                                bg=Colors.SUCCESS, fg=Colors.WHITE, relief='flat', bd=0,
                                padx=12, pady=4, cursor='hand2',
                                command=lambda n=item['name'], p=item['price']:
                                self.add_to_cart(n, p),
                                activebackground=Colors.SUCCESS_DARK,
                                activeforeground=Colors.WHITE)
            add_btn.pack(side='right')
            add_btn.bind("<Enter>", lambda e, b=add_btn: b.config(bg=Colors.SUCCESS_DARK))
            add_btn.bind("<Leave>", lambda e, b=add_btn: b.config(bg=Colors.SUCCESS))

            tk.Label(content, text=f"₹{item['price']:.0f}",
                     font=('Segoe UI', 11, 'bold'),
                     bg=Colors.LIGHT_GRAY, fg=Colors.SUCCESS,
                     anchor='e').pack(side='right', padx=(0, 15))

    def _build_cart_panel(self, parent):
        """Build the cart panel with items, totals, and action buttons."""
        # Cart header
        tk.Label(parent, text="🛒 Current Order", font=('Segoe UI', 16, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(padx=15, pady=(15, 10))

        # Scrollable cart items
        cart_container = tk.Frame(parent, bg=Colors.CARD)
        cart_container.pack(fill='both', expand=True, padx=10)

        cart_canvas = tk.Canvas(cart_container, bg=Colors.CARD, highlightthickness=0)
        cart_scrollbar = ttk.Scrollbar(cart_container, orient='vertical',
                                       command=cart_canvas.yview)
        self.cart_frame_ref = tk.Frame(cart_canvas, bg=Colors.CARD)

        self.cart_frame_ref.bind('<Configure>',
                                 lambda e: cart_canvas.configure(
                                     scrollregion=cart_canvas.bbox('all')))

        cart_canvas.create_window((0, 0), window=self.cart_frame_ref, anchor='nw')
        cart_canvas.configure(yscrollcommand=cart_scrollbar.set)

        cart_canvas.pack(side='left', fill='both', expand=True)
        cart_scrollbar.pack(side='right', fill='y')

        # --- Footer (pinned to bottom) ---
        footer = tk.Frame(parent, bg=Colors.CARD)
        footer.pack(fill='x', side='bottom', padx=15, pady=(0, 15))

        # Discount input
        disc_frame = tk.Frame(footer, bg=Colors.CARD)
        disc_frame.pack(fill='x', pady=(0, 5))

        tk.Label(disc_frame, text="Discount %:", font=('Segoe UI', 10),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(side='left')

        disc_entry = tk.Entry(disc_frame, textvariable=self.discount_pct,
                              font=('Segoe UI', 10), relief='flat', bd=3,
                              bg=Colors.LIGHT_GRAY, width=8, justify='right')
        disc_entry.pack(side='right')

        # Payment method
        pay_frame = tk.Frame(footer, bg=Colors.CARD)
        pay_frame.pack(fill='x', pady=(0, 8))

        tk.Label(pay_frame, text="Payment:", font=('Segoe UI', 10),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(side='left')

        for method in ['Cash', 'Card', 'UPI']:
            rb = tk.Radiobutton(pay_frame, text=method, variable=self.payment_method,
                                value=method, font=('Segoe UI', 9), bg=Colors.CARD,
                                fg=Colors.ON_SURFACE, selectcolor=Colors.LIGHT_GRAY,
                                activebackground=Colors.CARD)
            rb.pack(side='left', padx=3)

        # Totals display
        self.total_label_ref = tk.Frame(footer, bg=Colors.LIGHT_GRAY, relief='flat', bd=0)
        self.total_label_ref.pack(fill='x', pady=(5, 10))

        # Action buttons
        btn_frame = tk.Frame(footer, bg=Colors.CARD)
        btn_frame.pack(fill='x')

        place_btn = self._create_button(btn_frame, "✓ Place Order", self.place_order,
                                        bg=Colors.SUCCESS)
        place_btn.pack(fill='x', pady=(0, 5))

        clear_btn = self._create_button(btn_frame, "✕ Clear Cart", self._clear_cart,
                                        bg=Colors.ERROR)
        clear_btn.pack(fill='x')

        # Initial display
        self._update_cart_display()

    # ================================================================
    # CART OPERATIONS
    # ================================================================

    def add_to_cart(self, name, price):
        """Add an item to the cart or increase its quantity."""
        if name in self.cart:
            self.cart[name]['qty'] += 1
        else:
            self.cart[name] = {'price': price, 'qty': 1}
        self._update_cart_display()

    def _decrease_qty(self, name):
        """Decrease item quantity or remove it from the cart."""
        if name in self.cart:
            if self.cart[name]['qty'] > 1:
                self.cart[name]['qty'] -= 1
            else:
                del self.cart[name]
            self._update_cart_display()

    def _clear_cart(self):
        """Clear all items from the cart after confirmation."""
        if self.cart:
            if messagebox.askyesno("Clear Cart", "Remove all items from cart?"):
                self.cart.clear()
                self._update_cart_display()

    def _update_cart_display(self):
        """Refresh the cart items and totals display."""
        if not self.cart_frame_ref or not self.cart_frame_ref.winfo_exists():
            return

        for widget in self.cart_frame_ref.winfo_children():
            widget.destroy()

        if not self.cart:
            tk.Label(self.cart_frame_ref, text="Cart is empty\nAdd items from the menu",
                     font=('Segoe UI', 11), bg=Colors.CARD, fg=Colors.TEXT_SECONDARY,
                     justify='center').pack(pady=30)
        else:
            for name, data in self.cart.items():
                item_frame = tk.Frame(self.cart_frame_ref, bg=Colors.LIGHT_GRAY)
                item_frame.pack(fill='x', padx=5, pady=3)

                info = tk.Frame(item_frame, bg=Colors.LIGHT_GRAY)
                info.pack(fill='x', padx=10, pady=8)

                tk.Label(info, text=name, font=('Segoe UI', 10, 'bold'),
                         bg=Colors.LIGHT_GRAY, fg=Colors.ON_SURFACE,
                         anchor='w').pack(fill='x')

                detail = tk.Frame(info, bg=Colors.LIGHT_GRAY)
                detail.pack(fill='x', pady=(3, 0))

                # Minus button
                minus_btn = tk.Button(detail, text="−", font=('Segoe UI', 10, 'bold'),
                                      bg=Colors.ERROR, fg=Colors.WHITE, relief='flat',
                                      bd=0, width=3,
                                      command=lambda n=name: self._decrease_qty(n))
                minus_btn.pack(side='left')

                tk.Label(detail, text=f"  {data['qty']}  ",
                         font=('Segoe UI', 10, 'bold'),
                         bg=Colors.LIGHT_GRAY, fg=Colors.ON_SURFACE).pack(side='left')

                # Plus button
                plus_btn = tk.Button(detail, text="+", font=('Segoe UI', 10, 'bold'),
                                     bg=Colors.SUCCESS, fg=Colors.WHITE, relief='flat',
                                     bd=0, width=3,
                                     command=lambda n=name, p=data['price']:
                                     self.add_to_cart(n, p))
                plus_btn.pack(side='left')

                item_total = data['qty'] * data['price']
                tk.Label(detail, text=f"₹{item_total:.0f}",
                         font=('Segoe UI', 10, 'bold'),
                         bg=Colors.LIGHT_GRAY, fg=Colors.SUCCESS,
                         anchor='e').pack(side='right')

                tk.Label(detail, text=f"× ₹{data['price']:.0f}",
                         font=('Segoe UI', 9),
                         bg=Colors.LIGHT_GRAY, fg=Colors.TEXT_SECONDARY).pack(
                    side='right', padx=(0, 5))

        self._update_totals()

    def _update_totals(self):
        """Recalculate and refresh the totals display."""
        if not self.total_label_ref or not self.total_label_ref.winfo_exists():
            return

        for widget in self.total_label_ref.winfo_children():
            widget.destroy()

        subtotal = sum(d['qty'] * d['price'] for d in self.cart.values())

        try:
            disc_pct = float(self.discount_pct.get())
        except (tk.TclError, ValueError):
            disc_pct = 0

        disc_pct = max(0, min(100, disc_pct))
        disc_amt = subtotal * disc_pct / 100
        after_disc = subtotal - disc_amt
        tax_amt = after_disc * self.tax_rate / 100
        total = after_disc + tax_amt

        inner = tk.Frame(self.total_label_ref, bg=Colors.LIGHT_GRAY)
        inner.pack(fill='x', padx=12, pady=8)

        rows = [
            ("Subtotal:", f"₹{subtotal:,.0f}", Colors.ON_SURFACE),
            (f"Discount ({disc_pct:.0f}%):", f"-₹{disc_amt:,.0f}", Colors.ERROR),
            (f"Tax ({self.tax_rate:.0f}%):", f"₹{tax_amt:,.0f}", Colors.TEXT_SECONDARY),
        ]

        for label, value, color in rows:
            row = tk.Frame(inner, bg=Colors.LIGHT_GRAY)
            row.pack(fill='x', pady=1)
            tk.Label(row, text=label, font=('Segoe UI', 10),
                     bg=Colors.LIGHT_GRAY, fg=Colors.TEXT_SECONDARY,
                     anchor='w').pack(side='left')
            tk.Label(row, text=value, font=('Segoe UI', 10, 'bold'),
                     bg=Colors.LIGHT_GRAY, fg=color, anchor='e').pack(side='right')

        tk.Frame(inner, bg=Colors.BORDER, height=1).pack(fill='x', pady=5)

        total_row = tk.Frame(inner, bg=Colors.LIGHT_GRAY)
        total_row.pack(fill='x')
        tk.Label(total_row, text="TOTAL:", font=('Segoe UI', 13, 'bold'),
                 bg=Colors.LIGHT_GRAY, fg=Colors.ON_SURFACE,
                 anchor='w').pack(side='left')
        tk.Label(total_row, text=f"₹{total:,.0f}", font=('Segoe UI', 13, 'bold'),
                 bg=Colors.LIGHT_GRAY, fg=Colors.SUCCESS,
                 anchor='e').pack(side='right')

    def _go_back_to_tables(self):
        """Navigate back to table selection; confirm if cart has items."""
        if self.cart:
            if not messagebox.askyesno("Leave Table?",
                                       "Cart has items. Are you sure?"):
                return
        self.current_table = None
        self.cart = {}
        self.clear_content()
        self._show_table_grid()

    # ================================================================
    # ORDER OPERATIONS
    # ================================================================

    def place_order(self):
        """Process and save the current order."""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add items to your cart first.")
            return

        subtotal = sum(d['qty'] * d['price'] for d in self.cart.values())

        try:
            disc_pct = float(self.discount_pct.get())
        except (tk.TclError, ValueError):
            disc_pct = 0

        disc_pct = max(0, min(100, disc_pct))
        disc_amt = subtotal * disc_pct / 100
        after_disc = subtotal - disc_amt
        tax_amt = after_disc * self.tax_rate / 100
        total = after_disc + tax_amt

        msg = (f"Place order for Table {self.current_table}?\n\n"
               f"Items: {sum(d['qty'] for d in self.cart.values())}\n"
               f"Total: ₹{total:,.0f}\n"
               f"Payment: {self.payment_method.get()}")

        if not messagebox.askyesno("Confirm Order", msg):
            return

        items = [{'name': name, 'price': data['price'], 'qty': data['qty']}
                 for name, data in self.cart.items()]

        try:
            order_id = self.db.place_order(
                table_number=self.current_table,
                items=items,
                subtotal=subtotal,
                discount_pct=disc_pct,
                discount_amt=disc_amt,
                tax_pct=self.tax_rate,
                tax_amt=tax_amt,
                total=total,
                payment_method=self.payment_method.get(),
                created_by=self.current_user.get('username', ''),
            )

            self._show_receipt(order_id, items, subtotal, disc_pct, disc_amt,
                               self.tax_rate, tax_amt, total)

            self.cart.clear()
            self._update_cart_display()
            self.status_var.set(f"✅ Order #{order_id} placed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")

    def _show_receipt(self, order_id, items, subtotal, disc_pct, disc_amt,
                      tax_pct, tax_amt, total):
        """Show a formatted receipt in a popup window."""
        restaurant_name = self.db.get_setting('restaurant_name', 'SmartBill Restaurant')

        lines = [
            "=" * 44,
            restaurant_name.center(44),
            "=" * 44,
            f"  Order #: {order_id}",
            f"  Table  : {self.current_table}",
            f"  Date   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Staff  : {self.current_user.get('username', '')}",
            f"  Payment: {self.payment_method.get()}",
            "-" * 44,
            f"  {'Item':<20} {'Qty':>4} {'Price':>7} {'Total':>7}",
            "-" * 44,
        ]

        for item in items:
            name_trunc = item['name'][:20]
            lines.append(
                f"  {name_trunc:<20} {item['qty']:>4} "
                f"{item['price']:>7.0f} {item['qty'] * item['price']:>7.0f}"
            )

        lines.extend([
            "-" * 44,
            f"  {'Subtotal:':>35} {subtotal:>7,.0f}",
            f"  {'Discount (' + f'{disc_pct:.0f}' + '%)':>35} -{disc_amt:>6,.0f}",
            f"  {'Tax (' + f'{tax_pct:.0f}' + '%)':>35} {tax_amt:>7,.0f}",
            "=" * 44,
            f"  {'TOTAL:':>35} ₹{total:>6,.0f}",
            "=" * 44,
            "",
            "Thank you for dining with us!".center(44),
            "=" * 44,
        ])

        receipt_text = "\n".join(lines)

        # Receipt popup
        popup = tk.Toplevel(self.root)
        popup.title(f"Receipt - Order #{order_id}")
        popup.geometry("500x620")
        popup.configure(bg=Colors.CARD)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="🧾 Order Receipt", font=('Segoe UI', 16, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(pady=(15, 10))

        text_widget = tk.Text(popup, font=('Courier New', 10), bg=Colors.LIGHT_GRAY,
                              fg=Colors.ON_SURFACE, relief='flat', bd=10, wrap='none')
        text_widget.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        text_widget.insert('1.0', receipt_text)
        text_widget.config(state='disabled')

        btn_frame = tk.Frame(popup, bg=Colors.CARD)
        btn_frame.pack(fill='x', padx=20, pady=(0, 15))

        def save_receipt():
            reports_dir = os.path.join(BASE_DIR, 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            filepath = os.path.join(reports_dir, f"receipt_{order_id}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            messagebox.showinfo("Saved", f"Receipt saved to:\n{filepath}")

        save_btn = self._create_button(btn_frame, "💾 Save Receipt", save_receipt,
                                       bg=Colors.ACCENT)
        save_btn.pack(side='left', padx=(0, 5))

        close_btn = self._create_button(btn_frame, "Close", popup.destroy,
                                        bg=Colors.TEXT_SECONDARY)
        close_btn.pack(side='right')

    # ================================================================
    # ORDER HISTORY VIEW
    # ================================================================

    def show_orders(self):
        """Display order history with filters and a sortable table."""
        header = self._create_header(self.content_frame, "Order History",
                                     "View and manage past orders")

        export_btn = self._create_button(header, "📤 Export CSV", self.export_orders,
                                         bg=Colors.PURPLE)
        export_btn.pack(side='right')

        # Filters
        filter_card = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                               highlightbackground=Colors.BORDER, highlightthickness=1)
        filter_card.pack(fill='x', padx=30, pady=(0, 15))

        f_inner = tk.Frame(filter_card, bg=Colors.CARD)
        f_inner.pack(fill='x', padx=15, pady=12)

        tk.Label(f_inner, text="From:", font=('Segoe UI', 10),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(side='left', padx=(0, 5))

        start_var = tk.StringVar(
            value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        tk.Entry(f_inner, textvariable=start_var, font=('Segoe UI', 10),
                 relief='flat', bd=5, bg=Colors.LIGHT_GRAY, width=12).pack(
            side='left', padx=(0, 15))

        tk.Label(f_inner, text="To:", font=('Segoe UI', 10),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(side='left', padx=(0, 5))

        end_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        tk.Entry(f_inner, textvariable=end_var, font=('Segoe UI', 10),
                 relief='flat', bd=5, bg=Colors.LIGHT_GRAY, width=12).pack(
            side='left', padx=(0, 15))

        tk.Label(f_inner, text="Table:", font=('Segoe UI', 10),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(side='left', padx=(0, 5))

        num_tables = int(self.db.get_setting('num_tables', '20'))
        table_var = tk.StringVar(value='All')
        ttk.Combobox(f_inner, textvariable=table_var, width=8,
                     values=['All'] + [str(i) for i in range(1, num_tables + 1)],
                     state='readonly').pack(side='left', padx=(0, 15))

        # Treeview for orders
        tree_frame = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                              highlightbackground=Colors.BORDER, highlightthickness=1)
        tree_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))

        columns = ('id', 'table', 'datetime', 'items', 'subtotal',
                   'discount', 'tax', 'total', 'payment')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                            style='Custom.Treeview')

        headings = {
            'id': ('Order #', 70), 'table': ('Table', 60),
            'datetime': ('Date & Time', 150), 'items': ('Items', 60),
            'subtotal': ('Subtotal', 90), 'discount': ('Discount', 80),
            'tax': ('Tax', 70), 'total': ('Total', 100),
            'payment': ('Payment', 80),
        }
        for col, (heading, width) in headings.items():
            tree.heading(col, text=heading)
            tree.column(col, width=width, minwidth=50, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def populate_tree(orders):
            tree.delete(*tree.get_children())
            for order in orders:
                order_items = self.db.get_order_items(order['id'])
                item_count = sum(i.get('quantity', 0) for i in order_items)
                tree.insert('', 'end', values=(
                    f"#{order['id']}",
                    order.get('table_number', '-'),
                    order['datetime'][:16],
                    item_count,
                    f"₹{order.get('subtotal', order['total_amount']):,.0f}",
                    f"-₹{order.get('discount_amount', 0):,.0f}",
                    f"₹{order.get('tax_amount', 0):,.0f}",
                    f"₹{order['total_amount']:,.0f}",
                    order.get('payment_method', 'Cash'),
                ))

        def apply_filter():
            table_num = None if table_var.get() == 'All' else int(table_var.get())
            orders = self.db.get_orders(start_date=start_var.get(),
                                        end_date=end_var.get(),
                                        table_number=table_num)
            populate_tree(orders)

        filter_btn = self._create_button(f_inner, "🔍 Filter", apply_filter,
                                         bg=Colors.ACCENT)
        filter_btn.pack(side='left')

        # Double-click to view details
        def on_double_click(event):
            selected = tree.selection()
            if selected:
                values = tree.item(selected[0])['values']
                order_id = int(str(values[0]).replace('#', ''))
                self._view_order_details(order_id)

        tree.bind('<Double-1>', on_double_click)

        tk.Label(self.content_frame, text="💡 Double-click an order to view details",
                 font=('Segoe UI', 9), bg=Colors.SURFACE,
                 fg=Colors.TEXT_SECONDARY).pack(pady=(0, 10))

        # Load initial data
        apply_filter()

    def _view_order_details(self, order_id):
        """Show detailed order information in a popup."""
        orders = self.db.get_orders()
        order = next((o for o in orders if o['id'] == order_id), None)
        if not order:
            messagebox.showerror("Error", "Order not found.")
            return

        items = self.db.get_order_items(order_id)

        popup = tk.Toplevel(self.root)
        popup.title(f"Order #{order_id} Details")
        popup.geometry("500x580")
        popup.configure(bg=Colors.CARD)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text=f"📋 Order #{order_id}", font=('Segoe UI', 18, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(pady=(15, 5))

        # Order info
        info_frame = tk.Frame(popup, bg=Colors.LIGHT_GRAY)
        info_frame.pack(fill='x', padx=20, pady=10)

        info_data = [
            ("Table:", order.get('table_number', '-')),
            ("Date:", order['datetime']),
            ("Staff:", order.get('created_by', 'N/A')),
            ("Payment:", order.get('payment_method', 'Cash')),
            ("Status:", order.get('status', 'Completed')),
        ]

        for label, value in info_data:
            row = tk.Frame(info_frame, bg=Colors.LIGHT_GRAY)
            row.pack(fill='x', padx=15, pady=3)
            tk.Label(row, text=label, font=('Segoe UI', 10, 'bold'),
                     bg=Colors.LIGHT_GRAY, fg=Colors.ON_SURFACE, width=10,
                     anchor='w').pack(side='left')
            tk.Label(row, text=str(value), font=('Segoe UI', 10),
                     bg=Colors.LIGHT_GRAY, fg=Colors.TEXT_SECONDARY).pack(side='left')

        # Items list
        tk.Label(popup, text="Items Ordered:", font=('Segoe UI', 12, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE,
                 anchor='w').pack(fill='x', padx=20, pady=(15, 5))

        for item in items:
            row = tk.Frame(popup, bg=Colors.CARD)
            row.pack(fill='x', padx=25, pady=2)
            tk.Label(row, text=f"• {item.get('item_name', '')}", font=('Segoe UI', 10),
                     bg=Colors.CARD, fg=Colors.ON_SURFACE, anchor='w').pack(side='left')
            qty = item.get('quantity', 0)
            tp = item.get('total_price', 0)
            tk.Label(row, text=f"x{qty}  ₹{tp:,.0f}",
                     font=('Segoe UI', 10, 'bold'), bg=Colors.CARD,
                     fg=Colors.SUCCESS, anchor='e').pack(side='right')

        # Totals
        tk.Frame(popup, bg=Colors.BORDER, height=1).pack(fill='x', padx=20, pady=10)

        totals = [
            ("Subtotal:", f"₹{order.get('subtotal', order['total_amount']):,.0f}"),
            (f"Discount ({order.get('discount_percent', 0):.0f}%):",
             f"-₹{order.get('discount_amount', 0):,.0f}"),
            (f"Tax ({order.get('tax_percent', 0):.0f}%):",
             f"₹{order.get('tax_amount', 0):,.0f}"),
            ("TOTAL:", f"₹{order['total_amount']:,.0f}"),
        ]

        for label, value in totals:
            row = tk.Frame(popup, bg=Colors.CARD)
            row.pack(fill='x', padx=25, pady=2)
            is_total = label == "TOTAL:"
            font = ('Segoe UI', 12 if is_total else 10, 'bold')
            color = Colors.SUCCESS if is_total else Colors.ON_SURFACE
            tk.Label(row, text=label, font=font, bg=Colors.CARD,
                     fg=Colors.ON_SURFACE, anchor='w').pack(side='left')
            tk.Label(row, text=value, font=font, bg=Colors.CARD,
                     fg=color, anchor='e').pack(side='right')

        self._create_button(popup, "Close", popup.destroy,
                            bg=Colors.TEXT_SECONDARY).pack(pady=15)

    # ================================================================
    # MENU MANAGEMENT VIEW
    # ================================================================

    def show_menu(self):
        """Display the menu management view with CRUD operations."""
        header = self._create_header(self.content_frame, "Menu Manager",
                                     "Add, edit, and remove menu items")

        add_btn = self._create_button(header, "+ Add New Item", self._add_item_dialog,
                                      bg=Colors.SUCCESS)
        add_btn.pack(side='right')

        # Filters row
        filter_frame = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        filter_frame.pack(fill='x', padx=30, pady=(0, 10))

        tk.Label(filter_frame, text="Category:", font=('Segoe UI', 10),
                 bg=Colors.SURFACE, fg=Colors.ON_SURFACE).pack(side='left')

        categories = ['All'] + self.db.get_categories()
        cat_var = tk.StringVar(value='All')
        cat_combo = ttk.Combobox(filter_frame, textvariable=cat_var, values=categories,
                                 state='readonly', width=20)
        cat_combo.pack(side='left', padx=10)

        tk.Label(filter_frame, text="Search:", font=('Segoe UI', 10),
                 bg=Colors.SURFACE, fg=Colors.ON_SURFACE).pack(side='left', padx=(20, 5))

        search_var = tk.StringVar()
        tk.Entry(filter_frame, textvariable=search_var, font=('Segoe UI', 10),
                 relief='flat', bd=5, bg=Colors.LIGHT_GRAY, width=20).pack(side='left')

        # Treeview
        tree_frame = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                              highlightbackground=Colors.BORDER, highlightthickness=1)
        tree_frame.pack(fill='both', expand=True, padx=30, pady=(0, 10))

        columns = ('id', 'name', 'price', 'category')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                            style='Custom.Treeview')

        for col, heading, width in [('id', 'ID', 60), ('name', 'Item Name', 250),
                                     ('price', 'Price (₹)', 120),
                                     ('category', 'Category', 200)]:
            tree.heading(col, text=heading)
            tree.column(col, width=width, anchor='center')

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        def load_items():
            tree.delete(*tree.get_children())
            cat = None if cat_var.get() == 'All' else cat_var.get()
            search = search_var.get() if search_var.get() else None
            items = self.db.get_menu_items(category=cat, search=search)
            for item in items:
                tree.insert('', 'end', values=(
                    item['id'], item['name'],
                    f"₹{item['price']:.0f}", item['category']))

        cat_combo.bind('<<ComboboxSelected>>', lambda e: load_items())
        search_var.trace_add('write', lambda *args: load_items())

        # Action buttons
        btn_frame = tk.Frame(self.content_frame, bg=Colors.SURFACE)
        btn_frame.pack(fill='x', padx=30, pady=(0, 15))

        def edit_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Item", "Please select an item to edit.")
                return
            values = tree.item(selected[0])['values']
            item = {
                'id': values[0], 'name': values[1],
                'price': float(str(values[2]).replace('₹', '').replace(',', '')),
                'category': values[3],
            }
            self._edit_item_dialog(item, load_items)

        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select Item", "Please select an item to delete.")
                return
            values = tree.item(selected[0])['values']
            if messagebox.askyesno("Delete Item", f"Delete '{values[1]}'?"):
                self.db.delete_menu_item(values[0])
                load_items()
                self.status_var.set(f"✅ '{values[1]}' removed from menu")

        self._create_button(btn_frame, "✏️ Edit Selected", edit_selected,
                            bg=Colors.ACCENT).pack(side='left', padx=(0, 10))
        self._create_button(btn_frame, "🗑️ Delete Selected", delete_selected,
                            bg=Colors.ERROR).pack(side='left')

        self._menu_loader = load_items
        load_items()

    def _add_item_dialog(self):
        """Show a dialog to add a new menu item."""
        popup = tk.Toplevel(self.root)
        popup.title("Add New Menu Item")
        popup.geometry("420x380")
        popup.configure(bg=Colors.CARD)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="➕ Add Menu Item", font=('Segoe UI', 16, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(pady=(15, 15))

        form = tk.Frame(popup, bg=Colors.CARD)
        form.pack(fill='x', padx=30)

        # Name
        tk.Label(form, text="Item Name:", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
        name_entry = tk.Entry(form, font=('Segoe UI', 11), relief='flat', bd=5,
                              bg=Colors.LIGHT_GRAY)
        name_entry.pack(fill='x', pady=(0, 12))

        # Price
        tk.Label(form, text="Price (₹):", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
        price_entry = tk.Entry(form, font=('Segoe UI', 11), relief='flat', bd=5,
                               bg=Colors.LIGHT_GRAY)
        price_entry.pack(fill='x', pady=(0, 12))

        # Category
        tk.Label(form, text="Category:", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
        categories = self.db.get_categories()
        cat_var = tk.StringVar()
        ttk.Combobox(form, textvariable=cat_var, values=categories,
                     font=('Segoe UI', 11)).pack(fill='x', pady=(0, 20))

        def save():
            name = name_entry.get().strip()
            price_str = price_entry.get().strip()
            category = cat_var.get().strip()

            if not name or not price_str or not category:
                messagebox.showwarning("Missing Data", "Please fill all fields.")
                return
            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Price", "Price must be a positive number.")
                return

            self.db.add_menu_item(name, price, category)
            messagebox.showinfo("Success", f"'{name}' added successfully!")
            popup.destroy()
            if self._menu_loader:
                self._menu_loader()

        btn_frame = tk.Frame(form, bg=Colors.CARD)
        btn_frame.pack(fill='x')

        self._create_button(btn_frame, "Save", save, bg=Colors.SUCCESS).pack(side='left')
        self._create_button(btn_frame, "Cancel", popup.destroy,
                            bg=Colors.TEXT_SECONDARY).pack(side='right')

        name_entry.focus_set()

    def _edit_item_dialog(self, item, refresh_callback):
        """Show a dialog to edit an existing menu item."""
        popup = tk.Toplevel(self.root)
        popup.title(f"Edit: {item['name']}")
        popup.geometry("420x380")
        popup.configure(bg=Colors.CARD)
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="✏️ Edit Menu Item", font=('Segoe UI', 16, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(pady=(15, 15))

        form = tk.Frame(popup, bg=Colors.CARD)
        form.pack(fill='x', padx=30)

        tk.Label(form, text="Item Name:", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
        name_entry = tk.Entry(form, font=('Segoe UI', 11), relief='flat', bd=5,
                              bg=Colors.LIGHT_GRAY)
        name_entry.pack(fill='x', pady=(0, 12))
        name_entry.insert(0, item['name'])

        tk.Label(form, text="Price (₹):", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
        price_entry = tk.Entry(form, font=('Segoe UI', 11), relief='flat', bd=5,
                               bg=Colors.LIGHT_GRAY)
        price_entry.pack(fill='x', pady=(0, 12))
        price_entry.insert(0, str(item['price']))

        tk.Label(form, text="Category:", font=('Segoe UI', 11, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
        categories = self.db.get_categories()
        cat_var = tk.StringVar(value=item['category'])
        ttk.Combobox(form, textvariable=cat_var, values=categories,
                     font=('Segoe UI', 11)).pack(fill='x', pady=(0, 20))

        def save():
            name = name_entry.get().strip()
            price_str = price_entry.get().strip()
            category = cat_var.get().strip()

            if not name or not price_str or not category:
                messagebox.showwarning("Missing Data", "Please fill all fields.")
                return
            try:
                price = float(price_str)
                if price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Price", "Price must be a positive number.")
                return

            self.db.update_menu_item(item['id'], name, price, category)
            messagebox.showinfo("Success", f"'{name}' updated!")
            popup.destroy()
            refresh_callback()

        btn_frame = tk.Frame(form, bg=Colors.CARD)
        btn_frame.pack(fill='x')

        self._create_button(btn_frame, "Save Changes", save,
                            bg=Colors.SUCCESS).pack(side='left')
        self._create_button(btn_frame, "Cancel", popup.destroy,
                            bg=Colors.TEXT_SECONDARY).pack(side='right')

    # ================================================================
    # ANALYTICS VIEW
    # ================================================================

    def show_analytics(self):
        """Display analytics with embedded matplotlib charts."""
        self._create_header(self.content_frame, "Analytics", "Sales insights and trends")

        if not MATPLOTLIB_AVAILABLE:
            msg_frame = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                                 highlightbackground=Colors.BORDER, highlightthickness=1)
            msg_frame.pack(fill='both', expand=True, padx=30, pady=20)

            tk.Label(msg_frame, text="📊 Charts require matplotlib",
                     font=('Segoe UI', 16, 'bold'), bg=Colors.CARD,
                     fg=Colors.ON_SURFACE).pack(pady=(40, 10))
            tk.Label(msg_frame, text="Install it with:  pip install matplotlib",
                     font=('Segoe UI', 12), bg=Colors.CARD,
                     fg=Colors.TEXT_SECONDARY).pack()

            self._show_text_analytics(msg_frame)
            return

        # Tabbed charts
        notebook = ttk.Notebook(self.content_frame)
        notebook.pack(fill='both', expand=True, padx=30, pady=(0, 20))

        tabs = [
            ("  Top Items  ", self._chart_top_items),
            ("  Monthly Sales  ", self._chart_monthly_sales),
            ("  Categories  ", self._chart_categories),
            ("  Hourly Trend  ", self._chart_hourly),
        ]

        for title, builder in tabs:
            tab = tk.Frame(notebook, bg=Colors.CARD)
            notebook.add(tab, text=title)
            builder(tab)

    def _chart_top_items(self, parent):
        """Horizontal bar chart of top selling items."""
        items = self.db.get_top_items(10)
        if not items:
            tk.Label(parent, text="No order data yet.", font=('Segoe UI', 14),
                     bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(expand=True)
            return

        fig = Figure(figsize=(9, 5), facecolor=Colors.CARD)
        ax = fig.add_subplot(111)

        names = [i['item_name'][:18] for i in reversed(items)]
        qtys = [i['total_qty'] for i in reversed(items)]

        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                  '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#a18cd1']

        bars = ax.barh(names, qtys, color=colors[:len(names)])
        ax.set_title('Top 10 Selling Items', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Quantity Sold', fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.3, bar.get_y() + bar.get_height() / 2,
                    f'{int(w)}', ha='left', va='center', fontsize=9, fontweight='bold')

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def _chart_monthly_sales(self, parent):
        """Bar chart of monthly sales revenue."""
        data = self.db.get_monthly_sales(12)
        if not data:
            tk.Label(parent, text="No order data yet.", font=('Segoe UI', 14),
                     bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(expand=True)
            return

        fig = Figure(figsize=(9, 5), facecolor=Colors.CARD)
        ax = fig.add_subplot(111)

        months = [d['month'] for d in reversed(data)]
        totals = [d['total'] for d in reversed(data)]

        bars = ax.bar(months, totals, color='#667eea', width=0.6)
        ax.set_title('Monthly Sales Revenue', fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel('Revenue (₹)', fontsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 20,
                    f'₹{int(h):,}', ha='center', va='bottom',
                    fontsize=8, fontweight='bold')

        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def _chart_categories(self, parent):
        """Pie chart of sales by category."""
        data = self.db.get_category_sales()
        if not data:
            tk.Label(parent, text="No order data yet.", font=('Segoe UI', 14),
                     bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(expand=True)
            return

        fig = Figure(figsize=(9, 5), facecolor=Colors.CARD)
        ax = fig.add_subplot(111)

        cats = [d['category'] for d in data]
        totals = [d['total'] for d in data]

        pie_colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe',
                      '#00f2fe', '#43e97b', '#fa709a', '#fee140', '#a18cd1',
                      '#fbc2eb', '#89f7fe']

        wedges, texts, autotexts = ax.pie(
            totals, labels=cats, autopct='%1.1f%%',
            colors=pie_colors[:len(cats)], startangle=90, pctdistance=0.85)

        for t in texts:
            t.set_fontsize(9)
        for at in autotexts:
            at.set_fontsize(8)
            at.set_fontweight('bold')

        ax.set_title('Sales by Category', fontsize=14, fontweight='bold', pad=15)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def _chart_hourly(self, parent):
        """Area chart of orders by hour of day."""
        data = self.db.get_hourly_distribution()
        if not data:
            tk.Label(parent, text="No order data yet.", font=('Segoe UI', 14),
                     bg=Colors.CARD, fg=Colors.TEXT_SECONDARY).pack(expand=True)
            return

        fig = Figure(figsize=(9, 5), facecolor=Colors.CARD)
        ax = fig.add_subplot(111)

        hours = [d['hour'] for d in data]
        counts = [d['count'] for d in data]

        ax.fill_between(hours, counts, alpha=0.3, color='#667eea')
        ax.plot(hours, counts, color='#667eea', linewidth=2, marker='o', markersize=6)

        ax.set_title('Orders by Hour of Day', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Hour', fontsize=11)
        ax.set_ylabel('Number of Orders', fontsize=11)
        ax.set_xticks(range(0, 24))
        ax.set_xticklabels([f'{h}:00' for h in range(0, 24)], rotation=45, fontsize=7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

    def _show_text_analytics(self, parent):
        """Fallback text-based analytics when matplotlib is not installed."""
        stats = self.db.get_dashboard_stats()
        top_items = self.db.get_top_items(5)

        tk.Label(parent, text="\n📊 Quick Stats", font=('Segoe UI', 14, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', padx=20)

        for line in [f"Total Orders: {stats['total_orders']}",
                     f"Total Revenue: ₹{stats['total_revenue']:,.0f}",
                     f"Average Order: ₹{stats['avg_order']:,.0f}",
                     f"Menu Items: {stats['menu_count']}"]:
            tk.Label(parent, text=f"  {line}", font=('Segoe UI', 11),
                     bg=Colors.CARD, fg=Colors.ON_SURFACE,
                     anchor='w').pack(fill='x', padx=20, pady=2)

        if top_items:
            tk.Label(parent, text="\n🏆 Top Selling Items",
                     font=('Segoe UI', 14, 'bold'),
                     bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', padx=20)
            for i, item in enumerate(top_items, 1):
                tk.Label(parent,
                         text=f"  {i}. {item['item_name']} — {item['total_qty']} sold",
                         font=('Segoe UI', 11), bg=Colors.CARD, fg=Colors.ON_SURFACE,
                         anchor='w').pack(fill='x', padx=20, pady=2)

    # ================================================================
    # SETTINGS VIEW
    # ================================================================

    def show_settings(self):
        """Display settings view for configuring the application."""
        self._create_header(self.content_frame, "Settings", "Configure your restaurant")

        # Main settings card
        card = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(fill='x', padx=30, pady=(0, 20))

        form = tk.Frame(card, bg=Colors.CARD)
        form.pack(fill='x', padx=30, pady=25)

        fields = []

        def make_field(label_text, default_key, default_value, width=40):
            tk.Label(form, text=label_text, font=('Segoe UI', 12, 'bold'),
                     bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 3))
            var = tk.StringVar(value=self.db.get_setting(default_key, default_value))
            entry = tk.Entry(form, textvariable=var, font=('Segoe UI', 12),
                             relief='flat', bd=5, bg=Colors.LIGHT_GRAY, width=width)
            entry.pack(anchor='w', pady=(0, 18))
            fields.append((default_key, var))
            return var

        name_var = make_field("Restaurant Name:", "restaurant_name",
                              "SmartBill Restaurant")
        tax_var = make_field("Tax Rate (%):", "tax_rate", "5", width=10)
        tables_var = make_field("Number of Tables:", "num_tables", "20", width=10)
        curr_var = make_field("Currency Symbol:", "currency_symbol", "₹", width=5)

        def save_settings():
            try:
                tax = float(tax_var.get())
                tables = int(tables_var.get())

                if not (0 <= tax <= 100):
                    raise ValueError("Tax rate must be between 0 and 100")
                if not (1 <= tables <= 100):
                    raise ValueError("Tables must be between 1 and 100")

                for key, var in fields:
                    self.db.set_setting(key, var.get())

                self.tax_rate = tax

                messagebox.showinfo("Settings Saved", "Settings saved successfully!")
                self.status_var.set("✅ Settings saved")

            except ValueError as e:
                messagebox.showerror("Invalid Input", str(e))

        self._create_button(form, "💾 Save Settings", save_settings,
                            bg=Colors.SUCCESS).pack(anchor='w')

        # Account info card
        account_card = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                                highlightbackground=Colors.BORDER, highlightthickness=1)
        account_card.pack(fill='x', padx=30, pady=(0, 20))

        acc_inner = tk.Frame(account_card, bg=Colors.CARD)
        acc_inner.pack(fill='x', padx=30, pady=20)

        tk.Label(acc_inner, text="👤 Account Information",
                 font=('Segoe UI', 14, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 10))
        tk.Label(acc_inner,
                 text=f"Username: {self.current_user.get('username', '')}",
                 font=('Segoe UI', 11), bg=Colors.CARD,
                 fg=Colors.ON_SURFACE).pack(anchor='w', pady=2)
        tk.Label(acc_inner,
                 text=f"Role: {self.current_user.get('role', '').title()}",
                 font=('Segoe UI', 11), bg=Colors.CARD,
                 fg=Colors.ON_SURFACE).pack(anchor='w', pady=2)

        # About card
        about_card = tk.Frame(self.content_frame, bg=Colors.CARD, relief='flat', bd=0,
                              highlightbackground=Colors.BORDER, highlightthickness=1)
        about_card.pack(fill='x', padx=30, pady=(0, 20))

        about_inner = tk.Frame(about_card, bg=Colors.CARD)
        about_inner.pack(fill='x', padx=30, pady=20)

        tk.Label(about_inner, text="ℹ️ About SmartBill Pro",
                 font=('Segoe UI', 14, 'bold'),
                 bg=Colors.CARD, fg=Colors.ON_SURFACE).pack(anchor='w', pady=(0, 5))
        tk.Label(about_inner,
                 text="Version 2.0 • Restaurant Billing & Management System",
                 font=('Segoe UI', 11), bg=Colors.CARD,
                 fg=Colors.TEXT_SECONDARY).pack(anchor='w')
        tk.Label(about_inner, text="Built with Python & Tkinter",
                 font=('Segoe UI', 10), bg=Colors.CARD,
                 fg=Colors.TEXT_SECONDARY).pack(anchor='w')

    # ================================================================
    # UTILITY METHODS
    # ================================================================

    def logout(self):
        """Logout the current user and return to the login screen."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.current_table = None
            self.cart = {}
            self.show_login()

    def export_orders(self):
        """Export orders to a CSV file via a save dialog."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Export Orders",
            initialfile=f"orders_{datetime.now().strftime('%Y%m%d')}.csv",
        )

        if filepath:
            try:
                self.db.export_orders_csv(filepath)
                messagebox.showinfo("Export Complete",
                                    f"Orders exported to:\n{filepath}")
                self.status_var.set(
                    f"✅ Orders exported to {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Export Error",
                                     f"Failed to export: {str(e)}")


# ====================================================================
# ENTRY POINT
# ====================================================================

if __name__ == "__main__":
    app = SmartBillApp()