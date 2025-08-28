import argparse
import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import ipaddress
import subprocess
import platform
import sys

# ----------- Helper Functions ------------- #
def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return None

def resolve_dns(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.error:
        return None

def ping_host(host):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        cmd = ["ping", param, "2", host]
        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return output.returncode == 0
    except Exception:
        return False

def check_port(host, port=22, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "open"
    except socket.timeout:
        return "filtered (timeout)"
    except ConnectionRefusedError:
        return "closed (refused)"
    except Exception as e:
        return f"error: {e}"

# ----------- Troubleshooting Suggestions ------------- #
def suggest_fixes(ip, dns_ok, ping_ok, port_status):
    suggestions = []

    if not dns_ok:
        suggestions.append("❌ DNS resolution failed → Check if domain is correct, or verify local DNS settings.")

    if not ping_ok:
        suggestions.append("❌ Host unreachable → Possible causes: Instance stopped, wrong IP, or network ACL blocking ICMP.")

    if "open" in port_status:
        suggestions.append("✅ Port is open → Try connecting with the right client or credentials.")
    elif "filtered" in port_status:
        suggestions.append("⚠️ Port is filtered → Likely blocked by Security Group, NACL, or Firewall.")
    elif "closed" in port_status:
        suggestions.append("❌ Port is closed → Service may not be running on this port.")
    elif "error" in port_status:
        suggestions.append(f"❌ Error checking port: {port_status}")

    try:
        if is_private_ip(ip):
            suggestions.append("ℹ️ Private IP detected → Ensure VPN/Direct Connect/Bastion Host is configured.")
        else:
            suggestions.append("ℹ️ Public IP detected → Ensure firewall/security group allows access from your IP.")
    except:
        suggestions.append("⚠️ Could not determine if IP is public or private.")

    if not suggestions:
        suggestions.append("✅ No obvious issues detected. Try verbose mode or deeper diagnostics.")

    return "\n".join(suggestions)

# ----------- Diagnostics Function ------------- #
def run_diagnostics_cli(host, port):
    print(f"=== Running Diagnostics for {host}:{port} ===")
    ip = resolve_dns(host)
    dns_ok = True if ip else False
    if not ip:
        ip = host

    # Public/private check
    private_status = is_private_ip(ip)
    if private_status is None:
        pubpriv = "Unknown"
    elif private_status:
        pubpriv = "Private"
    else:
        pubpriv = "Public"

    # Ping
    ping_ok = ping_host(ip)

    # Port check
    port_status = check_port(ip, port)

    # Summary
    print(f"- Resolved IP: {ip if dns_ok else 'DNS resolution failed'}")
    print(f"- IP Type: {pubpriv}")
    print(f"- Ping: {'Reachable' if ping_ok else 'Unreachable'}")
    print(f"- Port {port}: {port_status}")
    print("\n=== Suggested Fixes ===")
    print(suggest_fixes(ip, dns_ok, ping_ok, port_status))

# ----------- GUI App ------------- #
def run_diagnostics_gui():
    host = entry.get().strip()
    if not host:
        messagebox.showwarning("Input Error", "Please enter a valid IP or DNS name.")
        return
    
    log_window.delete(1.0, tk.END)
    output_window.delete(1.0, tk.END)

    log_window.insert(tk.END, f"Starting diagnostics for: {host}\n")
    
    ip = resolve_dns(host)
    dns_ok = True if ip else False
    if not ip:
        ip = host
        log_window.insert(tk.END, f"[✗] DNS resolution failed for {host}\n")
    else:
        log_window.insert(tk.END, f"[✓] DNS resolved: {host} -> {ip}\n")

    try:
        private = is_private_ip(ip)
        if private:
            log_window.insert(tk.END, f"[i] {ip} is a PRIVATE IP\n")
        elif private is False:
            log_window.insert(tk.END, f"[i] {ip} is a PUBLIC IP\n")
        else:
            log_window.insert(tk.END, f"[!] Could not determine if {ip} is public/private\n")
    except Exception as e:
        log_window.insert(tk.END, f"[!] Error checking IP type: {e}\n")

    ping_ok = ping_host(ip)
    log_window.insert(tk.END, f"[✓] Host {ip} is reachable (ping success)\n" if ping_ok else f"[✗] Host {ip} is NOT reachable (ping failed)\n")

    port_status = check_port(ip, 22)
    log_window.insert(tk.END, f"[i] Port 22 (SSH) status: {port_status}\n")

    summary = f"Diagnostics for {host} ({ip}):\n"
    summary += f" - Public/Private: {'Private' if is_private_ip(ip) else 'Public'}\n"
    summary += f" - Ping: {'Reachable' if ping_ok else 'Unreachable'}\n"
    summary += f" - SSH Port 22: {port_status}\n"
    summary += "\n=== Suggested Fixes ===\n"
    summary += suggest_fixes(ip, dns_ok, ping_ok, port_status)

    output_window.insert(tk.END, summary)

def start_gui():
    global root, entry, log_window, output_window
    root = tk.Tk()
    root.title("EC2/Linux SSH Troubleshooter")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Enter IP or DNS:").grid(row=0, column=0, sticky="w")
    entry = tk.Entry(frame, width=40)
    entry.grid(row=0, column=1, padx=5)

    run_button = tk.Button(frame, text="Run Diagnostics", command=run_diagnostics_gui)
    run_button.grid(row=0, column=2, padx=5)

    tk.Label(frame, text="Logs:").grid(row=1, column=0, sticky="w")
    log_window = scrolledtext.ScrolledText(frame, width=80, height=15)
    log_window.grid(row=2, column=0, columnspan=3, pady=5)

    tk.Label(frame, text="Summary:").grid(row=3, column=0, sticky="w")
    output_window = scrolledtext.ScrolledText(frame, width=80, height=8)
    output_window.grid(row=4, column=0, columnspan=3, pady=5)

    root.mainloop()

# ----------- Main Entry ------------- #
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PortHound - EC2/Linux SSH Troubleshooter")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--host", type=str, help="Host IP or DNS name")
    parser.add_argument("--port", type=int, default=22, help="Port number to check (default 22)")
    args = parser.parse_args()

    if args.gui:
        start_gui()
    elif args.host:
        run_diagnostics_cli(args.host, args.port)
    else:
        parser.print_help()
