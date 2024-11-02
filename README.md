# Unraid Docker Templates Creator

## Overview
The **Unraid Docker Templates Creator** is a Python script designed to assist users in generating XML templates for Docker containers in Unraid. This tool is particularly useful for users who have lost their XML files due to backup failures or other issues. By converting Docker container configurations from JSON (obtained via `docker inspect`) to XML, users can quickly restore their templates and continue managing their containers efficiently.

## Why Use This Tool?
If you’ve ever lost your XML template files, recovering the configurations for your Docker containers can be a hassle. This tool automates the process of retrieving container information and converting it into the appropriate XML format needed by Unraid. With this script, you can:
- **Quickly regenerate lost XML templates** for your running and non-running Docker containers.
- **Save time** by automating the extraction and conversion processes.
- **Easily manage your containers** again through the Unraid web interface.

## Requirements
- Python 3.x
- Access to the Unraid command line interface
- Docker installed and running on your Unraid server

## How to Run the Tool
1. **Clone the repository or download the script** to your local machine.
2. **Navigate to the script directory** in your terminal.
   ```bash
   cd /path/to/unraid_docker_templates_creator

## Create a Python virtual environment (optional but recommended)
python3 -m venv myenv
source myenv/bin/activate

## Run the script
python unraid_docker_templates_creator.py

Then follow the prompts. your running and non-running containers are now back in the right xml format in /boot/config/plugins/dockerMan/templates-user

Oof! 

