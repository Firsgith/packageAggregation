import os
import shutil
import subprocess
from pathlib import Path


def parse_packages_file(packages_path):
    """解析 packages 文件，返回仓库地址和路径信息"""
    repos = []
    with open(packages_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):  # 跳过注释和空行
                continue
            if "," in line:
                repo_url, folder_path = line.split(",", 1)
                repos.append((repo_url.strip().rstrip(";"), folder_path.strip()))
            else:
                repos.append((line.strip().rstrip(";"), None))
    return repos


def clone_and_sync_repo(repo_url, folder_path=None):
    """克隆仓库并保留指定文件夹的内容"""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    print(f"Cloning {repo_url}...")
    subprocess.run(["git", "clone", repo_url], check=True)

    if folder_path:
        # 如果指定了文件夹，只保留该文件夹及其内容
        target_dir = Path(repo_name) / folder_path
        if not target_dir.exists():
            raise FileNotFoundError(f"Folder {folder_path} not found in {repo_name}")
        print(f"Retaining folder {folder_path} from {repo_name}...")
        shutil.move(str(target_dir), folder_path)
        shutil.rmtree(repo_name)
    else:
        # 如果没有指定文件夹，保留整个仓库内容
        print(f"Retaining entire repository {repo_name}...")
        shutil.move(repo_name, repo_name)


def remove_old_repos(current_repos):
    """删除不再需要的旧仓库内容"""
    for item in Path(".").iterdir():
        if item.is_dir() and item.name not in current_repos:
            print(f"Removing old repository content: {item.name}")
            shutil.rmtree(item)


def main():
    packages_path = "packages"
    if not Path(packages_path).exists():
        raise FileNotFoundError(f"{packages_path} file not found!")

    # 解析 packages 文件
    repos = parse_packages_file(packages_path)
    current_repos = set()

    # 删除所有现有的 .git 文件夹
    for git_dir in Path(".").rglob(".git"):
        shutil.rmtree(git_dir)

    # 克隆并同步每个仓库
    for repo_url, folder_path in repos:
        try:
            clone_and_sync_repo(repo_url, folder_path)
            if folder_path:
                current_repos.add(folder_path)
            else:
                current_repos.add(repo_url.split("/")[-1].replace(".git", ""))
        except Exception as e:
            print(f"Error processing {repo_url}: {e}")

    # 删除不再需要的旧仓库内容
    remove_old_repos(current_repos)


if __name__ == "__main__":
    main()
