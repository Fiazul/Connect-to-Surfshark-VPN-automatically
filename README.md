# Connect-to-Surfshark-VPN-With-CLI

A CLI tool to manage Surfshark WireGuard VPN connections on Linux. This README walks you through grabbing Surfshark `.conf` files, installing the tool, and what’s happening under the hood.
## About
A CLI tool to automate Surfshark VPN connections using WireGuard, designed for server-side environments. It eliminates manual VPN setup and GUI dependencies, enabling developers and sysadmins to manage secure connections effortlessly in headless systems for tasks like automated testing, secure data transfers, or scripted workflows.

## Features
- **Automated Setup**: Installs WireGuard dependencies and configures Surfshark `.conf` files.
- **Seamless Connections**: Connects to a random Surfshark server with a single command.
- **Easy Disconnection**: Shuts down active VPN interfaces cleanly.
- **Status Checks**: Verifies VPN status and public IP address.
## Prerequisites

- Linux system with `sudo` access
- Active Surfshark VPN subscription
- Internet connection

## Getting Surfshark WireGuard Config Files

You’ll need WireGuard `.conf` files from Surfshark to use this tool. Here’s how to get ‘em:

1. Log in to your Surfshark account on their website.
2. Head to **VPN** > **Manual Setup**.
3. Select **WireGuard** as the protocol.
4. Click **Get Key Pair** to generate your public/private keys.
5. Pick your server locations, download the `.conf` files, and save them to the `wireguard/` folder in this repo (after cloning, see below).

## Installation

1. **Install Dependencies**  
   Make sure Python 3, pip, and Git are ready to roll:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip git
   ```

2. **Clone the Repo**  
   Grab the code and hop into the directory:

   ```bash
   git clone https://github.com/Fiazul/Connect-to-Surfshark-VPN-With-CLI.git
   cd Connect-to-Surfshark-VPN-With-CLI
   ```

3. **Add Config Files**  
   Drop your downloaded `.conf` files into the `wireguard/` folder.

4. **Run the Install Script**  
   Fire up the setup script:

   ```bash
   sudo python3 install.py
   ```

5. **Set Up WireGuard CLI**  
   Get WireGuard ready to go:

   ```bash
   wireguard-cli setup
   ```

## What’s Happening Under the Hood

The `wireguard-cli` tool runs system commands to handle WireGuard connections. Here’s the lowdown on each command:

### `wireguard-cli setup`
- **What it does**: Sets up your system for WireGuard.
- **How it works**:
  - Checks for `wireguard`, `wg`, `wg-quick`, and `resolvconf`. If they’re missing, it installs them:
    ```bash
    sudo apt-get update
    sudo apt-get install -y wireguard wireguard-tools resolvconf
    sudo systemctl enable resolvconf.service
    sudo systemctl start resolvconf.service
    ```
  - Moves `.conf` files from `wireguard/` to `/etc/wireguard/` with proper perms (`chmod 600`).
  - Scans `/etc/wireguard/` for configs and saves the server list to a JSON file.

### `wireguard-cli connect`
- **What it does**: Hooks you up to a random Surfshark server.
- **How it works**:
  - Kills any active WireGuard interfaces:
    ```bash
    sudo wg-quick down <interface>
    ```
  - Picks a random server from the JSON list and brings it online:
    ```bash
    sudo wg-quick up <server>
    ```

### `wireguard-cli disconnect`
- **What it does**: Cuts off all WireGuard connections.
- **How it works**:
  - Checks active interfaces:
    ```bash
    sudo wg show
    ```
  - Shuts them down:
    ```bash
    sudo wg-quick down <interface>
    ```

### `wireguard-cli status`
- **What it does**: Shows your VPN status and public IP.
- **How it works**:
  - Lists active interfaces:
    ```bash
    sudo wg show
    ```
  - Grabs your public IP:
    ```bash
    curl -s https://api.ipify.org
    ```

## Notes

- Make sure your `.conf` files are in the `wireguard/` folder before running `wireguard-cli setup`.
- The tool needs `sudo` for installing packages and messing with WireGuard interfaces.
- Check that `resolvconf` is running and `/etc/wireguard/` configs have `chmod 600` perms.
- If connections flake out, grab fresh `.conf` files from Surfshark’s site.

## Troubleshooting

- **Connection fails?** Double-check your `.conf` files and internet.
- **Perms issue?** Run `sudo chmod 600 /etc/wireguard/*.conf`.
- **Still stuck?** Hit up the [GitHub Issues](https://github.com/Fiazul/Connect-to-Surfshark-VPN-With-CLI/issues) page.

