#!/usr/bin/env python3
"""
Agnes AI API 客户端封装模块
================================
封装调用 Agnes AI 的接口，支持 OpenAI 兼容格式。
API 地址: https://apihub.agnes-ai.com/v1
API Key 从根目录 .env 文件读取（变量名: AGNES_API_KEY）

主要功能:
- generate_image(prompt): 图片生成
- chat_completion(messages): 文本对话补全
"""

import os
import json
import time
import base64
import requests
import io
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# ============================================================
# 配置常量
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API_BASE_URL = "https://apihub.agnes-ai.com/v1"
API_ENV_KEY = "AGNES_API_KEY"

DEFAULT_IMAGE_MODEL = "dall-e-3"
DEFAULT_CHAT_MODEL = "gpt-4o"
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_N = 1

MAX_RETRIES = 3
RETRY_DELAYS = [1, 3, 5]

# ============================================================
# 环境变量加载
# ============================================================

def load_env_file(env_path=None):
    """加载 .env 文件"""
    if env_path is None:
        env_path = PROJECT_ROOT / ".env"
    env_vars = {}
    if not env_path.exists():
        return env_vars
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                env_vars[key] = value
                if key not in os.environ:
                    os.environ[key] = value
    return env_vars

def get_api_key():
    """获取 API Key"""
    api_key = os.environ.get(API_ENV_KEY)
    if api_key:
        return api_key
    load_env_file()
    api_key = os.environ.get(API_ENV_KEY)
    if api_key:
        return api_key
    raise ValueError(
        f"API Key 未配置！\n"
        f"请在项目根目录的 .env 文件中添加:\n"
        f"  {API_ENV_KEY}=你的密钥\n"
        f"或设置系统环境变量: export {API_ENV_KEY}=你的密钥"
    )

def _get_headers():
    """构建请求头"""
    api_key = get_api_key()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

def _request_with_retry(method, endpoint, **kwargs):
    """带重试的 HTTP 请求"""
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    headers = kwargs.pop("headers", _get_headers())
    last_exception = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.request(method, url, headers=headers, timeout=60, **kwargs)
            if response.status_code == 200:
                return response
            if 400 <= response.status_code < 500:
                print(f"[ERROR] API 错误 [{response.status_code}]: {response.text}")
                response.raise_for_status()
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                print(f"[RETRY] {response.status_code}, {delay}s后重试 ({attempt+1}/{MAX_RETRIES})...")
                time.sleep(delay)
                continue
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                print(f"[RETRY] 异常: {e}, {delay}s后重试...")
                time.sleep(delay)
                continue
    raise last_exception

# ============================================================
# 图片生成接口（核心函数）
# ============================================================

def generate_image(
    prompt: str,
    model: Optional[str] = None,
    size: str = DEFAULT_IMAGE_SIZE,
    n: int = DEFAULT_IMAGE_N,
    style: Optional[str] = None,
    quality: str = "standard",
    save_to_output: bool = True,
    output_dir=None,
) -> Dict[str, Any]:
    """
    通过 Agnes AI API 生成图片。
    
    Args:
        prompt: 图片提示词（建议英文）
        model: 模型名称，默认 dall-e-3
        size: 尺寸，如 "1024x1024"
        n: 生成数量
        style: 风格 ("vivid"/"natural")
        quality: 质量 ("standard"/"hd")
        save_to_output: 是否保存到 output/images/
        
    Returns:
        {"success": bool, "images": [...], "error": str|None}
    """
    if model is None:
        model = DEFAULT_IMAGE_MODEL
    
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "n": n,
        "quality": quality,
    }
    if style:
        payload["style"] = style
    
    print(f"[IMAGE GEN] Model={model} Size={size}")
    print(f"[IMAGE GEN] Prompt: {prompt[:100]}...")
    
    try:
        response = _request_with_retry("POST", "images/generations", json=payload)
        data = response.json()
        
        images_result = []
        for img_data in data.get("data", []):
            images_result.append({
                "url": img_data.get("url"),
                "b64_json": img_data.get("b64_json"),
                "revised_prompt": img_data.get("revised_prompt", prompt),
                "local_path": None,
            })
        
        result = {
            "success": True,
            "images": images_result,
            "model": data.get("model", model),
            "prompt": prompt,
            "error": None,
        }
        
        # 自动保存到 output/images/
        if save_to_output and images_result:
            from scripts.image_downloader import save_images
            saved_paths = save_images(images_result, output_dir=output_dir)
            for i, p in enumerate(saved_paths):
                if i < len(result["images"]):
                    result["images"][i]["local_path"] = p
        
        print(f"[IMAGE GEN] 成功生成 {len(images_result)} 张图片")
        return result
        
    except ValueError as e:
        return {"success": False, "images": [], "model": model, "prompt": prompt, "error": str(e)}
    except Exception as e:
        return {"success": False, "images": [], "model": model, "prompt": prompt, "error": f"请求失败: {e}"}

# ============================================================
# 文本对话补全
# ============================================================

def chat_completion(messages, model=None, temperature=0.7, max_tokens=2000):
    """文本对话补全"""
    if model is None:
        model = DEFAULT_CHAT_MODEL
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        response = _request_with_retry("POST", "chat/completions", json=payload)
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        return {"success": True, "content": content, "model": data.get("model", model), "usage": data.get("usage", {}), "error": None}
    except Exception as e:
        return {"success": False, "content": "", "model": model, "usage": {}, "error": str(e)}

if __name__ == "__main__":
    # 设置UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("=" * 50)
    print("  Agnes AI Client 测试")
    print("=" * 50)
    try:
        key = get_api_key()
        print(f"\nAPI Key 已加载: {key[:8]}...{key[-4:]}")
    except ValueError as e:
        print(f"\n{e}")
        import sys; sys.exit(1)
    
    test_prompt = "A beautiful marketing product photo, clean background, professional lighting, 8k"
    result = generate_image(test_prompt)
    if result["success"]:
        print("\n测试成功!")
        for i, img in enumerate(result["images"]):
            print(f"  图片{i+1}: {img.get('local_path') or img.get('url')}")
    else:
        print(f"\n测试失败: {result['error']}")
