import requests, json
import sys
import time
from pprint import pprint

try:
    API_KEY = sys.argv[1]
    NETWORK_ID = sys.argv[2]
except Exception as e:
    print(e)
    sys.exit()

meraki_header = {"Content-type": "application/json",
          "Accept": "application/json",
          "X-Cisco-Meraki-API-Key": API_KEY}

try:
    url = f"https://api.meraki.com/api/v1/networks/{NETWORK_ID}/devices"
    network_devices_request = requests.get(url, headers=meraki_header, timeout=2)
    
    if network_devices_request.status_code == 200:
        network_devices = network_devices_request.json()
    
    elif network_devices_request.status_code == 429:
        time.sleep(int(network_devices_request.headers.get('Retry-After', 2)))
        network_devices = requests.get(url, headers=meraki_header, timeout=2).json()
    
    else:
        print('Error occured while making call for network devices.')
        print(url)
        print(network_devices_request.status_code)
        sys.exit()

except Exception as e:
    print('Error occured while making call for network devices.')
    print(e)
    sys.exit()

for network_device in network_devices:
    model = network_device.get('model')
    if 'MR' in model:
        serial = network_device.get('serial')
        if network_device.get('name'):
            name = network_device.get('name')
        else:
            name = serial
        print(f"Restarting device {model} - {name}.")
        try:
            time.sleep(0.1)
            url = f"https://api.meraki.com/api/v1/devices/{serial}/reboot"
            request = requests.post(url, headers=meraki_header, timeout=2)
            if request.status_code == 202:
                response = request.json()
                if response.get('success') == True:
                    print(f"Restartet device {model} - {name} succesfully.")
            
            elif request.status_code == 429:
                time.sleep(int(request.headers.get('Retry-After', 2)))
                response = requests.get(url, headers=meraki_header, timeout=2).json()
                if response.get('success') == True:
                    print(f"Restartet device {model} - {name} succesfully.")

            else:
                print(f"Error occured while rebooting device {serial}")
                continue
            
        except Exception as e:
            print(f"Error occured while rebooting device {serial}")
            continue