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

Already finished testing and want a clickable Windows app to hand to someone else? The project includes a ready-made PyInstaller file named `pyinstaller.spec`. Follow these steps from a Windows machine (PyInstaller can't cross-compile a `.exe` from macOS or Linux — you must build on Windows).

1. **Create a dedicated build environment** rather than reusing your regular dev virtual environment, so the exe only bundles what the app actually needs:
   ```cmd
   python -m venv build_env
   build_env\Scripts\activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
2. **Check the app icon path.** The spec file expects an icon at `resources/icons/app_icon.ico`. If you have a different icon, update the path inside `pyinstaller.spec` before building.
3. **Build the executable** from the project folder:
   ```cmd
   pyinstaller --noconfirm pyinstaller.spec
   ```
4. **Find the results:**
   - `dist/Mini Email CRM/` — this folder contains `Mini Email CRM.exe` and everything it needs.
   - `build/` — temporary files created during the build. You can delete this folder after you test the `.exe`.
5. **Test it before sharing.** Double-click `Mini Email CRM.exe` inside `dist/Mini Email CRM/` and confirm the app window opens normally.
6. **Share the app:** Zip the entire `dist/Mini Email CRM/` folder (right-click it → Send to → Compressed (zipped) folder) and send the zip to the other machine. The recipient should unzip it first, then double-click `Mini Email CRM.exe` from inside the unzipped folder — running it directly from inside the zip (without extracting) will fail, since the exe needs its sibling `_internal` folder to sit next to it on a real disk path.

> Want a fresh build? Delete any old `build/` and `dist/` folders first, then run the command again.

### Troubleshooting the build

**`ImportError: cannot import name 'Tree' from 'PyInstaller.utils.hooks'`**
Newer versions of PyInstaller (6.x) moved `Tree` to a different module and changed the format it produces. `pyinstaller.spec` in this repo has already been updated to use plain `('source_folder', 'dest_folder')` tuples in `datas` instead of `Tree(...)`, so if you're on an up-to-date checkout you shouldn't hit this. If you do (e.g. working from an older copy of the spec file), either pull the latest `pyinstaller.spec` or make the same change yourself.

**`ValueError: too many values to unpack (expected 2)` during `Analysis(...)`**
Same root cause as above — `Tree(...)` objects produce 3-element entries meant for `COLLECT`, not the 2-element `(source, dest)` tuples `Analysis(datas=...)` expects. Fixed the same way, by using plain tuples.

**`ERROR: Could not find a version that satisfies the requirement PyQt5-Qt5==5.15.17`**
This pin in `requirements.txt` doesn't have a published Windows wheel — only `PyQt5-Qt5==5.15.2` is available on PyPI, likely because the original `requirements.txt` was captured with `pip freeze` on a different OS/Python version. If you hit this, install a compatible set manually before running the rest of `requirements.txt`:
```cmd
pip install PyQt5==5.15.11 PyQt5-Qt5==5.15.2 PyQt5-sip==12.17.0
pip install -r requirements.txt
```
The second install will simply confirm the already-satisfied packages and pull in everything else (pandas, numpy, PyInstaller, etc.).

**"Windows cannot find '\\'. Make sure you typed the name correctly, and then try again."**
This is a generic Windows shell error, not specific to this project — it usually means a command was handed an empty or malformed path (for example, a variable that expanded to nothing, or a path with a trailing/standalone backslash). If you hit this while building, check the exact command you ran for typos or missing quotes around folder names that contain spaces (like `Mini Email CRM`), and confirm you're running commands from inside the project folder.

**App window won't resize / launching the app prints odd characters then crashes**
These were bugs in older versions of this app that have since been fixed: the compose window's text box used to have a fixed maximum height, and some startup status messages used emoji characters that could crash on Windows' default console codepage. Make sure you're building from an up-to-date checkout if you still see either issue.

Your Mini Email CRM project is ready to go—enjoy managing your email campaigns with a single, tidy workspace!
