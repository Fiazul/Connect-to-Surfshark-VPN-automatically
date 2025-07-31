## What Happens Under the Hood

When you run commands, this CLI tool executes system commands to manage WireGuard VPN connections. Here’s a breakdown:

- **Setup (`wireguard-cli setup`)**
  - Checks if `wireguard` and related tools (`wg`, `wg-quick`, `resolvconf`) are installed; if not, installs them via:
    ```
    sudo apt-get update
    sudo apt-get install -y wireguard wireguard-tools resolvconf
    sudo systemctl enable resolvconf.service
    sudo systemctl start resolvconf.service
    ```
  - Copies your `.conf` files from the `wireguard/` directory to `/etc/wireguard/` with correct ownership and permissions (`chmod 600`).
  - Scans `/etc/wireguard/` for config files and saves the list of servers to a JSON file for later use.

- **Connect (`wireguard-cli connect`)**
  - Disconnects any existing WireGuard interfaces via:
    ```
    sudo wg-quick down <interface>
    ```
  - Randomly selects a server and brings up its interface:
    ```
    sudo wg-quick up <server>
    ```

- **Disconnect (`wireguard-cli disconnect`)**
  - Lists active WireGuard interfaces with:
    ```
    sudo wg show
    ```
  - Shuts down all active interfaces:
    ```
    sudo wg-quick down <interface>
    ```

- **Status (`wireguard-cli status`)**
  - Checks active WireGuard interfaces:
    ```
    sudo wg show
    ```
  - Fetches your current public IP address:
    ```
    curl -s https://api.ipify.org
    ```

---

This section helps users understand exactly what’s happening on their system and eases debugging when something goes wrong.

Want me to add this to the README draft? Or tweak any parts to fit your style?
