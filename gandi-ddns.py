#!/usr/bin/env python3

import requests
import json
import socket
import sys
import os

def modify_record_ip(ip_add, config):
    """ Change the zone record to the new IP """

    headers = {
        'authorization': 'Apikey {}'.format(config["apikey"]),
        'content-type': "application/json"
        }

    # Delete A record
    url = "https://api.gandi.net/v5/livedns/domains/{}/records/{}/A".format(config["domain"], config["a_name"])
    response = requests.request("DELETE", url, headers=headers)

    # Create A record
    url = "https://api.gandi.net/v5/livedns/domains/{}/records".format(config["domain"])
    payload = "{{\"rrset_name\":\"{}\",\"rrset_type\":\"A\",\"rrset_values\":[\"{}\"],\"rrset_ttl\":{}}}".format(config["a_name"], ip_add, config["ttl"])
    response = requests.request("POST", url, data=payload, headers=headers)


def get_record_ip(config):
    """Get the current IP from the A record in the DNS zone """

    headers = {'authorization': 'Apikey {}'.format(config["apikey"])}

    # Get Records
    url = "https://api.gandi.net/v5/livedns/domains/{}/records".format(config["domain"])
    response = requests.request("GET", url, headers=headers)
    records = json.loads(response.text)

    for record in records:
        if record['rrset_name'] == config["a_name"] and record['rrset_type'] == 'A':
            return record['rrset_values'][0]
    # Throw error


def hostname_to_ip():
    """ Get external IP """

    host_ip = socket.gethostbyname(config["host"])
    if host_ip == '127.0.0.1':
        try:
            host_ip = requests.get('https://api.ipify.org').text
        except Exception:
            print('Unable to external IP address.')
            sys.exit(2)

    return host_ip


def read_config(config_path):
    """ Open the configuration file or create it if it doesn't exists """

    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write(default_config)
        return None
    else:
        with open(config_path) as json_file:
            return json.load(json_file)


if __name__ == "__main__":
    default_config = """{
        "apikey":"<CHANGE ME>",
        "domain":"<CHANGE ME>",
        "a_name": "@",
        "ttl":900,
        "host": "localhost"
    }"""

    config_path = os.path.dirname(os.path.realpath(__file__)) + "/config.json"

    config = read_config(config_path)
    if not config:
        sys.exit("please fill in the 'config.txt' file")

    public_ip = hostname_to_ip()
    record_ip = get_record_ip(config)

    if record_ip != public_ip:
        print('DNS Mistmatch detected: A-record: ', record_ip, ' WAN IP: ', public_ip)
        modify_record_ip(public_ip, config)
        print('DNS A record update complete - set to ', public_ip)
    else:
        print("No DNS Mistmatch detected.")
