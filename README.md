# **GitHub Actions: Sync Packages and Clean Up Workflow Runs**

This repository contains a GitHub Actions workflow that automates the process of syncing packages from repositories and cleaning up old workflow runs. Below are the instructions for setting up and using this workflow.

---

## **Features**
1. **Sync Packages**:
   - Automatically run a Python script (`sync_packages.py`) to sync packages from repositories.
   - Commit and push changes back to the main branch.

2. **Clean Up Old Workflow Runs**:
   - Retain only the latest 3 workflow runs on the `main` branch.
   - Delete older workflow runs to reduce clutter and save storage space.

---

## **Prerequisites**

### **1. Required Permissions**
To ensure the workflow functions correctly, you need to configure the following permissions:

#### **Personal Access Token (PAT)**
- Create a PAT with the following scopes:
  - `repo`: Full control of private repositories.
  - `admin:org`: Full control of organization resources.

#### **Store the PAT in Repository Secrets**
1. Go to your repository's **Settings > Secrets and variables > Actions**.
2. Click **New repository secret**.
3. Set the name as `SYNC_TOKEN` and paste the value of your PAT.
4. Save the secret.

#### **Repository Settings**
1. Go to **Settings > Actions > General** in your repository.
2. Under **Workflow permissions**, select **Read and write permissions**.
   - This allows the workflow to push changes and delete workflow runs.
3. Enable **Allow GitHub Actions to create and approve pull requests**.
   - This ensures the workflow has sufficient permissions to perform actions like committing changes and deleting runs.

---

## **How It Works**
1. **Triggering the Workflow**:
   - The workflow can be triggered manually via the **workflow_dispatch** event or automatically when pushing to the `main` branch.

2. **Syncing Packages**:
   - The workflow checks out the repository, sets up Python 3.10, and runs the `sync_packages.py` script.
   - Any changes made by the script are committed and pushed back to the repository using the `SYNC_TOKEN`.

3. **Cleaning Up Workflow Runs**:
   - The workflow fetches all runs on the `main` branch and retains only the latest 3 runs.
   - Older runs are deleted to reduce clutter and save storage space.

---

## **Troubleshooting**

### **1. Permission Errors**
- If you encounter `403 Forbidden` errors during the cleanup step:
  - Verify that the `SYNC_TOKEN` has the correct scopes (`repo` and `admin:org`).
  - Ensure **Read and write permissions** is selected under **Workflow permissions** in your repository settings.
  - Ensure **Allow GitHub Actions to create and approve pull requests** is enabled.

### **2. Invalid Run IDs**
- If the cleanup step skips Run IDs:
  - Check the API response to ensure the correct IDs are being extracted.
  - Add debug logs to print the API response:
    ```bash
    echo "API Response: $RESPONSE"
    ```

---

## **Contributing**
If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.

---

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

By following these instructions, you should be able to set up and use this GitHub Actions workflow effectively. Let me know if you have any questions!

---
