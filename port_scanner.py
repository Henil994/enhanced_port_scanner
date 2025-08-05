#!/usr/bin/env python3

import socket
import threading
from datetime import datetime
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

open_tcp_ports = []
open_udp_ports = []
banner_results = []
lock = threading.Lock()

def grab_banner(target, port):
    try:
        sock = socket.socket()
        sock.settimeout(1)
        sock.connect((target, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner
    except:
        return ""

def scan_tcp_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    result = sock.connect_ex((target, port))
    if result == 0:
        banner = grab_banner(target, port)
        with lock:
            open_tcp_ports.append(port)
            banner_results.append((port, banner))
            print(f"TCP Port {port} OPEN - Banner: {banner}")
    sock.close()

def scan_udp_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    try:
        # Send empty packet
        sock.sendto(b'', (target, port))
        data, _ = sock.recvfrom(1024)
        with lock:
            open_udp_ports.append(port)
            print(f"UDP Port {port} OPEN or FILTERED (response received)")
    except socket.timeout:
        # No response - could be open or filtered, no guarantee
        pass
    except Exception as e:
        pass
    sock.close()

def scan_ports(target, start_port, end_port, protocol="TCP"):
    threads = []
    print(f"Starting {protocol} scan on {target} ports {start_port}-{end_port}")

    for port in range(start_port, end_port + 1):
        if protocol == "TCP":
            t = threading.Thread(target=scan_tcp_port, args=(target, port))
        else:
            t = threading.Thread(target=scan_udp_port, args=(target, port))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def save_results_to_file(filename):
    try:
        with open(filename, "w") as f:
            f.write("Open TCP Ports and Banners:\n")
            for port, banner in banner_results:
                f.write(f"Port {port}: {banner}\n")
            f.write("\nOpen UDP Ports:\n")
            for port in open_udp_ports:
                f.write(f"Port {port}\n")
        print(f"Results saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

# -------- GUI --------
class PortScannerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Port Scanner")

        # Target IP
        tk.Label(master, text="Target IP:").grid(row=0, column=0, sticky="e")
        self.target_entry = tk.Entry(master)
        self.target_entry.grid(row=0, column=1, padx=5, pady=5)

        # Start port
        tk.Label(master, text="Start Port:").grid(row=1, column=0, sticky="e")
        self.start_entry = tk.Entry(master)
        self.start_entry.grid(row=1, column=1, padx=5, pady=5)
        self.start_entry.insert(0, "1")

        # End port
        tk.Label(master, text="End Port:").grid(row=2, column=0, sticky="e")
        self.end_entry = tk.Entry(master)
        self.end_entry.grid(row=2, column=1, padx=5, pady=5)
        self.end_entry.insert(0, "1024")

        # Protocol selection
        tk.Label(master, text="Protocol:").grid(row=3, column=0, sticky="e")
        self.protocol_var = tk.StringVar(value="TCP")
        tk.Radiobutton(master, text="TCP", variable=self.protocol_var, value="TCP").grid(row=3, column=1, sticky="w")
        tk.Radiobutton(master, text="UDP", variable=self.protocol_var, value="UDP").grid(row=3, column=1)

        # Start Scan button
        self.scan_button = tk.Button(master, text="Start Scan", command=self.start_scan)
        self.scan_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Results display
        self.result_text = scrolledtext.ScrolledText(master, width=60, height=20)
        self.result_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Save results button
        self.save_button = tk.Button(master, text="Save Results", command=self.save_results)
        self.save_button.grid(row=6, column=0, columnspan=2, pady=5)

    def start_scan(self):
        target = self.target_entry.get().strip()
        try:
            start_port = int(self.start_entry.get())
            end_port = int(self.end_entry.get())
            if start_port < 1 or end_port > 65535 or start_port > end_port:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid port numbers (1-65535) and range.")
            return

        protocol = self.protocol_var.get()

        # Clear previous results
        self.result_text.delete('1.0', tk.END)
        open_tcp_ports.clear()
        open_udp_ports.clear()
        banner_results.clear()

        self.result_text.insert(tk.END, f"Scanning {target} ports {start_port}-{end_port} with {protocol} protocol...\n")
        self.master.update()

        # Run scan in background thread to not freeze GUI
        threading.Thread(target=self.run_scan, args=(target, start_port, end_port, protocol), daemon=True).start()

    def run_scan(self, target, start_port, end_port, protocol):
        scan_ports(target, start_port, end_port, protocol)
        self.result_text.insert(tk.END, "\nScan complete!\n")

        if protocol == "TCP" and banner_results:
            self.result_text.insert(tk.END, "\nOpen TCP Ports and Banners:\n")
            for port, banner in banner_results:
                self.result_text.insert(tk.END, f"Port {port}: {banner}\n")

        if protocol == "UDP" and open_udp_ports:
            self.result_text.insert(tk.END, "\nOpen UDP Ports:\n")
            for port in open_udp_ports:
                self.result_text.insert(tk.END, f"Port {port}\n")

        if not (open_tcp_ports or open_udp_ports):
            self.result_text.insert(tk.END, "No open ports found.\n")

    def save_results(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, "w") as f:
                    if banner_results:
                        f.write("Open TCP Ports and Banners:\n")
                        for port, banner in banner_results:
                            f.write(f"Port {port}: {banner}\n")
                    if open_udp_ports:
                        f.write("\nOpen UDP Ports:\n")
                        for port in open_udp_ports:
                            f.write(f"Port {port}\n")
                messagebox.showinfo("Success", f"Results saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = PortScannerGUI(root)
    root.mainloop()
