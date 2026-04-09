#!/usr/bin/env python3
"""
Trading Assistant Database Initialization
创建和初始化持仓数据库
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加父目录到路径
SKILL_ROOT = Path(__file__).parent.parent
DB_DIR = SKILL_ROOT / "database"


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.db_dir = DB_DIR
        self.db_dir.mkdir(exist_ok=True)

        # 数据库路径
        self.positions_db_path = self.db_dir / "positions.db"
        self.transactions_db_path = self.db_dir / "transactions.db"
        self.alerts_db_path = self.db_dir / "alerts.db"

    def init_positions_db(self):
        """初始化持仓数据库"""
        conn = sqlite3.connect(self.positions_db_path)
        cursor = conn.cursor()

        # 创建持仓表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT,
                sector TEXT,
                exchange TEXT,
                quantity INTEGER DEFAULT 0,
                cost_price REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                current_price REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                pnl REAL DEFAULT 0,
                pnl_pct REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_positions_sector ON positions(sector)')

        # 创建持仓汇总视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS position_summary AS
            SELECT
                COUNT(*) as total_positions,
                SUM(market_value) as total_value,
                SUM(total_cost) as total_cost,
                SUM(pnl) as total_pnl,
                CASE
                    WHEN SUM(total_cost) > 0 THEN (SUM(pnl) / SUM(total_cost) * 100)
                    ELSE 0
                END as total_pnl_pct
            FROM positions WHERE quantity > 0
        ''')

        conn.commit()
        conn.close()

        print(f"✓ Positions database initialized: {self.positions_db_path}")

    def init_transactions_db(self):
        """初始化交易记录数据库"""
        conn = sqlite3.connect(self.transactions_db_path)
        cursor = conn.cursor()

        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT,
                action TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                amount REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                fee REAL DEFAULT 0
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON transactions(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_action ON transactions(action)')

        # 创建交易汇总视图（按股票）
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS transaction_summary_by_stock AS
            SELECT
                symbol,
                name,
                SUM(CASE WHEN action = 'buy' THEN quantity ELSE 0 END) as total_bought,
                SUM(CASE WHEN action = 'sell' THEN quantity ELSE 0 END) as total_sold,
                SUM(CASE WHEN action = 'buy' THEN amount ELSE 0 END) as total_bought_amount,
                SUM(CASE WHEN action = 'sell' THEN amount ELSE 0 END) as total_sold_amount
            FROM transactions
            GROUP BY symbol, name
        ''')

        conn.commit()
        conn.close()

        print(f"✓ Transactions database initialized: {self.transactions_db_path}")

    def init_alerts_db(self):
        """初始化提醒记录数据库"""
        conn = sqlite3.connect(self.alerts_db_path)
        cursor = conn.cursor()

        # 创建提醒记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                name TEXT,
                rule_id TEXT,
                rule_name TEXT,
                condition TEXT,
                alert_type TEXT,
                current_price REAL,
                trigger_level REAL,
                triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at TIMESTAMP
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_rule_id ON alerts(rule_id)')

        # 创建提醒统计视图
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS alert_stats AS
            SELECT
                symbol,
                COUNT(*) as total_alerts,
                SUM(CASE WHEN acknowledged = 0 THEN 1 ELSE 0 END) as unacknowledged,
                MAX(triggered_at) as last_alert_at
            FROM alerts
            GROUP BY symbol
        ''')

        conn.commit()
        conn.close()

        print(f"✓ Alerts database initialized: {self.alerts_db_path}")

    def init_all_databases(self):
        """初始化所有数据库"""
        print("Initializing Trading Assistant databases...")
        print()

        self.init_positions_db()
        self.init_transactions_db()
        self.init_alerts_db()

        print()
        print("All databases initialized successfully!")

    # 持仓操作
    def add_position(self, symbol: str, name: str, quantity: int, cost_price: float, sector: str = "", exchange: str = ""):
        """添加持仓"""
        conn = sqlite3.connect(self.positions_db_path)
        cursor = conn.cursor()

        total_cost = quantity * cost_price

        try:
            cursor.execute('''
                INSERT INTO positions (symbol, name, sector, exchange, quantity, cost_price, total_cost, current_price, market_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, name, sector, exchange, quantity, cost_price, total_cost, cost_price, total_cost))
            conn.commit()
            print(f"✓ Added position: {symbol} {name} - {quantity} shares @ {cost_price}")
        except sqlite3.IntegrityError:
            print(f"✗ Position already exists: {symbol}. Use update_position instead.")
        finally:
            conn.close()

    def update_position_price(self, symbol: str, current_price: float):
        """更新持仓当前价格"""
        conn = sqlite3.connect(self.positions_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE positions
            SET current_price = ?,
                market_value = quantity * ?,
                pnl = (quantity * ?) - total_cost,
                pnl_pct = ((quantity * ?) - total_cost) / total_cost * 100,
                updated_at = CURRENT_TIMESTAMP
            WHERE symbol = ?
        ''', (current_price, current_price, current_price, current_price, symbol))

        conn.commit()
        conn.close()

    def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        conn = sqlite3.connect(self.positions_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM positions WHERE quantity > 0')
        rows = cursor.fetchall()

        positions = [dict(row) for row in rows]
        conn.close()

        return positions

    def get_position_summary(self) -> Dict:
        """获取持仓汇总"""
        conn = sqlite3.connect(self.positions_db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM position_summary')
        row = cursor.fetchone()

        if row:
            summary = {
                "total_positions": row[0],
                "total_value": row[1] or 0,
                "total_cost": row[2] or 0,
                "total_pnl": row[3] or 0,
                "total_pnl_pct": row[4] or 0
            }
        else:
            summary = {
                "total_positions": 0,
                "total_value": 0,
                "total_cost": 0,
                "total_pnl": 0,
                "total_pnl_pct": 0
            }

        conn.close()
        return summary

    # 交易记录操作
    def add_transaction(self, symbol: str, name: str, action: str, quantity: int, price: float, notes: str = "", fee: float = 0):
        """添加交易记录"""
        conn = sqlite3.connect(self.transactions_db_path)
        cursor = conn.cursor()

        amount = quantity * price

        cursor.execute('''
            INSERT INTO transactions (symbol, name, action, quantity, price, amount, notes, fee)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, name, action, quantity, price, amount, notes, fee))

        conn.commit()
        conn.close()

        print(f"✓ Added transaction: {action} {symbol} {name} - {quantity} shares @ {price}")

        # 更新持仓
        self._update_position_from_transaction(symbol, action, quantity, price)

    def _update_position_from_transaction(self, symbol: str, action: str, quantity: int, price: float):
        """根据交易记录更新持仓"""
        conn = sqlite3.connect(self.positions_db_path)
        cursor = conn.cursor()

        # 检查持仓是否存在
        cursor.execute('SELECT quantity, total_cost FROM positions WHERE symbol = ?', (symbol,))
        row = cursor.fetchone()

        if row:
            # 更新现有持仓
            current_quantity = row[0]
            current_total_cost = row[1]

            if action == "buy":
                new_quantity = current_quantity + quantity
                new_total_cost = current_total_cost + (quantity * price)
            else:  # sell
                new_quantity = current_quantity - quantity
                # 卖出时不改变成本价，只减少数量和总成本（按比例）
                if current_quantity > 0:
                    cost_per_share = current_total_cost / current_quantity
                    new_total_cost = current_total_cost - (quantity * cost_per_share)
                else:
                    new_total_cost = 0

            # 更新或删除持仓
            if new_quantity > 0:
                new_cost_price = new_total_cost / new_quantity
                cursor.execute('''
                    UPDATE positions
                    SET quantity = ?, total_cost = ?, cost_price = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE symbol = ?
                ''', (new_quantity, new_total_cost, new_cost_price, symbol))
            else:
                cursor.execute('DELETE FROM positions WHERE symbol = ?', (symbol,))
        else:
            # 新建持仓（仅限买入）
            if action == "buy":
                total_cost = quantity * price
                cursor.execute('''
                    INSERT INTO positions (symbol, name, quantity, cost_price, total_cost, current_price, market_value)
                    VALUES (?, '', ?, ?, ?, ?, ?)
                ''', (symbol, quantity, price, total_cost, price, total_cost))

        conn.commit()
        conn.close()

    # 提醒操作
    def add_alert(self, symbol: str, name: str, rule_id: str, rule_name: str, condition: str,
                   alert_type: str, current_price: float, trigger_level: float):
        """添加提醒记录"""
        conn = sqlite3.connect(self.alerts_db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts (symbol, name, rule_id, rule_name, condition, alert_type, current_price, trigger_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, name, rule_id, rule_name, condition, alert_type, current_price, trigger_level))

        conn.commit()
        conn.close()

    def get_recent_alerts(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """获取最近的提醒"""
        conn = sqlite3.connect(self.alerts_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if symbol:
            cursor.execute('''
                SELECT * FROM alerts WHERE symbol = ?
                ORDER BY triggered_at DESC
                LIMIT ?
            ''', (symbol, limit))
        else:
            cursor.execute('''
                SELECT * FROM alerts
                ORDER BY triggered_at DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        alerts = [dict(row) for row in rows]

        conn.close()
        return alerts


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Trading Assistant Database Manager")
    parser.add_argument("--init", action="store_true", help="Initialize all databases")
    parser.add_argument("--add-position", nargs=4, metavar=("SYMBOL", "NAME", "QUANTITY", "COST_PRICE"),
                        help="Add a position (e.g., --add-position 000001 平安银行 1000 11.50)")
    parser.add_argument("--add-transaction", nargs=5, metavar=("SYMBOL", "NAME", "ACTION", "QUANTITY", "PRICE"),
                        help="Add a transaction (e.g., --add-transaction 000001 平安银行 buy 500 11.50)")
    parser.add_argument("--list-positions", action="store_true", help="List all positions")
    parser.add_argument("--list-alerts", action="store_true", help="List recent alerts")

    args = parser.parse_args()

    db = DatabaseManager()

    if args.init:
        db.init_all_databases()

    elif args.add_position:
        symbol, name, quantity, cost_price = args.add_position
        db.init_positions_db()  # 确保数据库已初始化
        db.add_position(symbol, name, int(quantity), float(cost_price))

    elif args.add_transaction:
        symbol, name, action, quantity, price = args.add_transaction
        db.init_transactions_db()  # 确保数据库已初始化
        db.init_positions_db()
        db.add_transaction(symbol, name, action, int(quantity), float(price))

    elif args.list_positions:
        db.init_positions_db()
        positions = db.get_positions()
        summary = db.get_position_summary()

        print("\n=== 持仓汇总 ===")
        print(f"总持仓: {summary['total_positions']}只")
        print(f"总成本: {summary['total_cost']:.2f}元")
        print(f"当前市值: {summary['total_value']:.2f}元")
        print(f"总盈亏: {summary['total_pnl']:.2f}元 ({summary['total_pnl_pct']:.2f}%)")
        print()

        if positions:
            print("=== 持仓明细 ===")
            for pos in positions:
                print(f"{pos['symbol']} {pos['name']}")
                print(f"  数量: {pos['quantity']} | 成本: {pos['cost_price']:.2f} | 当前: {pos['current_price']:.2f}")
                print(f"  盈亏: {pos['pnl']:.2f}元 ({pos['pnl_pct']:.2f}%)")
                print()

    elif args.list_alerts:
        db.init_alerts_db()
        alerts = db.get_recent_alerts()

        if alerts:
            print("\n=== 最近提醒 ===")
            for alert in alerts:
                print(f"{alert['triggered_at']} - {alert['symbol']} {alert['name']}")
                print(f"  {alert['rule_name']}: {alert['condition']}")
                print(f"  当前价: {alert['current_price']} | 触发位: {alert['trigger_level']}")
                print(f"  已确认: {'是' if alert['acknowledged'] else '否'}")
                print()
        else:
            print("\n暂无提醒记录")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
