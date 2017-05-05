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

    2017-05-05 11:46:33,671 INFO Work on domain somedomain.org
    2017-05-05 11:46:33,671 INFO Work on records ['video', 'dev']
    2017-05-05 11:46:33,671 INFO New IP 127.0.0.1
    2017-05-05 11:46:33,674 INFO Starting new HTTPS connection (1): api.cloudflare.com
    2017-05-05 11:46:34,490 INFO Skip somedomain.org
    2017-05-05 11:46:34,491 INFO Skip acceptance
    2017-05-05 11:46:34,491 INFO Skip api
    2017-05-05 11:46:34,491 INFO Skip developers
    2017-05-05 11:46:34,491 INFO Change dev.somedomain.org to 127.0.0.1
    2017-05-05 11:46:34,492 INFO Starting new HTTPS connection (1): api.cloudflare.com
    2017-05-05 11:46:34,778 INFO Updated dev.somedomain.org to 127.0.0.1
    2017-05-05 11:46:34,778 INFO Skip images
    2017-05-05 11:46:34,778 INFO Skip origin
    2017-05-05 11:46:34,778 INFO Skip static1
    2017-05-05 11:46:34,778 INFO Skip storage
    2017-05-05 11:46:34,778 INFO Keep video.somedomain.org unchanged with 127.0.0.1
    2017-05-05 11:46:34,778 INFO Skip www


Credits and Thanks
------------------

 - [CloudFlare](https://www.cloudflare.com/) for hosting DNS and having an [API](https://api.cloudflare.com/).
 - [thatjpk/cloudflare-ddns](https://github.com/thatjpk/cloudflare-ddns) for writing cloudflare-ddns

