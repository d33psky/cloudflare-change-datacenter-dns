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

CLOUDFLARE_URL = 'https://api.cloudflare.com/client/v4'
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

    # [1] get zone identifier. https://api.cloudflare.com/#zone-list-zones
    cf_headers = {
        'X-Auth-Email': cf_email,
        'X-Auth-Key': cf_key,
        'Content-Type': 'application/json',
        }
    cf_params = {
        'name': zone,
        }
    cf_response = requests.get(CLOUDFLARE_URL + '/zones', headers=cf_headers, params=cf_params)
    if cf_response.status_code < 200 or cf_response.status_code > 299:
        msg = "CloudFlare returned an unexpected status code: {}".format(cf_response.status_code)
        logging.error(msg)
        exit(1)
    response = json.loads(cf_response.text)
    #logging.debug('response=[%s]', response)
    zone_id = response["result"][0]["id"]
    logging.debug('response[result][0][id]=[%s]', zone_id)

    # [2] list records. https://api.cloudflare.com/#dns-records-for-a-zone-list-dns-records
    cf_params = {
        'type': RECORD_TYPE,
        'page': 1,
        'per_page': 100,
        }
    cf_response = requests.get(CLOUDFLARE_URL + "/zones/" + zone_id + "/dns_records", headers=cf_headers, params=cf_params)
    if cf_response.status_code < 200 or cf_response.status_code > 299:
        msg = "CloudFlare returned an unexpected status code: {}".format(cf_response.status_code)
        logging.error(msg)
        exit(1)
    response = json.loads(cf_response.text)
    #logging.debug('response=[%s]', response)
    if response["result"] == "error":
        logging.error("error: %s", response["msg"])
        exit(1)

    # [3] update ones that need to.
    for record in response["result"]:
        #logging.debug('record=%s', record)
        record_id = record['id']
        shortname = record["name"].replace( str('.'+zone) , '')
        #logging.debug('recordname [%s] zone [%s] shortname [%s]', record["name"], zone, shortname)
        if (record["type"] == RECORD_TYPE) :
            #logging.debug('Consider %s', record["name"])
            if ( shortname in records ):
                if record["content"] == newip:
                    logging.info('Keep %s unchanged with %s', record["name"], newip)
                else:
                    logging.info('Change %s to %s', record["name"], newip)
                    logging.debug('record %s', record)
                    repoint(cf_headers, record, newip)
            else:
                logging.info('Skip %s %s %s ttl=%s accellerated=%s', shortname, record["type"], record["content"], record["ttl"], record["proxied"])

# https://api.cloudflare.com/#dns-records-for-a-zone-update-dns-record
def repoint(cf_headers, record, newip):
    cf_json = {
        'type': record["type"],
        'name': record["name"],
        'content': newip,
        'ttl': record["ttl"],
        'proxied': record["proxied"],
        }
    cf_response = requests.put(CLOUDFLARE_URL + "/zones/" + record["zone_id"] + "/dns_records/" + record["id"], headers=cf_headers, json=cf_json)
    logging.debug('cf_json=[%s]', cf_json)
    logging.debug('response=[%s]', cf_response)
    if cf_response.status_code < 200 or cf_response.status_code > 299:
        msg = "CloudFlare returned an unexpected status code: {}".format(cf_response.status_code)
        logging.error(msg)
        raise Exception(msg)
    response = json.loads(cf_response.text)

    if response["errors"]:
        msg = "Updating record failed with the result '{}'".format(response)
        logging.error(msg)
        raise Exception(msg)
    else:
        logging.info('Updated %s to %s', record["name"], newip)

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

