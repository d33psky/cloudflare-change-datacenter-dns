cloudflare-change-datacenter-dns
================================

Introduction
------------

A script to update a selection of DNS zone records at CloudFlare. Intended to
be used when failing over to another datacenter where multiple services are
hosted on 1 IP address and no other changes to these records are wanted and all
other records are to remain untouched.

This work is based on [thatjpk/cloudflare-ddns](https://github.com/thatjpk/cloudflare-ddns). Thanks !

Dependencies
------------

You'll need a python interpreter and the following libraries:

 - [PyYAML](https://bitbucket.org/xi/pyyaml) (`pip install pyyaml`)
 - [Requests](http://docs.python-requests.org/en/latest/) (`pip install requests`)

Usage
-----

First copy `config.yaml.template` file to `config.yaml` and fill in your
CloudFlare email address and API key. Then run the script as follows :

    cloudflare-change-datacenter-dns.py [-h] [--debug] [--config CONFIG] [--zone ZONE] [--records RECORDS] [--newip NEWIP]

    optional arguments:
      -h, --help         show this help message and exit
      --debug            Enable debug level logging (default: info level)
      --config CONFIG    Yaml config file (default: config.yaml)
      --zone ZONE        DNS zone (example: somezone.org)
      --records RECORDS  DNS zone records to change (example: www03,somezone.org,acceptance)
      --newip NEWIP      New IP address (example: 127.0.0.1)

Here is an example run where video was already set to the new intended IP
address but dev not yet. The script skips all other records it finds in the zone :

    ./cloudflare-change-datacenter-dns.py --zone somedomain.org --records video,dev --newip 127.0.0.1

    2016-03-09 13:45:50,336 INFO Work on domain somedomain.org
    2016-03-09 13:45:50,336 INFO Work on records ['video', 'dev']
    2016-03-09 13:45:50,337 INFO New IP 127.0.0.1
    2016-03-09 13:45:50,345 INFO Starting new HTTPS connection (1): www.cloudflare.com
    2016-03-09 13:45:51,020 INFO Skip somedomain.org
    2016-03-09 13:45:51,020 INFO Skip acceptance
    2016-03-09 13:45:51,020 INFO Skip api
    2016-03-09 13:45:51,020 INFO Skip developers
    2016-03-09 13:45:51,020 INFO Change dev.somedomain.org to 127.0.0.1
    2016-03-09 13:45:51,021 INFO Starting new HTTPS connection (1): www.cloudflare.com
    2016-03-09 13:45:51,276 INFO Updated dev.somedomain.org to 127.0.0.1
    2016-03-09 13:45:51,278 INFO Skip images
    2016-03-09 13:45:51,278 INFO Skip origin
    2016-03-09 13:45:51,278 INFO Skip static1
    2016-03-09 13:45:51,278 INFO Keep video.somedomain.org unchanged with 127.0.0.1
    2016-03-09 13:45:51,278 INFO Skip www

Credits and Thanks
------------------

 - [CloudFlare](https://www.cloudflare.com/) for hosting DNS and having an [API](http://www.cloudflare.com/docs/client-api.html).
 - [thatjpk/cloudflare-ddns](https://github.com/thatjpk/cloudflare-ddns) for
   writing cloudflare-ddns

