# meraki_tools.py

from meraki import DashboardAPI
import os
from dotenv import load_dotenv
import logging

load_dotenv()
MERAKI_API_KEY = os.getenv("MERAKI_API_KEY")

client = DashboardAPI(api_key=MERAKI_API_KEY)

# --- Switch Port Management ---
def get_switch_ports(network_id, switch_serial):
    """
    Get the list of ports on a specific switch in the given network.
    """
    ports = client.switches.getDeviceSwitchPorts(switch_serial)
    return ports
# meraki_tools.py

# meraki_tools.py

def get_vpn_status(network_id):
    """
    Fetch the VPN status for a network.
    This method specifically retrieves VPN status for Meraki MX security appliances.
    """
    try:
        # Get the VPN status for the network's appliances (Meraki MX device)
        vpn_status = client.appliance.getNetworkApplianceVpnStatus(network_id)
        return vpn_status
    except Exception as e:
        return f"Error fetching VPN status: {str(e)}"

def configure_switch_port(network_id, switch_serial, port_id, name=None, vlan=None, enabled=None, poe_enabled=None,
                          speed=None):
    """
    Configure settings for a specific switch port.
    """
    data = {}
    if name:
        data['name'] = name
    if vlan is not None:
        data['vlan'] = vlan
    if enabled is not None:
        data['enabled'] = enabled
    if poe_enabled is not None:
        data['poeEnabled'] = poe_enabled
    if speed:
        data['speed'] = speed

    updated_port = client.switches.updateDeviceSwitchPort(switch_serial, port_id, **data)
    return updated_port

# --- Real-Time Data Integration ---
def fetch_real_time_data():
    """
    Fetch the latest data from Meraki (e.g., devices, network status).
    """
    response = client.networks.getNetworkDevices("network_id")  # Replace with actual network ID
    devices = response.json()
    return devices

# # --- Network Management ---
# def create_network(org_id, network_name, network_type='wireless'):
#     network = client.organizations.createOrganizationNetwork(org_id, name=network_name, type=network_type)
#     return network
#
# # --- Device Management ---
# def reboot_device(network_id, serial):
#     result = client.networks.rebootNetworkDevice(network_id, serial)
#     return result
def get_organizations():
    """
    Fetch the list of organizations associated with the Meraki API key.
    """
    orgs = client.organizations.getOrganizations()
    return orgs

def get_networks_for_org(org_id):
    """
    Fetch the list of networks for a given organization ID.
    """
    nets = client.organizations.getOrganizationNetworks(org_id)
    return nets

def list_vlans(network_id):
    """
    Fetch the list of VLANs for a given Meraki network.
    """
    return client.appliance.getNetworkApplianceVlans(network_id)

def list_uplinks(network_id):
    """
    Fetch the uplink status for a given Meraki network.
    """
    return client.appliance.getNetworkApplianceUplinksStatuses(network_id)

def list_firewall_events(network_id):
    """
    Fetch the firewall events for a given Meraki network.
    """
    import requests

    url = "https://api.meraki.com/api/v1/organizations/{organizationId}/wireless/ssids/firewall/isolation/allowlist/entries"

    payload = None

    headers = {
        "Authorization": "Bearer 75dd5334bef4d2bc96f26138c163c0a3fa0b5ca6",
        "Accept": "application/json"
    }

    response = requests.request('GET', url, headers=headers, data=payload)
    if not response:
        return "No firewall events found for this network."

    return response

    # return client.events.getNetworkEvents(network_id, productType='appliance')

def list_clients(network_id):
    """
    Fetch the list of clients for a given Meraki network.
    """
    return client.networks.getNetworkClients(network_id)

def list_switches(network_id):
    """
    Fetch the list of switches for a given Meraki network.
    """
    devices = list_devices(network_id)
    return [d for d in devices if d.get("model", "").startswith("MS")]

def list_access_points(network_id):
    """
    Fetch the list of access points for a given Meraki network.
    """
    devices = list_devices(network_id)
    return [d for d in devices if d["model"].startswith("MR")]

def list_devices(network_id):
    """
    Fetch the list of devices for a given Meraki network.
    """
    return client.networks.getNetworkDevices(network_id)

def list_ssids(network_id):
    """
    Fetch the list of SSIDs for a given Meraki network.
    """
    return client.wireless.getNetworkWirelessSsids(network_id)

def get_vpn_status(dashboard, network_id):
    """
    Fetch VPN status of the given Meraki network.
    """
    try:
        status = dashboard.appliance.getNetworkApplianceVpnStatus(network_id)

        if not status:
            return "⚠️ No VPN status data available."

        output = {
            "Device Status": status.get("deviceStatus", "Unknown"),
            "Meraki VPN Peers": [
                {
                    "Peer Network ID": peer.get("networkId"),
                    "Status": peer.get("status"),
                    "Reachability": peer.get("reachability"),
                    "Latency (ms)": peer.get("latencyMs")
                }
                for peer in status.get("merakiVpnPeers", [])
            ],
            "Non-Meraki VPN Peers": [
                {
                    "Public IP": peer.get("publicIp"),
                    "Status": peer.get("status"),
                    "Reachability": peer.get("reachability")
                }
                for peer in status.get("nonMerakiVpnPeers", [])
            ]
        }

        return output

    except Exception as e:
        return f"❌ Error fetching VPN status: {str(e)}"

# meraki_tools.py

# --- Network Management ---
def create_network(org_id, network_name, product_type='wireless'):
    """
    Create a new network within an organization.
    """
    network = client.organizations.createOrganizationNetwork(org_id, name=network_name, productTypes=product_type)
    return network

def update_network(network_id, name=None, type=None, tags=None):
    """
    Update network settings such as name, type, and tags.
    """
    data = {}
    if name:
        data['name'] = name
    if type:
        data['type'] = type
    if tags:
        data['tags'] = tags
    updated_network = client.networks.updateNetwork(network_id, **data)
    return updated_network

# --- VLAN Management ---
def create_vlan(network_id, vlan_id, name, subnet, appliance_ip):
    """
    Create a new VLAN in the specified network.
    """
    vlan = client.appliance.createNetworkApplianceVlan(network_id, id=vlan_id, name=name, subnet=subnet, applianceIp=appliance_ip)
    return vlan

def update_vlan(network_id, vlan_id, name=None, subnet=None, appliance_ip=None):
    """
    Update VLAN settings.
    """
    data = {}
    if name:
        data['name'] = name
    if subnet:
        data['subnet'] = subnet
    if appliance_ip:
        data['applianceIp'] = appliance_ip
    updated_vlan = client.appliance.updateNetworkApplianceVlan(network_id, vlan_id, **data)
    return updated_vlan

# --- SSID Management ---
def create_ssid(network_id, ssid_number, name, enabled=True, security='wpa', password=None):
    """
    Create a new SSID (wireless network) in the specified network.
    """
    ssid = client.wireless.createNetworkWirelessSsid(network_id, number=ssid_number, name=name, enabled=enabled, security=security, password=password)
    return ssid

def update_ssid(network_id, ssid_number, name=None, enabled=None, security=None, password=None):
    """
    Update SSID settings.
    """
    data = {}
    if name:
        data['name'] = name
    if enabled is not None:
        data['enabled'] = enabled
    if security:
        data['security'] = security
    if password:
        data['password'] = password
    updated_ssid = client.wireless.updateNetworkWirelessSsid(network_id, ssid_number, **data)
    return updated_ssid

# --- Device Management ---
def reboot_device(network_id, serial):
    """
    Reboot a device in the network.
    """
    result = client.networks.rebootNetworkDevice(network_id, serial)
    return result

def claim_device(network_id, serial):
    """
    Claim a device to the network.
    """
    result = client.networks.claimNetworkDevice(network_id, serial)
    return result

# --- Firewall Management ---
def create_firewall_rule(network_id, policy, protocol, src_port, dest_port, src_ip, dest_ip):
    """
    Create a firewall rule for the specified network.
    """
    rule = client.appliance.createNetworkApplianceFirewallL3FirewallRule(network_id, policy=policy, protocol=protocol, srcPort=src_port, destPort=dest_port, srcCidr=src_ip, destCidr=dest_ip)
    return rule

def update_firewall_rule(network_id, rule_id, policy=None, protocol=None, src_port=None, dest_port=None, src_ip=None, dest_ip=None):
    """
    Update an existing firewall rule.
    """
    data = {}
    if policy:
        data['policy'] = policy
    if protocol:
        data['protocol'] = protocol
    if src_port:
        data['srcPort'] = src_port
    if dest_port:
        data['destPort'] = dest_port
    if src_ip:
        data['srcCidr'] = src_ip
    if dest_ip:
        data['destCidr'] = dest_ip
    updated_rule = client.appliance.updateNetworkApplianceFirewallL3FirewallRule(network_id, rule_id, **data)
    return updated_rule
