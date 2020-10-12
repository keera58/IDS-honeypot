# IDS-honeypot

In this project, I setup my own Network Intrusion Detection System using a Raspberry Pi Honeypot.

1. The Raspberry Pi Honeypot acts as a decoy machine in the case the intruder enters the network.
2. The alert system gathers information about the attacker such as IP address, and uses OSINT tools to retrieve more details using web scraping
3. The inturder is then blocked from the network, and the logs and IP details are sent to the user via email.
