import os
import subprocess
import shutil

def clean_existing_files(packages_file):
    print("Cleaning existing files and directories...")
    with open(packages_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.rstrip(";")
            parts = line.split(",", 1)
            folder_path = parts[1].strip() if len(parts) > 1 else None
            target_path = os.path.join(".", folder_path) if folder_path else "."
            if os.path.exists(target_path):
                print(f"Removing existing path: {target_path}")
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)

def sync_repositories(packages_file):
    print("Syncing repositories...")
    with open(packages_file, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line = line.rstrip(";")
            parts = line.split(",", 1)
            repo_url = parts[0].strip()
            folder_path = parts[1].strip() if len(parts) > 1 else None
            repo_name = os.path.basename(repo_url).replace(".git", "")
            temp_dir = f"/tmp/{repo_name}"
            print(f"Cloning {repo_url}...")
            try:
                subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to clone {repo_url}: {e}")
                continue
            git_dir = os.path.join(temp_dir, ".git")
            if os.path.exists(git_dir):
                shutil.rmtree(git_dir)
            source_path = os.path.join(temp_dir, folder_path) if folder_path else temp_dir
            if not os.path.exists(source_path):
                print(f"Source path {source_path} does not exist, skipping...")
                shutil.rmtree(temp_dir)
                continue
            print(f"Copying files from {source_path} to root directory...")
            for item in os.listdir(source_path):
                src = os.path.join(source_path, item)
                dst = os.path.join(".", item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            shutil.rmtree(temp_dir)
            print(f"Synced {repo_name} successfully.")

if __name__ == "__main__":
    packages_file = "packages"
    clean_existing_files(packages_file)
    sync_repositories(packages_file)
