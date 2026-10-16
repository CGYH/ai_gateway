"""SQLite 连接管理：单文件数据库 gateway.db，单进程使用。

个人量级不值得上连接池/ORM，标准库 sqlite3 足够；
WAL 模式让读写互不阻塞，路径锚定在项目根目录而不是当前工作目录。
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "gateway.db"


def connect() -> sqlite3.Connection:
    """返回一个新连接（短连接模式，用完即关）。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn
