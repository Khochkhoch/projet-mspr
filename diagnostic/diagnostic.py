import os
import platform
import dns.resolver
import mysql.connector
import psutil
import time
from datetime import datetime, timedelta
import json
import logging



logging.basicConfig(
    filename ='diagnostic.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def save_json(filename , data):
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    with open(filename , "w") as f:
        json.dump(data , f ,indent=4)
    print(f"JSON sauvgardé dans {filename}")


def ping(ip):
    # Détecter si on est sous Windows ou Linux
    param = "-n" if platform.system().lower() == "windows" else "-c"
    #print(f"{param}")
    # Construire la commande ping
    command = f"ping {param} 1 {ip}"

    print(f"Test de ping vers {ip}...")
    #os.system() → exécute la commande
    response = os.system(command)

    success = (response == 0)

    logging.info(f"Ping vers {ip} -> {'OK' if success else 'ECHEC'}")

    # Génération JSON
    data = {
        "test" : "ping",
        "ip" : ip,
        "status" : "success" if success else "failed",
        "return_code": 0 if success else 1
    }
    save_json("ping_result_json" , data)
    return success


def dns_lookup(domain):

    print(f"Test DNS pour {domain}...")

    try:
        result = dns.resolver.resolve(domain , 'A')
        #print(f"voila result => =>{result}")

        for ip in result:
            print(f"Résolution Ok ✔ : {domain} => {ip}")
            successdns = True
            logging.info(f"DNS {domain} → {'OK' if successdns else 'ECHEC'}")
            # Génération JSON
            data = {
                "test": "dns",
                "domain": domain,
                "status": "success" if successdns else "failed",
                "return_code": 0 if successdns else 1
            }
            save_json("dns_result_json", data)
        return True
    except Exception as e:
        print(f"Erreur DNS ✖ : {e}")
        successdns = False
        logging.info(f"DNS {domain} → {'OK' if successdns else 'ECHEC'}")
        return False

from mysql.connector import Error

def test_mysql_connection(host , user , password):

    print(f"Test de connexion MySQL vers {host}...")

    try:
       # Tentative de connexion
       connection = mysql.connector.connect(
           host = host,
           user = user,
           password = password
       )
       if connection.is_connected():
           print("Connexion Mysql réussie ✔")
           connection.close()
           successmysql = True
           logging.info(f"MySQL {host} → {'OK' if successmysql else 'ECHEC'}")
           data = {
               "host": "host",
               "domain": host,
               "status": "success" if successmysql else "failed",
               "return_code": 0 if successmysql else 1
           }
           save_json("mysql_result_json", data)
           return True

    except Error as er:
        print(f"Erreur Mysql ✖ : {er}")
        successmysql = False
        logging.info(f"MySQL {host} → {'OK' if successmysql else 'ECHEC'}")
        return False


def get_system_info():

    print("Récupération des informations système...\n")

    # CPU %
    cpu = psutil.cpu_percent(interval = 1)

    # RAM %
    ram = psutil.virtual_memory().percent

    # Disque %
    disk = psutil.disk_usage('/').percent

    # Uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    uptime = str(timedelta(seconds=int(uptime_seconds)))


    print(f"CPU utilisé : {cpu}%")
    print(f"RAM utilisé : {ram}%")
    print(f"Espace disque utilisé : {disk}%")
    print(f"Uptime : {uptime}")

    logging.info("Récupération infos système OK")

    # Données JSON
    data = {
        "test": "system_info",
        "cpu_percent": cpu,
        "ram_percent": ram,
        "disk_percent": disk,
        "uptime": uptime,
        "status": "success",
        "return_code": 0
    }

    # Sauvegarde JSON
    save_json("system_info_result.json", data)

    return data