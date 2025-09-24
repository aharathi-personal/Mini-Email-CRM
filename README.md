# Mini Email CRM

Mini Email CRM is a desktop program that helps you organise contact lists, build email templates, and send campaigns without juggling lots of tools.

## Before you start

- A Windows 10 or 11 computer with [Python 3.11 or newer](https://www.python.org/downloads/windows/) installed. When installing Python, tick the box that says **“Add Python to PATH.”**
- (Optional) [Git for Windows](https://git-scm.com/download/win) if you prefer to use Git Bash instead of Command Prompt or PowerShell.
- The project files from this repository, including `requirements.txt`.

> Not sure which Python version you have? Open Command Prompt and run `python --version` (or `py --version`).

## Step 1: Create a private Python workspace (virtual environment)

A virtual environment is a safe folder where Python keeps the packages for this project. It prevents clashes with other apps on your computer. Pick the option that matches the tool you like to use, then run the commands from inside the project folder (the one that contains `main.py`).

### Option A — Command Prompt (`cmd.exe`)

1. Open the Start menu, type **Command Prompt**, and press Enter.
2. Move into the project folder:
   ```cmd
   cd C:\path\to\Mini-Email-CRM
   ```
   Replace `C:\path\to\Mini-Email-CRM` with the real location on your computer.
3. Create the virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Turn it on:
   ```cmd
   venv\Scripts\activate
   ```

You will know it worked when you see `(venv)` at the beginning of the prompt. Type `venv\Scripts\deactivate.bat` later to turn it off.

### Option B — Windows PowerShell

1. Open the Start menu, type **PowerShell**, and press Enter.
2. The first time you do this, Windows might block scripts. Tell it that your scripts are safe:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```
   When asked, type `Y` for Yes. You can change this back later.
3. Move into the project folder:
   ```powershell
   cd C:\path\to\Mini-Email-CRM
   ```
4. Create and activate the virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

When you are finished working, type `Deactivate` to leave the environment.

### Option C — Git Bash

1. Open **Git Bash**.
2. Move into the project folder. In Git Bash, Windows drives are written with lowercase letters:
   ```bash
   cd /c/path/to/Mini-Email-CRM
   ```
3. Create and activate the virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

Type `deactivate` to switch it off later.

## Step 2: Install the app's required packages

Do this step while the virtual environment is turned on. It only needs to be done after the first setup or when `requirements.txt` changes.

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

These commands download everything the app needs, such as the screen toolkit (PyQt5) and supporting libraries.

## Step 3: Open the Mini Email CRM app

Stay inside the project folder with the virtual environment active, then run:

```bash
python main.py
```

The Mini Email CRM window will appear. Keep the terminal window open; it shows helpful status messages. When you're done, close the app window. Press `Ctrl + C` in the terminal if the program is still running.

---

## Extra: Build a Windows `.exe` using the provided files

Already finished testing and want a clickable Windows app? The project includes a ready-made PyInstaller file named `pyinstaller.spec`. Follow these steps:

1. **Turn on your virtual environment** (see Step 1) and make sure the packages are installed (Step 2).
2. **Check the app icon path.** The spec file expects an icon at `resources/icons/app_icon.ico`. If you have a different icon, update the path inside `pyinstaller.spec` before building.
3. **Build the executable** from the project folder:
   ```bash
   pyinstaller --noconfirm pyinstaller.spec
   ```
4. **Find the results:**
   - `dist/Mini Email CRM/` — this folder contains `Mini Email CRM.exe` and everything it needs.
   - `build/` — temporary files created during the build. You can delete this folder after you test the `.exe`.
5. **Share the app:** Zip the entire `dist/Mini Email CRM/` folder or copy it to another machine. Double-click `Mini Email CRM.exe` to launch it.

> Want a fresh build? Delete any old `build/` and `dist/` folders first, then run the command again.

Your Mini Email CRM project is ready to go—enjoy managing your email campaigns with a single, tidy workspace!
