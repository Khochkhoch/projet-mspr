import subprocess
import re
import json
import datetime


def scan_network(network_range):
    print(f"[+] Scan du réseau : {network_range}")

    output_file = "scan_output.txt"

    subprocess.run(
        ["nmap", "-sS", "-sV", "-p", "22,135,445,3389", network_range, "-oN", output_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    machines = []
    current_machine = None

    with open(output_file, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:

            ip_match = re.search(r"Nmap scan report for ([0-9\.]+)", line)
            if ip_match:
                current_machine = {
                    "ip": ip_match.group(1),
                    "os": "Inconnu",
                    "version": "Inconnue"
                }
                machines.append(current_machine)

            if "Microsoft" in line:
                current_machine["os"] = "Windows Server"
                if "2019" in line:
                    current_machine["version"] = "2019"
                elif "2022" in line:
                    current_machine["version"] = "2022"
                elif "2016" in line:
                    current_machine["version"] = "2016"

            if "OpenSSH" in line or "Ubuntu" in line:
                current_machine["os"] = "Linux"
                ubuntu_match = re.search(r"Ubuntu\s+([\d\.]+)", line)
                if ubuntu_match:
                    current_machine["version"] = ubuntu_match.group(1)

    return machines


if __name__ == "__main__":
    network = input("Entrez la plage réseau (ex: 192.168.121.0/24) : ")
    result = scan_network(network)

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "network": network,
        "machines": result
    }

    print(json.dumps(report, indent=4, ensure_ascii=False))
