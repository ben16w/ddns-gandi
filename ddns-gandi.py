#!/usr/bin/env python3

import requests
from urllib.parse import urljoin
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

    try:
        # Delete A record
        endpoint = "domains/{}/records/{}/A".format(
            config["domain"], config["a_name"])
        url = urljoin(config['api'], endpoint)
        response = requests.request("DELETE", url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    try:
        # Create A record
        endpoint = "domains/{}/records".format(config["domain"])
        url = urljoin(config['api'], endpoint)
        payload = "{{\"rrset_name\":\"{}\",\"rrset_type\":\"A\",\"rrset_values\":[\"{}\"],\"rrset_ttl\":{}}}".format(
            config["a_name"], ip_add, config["ttl"])
        response = requests.request("POST", url, data=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_record_ip(config):
    """Get the current IP from the A record in the DNS zone """

    headers = {'authorization': 'Apikey {}'.format(config["apikey"])}

    try:
        # Get Record
        endpoint = "domains/{}/records/{}/A".format(
            config["domain"], config["a_name"])
        url = urljoin(config['api'], endpoint)
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()
        record = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        if e.response.status_code == 404:
            raise SystemExit("The A record in the DNS zone was not found.")
        else:
            raise SystemExit(e)

    return record['rrset_values'][0]


def hostname_to_ip():
    """ Get external IP """

    host_ip = socket.gethostbyname(config["host"])
    if host_ip == '127.0.0.1':
        try:
            host_ip = requests.get('https://api.ipify.org').text
        except Exception as e:
            raise SystemExit(e)

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
        "host": "localhost",
        "a_name": "@",
        "ttl":900,
        "api": "https://api.gandi.net/v5/livedns/"
    }"""

    config_path = os.path.dirname(os.path.realpath(__file__)) + "/config.json"

    config = read_config(config_path)
    if not config:
        sys.exit("Please fill in the 'config.json' file.")

    public_ip = hostname_to_ip()
    record_ip = get_record_ip(config)

    if record_ip != public_ip:
        print('DNS A-record mistmatch found: A-record: ',
              record_ip, ' WAN IP: ', public_ip)
        modify_record_ip(public_ip, config)
        print('DNS A record update complete. Now set to ', public_ip)
    else:
        print("No DNS Mistmatch detected, nothing to do. WAN IP: ", public_ip)
