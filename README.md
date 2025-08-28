# 🐾 Port Hound

Port Hound is a **friendly DevOps troubleshooting tool** that helps you quickly identify SSH (port 22) connectivity issues for your EC2 or Linux servers.  
It can run in **CLI mode** or **GUI mode**, making it versatile for both terminal users and GUI lovers.

---

## ✨ Features
- Detects if an IP/DNS is **public or private**
- Resolves DNS names to IPs
- Performs **ping test** to check reachability
- Checks **SSH (port 22) status** (open, closed, filtered)
- Provides **smart troubleshooting suggestions**
- Supports **GUI (`--gui`)** and **CLI modes**

---

## ⚙️ Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
tk
```

---

## 🚀 Usage

### CLI Mode
Run diagnostics directly from the terminal:

```bash
python port-hound.py <IP_or_DNS>
```

**Example:**
```bash
python port-hound.py ec2-3-123-45-67.compute-1.amazonaws.com
```

---

### GUI Mode
Launch the GUI tool:

```bash
python port-hound.py --gui
```

A window will open where you can enter IP/DNS and run diagnostics interactively.

---

## 🖼️ Screenshots

### GUI Mode
![GUI Example](images/gui-example.png)

### CLI Mode
![CLI Example](images/cli-example.png)

---

## 🔧 Example Scenarios

Test against common IPs/DNS names:

```bash
python port-hound.py 8.8.8.8        # Google DNS (Public, Reachable)
python port-hound.py localhost      # Localhost (Private, Reachable if SSH running)
python port-hound.py invalid.host   # Invalid DNS
```

---

## 📦 DevOps Style CI/CD (Optional)

Add a GitHub Action to test your script automatically on pushes:

```yaml
name: Python Application

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run CLI diagnostics (example)
      run: python port-hound.py 8.8.8.8
```

---

## 🛠️ Roadmap

- 🔜 **Extended version**: Support for multiple ports & services  
- 🔜 Export results as JSON/HTML reports  
- 🔜 Dockerized version for easy deployment  

---

## 👨‍💻 Author
Made with ❤️ by Akib for DevOps engineers who just want **answers, not headaches** 🐧⚡

