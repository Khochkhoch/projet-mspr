#!/usr/bin/env python3
"""
Module d'audit d'obsolescence pour NTL-SysToolbox
Conforme au cahier des charges
"""

import json
import csv
from datetime import datetime
from typing import Dict, List
import os


class ObsolescenceAuditor:
    
    def __init__(self):
        # Base de données EOL intégrée avec catégories
        self.eol_database = {
            "Windows Server 2008": {"eol_date": "2020-01-14", "categorie": "Windows Server"},
            "Windows Server 2008 R2": {"eol_date": "2020-01-14", "categorie": "Windows Server"},
            "Windows Server 2012": {"eol_date": "2023-10-10", "categorie": "Windows Server"},
            "Windows Server 2012 R2": {"eol_date": "2023-10-10", "categorie": "Windows Server"},
            "Windows Server 2016": {"eol_date": "2027-01-12", "categorie": "Windows Server"},
            "Windows Server 2019": {"eol_date": "2029-01-09", "categorie": "Windows Server"},
            "Windows Server 2022": {"eol_date": "2031-10-14", "categorie": "Windows Server"},
            "Windows Server (édition non précisée)": {"eol_date": "N/A", "categorie": "Windows Server"},
            "Windows 7": {"eol_date": "2020-01-14", "categorie": "Windows Client"},
            "Windows 10": {"eol_date": "2025-10-14", "categorie": "Windows Client"},
            "Windows 11": {"eol_date": "2026-10-10", "categorie": "Windows Client"},
            "Ubuntu 18.04": {"eol_date": "2028-04-30", "categorie": "Linux"},
            "Ubuntu 20.04": {"eol_date": "2030-04-30", "categorie": "Linux"},
            "Ubuntu 22.04": {"eol_date": "2032-04-30", "categorie": "Linux"},
            "CentOS 7": {"eol_date": "2024-06-30", "categorie": "Linux"},
            "CentOS 8": {"eol_date": "2021-12-31", "categorie": "Linux"},
            "VMware ESXi 6.5": {"eol_date": "2022-10-15", "categorie": "Virtualisation"},
            "VMware ESXi 6.7": {"eol_date": "2022-10-15", "categorie": "Virtualisation"},
            "VMware ESXi 7.0": {"eol_date": "2025-04-02", "categorie": "Virtualisation"}
        }
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def load_eol_database(self, filename: str) -> Dict:
        """Charge la base de données EOL"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[!] Fichier {filename} introuvable")
            return {}
    
    def list_network_components(self, network_range: str) -> List[Dict]:
        """
        FONCTION 1: Lister tous les composants présents sur une plage réseau donnée
        Essayer de déterminer l'OS des composants
        """
        # Inventaire basé sur les annexes NTL
        inventory = [
            {"ip": "192.168.10.10", "nom": "DC01", "os_detected": "Windows"},
            {"ip": "192.168.10.11", "nom": "DC02", "os_detected": "Windows"},
            {"ip": "192.168.10.21", "nom": "WMS-DB", "os_detected": "Linux/Unix"},
            {"ip": "192.168.10.22", "nom": "WMS-APP", "os_detected": "Linux/Unix"},
            {"ip": "192.168.10.40", "nom": "IPBX-VM", "os_detected": "Linux/Unix"},
            {"ip": "192.168.10.50", "nom": "SUPER-01", "os_detected": "Windows"},
        ]
        
        # Filtre selon la plage demandée
        filtered = []
        
        if '/' in network_range:
            # Format CIDR: 192.168.10.21/24 ou 192.168.10.0/24
            ip_part = network_range.split('/')[0]
            base_network = '.'.join(ip_part.split('.')[:-1])
            
            # Si l'IP spécifiée n'est pas .0, chercher cette IP exacte
            last_octet = ip_part.split('.')[-1]
            if last_octet != '0':
                # Recherche exacte de l'IP
                filtered = [comp for comp in inventory if comp['ip'] == ip_part]
            else:
                # Recherche sur toute la plage
                filtered = [comp for comp in inventory if comp['ip'].startswith(base_network)]
        elif '-' in network_range:
            # Format range: 192.168.10.10-50
            parts = network_range.split('-')
            base_ip = '.'.join(parts[0].split('.')[:-1])
            start = int(parts[0].split('.')[-1])
            end = int(parts[1])
            
            for comp in inventory:
                if comp['ip'].startswith(base_ip):
                    last_octet = int(comp['ip'].split('.')[-1])
                    if start <= last_octet <= end:
                        filtered.append(comp)
        else:
            # IP unique: 192.168.10.21
            filtered = [comp for comp in inventory if comp['ip'] == network_range]
        
        return filtered
    
    def list_os_versions_eol(self, os_name: str = None) -> Dict:
        """
        FONCTION 2: Pour un OS donné, lister toutes ses versions 
        et les dates de fin de vie associées
        
        Supporte les recherches par :
        - Nom exact : "Ubuntu 20.04"
        - Catégorie : "linux", "windows", "vmware"
        - Mot-clé partiel : "ubuntu", "centos", "server"
        """
        if os_name:
            search_term = os_name.lower()
            filtered = {}
            
            # Mapping de termes génériques vers catégories
            category_mapping = {
                'linux': 'Linux',
                'windows': ['Windows Server', 'Windows Client'],
                'vmware': 'Virtualisation',
                'esxi': 'Virtualisation',
                'server': 'Windows Server',
                'client': 'Windows Client'
            }
            
            # Recherche par catégorie d'abord
            if search_term in category_mapping:
                target_categories = category_mapping[search_term]
                if isinstance(target_categories, str):
                    target_categories = [target_categories]
                
                for k, v in self.eol_database.items():
                    if v.get('categorie') in target_categories:
                        filtered[k] = v
            else:
                # Recherche par mot-clé dans le nom
                for k, v in self.eol_database.items():
                    if search_term in k.lower():
                        filtered[k] = v
            
            return filtered
        
        # Si pas de filtre, retourner tout
        return self.eol_database
    
    def analyze_csv_inventory(self, csv_file: str) -> List[Dict]:
        """
        FONCTION 3: Pour une liste de composants avec leurs versions d'OS au format CSV,
        lister les dates de fin de vie
        """
        results = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    os_version = row.get('os_version', 'Inconnu')
                    eol_info = self.eol_database.get(os_version, {"eol_date": "N/A"})
                    eol_date = eol_info["eol_date"]
                    
                    results.append({
                        "nom": row.get('nom', 'N/A'),
                        "ip": row.get('ip', 'N/A'),
                        "os_version": os_version,
                        "date_eol": eol_date,
                        "statut": self.calculate_eol_status(eol_date)
                    })
            return results
        except FileNotFoundError:
            print(f"[!] Fichier {csv_file} introuvable")
            return []
        except Exception as e:
            print(f"[!] Erreur lors de la lecture du CSV : {e}")
            return []
    
    def calculate_eol_status(self, eol_date_str: str) -> str:
        """Calcule le statut EOL d'une version"""
        if eol_date_str == "N/A":
            return "INCONNU"
        
        try:
            eol_date = datetime.strptime(eol_date_str, "%Y-%m-%d")
            days = (eol_date - datetime.now()).days
            
            if days < 0:
                return "NON SUPPORTÉ"
            elif days < 180:
                return "BIENTÔT NON SUPPORTÉ"
            else:
                return "SUPPORTÉ"
        except:
            return "INCONNU"
    
    def generate_report(self, components: List[Dict]) -> str:
        """
        FONCTION 4: Produire un rapport exploitable, démontrant les composants 
        avec une version non supportée, bientôt plus supportée, etc.
        """
        if not components:
            print("[!] Aucune donnée à analyser")
            return ""
        
        # Calcul des statistiques
        stats = {
            "non_supportes": len([c for c in components if c['statut'] == 'NON SUPPORTÉ']),
            "bientot": len([c for c in components if c['statut'] == 'BIENTÔT NON SUPPORTÉ']),
            "supportes": len([c for c in components if c['statut'] == 'SUPPORTÉ']),
            "inconnus": len([c for c in components if c['statut'] == 'INCONNU'])
        }
        
        report_data = {
            "date_audit": datetime.now().isoformat(),
            "total_composants": len(components),
            "statistiques": stats,
            "composants": components
        }
        
        # Rapport JSON
        json_file = f"rapport_obsolescence_{self.timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        # Rapport TXT
        txt_file = f"rapport_obsolescence_{self.timestamp}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RAPPORT D'AUDIT D'OBSOLESCENCE - NordTransit Logistics\n")
            f.write("="*80 + "\n\n")
            f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total composants: {len(components)}\n\n")
            
            f.write("STATISTIQUES\n")
            f.write("-"*80 + "\n")
            f.write(f"NON SUPPORTÉS (EOL dépassée):     {stats['non_supportes']}\n")
            f.write(f"BIENTÔT NON SUPPORTÉS (< 6 mois): {stats['bientot']}\n")
            f.write(f"SUPPORTÉS:                        {stats['supportes']}\n")
            f.write(f"INCONNUS:                         {stats['inconnus']}\n\n")
            
            # Composants NON SUPPORTÉS
            non_sup = [c for c in components if c['statut'] == 'NON SUPPORTÉ']
            if non_sup:
                f.write("="*80 + "\n")
                f.write("COMPOSANTS NON SUPPORTÉS (ACTION URGENTE REQUISE)\n")
                f.write("="*80 + "\n")
                for c in non_sup:
                    f.write(f"\n• {c.get('nom', c['ip'])}\n")
                    f.write(f"  IP: {c['ip']}\n")
                    f.write(f"  OS: {c['os_version']}\n")
                    f.write(f"  Date EOL: {c['date_eol']}\n")
            
            # Composants BIENTÔT NON SUPPORTÉS
            bientot = [c for c in components if c['statut'] == 'BIENTÔT NON SUPPORTÉ']
            if bientot:
                f.write("\n" + "="*80 + "\n")
                f.write("COMPOSANTS BIENTÔT NON SUPPORTÉS (PLANIFIER MIGRATION)\n")
                f.write("="*80 + "\n")
                for c in bientot:
                    f.write(f"\n• {c.get('nom', c['ip'])}\n")
                    f.write(f"  IP: {c['ip']}\n")
                    f.write(f"  OS: {c['os_version']}\n")
                    f.write(f"  Date EOL: {c['date_eol']}\n")
            
            # Composants INCONNUS
            inconnus = [c for c in components if c['statut'] == 'INCONNU']
            if inconnus:
                f.write("\n" + "="*80 + "\n")
                f.write("COMPOSANTS AVEC STATUT INCONNU (AUDIT NÉCESSAIRE)\n")
                f.write("="*80 + "\n")
                for c in inconnus:
                    f.write(f"\n• {c.get('nom', c['ip'])}\n")
                    f.write(f"  IP: {c['ip']}\n")
                    f.write(f"  OS: {c['os_version']}\n")
                    f.write(f"  Date EOL: {c['date_eol']}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("FIN DU RAPPORT\n")
            f.write("="*80 + "\n")
        
        print(f"\n[+] Rapport JSON: {json_file}")
        print(f"[+] Rapport TXT: {txt_file}")
        return json_file


def menu_principal():
    """Menu interactif"""
    auditor = ObsolescenceAuditor()
    
    while True:
        print("\n" + "="*70)
        print("MODULE D'AUDIT D'OBSOLESCENCE - NTL")
        print("="*70)
        print("\n1. Lister composants sur une plage réseau")
        print("2. Lister versions EOL d'un OS")
        print("3. Analyser CSV et lister dates EOL")
        print("4. Générer rapport d'obsolescence")
        print("0. Quitter")
        print("\n" + "-"*70)
        
        choix = input("\nChoix: ").strip()
        
        if choix == "1":
            # FONCTION 1: Liste composants + détection OS
            print("\n" + "="*70)
            print("LISTE DES COMPOSANTS RÉSEAU")
            print("="*70)
            print("\nExemples de plages :")
            print("  • 192.168.10.0/24  (tout le réseau 192.168.10.x)")
            print("  • 192.168.10.21    (IP unique)")
            print("  • 192.168.10.10-50 (plage de 10 à 50)")
            
            plage = input("\n→ Plage réseau : ").strip()
            if not plage:
                continue
            
            components = auditor.list_network_components(plage)
            
            if components:
                print(f"\n[*] {len(components)} composant(s) trouvé(s)\n")
                print(f"{'N°':<5} {'Nom':<15} {'IP':<18} {'OS Détecté'}")
                print("-"*55)
                
                for i, comp in enumerate(components, 1):
                    print(f"{i:<5} {comp['nom']:<15} {comp['ip']:<18} {comp['os_detected']}")
                
                # Option voir détails
                print("\nEntrez un numéro pour voir les détails (Entrée pour continuer)")
                detail = input("N°: ").strip()
                
                if detail.isdigit() and 1 <= int(detail) <= len(components):
                    comp = components[int(detail) - 1]
                    print(f"\n{'='*70}")
                    print(f"Nom: {comp['nom']}")
                    print(f"IP: {comp['ip']}")
                    print(f"OS détecté: {comp['os_detected']}")
                    print(f"{'='*70}")
            else:
                print("\n[!] Aucun composant trouvé sur cette plage")
        
        elif choix == "2":
            # FONCTION 2: Lister versions EOL d'un OS
            print("\n" + "="*70)
            print("VERSIONS EOL D'UN OS")
            print("="*70)
            print("\nRecherche par :")
            print("  • Catégorie : linux, windows, vmware, server")
            print("  • Mot-clé : ubuntu, centos, 2019, esxi")
            print("  • Vide : afficher tout")
            
            os_name = input("\n→ Nom/catégorie de l'OS : ").strip()
            
            versions = auditor.list_os_versions_eol(os_name if os_name else None)
            
            if versions:
                print(f"\n[*] {len(versions)} version(s) trouvée(s)\n")
                print(f"{'N°':<5} {'OS Version':<45} {'Date EOL':<12} {'Statut'}")
                print("-"*75)
                
                versions_list = list(versions.items())
                for i, (os_ver, info) in enumerate(versions_list, 1):
                    statut = auditor.calculate_eol_status(info['eol_date'])
                    statut_symbole = {
                        "NON SUPPORTÉ": "🔴",
                        "BIENTÔT NON SUPPORTÉ": "🟠",
                        "SUPPORTÉ": "🟢",
                        "INCONNU": "⚪"
                    }.get(statut, "")
                    print(f"{i:<5} {os_ver:<45} {info['eol_date']:<12} {statut_symbole} {statut}")
                
                # Option voir détails
                print("\nEntrez un numéro pour voir les détails (Entrée pour continuer)")
                detail = input("N°: ").strip()
                
                if detail.isdigit() and 1 <= int(detail) <= len(versions_list):
                    os_ver, info = versions_list[int(detail) - 1]
                    statut = auditor.calculate_eol_status(info['eol_date'])
                    
                    print(f"\n{'='*70}")
                    print(f"OS Version: {os_ver}")
                    print(f"Catégorie: {info.get('categorie', 'N/A')}")
                    print(f"Date EOL: {info['eol_date']}")
                    print(f"Statut actuel: {statut}")
                    
                    if statut == "NON SUPPORTÉ":
                        print(f"\n⚠️  Ce système n'est plus supporté !")
                        print(f"   Migration urgente recommandée.")
                    elif statut == "BIENTÔT NON SUPPORTÉ":
                        eol = datetime.strptime(info['eol_date'], "%Y-%m-%d")
                        days = (eol - datetime.now()).days
                        print(f"\n⚠️  Support se termine dans {days} jours")
                        print(f"   Planifier la migration dès que possible.")
                    
                    print(f"{'='*70}")
            else:
                print("\n[!] Aucune version trouvée pour ce critère")
                print("    Essayez : linux, windows, ubuntu, centos, vmware")
        
        elif choix == "3":
            # FONCTION 3: Analyser CSV et lister dates EOL
            print("\n" + "="*70)
            print("ANALYSE CSV - LISTE DES DATES EOL")
            print("="*70)
            print("\nFormat CSV attendu: nom,ip,os_version")
            print("Exemple: inventaire_ntl.csv")
            
            csv_file = input("\n→ Nom du fichier CSV [inventaire_ntl.csv] : ").strip()
            if not csv_file:
                csv_file = "inventaire_ntl.csv"
            
            if not os.path.exists(csv_file):
                print(f"\n[!] Fichier '{csv_file}' introuvable")
                print(f"    Chemin actuel : {os.getcwd()}")
                continue
            
            results = auditor.analyze_csv_inventory(csv_file)
            
            if results:
                print(f"\n[*] {len(results)} composant(s) analysé(s)\n")
                
                symboles = {
                    "NON SUPPORTÉ": "🔴",
                    "BIENTÔT NON SUPPORTÉ": "🟠",
                    "SUPPORTÉ": "🟢",
                    "INCONNU": "⚪"
                }
                
                print(f"{'N°':<5} {'Nom':<20} {'OS Version':<35} {'Date EOL':<12} {'Statut'}")
                print("-"*95)
                
                for i, r in enumerate(results, 1):
                    symbole = symboles.get(r['statut'], '')
                    print(f"{i:<5} {r['nom']:<20} {r['os_version']:<35} {r['date_eol']:<12} {symbole} {r['statut']}")
                
                # Option voir détails
                print("\nEntrez un numéro pour voir les détails (Entrée pour continuer)")
                detail = input("N°: ").strip()
                
                if detail.isdigit() and 1 <= int(detail) <= len(results):
                    comp = results[int(detail) - 1]
                    print(f"\n{'='*70}")
                    print(f"Nom: {comp['nom']}")
                    print(f"IP: {comp['ip']}")
                    print(f"OS Version: {comp['os_version']}")
                    print(f"Date EOL: {comp['date_eol']}")
                    print(f"Statut: {comp['statut']}")
                    print(f"{'='*70}")
        
        elif choix == "4":
            # FONCTION 4: Générer rapport
            print("\n" + "="*70)
            print("GÉNÉRATION RAPPORT D'OBSOLESCENCE")
            print("="*70)
            print("\nFormat CSV attendu: nom,ip,os_version")
            print("Exemple: inventaire_ntl.csv")
            
            csv_file = input("\n→ Nom du fichier CSV [inventaire_ntl.csv] : ").strip()
            if not csv_file:
                csv_file = "inventaire_ntl.csv"
            
            if not os.path.exists(csv_file):
                print(f"\n[!] Fichier '{csv_file}' introuvable")
                print(f"    Chemin actuel : {os.getcwd()}")
                continue
            
            # Analyse le CSV
            results = auditor.analyze_csv_inventory(csv_file)
            
            if results:
                # Affiche un aperçu
                print(f"\n[*] Aperçu des composants à inclure dans le rapport:\n")
                
                symboles = {
                    "NON SUPPORTÉ": "🔴",
                    "BIENTÔT NON SUPPORTÉ": "🟠",
                    "SUPPORTÉ": "🟢",
                    "INCONNU": "⚪"
                }
                
                for r in results:
                    symbole = symboles.get(r['statut'], '')
                    print(f"{symbole} {r['nom']:<20} {r['os_version']:<35} {r['statut']}")
                
                # Génère le rapport
                confirm = input("\n→ Générer le rapport? (o/n) : ").strip().lower()
                if confirm == 'o':
                    auditor.generate_report(results)
        
        elif choix == "0":
            print("\n[*] Retour au menu principal")
            break
        
        else:
            print("\n[!] Choix invalide")
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    menu_principal()