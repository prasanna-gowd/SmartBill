"""
SmartBill Pro - Report Generator
Generates formatted text and CSV reports for sales data.
"""

import os
import csv
from datetime import datetime, timedelta


class ReportGenerator:
    """Generates various business reports from order data."""

    def __init__(self, db_manager, output_dir=None):
        self.db = db_manager
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'reports'
        )
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_filepath(self, prefix, extension='txt'):
        """Generate a timestamped filepath for a report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.{extension}"
        return os.path.join(self.output_dir, filename)

    # ================================================================
    # Daily Sales Report
    # ================================================================

    def generate_daily_report(self, date=None):
        """Generate a detailed daily sales report.

        Args:
            date: Date string in YYYY-MM-DD format. Defaults to today.

        Returns:
            str: Path to the generated report file.
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        orders = self.db.get_orders(start_date=date, end_date=date)
        top_items = self.db.get_top_items(limit=10, start_date=date, end_date=date)

        total_revenue = sum(o.get('total_amount', 0) for o in orders)
        total_orders = len(orders)
        avg_order = total_revenue / total_orders if total_orders > 0 else 0

        # Payment method breakdown
        payment_counts = {}
        for order in orders:
            method = order.get('payment_method', 'Cash')
            if method not in payment_counts:
                payment_counts[method] = {'count': 0, 'total': 0}
            payment_counts[method]['count'] += 1
            payment_counts[method]['total'] += order.get('total_amount', 0)

        # Build report
        lines = [
            "=" * 60,
            "DAILY SALES REPORT".center(60),
            "=" * 60,
            f"  Date          : {date}",
            f"  Generated     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "--- SUMMARY ---",
            f"  Total Orders  : {total_orders}",
            f"  Total Revenue : ₹{total_revenue:,.2f}",
            f"  Average Order : ₹{avg_order:,.2f}",
            "",
            "--- PAYMENT BREAKDOWN ---",
        ]

        for method, data in payment_counts.items():
            lines.append(
                f"  {method:<12} : {data['count']:>4} orders  |  ₹{data['total']:>10,.2f}"
            )

        if top_items:
            lines.extend(["", "--- TOP SELLING ITEMS ---"])
            lines.append(f"  {'#':<4} {'Item':<25} {'Qty':>6} {'Revenue':>12}")
            lines.append("  " + "-" * 50)
            for i, item in enumerate(top_items, 1):
                lines.append(
                    f"  {i:<4} {item['item_name'][:25]:<25} "
                    f"{item['total_qty']:>6} ₹{item.get('total_revenue', 0):>10,.2f}"
                )

        if orders:
            lines.extend(["", "--- ORDER DETAILS ---"])
            lines.append(
                f"  {'ID':<6} {'Table':>6} {'Time':>8} {'Items':>6} "
                f"{'Total':>10} {'Payment':<8}"
            )
            lines.append("  " + "-" * 55)
            for order in orders:
                items = self.db.get_order_items(order['id'])
                item_count = sum(i.get('quantity', 0) for i in items)
                time_str = order.get('datetime', '')
                if len(time_str) > 10:
                    time_str = time_str[11:16]
                lines.append(
                    f"  #{order['id']:<5} {order.get('table_number', '-'):>5} "
                    f"{time_str:>8} {item_count:>6} "
                    f"₹{order['total_amount']:>9,.2f} "
                    f"{order.get('payment_method', 'Cash'):<8}"
                )

        lines.extend([
            "",
            "=" * 60,
            "End of Report".center(60),
            "=" * 60,
        ])

        filepath = self._get_filepath(f"daily_report_{date}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return filepath

    # ================================================================
    # Monthly Summary Report
    # ================================================================

    def generate_monthly_report(self, year=None, month=None):
        """Generate a monthly summary report.

        Args:
            year: Year (int). Defaults to current year.
            month: Month (1-12). Defaults to current month.

        Returns:
            str: Path to the generated report file.
        """
        now = datetime.now()
        year = year or now.year
        month = month or now.month

        start_date = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1:04d}-01-01"
        else:
            end_date = f"{year:04d}-{month + 1:02d}-01"

        # Get last day of month
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        end_date = f"{year:04d}-{month:02d}-{last_day:02d}"

        orders = self.db.get_orders(start_date=start_date, end_date=end_date)
        daily_sales = self.db.get_daily_sales(start_date, end_date)
        top_items = self.db.get_top_items(limit=15, start_date=start_date,
                                           end_date=end_date)

        total_revenue = sum(o.get('total_amount', 0) for o in orders)
        total_orders = len(orders)
        avg_daily_revenue = total_revenue / last_day if last_day > 0 else 0
        avg_order = total_revenue / total_orders if total_orders > 0 else 0

        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[month]

        lines = [
            "=" * 60,
            "MONTHLY SALES REPORT".center(60),
            "=" * 60,
            f"  Month         : {month_name} {year}",
            f"  Period        : {start_date} to {end_date}",
            f"  Generated     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            "--- SUMMARY ---",
            f"  Total Orders       : {total_orders}",
            f"  Total Revenue      : ₹{total_revenue:,.2f}",
            f"  Avg Order Value    : ₹{avg_order:,.2f}",
            f"  Avg Daily Revenue  : ₹{avg_daily_revenue:,.2f}",
            f"  Active Days        : {len(daily_sales)} / {last_day}",
            "",
        ]

        if daily_sales:
            # Find best and worst days
            best_day = max(daily_sales, key=lambda d: d.get('total', 0))
            worst_day = min(daily_sales, key=lambda d: d.get('total', 0))

            lines.extend([
                "--- HIGHLIGHTS ---",
                f"  Best Day   : {best_day['date']} — ₹{best_day['total']:,.2f} "
                f"({best_day['order_count']} orders)",
                f"  Slowest Day: {worst_day['date']} — ₹{worst_day['total']:,.2f} "
                f"({worst_day['order_count']} orders)",
                "",
                "--- DAILY BREAKDOWN ---",
                f"  {'Date':<12} {'Orders':>8} {'Revenue':>12}",
                "  " + "-" * 35,
            ])
            for day in daily_sales:
                lines.append(
                    f"  {day['date']:<12} {day['order_count']:>8} "
                    f"₹{day['total']:>11,.2f}"
                )

        if top_items:
            lines.extend(["", "--- TOP 15 ITEMS ---"])
            lines.append(f"  {'#':<4} {'Item':<25} {'Qty':>6} {'Revenue':>12}")
            lines.append("  " + "-" * 50)
            for i, item in enumerate(top_items, 1):
                lines.append(
                    f"  {i:<4} {item['item_name'][:25]:<25} "
                    f"{item['total_qty']:>6} ₹{item.get('total_revenue', 0):>10,.2f}"
                )

        lines.extend([
            "",
            "=" * 60,
            "End of Report".center(60),
            "=" * 60,
        ])

        filepath = self._get_filepath(f"monthly_report_{year}_{month:02d}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return filepath

    # ================================================================
    # Orders CSV Export (enhanced)
    # ================================================================

    def export_detailed_csv(self, start_date=None, end_date=None):
        """Export detailed order data with items to CSV.

        Args:
            start_date: Start date filter (YYYY-MM-DD).
            end_date: End date filter (YYYY-MM-DD).

        Returns:
            str: Path to the generated CSV file.
        """
        orders = self.db.get_orders(start_date=start_date, end_date=end_date)
        filepath = self._get_filepath("orders_detailed", "csv")

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Order ID', 'Table', 'Date', 'Time', 'Item Name',
                'Quantity', 'Unit Price', 'Item Total', 'Order Subtotal',
                'Discount %', 'Discount Amount', 'Tax %', 'Tax Amount',
                'Order Total', 'Payment Method', 'Staff'
            ])

            for order in orders:
                items = self.db.get_order_items(order['id'])
                dt = order.get('datetime', '')
                date_part = dt[:10] if len(dt) >= 10 else dt
                time_part = dt[11:19] if len(dt) >= 19 else ''

                for item in items:
                    writer.writerow([
                        order['id'],
                        order.get('table_number', ''),
                        date_part,
                        time_part,
                        item.get('item_name', ''),
                        item.get('quantity', 0),
                        item.get('unit_price', 0),
                        item.get('total_price', 0),
                        order.get('subtotal', order['total_amount']),
                        order.get('discount_percent', 0),
                        order.get('discount_amount', 0),
                        order.get('tax_percent', 0),
                        order.get('tax_amount', 0),
                        order['total_amount'],
                        order.get('payment_method', 'Cash'),
                        order.get('created_by', ''),
                    ])

        return filepath

    # ================================================================
    # Menu Export
    # ================================================================

    def export_menu_csv(self):
        """Export the current menu to CSV.

        Returns:
            str: Path to the generated CSV file.
        """
        items = self.db.get_menu_items()
        filepath = self._get_filepath("menu_export", "csv")

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Price', 'Category', 'Active'])

            for item in items:
                writer.writerow([
                    item['id'], item['name'], item['price'],
                    item['category'], item.get('is_active', 1)
                ])

        return filepath
