#!/usr/bin/env python3
"""
批量生成尤溪品牌营销图片
========================
使用 Pollinations.ai 免费接口生成 6 张营销图片，保存到 output/images/
"""

import os
import sys
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime

# 路径配置
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Pollinations.ai 配置
POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"

# ============================================================
# 图片生成配置
# ============================================================

IMAGES = [
    {
        "id": 1,
        "name": "xiaohongshu_cover_01",
        "usage": "小红书封面",
        "style": "xiaohongshu-cover",
        "width": 1024,
        "height": 1024,
        "prompt": (
            "A premium glass skincare essence bottle with soft pink liquid, "
            "placed on a cream white marble surface, surrounded by scattered pink macarons "
            "and fresh cherry blossoms, soft natural window light, shallow depth of field, "
            "warm pink and cream color palette, minimalist elegant composition, "
            "8k resolution, commercial product photography"
        ),
    },
    {
        "id": 2,
        "name": "douyin_cover_02",
        "usage": "抖音封面",
        "style": "douyin-cover",
        "width": 1024,
        "height": 1792,
        "prompt": (
            "A luxurious facial cleanser foam bottle with fluffy white foam on pump, "
            "set against a gradient pink to cream background, dramatic soft lighting, "
            "visually striking product hero shot, high contrast clean composition, "
            "rose gold accents, premium skincare aesthetic, 8k resolution"
        ),
    },
    {
        "id": 3,
        "name": "lifestyle_scene_03",
        "usage": "生活场景配图",
        "style": "product-lifestyle",
        "width": 1365,
        "height": 1024,
        "prompt": (
            "A young Asian woman gently applying pink essence serum on her cheek in a bright clean bathroom, "
            "soft morning natural light, cream white tiles background, pink skincare bottles on marble vanity, "
            "warm and cozy atmosphere, authentic lifestyle moment, shallow depth of field, "
            "8k resolution, commercial aesthetic"
        ),
    },
    {
        "id": 4,
        "name": "illustration_3d_04",
        "usage": "3D插画品牌形象",
        "style": "illustration-3d",
        "width": 1024,
        "height": 1024,
        "prompt": (
            "Cute 3D render illustration of a small pink skincare bottle character with a happy face, "
            "sitting on a cloud of soft pink foam, pastel pink and cream white color palette, "
            "clay material texture, soft rounded shapes, isometric view, adorable kawaii style, "
            "studio lighting, 8k resolution"
        ),
    },
    {
        "id": 5,
        "name": "product_hero_05",
        "usage": "产品主角横幅",
        "style": "product-hero",
        "width": 1792,
        "height": 1024,
        "prompt": (
            "Two premium skincare products, a pink glass essence bottle and a foam cleanser, "
            "standing side by side on a reflective white surface, studio soft lighting, "
            "clean gradient pink to white background, luxury feel, sharp focus, "
            "professional product photography, rose gold accents, 8k resolution"
        ),
    },
    {
        "id": 6,
        "name": "social_proof_06",
        "usage": "社交证言配图",
        "style": "social-proof",
        "width": 1024,
        "height": 1024,
        "prompt": (
            "A cozy skincare vanity scene with pink skincare bottles and soft towels, "
            "warm golden hour light through window, pink macaron treats nearby, cream white aesthetic, "
            "genuine warm atmosphere, emotional connection, soft pink and cream tones, "
            "shallow depth of field, 8k resolution, lifestyle photography"
        ),
    },
]

# ============================================================
# 核心函数
# ============================================================

def download_image(url, save_path, timeout=120):
    """下载图片到本地"""
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = resp.read()
        with open(save_path, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        return 0


def generate_with_pollinations(img_config):
    """使用 Pollinations.ai 生成图片"""
    prompt = img_config["prompt"]
    width = img_config["width"]
    height = img_config["height"]
    
    encoded_prompt = urllib.request.quote(prompt)
    url = f"{POLLINATIONS_BASE}/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={img_config['id']*42+7}"
    
    return url


def generate_with_agnes(img_config, api_key):
    """使用 Agnes AI API 生成图片（备选方案）"""
    import requests
    
    api_url = "https://apihub.agnes-ai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "agnes-image-2.1-flash",
        "prompt": img_config["prompt"],
        "size": f"{img_config['width']}x{img_config['height']}",
        "n": 1,
    }
    
    resp = requests.post(api_url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    
    if "data" in data and len(data["data"]) > 0:
        return data["data"][0].get("url")
    return None


def main():
    print("=" * 60)
    print("  尤溪品牌营销图片批量生成")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  输出目录: {OUTPUT_DIR}")
    print("=" * 60)
    
    # 读取 Agnes API Key 作为备选
    env_path = PROJECT_ROOT / ".env"
    agnes_key = None
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("AGNES_API_KEY="):
                agnes_key = line.split("=", 1)[1].strip().strip('"').strip("'")
    
    use_provider = "pollinations"
    if agnes_key:
        print(f"  Pollinations.ai (首选) + Agnes AI (备选)")
    else:
        print(f"  Pollinations.ai (唯一)")
    print()
    
    results = []
    success_count = 0
    
    for img in IMAGES:
        idx = img["id"]
        name = img["name"]
        usage = img["usage"]
        print(f"[{idx}/6] 生成: {usage} ({img['width']}x{img['height']})")
        print(f"  Prompt: {img['prompt'][:80]}...")
        
        ts = datetime.now().strftime("%Y%m%d")
        ext = ".png"
        filename = f"{name}_{ts}{ext}"
        save_path = OUTPUT_DIR / filename
        
        image_url = None
        
        # 策略 1: Pollinations.ai
        try:
            poll_url = generate_with_pollinations(img)
            print(f"  [Pollinations] 下载中...")
            size = download_image(poll_url, save_path, timeout=120)
            if size > 5000:
                image_url = poll_url
                use_provider = "pollinations"
                print(f"  [SUCCESS] 已保存: {save_path.name} ({size/1024:.1f} KB)")
            else:
                print(f"  [WARN] 文件太小 ({size} bytes), 可能失败")
        except Exception as e:
            print(f"  [Pollinations FAILED] {e}")
        
        # 策略 2: Agnes AI (备选)
        if not image_url and agnes_key:
            try:
                print(f"  [Agnes] 尝试备用接口...")
                agnes_url = generate_with_agnes(img, agnes_key)
                if agnes_url:
                    size = download_image(agnes_url, save_path, timeout=120)
                    if size > 5000:
                        image_url = agnes_url
                        use_provider = "agnes"
                        print(f"  [SUCCESS - Agnes] 已保存: {save_path.name} ({size/1024:.1f} KB)")
                    else:
                        print(f"  [WARN - Agnes] 文件太小")
                else:
                    print(f"  [Agnes] 返回无URL")
            except Exception as e:
                print(f"  [Agnes FAILED] {e}")
        
        if image_url and save_path.exists():
            success_count += 1
            results.append({
                "filename": save_path.name,
                "filepath": str(save_path),
                "usage": usage,
                "style": img["style"],
                "size": f"{img['width']}x{img['height']}",
                "prompt": img["prompt"],
                "provider": use_provider,
                "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "success",
            })
        else:
            results.append({
                "filename": filename,
                "usage": usage,
                "style": img["style"],
                "size": f"{img['width']}x{img['height']}",
                "prompt": img["prompt"],
                "status": "failed",
            })
            print(f"  [FAILED] {usage} 生成失败")
        
        print()
    
    # 保存元数据
    metadata = {
        "version": "1.0",
        "brand": "尤溪",
        "total_count": len(results),
        "success_count": success_count,
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "records": results,
    }
    meta_path = OUTPUT_DIR / "_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print("=" * 60)
    print(f"  生成完成: {success_count}/{len(IMAGES)} 张成功")
    print(f"  元数据: {meta_path}")
    print("=" * 60)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
