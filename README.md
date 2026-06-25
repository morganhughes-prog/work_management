# DevOps Grimoire (Task Board)

Welcome to the DevOps Grimoire! This is a modern, dark-fantasy themed Kanban board built with Python, Flask, and SQLite. It features drag-and-drop task management, user authentication, and an admin dashboard for managing work classifications.

This guide will walk you through setting up your development environment from scratch, cloning the code from Bitbucket, and running the application locally.

---

## 1. Prerequisites
Before you begin, ensure you have the following installed on your computer:
* **[Python](https://www.python.org/downloads/)** (Make sure to check the box that says "Add Python to PATH" during installation).
* **[Git](https://git-scm.com/downloads)** (For version control and cloning).
* **[Visual Studio Code (VS Code)](https://code.visualstudio.com/)** (Our recommended code editor).

---

## 2. Recommended VS Code Extensions
To make working on this project easier, open VS Code, click on the **Extensions** icon on the left sidebar (or press `Ctrl+Shift+X`), and search for/install these extensions:
1. **Python** (by Microsoft) - Provides autocomplete, debugging, and linting for Python.
2. **SQLite** (by alexcvzz) - Allows you to view and explore the local `devops_board.db` database directly inside VS Code.

---

## 3. Configure Git (First Time Setup)
If this is your first time using Git on your machine, you need to tell it who you are so your commits are attributed correctly. 

Open a terminal in VS Code (`Terminal > New Terminal` or `Ctrl+\``) and run these commands, replacing the placeholders with your actual details:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
4. Clone the Repository from Bitbucket
To get the code onto your machine:

Go to your Bitbucket repository in your web browser.

Click the Clone button in the top right corner.

Copy the command provided (it will look something like git clone https://username@bitbucket.org/workspace/repo.git).

Open your VS Code terminal and navigate to the folder where you want to store your projects (e.g., cd Documents).

Paste the clone command and press Enter:

Bash
git clone [https://username@bitbucket.org/workspace/repo.git](https://username@bitbucket.org/workspace/repo.git)
Once downloaded, open the folder in VS Code by going to File > Open Folder... and selecting your newly cloned repository.

5. Environment Setup (Windows / PowerShell Fix)
By default, Windows PowerShell restricts running scripts, which prevents Python virtual environments from activating. Let's fix that.

In your VS Code terminal, run this command to update your Execution Policy (you only ever have to do this once on your PC):

PowerShell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
Create and Activate a Virtual Environment
A virtual environment (venv) keeps this project's dependencies isolated from the rest of your computer.

Create the environment: Run this command in your terminal:

Bash
python -m venv venv
(This creates a folder named venv in your project).

Activate the environment:

On Windows:

Bash
.\venv\Scripts\activate


6. Install Project Modules
With your virtual environment activated, install the required Python libraries for this project:

Bash
pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug
7. Running the Application
You are all set up! To start the local web server:

Ensure your terminal still shows (venv).

Run the main application file:

Bash
python app.py
The terminal will output a local web address (usually http://127.0.0.1:5000/).

Ctrl + Click that link to open the app in your browser!

Note: The very first account you register on the website will automatically be granted Admin privileges.

Project Structure Overview
app.py: The main Flask backend containing all routes, database models, and logic.

templates/: Contains the HTML files (using Jinja templating) for the frontend structure.

static/style.css: The custom CSS styling for the dark fantasy theme.

devops_board.db: The SQLite database file (auto-generated when you first run the app).

make_admin.py: A helper script to manually promote users to the Admin role via the terminal.