#!/usr/bin/env python
# Script to update a selection of CloudFlare DNS records.
# based on: CloudFlare DDNS script. by https://github.com/thatjpk/cloudflare-ddns
#
# usage:
#   cloudflare-change-datacenter-dns.py [config] zone records old_ip new_ip
#
# See README for details
#

import requests
import json
import time
import yaml
import os
import sys
import logging
from subprocess import Popen, PIPE

CLOUDFLARE_URL = 'https://www.cloudflare.com/api_json.html'
RECORD_TYPE = 'A'


def main(configfile, zone, records, newip):

    logging.debug('configfile %s', configfile)
    logging.info('Work on domain %s', zone)
    logging.info('Work on records %s', records)
    logging.info('New IP %s', newip)

    if not os.path.isfile(configfile):
        logging.critical("Configuration file %s not found.", configfile)
        exit(1)

    with open(configfile, 'r') as f:
        config = yaml.load(f)

    cf_key = config.get('cf_key')
    logging.debug('cf_key=%s', cf_key)

    cf_email = config.get('cf_email')
    logging.debug('cf_email=%s', cf_email)

    cf_params = {
        'a': 'rec_load_all',
        'tkn': cf_key,
        'email': cf_email,
        'z': zone,
        'o': 0
        }
    seenAllPages = False
    while not seenAllPages:
        cf_response = requests.get(CLOUDFLARE_URL, params=cf_params)
        if cf_response.status_code < 200 or cf_response.status_code > 299:
            msg = "CloudFlare returned an unexpected status code: {}".format(cf_response.status_code)
            logging.error(msg)
            exit(1)

        response = json.loads(cf_response.text)
        #logging.debug('response=[%s]', response)
        if response["result"] == "error":
            logging.error("error: %s", response["msg"])
            exit(1)

        for record in response["response"]["recs"]["objs"]:
            #logging.debug('record=%s', record)
            shortname = record["name"].replace( str('.'+zone) , '')
            #logging.debug('recordname [%s] zone [%s] shortname [%s]', record["name"], zone, shortname)

            if (record["type"] == RECORD_TYPE) :
                #logging.debug('Consider %s', record["name"])
                if ( shortname in records ):
                    if record["content"] == newip:
                        logging.info('Keep %s unchanged with %s', record["name"], newip)
                    else:
                        logging.info('Change %s to %s', record["name"], newip)
                        repoint(cf_key, cf_email, record, newip)
                else:
                    logging.info('Skip %s', shortname)

        if response["response"]["recs"]["has_more"]:
            logging.debug('We have not seen all pages yet, set a new start point')
            cf_params["o"] = response["response"]["recs"]["count"] 
        else:
            seenAllPages = True

# https://api.cloudflare.com/#dns-records-for-a-zone-dns-record-details
def repoint(cf_key, cf_email, record, newip):
    #logging.debug('record = %s', record)
    cf_params = {
        'a': 'rec_edit',
        'tkn': cf_key,
        'email': cf_email,
        'id': record["rec_id"],
        'z': record["zone_name"],
        'type': record["type"],
        'ttl': record["ttl"],
        'name': record["name"],
        'content': newip,
        }
    cf_response = requests.get(CLOUDFLARE_URL, params=cf_params)
    if cf_response.status_code < 200 or cf_response.status_code > 299:
        msg = "CloudFlare returned an unexpected status code: {}".format(response.status_code)
        logging.error(msg)
        raise Exception(msg)
    response = json.loads(cf_response.text)

    if response["result"] == "success":
        logging.info('Updated %s to %s', record["name"], newip)
    else:
        msg = "Updating record failed with the result '{}'".format(response["result"])
        logging.error(msg)
        raise Exception(msg)

    return

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug level logging (default: info level)")
    parser.add_argument("--config", default='config.yaml', type=str, dest="config", help="Yaml config file (default: config.yaml)")
    parser.add_argument("--zone", default='somezone.org', type=str, dest="zone", help="DNS zone (example: somezone.org)")
    parser.add_argument("--records", default='www03,somezone.org,acceptance', type=str, dest="records", help="DNS zone records to change (example: www03,somezone.org,acceptance)")
    parser.add_argument("--newip", default='127.0.0.1', type=str, dest="newip", help="New IP address (example: 127.0.0.1)")
    args = parser.parse_args()

    if args.debug:
        loglevel=logging.DEBUG
    else: 
        loglevel=logging.INFO
    logging.basicConfig(stream=sys.stderr, level=loglevel, format='%(asctime)s %(levelname)s %(message)s')

    main(args.config, args.zone, args.records.split(","), args.newip)

