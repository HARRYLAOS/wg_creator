import os
import json
import subprocess
import qrcode
# File to store WireGuard server details
CONFIG_FILE = "wg_creator_data/wg_server_config.json"
# File to store assigned user IPs
USER_DB_FILE = "wg_creator_data/wg_userdb_ips.json"
# File to store server-side peer configuration
SERVER_PEER_CONFIG_FILE = "wg_creator_data/wg_server_peer_config.rsc"

# Load existing server details or prompt for new ones
def load_server_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return setup_server_config()

# Ask for server details and store them
def setup_server_config():
    server_config = {
        "server_name": input("Enter WireGuard Server Name: "),
        "server_ip": input("Enter WireGuard Server Public IP: "),
        "server_port": input("Enter WireGuard Port: "),
        "server_public_key": input("Enter WireGuard Server Public Key: "),
        "server_private_key": input("Enter WireGuard Server Private Key: "),
        "subnet": input("Enter WireGuard Subnet (e.g., 192.168.100.0/24): ")
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(server_config, f, indent=4)
    return server_config

# Load user database or create a new one
def load_user_db():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    return {}

# Save user database
def save_user_db(user_db):
    with open(USER_DB_FILE, "w") as f:
        json.dump(user_db, f, indent=4)

# Generate a new WireGuard key pair
def generate_keys():
    private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
    public_key = subprocess.run(["wg", "pubkey"], input=private_key, capture_output=True, text=True).stdout.strip()
    return private_key, public_key

# Get the next available IP address
def get_next_available_ip(user_db, subnet):
    base_ip = ".".join(subnet.split("/")[0].split(".")[:-1]) + "."
    used_ips = set(user_db.values())
    
    for i in range(2, 255):  # Start from .2 up to .254
        new_ip = f"{base_ip}{i}"
        if new_ip not in used_ips:
            return new_ip
    
    print("Error: No more available IPs in the subnet!")
    exit(1)

# Function to generate QR Code
def generate_qr_code(config_filename, qr_filename):
    with open(config_filename, "r") as f:
        config_data = f.read()
    
    # Generate QR code
    qr = qrcode.make(config_data)
    
    # Save QR Code as an image
    qr.save(qr_filename)
    
    # Display QR code in terminal (Linux/macOS only)
    try:
        subprocess.run(["qrencode", "-t", "utf8", config_data])
    except FileNotFoundError:
        print(f"QR code saved as {qr_filename}, but cannot display in terminal (qrencode not installed).")


# Generate WireGuard Windows config
def generate_windows_config(client_private_key, client_ip, server_config):
    return f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_ip}/24
DNS = 94.140.14.14

[Peer]
PublicKey = {server_config['server_public_key']}
Endpoint = {server_config['server_ip']}:{server_config['server_port']}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""

# Generate MikroTik client configuration
def generate_mikrotik_config(client_private_key, client_public_key, client_ip, server_config):
    return f"""# Create WireGuard interface
/interface wireguard add name=WireGuard_Client private-key={client_private_key}

# Assign IP to the WireGuard interface
/ip address add address={client_ip}/24 interface=WireGuard_Client

# Add server peer
/interface wireguard peers add interface=WireGuard_Client public-key={server_config['server_public_key']} endpoint={server_config['server_ip']}:{server_config['server_port']} allowed-address=0.0.0.0/0 persistent-keepalive=25

# Set default route through WireGuard tunnel
/ip route add dst-address=0.0.0.0/0 gateway=WireGuard_Client
"""

# Generate MikroTik server configuration for the new peer
def generate_server_peer_config(username, client_public_key, client_ip, server_config):
    return f"""# Add new peer to WireGuard server
/interface wireguard peers add name="{username}" interface="{server_config['server_name']}" public-key="{client_public_key}" allowed-address="{client_ip}/32"
"""

# Main function
def main():
    print("\n=== WireGuard Config Generator by Harry Christopoulos ===\n")
        # Ensure the folder exists
    os.makedirs("wg_creator_data", exist_ok=True)
    server_config = load_server_config()
    user_db = load_user_db()
    
    username = input("Enter the username for this WireGuard config: ")
    if username in user_db:
        print(f"Error: Username '{username}' already exists with IP {user_db[username]}.")
        exit(1)
    
    print("Generating client keys...")
    client_private_key, client_public_key = generate_keys()
    print("Client keys generated successfully!\n")
    
    client_ip = get_next_available_ip(user_db, server_config["subnet"])
    user_db[username] = client_ip
    save_user_db(user_db)
    
    windows_config = generate_windows_config(client_private_key, client_ip, server_config)
    mikrotik_config = generate_mikrotik_config(client_private_key, client_public_key, client_ip, server_config)
    server_peer_config = generate_server_peer_config(username, client_public_key, client_ip, server_config)
    
    windows_filename = f"wg_creator_data/{username}_wg_windows.conf"
    mikrotik_filename = f"wg_creator_data/{username}_wg_mt_setup.rsc"
    
    with open(windows_filename, "w") as f:
        f.write(windows_config)
    with open(mikrotik_filename, "w") as f:
        f.write(mikrotik_config)
    with open(f"{SERVER_PEER_CONFIG_FILE}", "a") as f:
        f.write(server_peer_config + "\n")
    
    print("Configuration files generated:")
    print(f"- {windows_filename} (Windows)")
    print(f"- {mikrotik_filename} (MikroTik)")
    print(f"- {SERVER_PEER_CONFIG_FILE} (Server Peer Configuration)\n")
    
    qr_filename = f"wg_creator_data/{username}_wg_qr.png"
    generate_qr_code(windows_filename, qr_filename)

    print(f"QR Code for mobile saved as: {qr_filename}")
    print("Setup complete! Copy the configurations to your devices.")

if __name__ == "__main__":
    main()
