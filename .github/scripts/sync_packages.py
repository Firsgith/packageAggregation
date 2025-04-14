import os
import shutil
import subprocess
from pathlib import Path

# 日志输出函数
def log(message):
    print(f"::notice::{message}")

def error(message):
    print(f"::error::{message}")
    exit(1)

# 获取白名单文件列表
def get_whitelist():
    whitelist_file = Path(".github/.syncconfig")
    if not whitelist_file.exists():
        error("Whitelist file .github/.syncconfig not found!")
    with open(whitelist_file, "r") as f:
        return [line.strip() for line in f if line.strip()]

# 清理仓库中的文件（保留白名单）
def clean_repository(whitelist):
    log("Cleaning repository...")
    for item in Path(".").iterdir():
        if item.name not in whitelist and item.name != ".github":
            if item.is_dir():
                shutil.rmtree(item)
                log(f"Removed directory: {item}")
            else:
                item.unlink()
                log(f"Removed file: {item}")

# 解析 packages 文件
def parse_packages_file():
    packages_file = Path("packages")
    if not packages_file.exists():
        error("Packages file not found!")
    with open(packages_file, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    repos = []
    for line in lines:
        if ";" not in line:
            error(f"Invalid line in packages file: {line}")
        repo_info, _ = line.split(";")
        if "," in repo_info:
            repo_url, folder_path = repo_info.split(",")
        else:
            repo_url, folder_path = repo_info, None
        repos.append((repo_url.strip(), folder_path.strip() if folder_path else None))
    return repos

# 克隆仓库并同步内容
def sync_repositories(repos):
    log("Syncing repositories...")
    for repo_url, folder_path in repos:
        log(f"Processing repository: {repo_url}, folder: {folder_path}")
        temp_dir = Path("temp_clone")
        try:
            # 克隆仓库到临时目录
            subprocess.run(["git", "clone", "--depth", "1", repo_url, str(temp_dir)], check=True)
            log(f"Cloned repository: {repo_url}")
            
            # 如果指定了文件夹，则只保留该文件夹
            if folder_path:
                source_dir = temp_dir / folder_path
                if not source_dir.exists():
                    error(f"Folder {folder_path} not found in repository: {repo_url}")
                target_dir = Path(folder_path)
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.move(source_dir, target_dir)
                log(f"Copied folder: {folder_path}")
            else:
                # 否则复制整个仓库内容
                for item in temp_dir.iterdir():
                    if item.is_dir():
                        shutil.copytree(item, item.name, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, item.name)
                log(f"Copied entire repository: {repo_url}")
        finally:
            # 删除临时克隆目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                log(f"Removed temporary clone directory: {temp_dir}")

# 提交更改到 main 分支
def commit_changes():
    log("Committing changes...")
    subprocess.run(["git", "config", "user.name", "GitHub Actions"], check=True)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    if subprocess.run(["git", "diff", "--staged", "--quiet"]).returncode != 0:
        subprocess.run(["git", "commit", "-m", "Sync packages"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        log("Changes pushed to main branch.")
    else:
        log("No changes to commit.")

# 主函数
def main():
    log("Starting package synchronization...")
    
    # 获取白名单
    whitelist = get_whitelist()
    log(f"Whitelist: {whitelist}")
    
    # 清理仓库
    clean_repository(whitelist)
    
    # 解析 packages 文件
    repos = parse_packages_file()
    log(f"Parsed repositories: {repos}")
    
    # 同步仓库内容
    sync_repositories(repos)
    
    # 提交更改
    commit_changes()
    
    log("Package synchronization completed successfully.")

if __name__ == "__main__":
    main()
