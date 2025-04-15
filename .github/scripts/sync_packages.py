#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
from urllib.parse import urlparse

def clone_and_copy(repo_url, subdir, target_dir):
    """克隆仓库并复制指定子目录到目标位置"""
    try:
        print(f"🔄 开始处理: {repo_url} -> {target_dir}")
        
        # 验证目标路径
        if not target_dir:
            raise ValueError("目标目录不能为空")
            
        target_dir = os.path.abspath(target_dir)
        parent_dir = os.path.dirname(target_dir)
        
        print(f"📁 目标目录: {target_dir}")
        print(f"📂 父目录: {parent_dir}")
        
        # 创建父目录
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
            print(f"✅ 已创建父目录: {parent_dir}")

        # 临时克隆目录
        temp_dir = os.path.join(os.getcwd(), "temp_clone")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🧹 已清理临时目录: {temp_dir}")

        # 克隆仓库
        print(f"⏬ 正在克隆仓库: {repo_url}")
        subprocess.run(
            ["git", "clone", "--depth=1", repo_url, temp_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # 复制文件
        src_path = os.path.join(temp_dir, subdir.strip('/'))
        if not os.path.exists(src_path):
            raise FileNotFoundError(f"源目录不存在: {src_path}")

        print(f"📤 正在复制: {src_path} -> {target_dir}")
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
            
        shutil.copytree(src_path, target_dir)
        print(f"✅ 成功复制到: {target_dir}")

        # 清理临时目录
        shutil.rmtree(temp_dir)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git命令执行失败: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        print(f"❌ 处理出错: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False

def main():
    # 配置要同步的仓库列表
    repos = [
        {
            "url": "https://github.com/sirpdboy/luci-app-ddns-go.git",
            "subdir": "",
            "target": "luci-app-ddns-go"
        }
        # 可以添加更多仓库...
    ]

    for repo in repos:
        repo_url = repo["url"]
        subdir = repo.get("subdir", "")
        target_dir = repo["target"]
        
        # 获取仓库名称
        repo_name = os.path.splitext(os.path.basename(urlparse(repo_url).path))[0]
        
        # 尝试移除旧的git子模块配置
        try:
            subprocess.run(
                ["git", "config", "--remove-section", f"submodule.{repo_name}"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception:
            pass
            
        if not clone_and_copy(repo_url, subdir, target_dir):
            print(f"⛔ 处理仓库失败: {repo_url}")
            continue

if __name__ == "__main__":
    main()
