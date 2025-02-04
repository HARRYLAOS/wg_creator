# wg_creator

Charilaos (Harry) Christopoulos 

LinkedIn: https://www.linkedin.com/in/charilaos-christopoulos/

Description:
This Python script automates the process of generating WireGuard client configurations for both Windows Operating Wireguard Application and MikroTik routers, while also managing IP allocations and generating server-side configurations for new peers. The script is designed for road warrior clients,  all client traffic is routed through the WireGuard tunnel (0.0.0.0/0)

Prerequisites:
+ sudo apt install wireguard
+ Coding and Testing was performed on a Kali Linux VM.
+ sudo apt install qrencode -y - First major Update - Admins can now generate QR Codes of the Client Mobile Wireguard Application. 4th February

It is particularly useful for network engineers who manage multiple WireGuard clients and want a streamlined way to:

+ Assign unique IPs to each client automatically.
+ Generate client configuration files in the correct format.
+ Generate a MikroTik setup script for router-based clients.
+ Append new peer details to the WireGuard server configuration.
+ Store and track assigned IPs to avoid conflicts.
+ Store user based QR Codes. (Update 4th February)

Features & Functionality

+ Initial Setup & Configuration Storage
        The script prompts for WireGuard server details (name, public IP, port, public key, and subnet) on the first run.
        Stores these details in wg_server_config.json for future use.

+ Client Configuration Generation
        Asks for a username to associate with the client.
        Automatically assigns a unique ascending IP from the defined WireGuard subnet.
        Generates client key pairs using wg genkey.
        Generates two configuration files:
            Windows WireGuard client config (user_wg_windows.conf)
            MikroTik setup script (user_mt_wg_setup.rsc)

+ Server-Side Peer Configuration Generation
        Creates/updates a server-side peer configuration file (wg_server_peer_config.rsc) that contains the new peer’s public key and assigned IP.
        This allows the WireGuard administrator to simply copy and paste the configuration into the server’s WireGuard config.

+ IP Address Management
        Keeps track of assigned IPs in userdb_wg_ips.json.
        Ensures each client gets a unique IP.
        Warns when no more IPs are available in the subnet.

+ MikroTik-Specific Configuration
        Generates a script that can be copied into a MikroTik router to configure a WireGuard tunnel.
        The MikroTik script:
            Creates a WireGuard interface and assigns the private key.
            Assigns the allocated IP to the interface.
            Adds a peer (the WireGuard server) with the necessary settings.
            Sets up a default route to force all traffic through the tunnel.

+ Error Handling & User Guidance
        Detects duplicate usernames and prevents IP conflicts.
        Informs the user when all available IPs are allocated.
        Ensures configuration files are properly saved and named.

Use Cases

+ Network Engineers & Administrators managing multiple WireGuard clients.
+ Remote Work & VPN Deployments, ensuring all client traffic is securely routed.
+ MikroTik Router Users who need WireGuard connectivity but prefer an automated setup.
+ Companies & Teams requiring an easy way to distribute WireGuard configurations to employees.


