#!/usr/bin/python3
import sys
import os
import base64
import json
import requests
import jwt
import logging
from logging.handlers import RotatingFileHandler  # Import RotatingFileHandler
from typing import Any, Dict, Optional

# Utility function for parameter parsing
def parse_params(params: list[str], name: str, default: str = "") -> str:
    return next((p.split('=')[1] for p in params if p.startswith(f"{name}=")), default)

# Fetch parameters from sys.argv
user = parse_params(sys.argv, 'user')
password = parse_params(sys.argv, 'password')
id = parse_params(sys.argv, 'id')
action = parse_params(sys.argv, 'action')
pssh = parse_params(sys.argv, 'pssh')

# Dynamically set the log filename based on the 'id' parameter

log_filename = f"{id}.log" if id else f"default.log"
# Setup logging to a dynamically named file
logging.basicConfig(
    level=logging.DEBUG,  # Capture all log messages
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(log_filename, maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)

# Constants for URLs
CHANNELS_API_URL = 'https://cbd46b77.cdn.cms.movetv.com/cms/publish3/domain/summary/ums/1.json'
PLAYBACK_API_URL = 'https://cbd46b77.cdn.cms.movetv.com/playermetadata/sling/v1/api/channels/{id}/schedule/now/playback_info.qvt'

# API headers
api_headers = {"ccdodlad-api-key": "bluechip_studio_696223755_api_and_extension_unlimited"}

# CDM process
def do_cdm(pssh: str, id: str) -> Optional[Dict[str, Any]]:
    try:
        # Use f-string for URL formatting
        sling_key_api = f"id={id}&pssh={pssh}"
        
        # Make the request
        response = requests.get(sling_key_api)
        response.raise_for_status()  # Raise an error for bad HTTP status codes

        try:
            key_data = response.json()  # Attempt to parse JSON
        except ValueError:
            logging.error(f"Invalid JSON response: {response.content}")
            return None
        
        # Check if 'status' is present in the response and handle 'false' status
        if key_data.get('status') == 'false':
            logging.error("Failed to Grab Key: Status is false")
            return None
        
        # Return the 'keys' field from the response if present
        keys = key_data.get('keys', None)
        if keys is None or not keys:  # Check if keys is None or an empty list
            logging.error("Keys are empty or not present")
            return None
            
        list = "\n".join(keys)
        
        print(list)

    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in do_cdm: {e}")

    return None

# Function to process channels and fetch playback manifest
def process_channel(id: str) -> Optional[str]:
    try:
        response = requests.get(PLAYBACK_API_URL.format(id=id))
        response.raise_for_status()

        data = response.json()
        dash_manifest_url = data.get('playback_info', {}).get('dash_manifest_url')

        if dash_manifest_url:
            return dash_manifest_url
        else:
            logging.error("dash_manifest_url not found in the response")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"API request error: {e}")
    except KeyError as e:
        logging.error(f"KeyError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None

# Function to handle the channels action
def handle_channels() -> None:
    output = {"Channels": []}

    try:
        response = requests.get(CHANNELS_API_URL).json()
        channels = response.get('channels', [])

        for channel_data in channels:
            channelid = str(channel_data['channel_guid'])

            channel_info = {
                "Name": channel_data['metadata']['channel_name'],
                "Mode": "live",
                "SessionManifest": True,
                "ManifestScript": f'id={channelid}',
                "CdmType": "widevine",
                "UseCdm": True,
                "Cdm": f'id={channelid}',
                "Video": "best",
                "OnDemand": True,
                "SpeedUp": True,
                "CdmMode": "external"
            }

            output['Channels'].append(channel_info)

        print(json.dumps(output, indent=2))

    except (KeyError, ValueError, requests.RequestException) as e:
        logging.error(f"Error while handling channels: {e}")

# Function to handle the manifest action
def handle_manifest(id: str) -> None:
    try:
        manifest_url = process_channel(id)
        output = {
            "ManifestUrl": manifest_url,
            "Headers": {
                "Manifest": {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
                },
                "Media": {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
                }
            },
            "Heartbeat": {
                "Url": '',
                "Params": '',
                "PeriodMs": 5 * 60 * 1000
            }
        }
        print(json.dumps(output, indent=4))

    except Exception as e:
        logging.error(f"Error while handling manifest: {e}")


def fix_base64(encoded_str):
    # Add necessary padding if needed
    missing_padding = len(encoded_str) % 4
    if missing_padding:
        encoded_str += '=' * (4 - missing_padding)  # Add '=' padding
    
    return encoded_str
    
# Main control flow
logging.error("Running with action : " + action)
if action == "cdm":
    logging.error("Requesting keys")
    do_cdm(pssh, id)

elif action == "channels":
    logging.error("Reloading channels")
    handle_channels()

elif action == "manifest":
    logging.error("Requesting manifest")
    handle_manifest(id)
