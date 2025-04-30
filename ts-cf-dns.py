#!/usr/bin/env python3

import requests
import argparse

from config import settings

def get_tailscale_ips():
    url = f"https://api.tailscale.com/api/v2/tailnet/{settings.TAILSCALE_TAILNET}/devices"
    headers = {
        "Authorization": f"Basic {settings.TAILSCALE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    devices = response.json()["devices"]
    
    ipv6_addresses = {
        device["hostname"]: next((ip for ip in device["addresses"] if ":" in ip), None)
        for device in devices
    }
    return {host: ip for host, ip in ipv6_addresses.items() if ip is not None}

def update_cloudflare_dns(hostname, ipv6):
    dns_name = f"{hostname}.{settings.DNS_DOMAIN}"
    url = f"https://api.cloudflare.com/client/v4/zones/{settings.CLOUDFLARE_ZONE_ID}/dns_records"
    headers = {
        "Authorization": f"Bearer {settings.CLOUDFLARE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Check if the record already exists
    params = {"type": "AAAA", "name": dns_name}
    existing_records = requests.get(url, headers=headers, params=params).json()
    
    if existing_records["success"] and existing_records["result"]:
        record_id = existing_records["result"][0]["id"]
        update_url = f"{url}/{record_id}"
        data = {"type": "AAAA", "name": dns_name, "content": ipv6, "ttl": 1, "proxied": False}
        response = requests.put(update_url, headers=headers, json=data)
    else:
        data = {"type": "AAAA", "name": dns_name, "content": ipv6, "ttl": 1, "proxied": False}
        response = requests.post(url, headers=headers, json=data)
    
    return response.json()

def format_bind(ipv6_records):
    return "\n".join(f"{hostname}. IN AAAA {ipv6}" for hostname, ipv6 in ipv6_records.items())

def format_pihole(ipv6_records):
    return "\n".join(f"{ipv6} {hostname}.{settings.DNS_DOMAIN}" for hostname, ipv6 in ipv6_records.items())

def main():
    parser = argparse.ArgumentParser(description="Tailscale to Cloudflare DNS Updater")
    parser.add_argument("-c", action="store_true", help="Perform Cloudflare migration")
    parser.add_argument("-b", action="store_true", help="Format output as BIND zone file")
    parser.add_argument("-p", action="store_true", help="Format output as Pi-hole local.list format")
    parser.add_argument("-o", type=str, help="Output to a named file")
    args = parser.parse_args()
    
    ipv6_records = get_tailscale_ips()
    output = ""
    
    if args.c:
        for hostname, ipv6 in ipv6_records.items():
            result = update_cloudflare_dns(hostname, ipv6)
            print(f"Updated {hostname}: {result}")
    
    if args.b:
        output = format_bind(ipv6_records)
    elif args.p:
        output = format_pihole(ipv6_records)
    
    if args.o:
        with open(args.o, "w") as f:
            f.write(output)
    else:
        print(output)

if __name__ == "__main__":
    main()
