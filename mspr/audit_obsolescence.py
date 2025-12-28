import csv
import json
import os
from datetime import datetime

# FONCTION POUR CHARGER LES DONNÉES EOL
def charger_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# FONCTION PRINCIPALE D'AUDIT
def executer_audit(fichier_csv):
    config = charger_config()
    dates_eol = config['eol_reference']
    resultats_audit = []
    
    print(f"--- ANALYSE D'OBSOLESCENCE NTL ---")

    try:
        with open(fichier_csv, mode='r', encoding='utf-8') as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                nom = ligne['nom']
                # On assemble l'OS et la version (ex: "Ubuntu 20.04")
                systeme = f"{ligne['os']} {ligne['version']}"
                
                # On récupère la date EOL correspondante
                date_limite_str = dates_eol.get(systeme)
                
                if date_limite_str:
                    date_limite = datetime.strptime(date_limite_str, "%Y-%m-%d")
                    # Comparaison avec la date du jour
                    if date_limite < datetime.now():
                        statut = "CRITIQUE"
                        detail = f"Obsolète depuis le {date_limite_str}"
                    else:
                        statut = "OK"
                        detail = f"Supporté (Fin : {date_limite_str})"
                else:
                    statut = "INCONNU"
                    detail = "Version non répertoriée dans la base EOL"

                print(f"[{statut}] {nom} ({systeme}) : {detail}")
                
                # Stockage pour le rapport JSON
                resultats_audit.append({
                    "machine": nom,
                    "os": systeme,
                    "statut": statut,
                    "details": detail
                })
        
        # Générer le livrable final
        sauvegarder_rapport(resultats_audit)

    except FileNotFoundError:
        print(f"Erreur : Le fichier {fichier_csv} est introuvable.")

# FONCTION POUR CRÉER LE RAPPORT JSON (Livrable demandé)
def sauvegarder_rapport(donnees):
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"rapport_audit_{horodatage}.json"
    
    structure_rapport = {
        "metadata": {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "client": "Nord Transit Logistics",
            "module": "Audit Obsolescence (Module 3)"
        },
        "resultats": donnees
    }
    
    with open(nom_fichier, 'w', encoding='utf-8') as f:
        json.dump(structure_rapport, f, indent=4, ensure_ascii=False)
    
    print(f"\n[SUCCÈS] Rapport généré : {nom_fichier}")

# LANCEMENT DU SCRIPT
if __name__ == "__main__":
    executer_audit('inventaire.csv')