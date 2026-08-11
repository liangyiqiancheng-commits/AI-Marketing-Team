#!/usr/bin/env python3
"""
图片下载与保存模块
==================
负责从 URL 或 Base64 数据下载图片并保存到指定目录。
支持批量下载、自动命名、元数据记录。

主要功能:
- save_images(): 批量保存图片列表
- download_from_url(): 从 URL 下载单张图片
- save_from_base64(): 从 Base64 数据保存图片
"""

import os
import json
import base64
import hashlib
import urllib.request
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# 项目路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_IMAGES_DIR = PROJECT_ROOT / "output" / "images"
METADATA_FILE = OUTPUT_IMAGES_DIR / "_metadata.json"


def ensure_output_dir(output_dir=None) -> Path:
    """确保输出目录存在"""
    if output_dir is None:
        output_dir = OUTPUT_IMAGES_DIR
    dir_path = Path(output_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generate_filename(prefix: str, extension: str = ".png") -> str:
    """
    生成带时间戳的唯一文件名。
    
    格式: {prefix}_{YYYYMMDD_HHMMSS}_{短哈希}.{ext}
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_hash = hashlib.md5(ts.encode()).hexdigest()[:6]
    return f"{prefix}_{ts}_{short_hash}{extension}"


def download_from_url(
    url: str,
    save_path: Path,
    timeout: int = 30,
) -> Optional[Path]:
    """
    从 URL 下载图片并保存到指定路径。
    
    Args:
        url: 图片 URL
        save_path: 保存路径
        timeout: 下载超时时间（秒）
        
    Returns:
        保存后的路径，失败返回 None
    """
    try:
        urllib.request.urlretrieve(url, str(save_path))
        actual_size = save_path.stat().st_size
        if actual_size < 1000:
            print(f"[WARNING] 下载的文件可能不完整: {save_path} ({actual_size} bytes)")
        return save_path
    except Exception as e:
        print(f"[ERROR] 下载失败 [{url}]: {e}")
        return None


def save_from_base64(
    b64_data: str,
    save_path: Path,
) -> Optional[Path]:
    """
    将 Base64 编码的图片数据保存为文件。
    
    Args:
        b64_data: Base64 编码字符串
        save_path: 保存路径
        
    Returns:
        保存后的路径，失败返回 None
    """
    try:
        image_bytes = base64.b64decode(b64_data)
        with open(save_path, "wb") as f:
            f.write(image_bytes)
        return save_path
    except Exception as e:
        print(f"[ERROR] Base64 保存失败: {e}")
        return None


def save_images(
    images_list: List[Dict[str, Any]],
    prefix: str = "img",
    output_dir=None,
    extension: str = ".png",
) -> List[str]:
    """
    批量保存图片列表。
    
    每个图片字典应包含 url 或 b64_json 至少一个字段。
    
    Args:
        images_list: 图片信息列表，每项包含 {url, b64_json, revised_prompt}
        prefix: 文件名前缀
        output_dir: 输出目录，默认 output/images/
        extension: 文件扩展名
        
    Returns:
        保存成功的本地路径列表
    """
    target_dir = ensure_output_dir(output_dir)
    saved_paths = []
    
    for idx, img_info in enumerate(images_list):
        filename = generate_filename(f"{prefix}_{idx+1}", extension)
        save_path = target_dir / filename
        local_path = None
        
        # 优先使用 URL
        if img_info.get("url"):
            local_path = download_from_url(img_info["url"], save_path)
        
        # 如果 URL 失败或不存在，尝试 Base64
        if not local_path and img_info.get("b64_json"):
            local_path = save_from_base64(img_info["b64_json"], save_path)
        
        if local_path:
            saved_paths.append(str(local_path))
            print(f"[SAVE] 已保存: {local_path}")
            
            # 记录元数据
            record = {
                "filename": filename,
                "filepath": str(local_path),
                "url_source": img_info.get("url") is not None,
                "revised_prompt": img_info.get("revised_prompt", ""),
                "size_bytes": save_path.stat().st_size if save_path.exists() else 0,
                "saved_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            }
            append_metadata(record)
        else:
            saved_paths.append(None)
            print(f"[FAIL] 图片 {idx+1} 保存失败")
    
    return saved_paths


def append_metadata(record: Dict[str, Any]) -> None:
    """
    追加一条记录到元数据 JSON 文件。
    
    Args:
        record: 要追加的记录字典
    """
    ensure_output_dir()
    
    # 读取现有数据
    records = []
    if METADATA_FILE.exists():
        try:
            existing = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
            records = existing.get("records", [])
        except (json.JSONDecodeError, KeyError):
            records = []
    
    # 追加新记录
    records.append(record)
    
    # 写回文件
    metadata = {
        "version": "1.0",
        "total_count": len(records),
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "records": records,
    }
    
    METADATA_FILE.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_metadata() -> Dict[str, Any]:
    """获取完整的元数据"""
    if METADATA_FILE.exists():
        return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    return {"records": [], "total_count": 0}


def list_saved_images(output_dir=None) -> List[Path]:
    """列出已保存的所有图片文件"""
    target_dir = ensure_output_dir(output_dir)
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    files = []
    for f in sorted(target_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.suffix.lower() in extensions and f.name != "_metadata.json":
            files.append(f)
    return files


if __name__ == "__main__":
    print("=" * 50)
    print("  Image Downloader 测试")
    print("=" * 50)
    
    # 测试：列出已有图片
    images = list_saved_images()
    print(f"\n已保存的图片数量: {len(images)}")
    for img in images[:10]:
        size_kb = img.stat().st_size / 1024
        print(f"  - {img.name} ({size_kb:.1f} KB)")
    
    # 测试元数据
    meta = get_metadata()
    print(f"\n元数据记录总数: {meta.get('total_count', 0)}")
