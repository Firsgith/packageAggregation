import os
import subprocess
import shutil

def clean_existing_files(packages_file):
    """
    清理主仓库中已存在的、由 packages 文件定义的文件或目录。
    """
    print("Cleaning existing files and directories...")
    if not os.path.exists(packages_file):
        print(f"Error: {packages_file} not found.")
        return

    with open(packages_file, "r") as file:
        for line in file:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith("#"):
                if line.strip().startswith("#") and len(line.strip()) > 1:  # 忽略纯说明性注释
                    print(f"Skipping comment or empty line: {line}")
                continue

            # 分割仓库地址和目标文件夹路径
            if ";" not in line:
                print(f"Invalid line format: {line}")
                continue
            line = line.rstrip(";")  # 去掉末尾的分号
            parts = line.split(",", 1)
            repo_url = parts[0].strip()
            folder_path = parts[1].strip() if len(parts) > 1 else None

            if not folder_path:
                print(f"Error: Missing target path for repository in line: {line}")
                continue

            # 确定需要删除的路径
            target_path = os.path.join(".", folder_path)
            
            # 跳过当前工作目录（"."）
            if os.path.abspath(target_path) == os.path.abspath("."):
                print(f"Skipping removal of current working directory: {target_path}")
                continue

            if os.path.exists(target_path):
                print(f"Removing existing path: {target_path}")
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)

def sync_repositories(packages_file):
    """
    同步 packages 文件中定义的仓库内容到主仓库。
    """
    print("Syncing repositories...")
    if not os.path.exists(packages_file):
        print(f"Error: {packages_file} not found.")
        return

    with open(packages_file, "r") as file:
        for line in file:
            line = line.strip()
            # 跳过空行和注释行
            if not line or line.startswith("#"):
                if line.strip().startswith("#") and len(line.strip()) > 1:  # 忽略纯说明性注释
                    print(f"Skipping comment or empty line: {line}")
                continue

            # 分割仓库地址和目标文件夹路径
            if ";" not in line:
                print(f"Invalid line format: {line}")
                continue
            line = line.rstrip(";")  # 去掉末尾的分号
            parts = line.split(",", 1)
            repo_url = parts[0].strip()
            folder_path = parts[1].strip() if len(parts) > 1 else None

            if not folder_path:
                print(f"Error: Missing target path for repository in line: {line}")
                continue

            # 提取仓库名称作为临时目录名
            repo_name = os.path.basename(repo_url).replace(".git", "")

            # 克隆仓库到临时目录
            temp_dir = f"/tmp/{repo_name}"
            print(f"Cloning {repo_url}...")
            try:
                subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone {repo_url}: {e}")
                continue

            # 删除 .git 目录
            git_dir = os.path.join(temp_dir, ".git")
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir)

            # 确定需要复制的文件夹路径
            source_path = os.path.join(temp_dir, folder_path)
            if not os.path.exists(source_path):
                print(f"Source path {source_path} does not exist, skipping...")
                shutil.rmtree(temp_dir)
                continue

            # 确定目标路径
            target_dir = "."  # 主仓库的根目录
            target_path = os.path.join(target_dir, os.path.basename(source_path))

            # 复制整个文件夹到目标路径
            print(f"Copying folder {source_path} to {target_path}...")
            if os.path.exists(target_path):
                shutil.rmtree(target_path)  # 如果目标路径已存在，先删除
            shutil.copytree(source_path, target_path)

            # 清理临时目录
            shutil.rmtree(temp_dir)
            print(f"Synced {repo_name} successfully.")

if __name__ == "__main__":
    # 主仓库根目录下的 packages 文件路径
    packages_file = "packages"

    # 清理已存在的内容
    clean_existing_files(packages_file)

    # 同步新的内容
    sync_repositories(packages_file)
