"""
Simple Surfshark Wireguard CLI Tool
[connect|disconnect|status|setup]
"""

import os
import sys
import json
import random
import subprocess
import time
from pathlib import Path


class WireguardCLI:
    def __init__(self):
        self.wireguard_dir = "/etc/wireguard"
        self.config_source_dir = "./wireguard"
        self.servers_file = "wireguard_servers.json"
        self.current_interface = "wg0"

    def check_and_install_wireguard(self):
        """Check if Wireguard is installed, install if not"""
        try:
            result = subprocess.run(["which", "wg"], capture_output=True, text=True)
            if result.returncode == 0:
                print("Wireguard already installed")
                return True
        except:
            pass

        print("Installing Wireguard...")
        try:
            subprocess.run(
                ["sudo", "apt-get", "update"], check=True, capture_output=True
            )
            subprocess.run(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "wireguard",
                    "wireguard-tools",
                    "resolvconf",
                ],
                check=True,
            )

            subprocess.run(
                ["sudo", "systemctl", "enable", "resolvconf.service"],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["sudo", "systemctl", "start", "resolvconf.service"],
                check=True,
                capture_output=True,
            )

            print("Wireguard installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Wireguard: {e}")
            return False

    def copy_configs_to_system(self):
        """Copy configuration files from local folder to /etc/wireguard/"""
        print("Copying Wireguard configurations...")

        if not os.path.exists(self.config_source_dir):
            print(f"Configuration directory {self.config_source_dir} not found")
            return False

        try:
            subprocess.run(
                ["sudo", "mkdir", "-p", self.wireguard_dir],
                check=True,
                capture_output=True,
            )

            conf_files = [
                f for f in os.listdir(self.config_source_dir) if f.endswith(".conf")
            ]

            if not conf_files:
                print(f"No .conf files found in {self.config_source_dir}")
                return False

            for conf_file in conf_files:
                source_path = os.path.join(self.config_source_dir, conf_file)
                country_code = conf_file.split("-")[0]
                dest_file = f"{country_code}.conf"
                dest_path = os.path.join(self.wireguard_dir, dest_file)

                subprocess.run(["sudo", "cp", source_path, dest_path], check=True)

                subprocess.run(["sudo", "chmod", "600", dest_path], check=True)
                subprocess.run(["sudo", "chown", "root:root", dest_path], check=True)

            print(f"Copied {len(conf_files)} configuration files")
            return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to copy configurations: {e}")
            return False

    def scan_and_save_servers(self):
        """Scan for .conf files and save server list"""
        try:
            if not os.path.exists(self.wireguard_dir):
                print("Wireguard directory not found")
                return []
            result = subprocess.run(
                ["sudo", "ls", self.wireguard_dir],
                capture_output=True,
                text=True,
                check=True,
            )

            conf_files = [
                f for f in result.stdout.strip().split("\n") if f.endswith(".conf")
            ]
            servers = [f.replace(".conf", "") for f in conf_files if f]

            server_data = {"servers": servers, "total": len(servers)}

            with open(self.servers_file, "w") as f:
                json.dump(server_data, f, indent=2)

            print(f"Found and saved {len(servers)} servers")
            return servers

        except Exception as e:
            print(f"Failed to scan servers: {e}")
            return []

    def load_servers(self):
        """Load servers from JSON file"""
        if not os.path.exists(self.servers_file):
            print("No servers file found. Setting up...")
            if not self.setup():
                return []

        try:
            with open(self.servers_file, "r") as f:
                data = json.load(f)
                return data.get("servers", [])
        except Exception as e:
            print(f"Failed to load servers: {e}")
            return []

    def connect(self):
        """Connect to a random server"""
        print("Connecting to Surfshark Wireguard VPN...")

        self.disconnect()

        servers = self.load_servers()
        if not servers:
            print("No servers available")
            return False

        # Select random server
        server = random.choice(servers)
        print(f"Connecting to: {server}")

        try:
            # Use wg-quick to bring up the interface
            result = subprocess.run(
                ["sudo", "wg-quick", "up", server], capture_output=True, text=True
            )

            if result.returncode == 0:
                print("Successfully connected!")
                print(f"Connected to: {server}")
                return True
            else:
                print(f"Connection failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from VPN"""
        try:
            result = subprocess.run(
                ["sudo", "wg", "show"], capture_output=True, text=True
            )

            if result.returncode != 0 or not result.stdout.strip():
                print("No VPN connection found")
                return

            active_interfaces = []
            for line in result.stdout.split("\n"):
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    interface = line.split(":")[1].strip()
                    print(interface)
                    if interface:
                        active_interfaces.append(interface)

            for interface in active_interfaces:
                try:
                    subprocess.run(
                        ["sudo", "wg-quick", "down", interface],
                        capture_output=True,
                        check=True,
                    )
                    print(f"Disconnected from VPN ({interface})")
                except subprocess.CalledProcessError:
                    pass

            if not active_interfaces:
                print("No VPN connection found")

        except Exception as e:
            print(f"Disconnect error: {e}")

    def is_connected(self):
        """Check if VPN is connected"""
        try:
            result = subprocess.run(
                ["sudo", "wg", "show"], capture_output=True, text=True
            )
            return result.returncode == 0 and result.stdout.strip() != ""
        except:
            return False

    def status(self):
        """Show connection status"""
        if self.is_connected():
            print("VPN Status: CONNECTED")
            try:
                result = subprocess.run(
                    ["sudo", "wg", "show"], capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    print("Wireguard interfaces:")
                    print(result.stdout.strip())
            except:
                pass

            try:
                result = subprocess.run(
                    ["curl", "-s", "--max-time", "5", "https://api.ipify.org"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    print(f"Current IP: {result.stdout.strip()}")
            except:
                pass
        else:
            print("VPN Status: DISCONNECTED")

    def setup(self):
        """Initial setup - install Wireguard and copy configs"""
        print("Setting up Surfshark Wireguard...")

        if not self.check_and_install_wireguard():
            return False

        if not self.copy_configs_to_system():
            return False

        servers = self.scan_and_save_servers()
        if not servers:
            return False

        print("Setup completed!")
        print("You can now use:")
        print("  connect    - Connect to random server")
        print("  disconnect - Disconnect from all servers")
        print("  status     - Check connection status")
        return True


def main():
    if len(sys.argv) != 2:
        print("Surfshark Wireguard CLI")
        print("Usage: python3 wireguard_cli_tool.py [connect|disconnect|status|setup]")
        return

    cli = WireguardCLI()
    command = sys.argv[1].lower()

    if command == "setup":
        cli.setup()
    elif command == "connect":
        cli.connect()
    elif command == "disconnect":
        cli.disconnect()
    elif command == "status":
        cli.status()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: connect, disconnect, status, setup")


if __name__ == "__main__":
    main()
