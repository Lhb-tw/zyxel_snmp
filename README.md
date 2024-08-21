# Zyxel Enterprise Access Point SNMP Integration

## Overview
Welcome to the Zyxel Enterprise Access Point SNMP Integration! This custom Home Assistant component allows you to monitor and manage your Zyxel enterprise-grade access points using the Simple Network Management Protocol (SNMP). With this integration, you can easily keep track of your network devices, including their uptime, CPU usage, memory status, and more, all within the Home Assistant interface.

## Features
Real-Time Monitoring: Get instant access to crucial metrics such as system uptime, CPU usage, and memory usage.
Device Grouping: Automatically group SNMP entities under a single device, making it easy to manage multiple access points.
Custom Icons: Visualize your access point data with relevant and intuitive icons based on the data type.
Flexible Update Intervals: Customize the frequency of SNMP data updates according to your needs.
Newbie-Friendly Configuration: A simple setup process that guides you through the configuration with helpful descriptions and validation.
## Supported Zyxel Devices
Before proceeding, please ensure that your Zyxel Enterprise Access Point supports SNMP. This integration is designed specifically for Zyxel’s enterprise-grade devices, which include but are not limited to:

Zyxel NWA1123ACv3  
Zyxel WAC500  
Zyxel WAC500h  
Zyxel NWA110AX  
Zyxel Nwa210AX  
Zyxel WAX510D  
Zyxel WAX610D  
Zyxel WAX630S  
Zyxel WAX650S  
Zyxel NWA220AX-6E  
Zyxel NWA620D-6E  
Zyxel WAX640S-6E  
Zyxel NWA130BE  
Zyxel WBE660S


If your device is not listed here, please refer to the device's manual or contact Zyxel support to confirm SNMP compatibility.

### Ensure you have installed pysnmp, voluptuous on your Home Assistant  



\```
pip install pysnmp
pip install voluptuous
\```



## Installation & Configuration
### Step 1: Install the Integration
Download the Repository: Clone or download the repository from GitHub.
Copy the Files: Copy the zyxel_snmp folder into your Home Assistant’s custom_components directory.
Restart Home Assistant: Restart your Home Assistant instance to load the custom component.
### Step 2: Add the Integration via Home Assistant UI
Navigate to Integrations: In Home Assistant, go to Settings > Devices & Services > + Add Integration.

Search for 'ZYXEL SNMP': Select the "ZYXEL SNMP" integration from the list.

Configure the Integration:

Device Name: Enter a friendly name for your Zyxel access point.
IP Address: Input the IP address of your access point (e.g., 192.168.1.1).
Community String: Provide the SNMP community string. The default is usually 'public'.
Update Interval: Set how frequently the SNMP data should be updated (between 5 to 300 seconds).
Validate & Save: The integration will validate the inputs and, if successful, create the entities for your device.

### Step 3: Monitor Your Devices
After the configuration, your Zyxel Access Points will be visible in the Home Assistant dashboard. You can now monitor the following metrics:

System Uptime: Tracks the total uptime of your access point.
CPU Usage: Displays the current CPU utilization percentage.
Memory Usage: Shows the current memory usage percentage.
Network Interface Status: Monitor the status of 2.4GHz and 5GHz network interfaces.
Troubleshooting
If you encounter any issues during setup or monitoring, ensure that:

Your access point’s SNMP service is enabled.
The correct IP address and community string are used.
Your device is reachable over the network from your Home Assistant instance.
For detailed troubleshooting, please refer to the Zyxel Access Point manual or the Home Assistant community forums.

## Contributing
We welcome contributions to enhance this integration further.
If you have any feature requests or bug reports, feel free to open an issue or submit a pull request.
Ensure that your code follows the contribution guidelines provided in the repository.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
Special thanks to the Home Assistant community and Zyxel for providing extensive documentation and support for SNMP.
Created by Lhb
