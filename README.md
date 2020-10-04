# ddns-gandi

## About

This is a simple script to update the DNS A record of your gandi.net domain dynamically using Gandi's [LiveDNS API](https://api.gandi.net/docs/livedns/). This was written specifically for the Raspberry Pi, but it could be used anywhere. It is very similar to no-ip and dyndns, where you can have a domain on the internet which points at your computer's IP address, except it is free (once you have registered the domain) and does not suffer from any forced refreshing etc.

This project is based originally on [matt1's excellent gandi-ddns script](https://github.com/matt1/gandi-ddns), however it has been rewritten to use Gandi's new v5 LiveDNS API, instead of the old XML-RPC API.

The major differences are:

* Uses the v5 LiveDNS API and therefore requires a LiveDNS API key.
* Compatible with Python 3.3+, as Python 2.7 will be officially retired in 2020.
* Dependent on the [Requests](http://docs.python-requests.org/) library.

Every time the script runs it will get the current domain config from gandi.net's API and look for the IP in the A record for the domain (the default name for the record is '@' but you can change that if you want to). It will then get your current external IP from a public "what is my ip" site. Once it has both IPs it will compare what is in the DNS config vs what your IP is, and update the DNS config for the domain as appropriate so that it resolves to your current IP address.

The configuration is stored in the script directory under the file `config.json`. The syntax is the standard JSON file, and the format is the following:

    {
        "apikey":"<CHANGE ME>",
        "domain":"<CHANGE ME>",
        "a_name": "@", "ttl":900,
        "host": "localhost"
    }

* Do not forget to replace the values marked with `<CHANGE ME>` with your 24-character API key and domain.
* `host` is either `localhost` in which case the script will fetch the current external address, or any other public name. Using another ddns account will allow you to sync it with Gandi (useful when you are not running on the same IP as the one you want to update).

## Setup

Make sure you have Python 3.3+ installed, as well as Requests. If you are running a Linux distribution, Requests can likely be installed from your distribution's repositories.

On Debian-based distributions (Ubuntu, Mint, etc):

    apt install python3-requests

On Arch-based distributions:

    pacman -S python-requests

Then, simply download/clone the contents of this repository to a locationof your choice.

You should then run gandi-ddns.py, which generate the config.json file, and modify the values for `domain` and `apikey`. If you want to edit the DNS record for a subdomain, you should also edit the `a_name` entry.

## Usage

You will need to make sure that your domain is registered on gandi.net, and that you are using the gandi.net DNS servers. You'll also need to register for the API to get a key.

Once you have the production key and your domain on gandi.net, edit the 'apikey' and 'domain' variables in the script appropriately.

Once you have done this you can then set up the script to run via crontab:

    sudo crontab -e

Then add the following line so that the script is run after a reboot:

    @reboot python /home/pi/gandi-ddns.py &

And then to make it check for a new IP every 15 minutes you can add:

    */15 * * * * python /home/pi/gandi-ddns.py

You can then start and/or reload the cron config:

    sudo /etc/init.d/cron start sudo /etc/init.d/cron reload
