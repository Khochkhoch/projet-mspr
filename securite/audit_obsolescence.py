import csv
import json
import datetime
from collections import Counter


def load_eol_database():
    with open("eol_database.json", "r", encoding="utf-8") as file:
        return json.load(file)


def audit_csv(csv_file):
    eol_db = load_eol_database()
    today = datetime.date.today()
    results = []

    with open(csv_file, newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            os_name = row["os"]
            version = row["version"]

            eol_date = eol_db.get(os_name, {}).get(version, "Inconnue")

            status = "Inconnu"
            if eol_date != "Inconnue":
                eol = datetime.datetime.strptime(eol_date, "%Y-%m-%d").date()
                if eol < today:
                    status = "Obsolète"
                elif (eol - today).days < 365:
                    status = "Bientôt obsolète"
                else:
                    status = "Supporté"

            results.append({
                "ip": row["ip"],
                "os": os_name,
                "version": version,
                "eol": eol_date,
                "status": status
            })

    return results


def generate_report(audit_results):
    summary = Counter(item["status"] for item in audit_results)

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "total_machines": len(audit_results),
            "supporte": summary.get("Supporté", 0),
            "bientot_obsolete": summary.get("Bientôt obsolète", 0),
            "obsolete": summary.get("Obsolète", 0),
            "inconnu": summary.get("Inconnu", 0)
        },
        "details": audit_results
    }

    return report


if __name__ == "__main__":
    audit_results = audit_csv("machines.csv")
    final_report = generate_report(audit_results)

    # Écriture du fichier JSON
    with open("audit_report.json", "w", encoding="utf-8") as file:
        json.dump(final_report, file, indent=4, ensure_ascii=False)

    # Affichage console (interprétation humaine)
    print("\n===== RAPPORT D’AUDIT D’OBSOLESCENCE =====\n")
    print(f"Date de l’audit : {final_report['timestamp']}")
    print(f"Nombre total de machines : {final_report['summary']['total_machines']}")
    print(f"Systèmes supportés : {final_report['summary']['supporte']}")
    print(f"Systèmes bientôt obsolètes : {final_report['summary']['bientot_obsolete']}")
    print(f"Systèmes obsolètes : {final_report['summary']['obsolete']}")
    print(f"Systèmes inconnus : {final_report['summary']['inconnu']}")

    if final_report["summary"]["obsolete"] > 0:
        print("\n⚠️ ACTION PRIORITAIRE : des systèmes obsolètes ont été détectés.")
    elif final_report["summary"]["bientot_obsolete"] > 0:
        print("\n⚠️ ANTICIPATION RECOMMANDÉE : certains systèmes arrivent en fin de support.")
    else:
        print("\n✅ Aucun risque immédiat détecté.")

    print("\nRapport détaillé généré : audit_report.json")
