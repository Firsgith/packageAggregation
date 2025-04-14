import os
import shutil
import subprocess
from pathlib import Path
import logging
import stat

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# 定义常量
PACKAGES_FILE = "packages"
TEMP_DIR = "_temp_repos"
TARGET_DIR = "."


def parse_packages_file():
    """解析 packages 文件，返回仓库地址和路径的列表"""
    logging.info("Parsing packages file...")
    repositories = []
    with open(PACKAGES_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or not line:  # 跳过注释和空行
                continue
            if ";" not in line:
                logging.warning(f"Invalid line in packages file: {line}")
                continue
            repo_info = line.split(";")[0].strip()
            if "," in repo_info:
                repo_url, sub_path = repo_info.split(",")
                repositories.append((repo_url.strip(), sub_path.strip()))
            else:
                repositories.append((repo_info.strip(), None))
    logging.info(f"Parsed repositories: {repositories}")
    return repositories


def clone_and_extract(repo_url, sub_path=None):
    """克隆仓库并提取指定路径的内容"""
    logging.info(f"Cloning repository: {repo_url}")
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    temp_repo_path = Path(TEMP_DIR) / repo_name

    if temp_repo_path.exists():
        shutil.rmtree(temp_repo_path)  # 清理旧的临时目录

    # 克隆仓库
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(temp_repo_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logging.debug(result.stdout.decode())
        logging.debug(result.stderr.decode())
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone repository {repo_url}: {e.stderr.decode()}")
        return

    # 提取指定路径的内容
    source_path = temp_repo_path / sub_path if sub_path else temp_repo_path
    target_path = Path(TARGET_DIR) / repo_name if not sub_path else Path(TARGET_DIR) / sub_path.split("/")[-1]

    if source_path.exists():
        if target_path.exists():
            shutil.rmtree(target_path)  # 删除旧内容
        shutil.copytree(source_path, target_path)
        logging.info(f"Copied contents from {source_path} to {target_path}")
    else:
        logging.warning(f"Path {sub_path} does not exist in repository {repo_url}")


def remove_deleted_repos(existing_repos):
    """删除不再存在于 packages 文件中的仓库"""
    logging.info("Checking for deleted repositories...")
    current_dirs = {d.name for d in Path(TARGET_DIR).iterdir() if d.is_dir()}
    repos_in_packages = {repo.split("/")[-1].replace(".git", "") for repo, _ in existing_repos}

    # 排除 .git 目录
    protected_dirs = {".git"}

    for dir_name in current_dirs - repos_in_packages - protected_dirs:
        dir_path = Path(TARGET_DIR) / dir_name
        if dir_path.exists():
            logging.info(f"Removing directory {dir_path}")
            shutil.rmtree(dir_path)


def safe_rmtree(path):
    """安全地删除目录及其内容"""
    def on_error(func, path, exc_info):
        """处理删除失败的情况"""
        if not os.access(path, os.W_OK):
            logging.warning(f"Changing permissions for {path} to make it writable")
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            logging.warning(f"Failed to remove {path}: {exc_info}")

    if os.path.exists(path):
        logging.info(f"Attempting to remove directory: {path}")
        shutil.rmtree(path, onerror=on_error)
    else:
        logging.info(f"Directory does not exist: {path}")


def is_git_repo():
    """检查当前目录是否是一个 Git 仓库"""
    return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0


def commit_and_push_changes():
    """提交更改并推送到远程仓库"""
    if not is_git_repo():
        logging.error("Not a valid Git repository. Aborting commit and push.")
        return

    try:
        subprocess.run(["git", "config", "--global", "user.name", "GitHub Actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"], check=True)

        subprocess.run(["git", "add", "."], check=True)
        if subprocess.run(["git", "diff", "--quiet", "--staged"], capture_output=True).returncode != 0:
            subprocess.run(["git", "commit", "-m", "Automated sync of packages"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        logging.info("Changes committed and pushed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to commit or push changes: {e.stderr.decode()}")


def main():
    # 解析 packages 文件
    repositories = parse_packages_file()

    # 创建临时目录
    os.makedirs(TEMP_DIR, exist_ok=True)

    # 同步每个仓库
    for repo_url, sub_path in repositories:
        clone_and_extract(repo_url, sub_path)

    # 删除不再存在的仓库
    remove_deleted_repos(repositories)

    # 清理临时目录
    safe_rmtree(TEMP_DIR)

    # 提交更改并推送到远程仓库
    commit_and_push_changes()


if __name__ == "__main__":
    main()
