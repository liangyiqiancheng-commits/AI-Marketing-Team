#!/usr/bin/env python3
"""
文件读写工具模块
==================
提供统一的文件读写、JSON 处理、目录管理等功能，
供 agnes_client.py 和 image_downloader.py 共用。

主要功能:
- read_text / write_text: 文本文件读写
- read_json / write_json: JSON 文件读写
- append_text: 追加写入文本
- ensure_dir: 确保目录存在
- list_files: 列出目录文件
- get_timestamp: 获取时间戳字符串
"""

import os
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import Optional, Union, List, Any, Dict


# ============================================================
# 项目路径
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"


# ============================================================
# 时间戳工具
# ============================================================

def get_timestamp(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime(fmt)


def get_date_str() -> str:
    """获取日期字符串 YYYYMMDD"""
    return datetime.now().strftime("%Y%m%d")


def get_week_str() -> str:
    """获取年份周次 YYYYWW"""
    now = datetime.now()
    return f"{now.isocalendar()[0]}{now.isocalendar()[1]:02d}"


# ============================================================
# 目录管理
# ============================================================

def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    确保目录存在，如不存在则创建。
    
    Args:
        directory: 目录路径（字符串或 Path 对象）
        
    Returns:
        创建后的 Path 对象
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_output_subdir(subdir: str) -> Path:
    """获取 output 下的子目录，确保其存在"""
    path = OUTPUT_DIR / subdir
    return ensure_dir(path)


def get_input_filepath(category: str, filename: str) -> Path:
    """获取 input 下某分类的文件路径"""
    return INPUT_DIR / category / filename


# ============================================================
# 文本文件读写
# ============================================================

def read_text(filepath: Union[str, Path], encoding: str = "utf-8") -> str:
    """
    读取文本文件。
    
    Args:
        filepath: 文件路径
        encoding: 编码格式，默认 utf-8
        
    Returns:
        文件内容字符串
        
    Raises:
        FileNotFoundError: 文件不存在时
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return path.read_text(encoding=encoding)


def write_text(
    filepath: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> Path:
    """
    写入文本文件。
    
    Args:
        filepath: 文件路径
        content: 要写入的内容
        encoding: 编码格式
        create_dirs: 是否自动创建父目录
        
    Returns:
        写入后的 Path 对象
    """
    path = Path(filepath)
    if create_dirs:
        ensure_dir(path.parent)
    path.write_text(content, encoding=encoding)
    return path


def append_text(
    filepath: Union[str, Path],
    content: str,
    encoding: str = "utf-8",
    separator: str = "\n\n",
) -> Path:
    """
    追加写入文本文件。
    
    Args:
        filepath: 文件路径
        content: 要追加的内容
        encoding: 编码格式
        separator: 与现有内容的分隔符
        
    Returns:
        写入后的 Path 对象
    """
    path = Path(filepath)
    ensure_dir(path.parent)
    
    existing_content = ""
    if path.exists():
        existing_content = path.read_text(encoding=encoding)
    
    if existing_content and not existing_content.endswith(separator):
        existing_content += separator
    
    path.write_text(existing_content + content, encoding=encoding)
    return path


# ============================================================
# JSON 文件读写
# ============================================================

def read_json(
    filepath: Union[str, Path],
    encoding: str = "utf-8",
    default: Any = None,
) -> Any:
    """
    读取 JSON 文件。
    
    Args:
        filepath: 文件路径
        encoding: 编码格式
        default: 文件不存在或解析失败时的默认返回值
        
    Returns:
        解析后的 Python 对象
    """
    path = Path(filepath)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding=encoding))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"[WARNING] JSON 解析失败 {path}: {e}")
        return default


def write_json(
    filepath: Union[str, Path],
    data: Any,
    encoding: str = "utf-8",
    indent: int = 2,
    ensure_ascii: bool = False,
    create_dirs: bool = True,
) -> Path:
    """
    写入 JSON 文件（带美观格式化）。
    
    Args:
        filepath: 文件路径
        data: 要写入的数据（需 JSON 可序列化）
        encoding: 编码格式
        indent: 缩进空格数
        ensure_ascii: 是否转义非 ASCII 字符
        create_dirs: 是否自动创建父目录
        
    Returns:
        写入后的 Path 对象
    """
    path = Path(filepath)
    if create_dirs:
        ensure_dir(path.parent)
    
    content = json.dumps(data, indent=indent, ensure_ascii=ensure_ascii)
    path.write_text(content, encoding=encoding)
    return path


def append_json_record(
    filepath: Union[str, Path],
    record: Dict[str, Any],
    key: str = "records",
) -> Path:
    """
    向 JSON 文件追加一条记录（数组形式）。
    
    如果文件不存在则创建新数组；
    如果文件存在且为数组则追加；
    其他情况则覆盖。
    
    Args:
        filepath: 文件路径
        record: 要追加的记录字典
        key: 数组的键名
        
    Returns:
        写入后的 Path 对象
    """
    path = Path(filepath)
    ensure_dir(path.parent)
    
    # 读取现有数据
    existing_data = read_json(path, default={key: []})
    
    # 确保 records 是列表
    if isinstance(existing_data, dict) and key in existing_data:
        records_list = existing_data[key]
        if not isinstance(records_list, records_list):
            records_list = []
    else:
        existing_data = {key: []}
        records_list = existing_data[key]
    
    # 追加记录（带时间戳）
    record["_created_at"] = get_timestamp("%Y-%m-%dT%H:%M:%S")
    records_list.append(record)
    
    return write_json(path, existing_data)


# ============================================================
# 文件列表与查找
# ============================================================

def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False,
) -> List[Path]:
    """
    列出目录下的文件。
    
    Args:
        directory: 目录路径
        pattern: 通配符模式（如 "*.md", "*.png"）
        recursive: 是否递归子目录
        
    Returns:
        匹配的文件 Path 列表（按修改时间倒序）
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    
    if recursive:
        matches = list(dir_path.rglob(pattern))
    else:
        matches = list(dir_path.glob(pattern))
    
    # 只返回文件，排除目录
    files = [f for f in matches if f.is_file()]
    
    # 按修改时间倒序（最新的在前）
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files


def find_latest_file(
    directory: Union[str, Path],
    pattern: str = "*",
) -> Optional[Path]:
    """
    在目录中找到最新修改的匹配文件。
    
    Args:
        directory: 目录路径
        pattern: 通配符模式
        
    Returns:
        最新的文件 Path，未找到则返回 None
    """
    files = list_files(directory, pattern)
    return files[0] if files else None


# ============================================================
# Markdown 格式化辅助
# ============================================================

def markdown_header(title: str, level: int = 1) -> str:
    """生成 Markdown 标题"""
    return "#" * level + f" {title}"


def markdown_table(headers: List[str], rows: List[List[Any]]) -> str:
    """
    生成 Markdown 表格。
    
    Args:
        headers: 表头列表
        rows: 行数据列表（每行为一个列表）
        
    Returns:
        Markdown 表格字符串
    """
    # 表头
    line = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    lines = [line, separator]
    
    # 数据行
    for row in rows:
        line = "| " + " | ".join(str(cell) for cell in row) + " |"
        lines.append(line)
    
    return "\n".join(lines)


def markdown_code_block(content: str, language: str = "") -> str:
    """生成 Markdown 代码块"""
    return f"```{language}\n{content}\n```"


def markdown_link(text: str, url: str) -> str:
    """生成 Markdown 链接"""
    return f"[{text}]({url})"


def markdown_image(alt: str, url: str) -> str:
    """生成 Markdown 图片"""
    return f"![{alt}]({url})"


# ============================================================
# 日志工具
# ============================================================

class SimpleLogger:
    """简单的日志工具，同时输出到控制台和文件"""
    
    def __init__(self, log_file: Optional[Path] = None):
        self.log_file = log_file
        if log_file:
            ensure_dir(log_file.parent)
    
    def _format(self, level: str, message: str) -> str:
        ts = get_timestamp("%Y-%m-%d %H:%M:%S")
        return f"[{ts}] [{level}] {message}"
    
    def info(self, message: str):
        msg = self._format("INFO", message)
        print(msg)
        self._write(msg)
    
    def error(self, message: str):
        msg = self._format("ERROR", message)
        print(msg)
        self._write(msg)
    
    def success(self, message: str):
        msg = self._format("SUCCESS", message)
        print(msg)
        self._write(msg)
    
    def _write(self, message: str):
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(message + "\n")


# 全局日志实例
logger = SimpleLogger()


# ============================================================
# 测试入口
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("  File Utils 测试")
    print("=" * 50)
    
    # 测试路径
    print(f"\n📂 项目根目录: {PROJECT_ROOT}")
    print(f"📂 Input 目录: {INPUT_DIR}")
    print(f"📂 Output 目录: {OUTPUT_DIR}")
    
    # 测试目录创建
    test_dir = OUTPUT_DIR / "_test"
    ensure_dir(test_dir)
    print(f"\n✅ 创建测试目录: {test_dir}")
    
    # 测试文本读写
    test_file = test_dir / "test.txt"
    write_text(test_file, "Hello, AI Marketing Team!")
    content = read_text(test_file)
    print(f"✅ 文本读写测试: {content}")
    
    # 测试 JSON 读写
    json_file = test_dir / "test.json"
    test_data = {"name": "test", "items": [1, 2, 3]}
    write_json(json_file, test_data)
    loaded = read_json(json_file)
    print(f"✅ JSON 读写测试: {loaded}")
    
    # 测试追加
    append_text(test_file, "\nAppended line!")
    final = read_text(test_file)
    print(f"✅ 追加写入测试: {repr(final)}")
    
    # 清理测试文件
    import shutil
    shutil.rmtree(test_dir)
    print(f"\n🧹 已清理测试目录")
    
    print("\n🎉 所有测试通过！")
