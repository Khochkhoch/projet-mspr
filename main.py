#!/usr/bin/env python3
"""
NTL-SysToolbox - Menu CLI Interactif
Outil pour diagnostic, sauvegarde et audit d'obsolescence
Conforme au cahier des charges MSPR TPRE511
"""

import os
import sys
from datetime import datetime

# Import des modules avec gestion d'erreur
modules_disponibles = {}

try:
    import diagnostic
    modules_disponibles['diagnostic'] = True
except ImportError as e:
    print(f"[AVERTISSEMENT] Module diagnostic.py : {e}")
    modules_disponibles['diagnostic'] = False

try:
    import backup
    modules_disponibles['backup'] = True
except ImportError as e:
    print(f"[AVERTISSEMENT] Module backup.py : {e}")
    modules_disponibles['backup'] = False

try:
    import obsolescence_audit
    modules_disponibles['obsolescence'] = True
except ImportError as e:
    print(f"[AVERTISSEMENT] Module obsolescence_audit.py : {e}")
    modules_disponibles['obsolescence'] = False


class NTLSysToolbox:
    """Menu CLI interactif principal"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.nom_entreprise = "NordTransit Logistics"
    
    def clear_screen(self):
        """Efface l'écran selon l'OS"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Affiche l'en-tête"""
        print("=" * 80)
        print(f"  NTL-SYSTOOLBOX v{self.version} - {self.nom_entreprise}")
        print("=" * 80)
        print(f"  Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("-" * 80)
    
    def print_menu_principal(self):
        """Affiche le menu principal"""
        self.clear_screen()
        self.print_header()
        
        print("\n╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                            MENU PRINCIPAL                                  ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        
        # Module 1 - Diagnostic
        statut1 = "✓" if modules_disponibles.get('diagnostic') else "✗"
        print(f"\n  [{statut1}] 1. MODULE DIAGNOSTIC")
        print("      • Tester la connectivité réseau (ping)")
        print("      • Vérifier résolution DNS")
        print("      • Tester connexion MySQL/WMS")
        print("      • Récupérer informations système")
        
        # Module 2 - Sauvegarde
        statut2 = "✓" if modules_disponibles.get('backup') else "✗"
        print(f"\n  [{statut2}] 2. MODULE SAUVEGARDE WMS")
        print("      • Sauvegarde complète base de données (SQL)")
        print("      • Export de tables spécifiques (CSV)")
        
        # Module 3 - Obsolescence
        statut3 = "✓" if modules_disponibles.get('obsolescence') else "✗"
        print(f"\n  [{statut3}] 3. MODULE AUDIT D'OBSOLESCENCE")
        print("      • Scanner composants réseau")
        print("      • Lister versions OS et dates EOL")
        print("      • Analyser inventaire CSV")
        print("      • Générer rapport d'obsolescence")
        
        print("\n  [0] QUITTER")
        print("\n" + "=" * 80)
    
    # ========== MODULE 1 : DIAGNOSTIC ==========
    
    def menu_diagnostic(self):
        """Menu interactif du module diagnostic"""
        if not modules_disponibles.get('diagnostic'):
            print("\n[!] Module diagnostic non disponible")
            input("\nAppuyez sur Entrée...")
            return
        
        while True:
            self.clear_screen()
            self.print_header()
            print("\n╔════════════════════════════════════════════════════════════════════════════╗")
            print("║                         MODULE DIAGNOSTIC                                  ║")
            print("╚════════════════════════════════════════════════════════════════════════════╝")
            
            print("\n  1. Test de connectivité (PING)")
            print("  2. Test de résolution DNS")
            print("  3. Test connexion MySQL")
            print("  4. Informations système")
            print("  5. Diagnostic complet (tous les tests)")
            print("\n  0. Retour menu principal")
            print("\n" + "-" * 80)
            
            choix = input("\n→ Votre choix : ").strip()
            
            if choix == "1":
                self.diagnostic_ping()
            
            elif choix == "2":
                self.diagnostic_dns()
            
            elif choix == "3":
                self.diagnostic_mysql()
            
            elif choix == "4":
                self.diagnostic_system_info()
            
            elif choix == "5":
                self.diagnostic_complet()
            
            elif choix == "0":
                break
            
            else:
                print("\n[!] Choix invalide")
                input("\nAppuyez sur Entrée...")
    
    def diagnostic_ping(self):
        """Test PING avec demande d'arguments"""
        print("\n" + "=" * 80)
        print("TEST DE CONNECTIVITÉ (PING)")
        print("=" * 80)
        print("\nExemples d'adresses IP :")
        print("  • 192.168.10.10 (DC01)")
        print("  • 192.168.10.21 (WMS-DB)")
        print("  • 8.8.8.8 (Google DNS)")
        
        ip = input("\n→ Adresse IP à tester : ").strip()
        
        if not ip:
            print("[!] Adresse IP requise")
        else:
            print("\n" + "-" * 80)
            diagnostic.ping(ip)
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    def diagnostic_dns(self):
        """Test DNS avec demande d'arguments"""
        print("\n" + "=" * 80)
        print("TEST DE RÉSOLUTION DNS")
        print("=" * 80)
        print("\nExemples de domaines :")
        print("  • nordtransit.local")
        print("  • google.com")
        print("  • dc01.nordtransit.local")
        
        domaine = input("\n→ Domaine à résoudre : ").strip()
        
        if not domaine:
            print("[!] Nom de domaine requis")
        else:
            print("\n" + "-" * 80)
            diagnostic.dns_lookup(domaine)
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    def diagnostic_mysql(self):
        """Test MySQL avec demande d'arguments"""
        print("\n" + "=" * 80)
        print("TEST CONNEXION MYSQL")
        print("=" * 80)
        print("\n⚠️  Configuration WMS par défaut :")
        print("   Host: 192.168.10.21")
        print("   User: root")
        
        print("\n→ Paramètres de connexion :")
        host = input("  Host [192.168.10.21] : ").strip() or "192.168.10.21"
        user = input("  Utilisateur [root] : ").strip() or "root"
        password = input("  Mot de passe : ").strip()
        
        if not password:
            print("[!] Mot de passe requis")
        else:
            print("\n" + "-" * 80)
            diagnostic.test_mysql_connection(host, user, password)
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    def diagnostic_system_info(self):
        """Récupération informations système"""
        print("\n" + "=" * 80)
        print("INFORMATIONS SYSTÈME")
        print("=" * 80)
        print("\nRécupération des informations en cours...\n")
        print("-" * 80)
        
        diagnostic.get_system_info()
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    def diagnostic_complet(self):
        """Exécute tous les tests de diagnostic"""
        print("\n" + "=" * 80)
        print("DIAGNOSTIC COMPLET - INFRASTRUCTURE NTL")
        print("=" * 80)
        
        confirm = input("\nLancer le diagnostic complet ? (o/n) : ").strip().lower()
        
        if confirm != 'o':
            return
        
        print("\n[*] Démarrage du diagnostic complet...\n")
        
        # Test 1 : Contrôleurs de domaine
        print("\n" + "─" * 80)
        print("[1/5] TEST DES CONTRÔLEURS DE DOMAINE")
        print("─" * 80)
        diagnostic.ping("192.168.10.10")  # DC01
        diagnostic.ping("192.168.10.11")  # DC02
        
        # Test 2 : DNS
        print("\n" + "─" * 80)
        print("[2/5] TEST DNS")
        print("─" * 80)
        diagnostic.dns_lookup("nordtransit.local")
        
        # Test 3 : WMS Database
        print("\n" + "─" * 80)
        print("[3/5] TEST SERVEUR WMS")
        print("─" * 80)
        diagnostic.ping("192.168.10.21")  # WMS-DB
        diagnostic.ping("192.168.10.22")  # WMS-APP
        
        # Test 4 : MySQL
        print("\n" + "─" * 80)
        print("[4/5] TEST BASE DE DONNÉES MYSQL")
        print("─" * 80)
        print("⚠️  Test nécessitant les identifiants - Ignoré en mode auto")
        
        # Test 5 : Système
        print("\n" + "─" * 80)
        print("[5/5] INFORMATIONS SYSTÈME")
        print("─" * 80)
        diagnostic.get_system_info()
        
        print("\n" + "=" * 80)
        print("[✓] DIAGNOSTIC COMPLET TERMINÉ")
        print("=" * 80)
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    # ========== MODULE 2 : SAUVEGARDE ==========
    
    def menu_sauvegarde(self):
        """Menu interactif du module sauvegarde"""
        if not modules_disponibles.get('backup'):
            print("\n[!] Module backup non disponible")
            input("\nAppuyez sur Entrée...")
            return
        
        while True:
            self.clear_screen()
            self.print_header()
            print("\n╔════════════════════════════════════════════════════════════════════════════╗")
            print("║                       MODULE SAUVEGARDE WMS                                ║")
            print("╚════════════════════════════════════════════════════════════════════════════╝")
            
            # Détection du système
            import platform
            systeme = platform.system()
            
            print("\n  1. Sauvegarde complète (recommandé)")
            print("     → Dump SQL complet + Export CSV des commandes")
            
            print("\n  0. Retour menu principal")
            print("\n" + "-" * 80)
            
            # Message adapté selon l'OS
            if systeme == "Windows":
                print("ℹ️  Configuration : Windows détecté")
                print("   • Sauvegarde réelle avec MySQL")
                print("   • Répertoire : C:\\wms_backup\\backups\\")
            elif systeme == "Darwin":  # macOS
                print("ℹ️  Configuration : macOS détecté")
                print("   • Mode simulation (MySQL non requis)")
                print("   • Répertoire : ~/wms_backup/backups/")
            else:  # Linux
                print("ℹ️  Configuration : Linux détecté")
                print("   • Vérifier installation MySQL")
                print("   • Répertoire : ~/wms_backup/backups/")
            
            print("-" * 80)
            
            choix = input("\n→ Votre choix : ").strip()
            
            if choix == "1":
                self.sauvegarde_complete()
            
            elif choix == "0":
                break
            
            else:
                print("\n[!] Choix invalide")
                input("\nAppuyez sur Entrée...")
    
    def sauvegarde_complete(self):
        """Sauvegarde complète SQL + CSV"""
        import platform
        systeme = platform.system()
        
        print("\n" + "=" * 80)
        print("SAUVEGARDE COMPLÈTE WMS")
        print("=" * 80)
        
        if systeme == "Windows":
            print("\nMode : PRODUCTION (Windows + MySQL)")
            print("Cette opération va :")
            print("  • Créer un dump SQL complet de la base wms_db")
            print("  • Exporter la table 'orders' en CSV")
            print(f"  • Sauvegarder dans : C:\\wms_backup\\backups\\")
        elif systeme == "Darwin":
            print("\nMode : SIMULATION (macOS - Développement)")
            print("Cette opération va :")
            print("  • Créer des fichiers de démonstration SQL et CSV")
            print("  • Simuler le comportement du module sauvegarde")
            print(f"  • Sauvegarder dans : ~/wms_backup/backups/")
        else:
            print("\nMode : PRODUCTION (Linux)")
            print("Cette opération va :")
            print("  • Créer un dump SQL complet de la base wms_db")
            print("  • Exporter la table 'orders' en CSV")
            print(f"  • Sauvegarder dans : ~/wms_backup/backups/")
        
        confirm = input("\n→ Lancer la sauvegarde ? (o/n) : ").strip().lower()
        
        if confirm == 'o':
            print("\n" + "-" * 80)
            try:
                result = backup.main()
                if result == 0:
                    print("\n" + "=" * 80)
                    print("[✓] SAUVEGARDE COMPLÈTE RÉUSSIE")
                    print("=" * 80)
                    
                    if systeme == "Darwin":
                        print("\n💡 Fichiers de test créés pour la démonstration")
                        print("   Sur Windows avec MySQL, la sauvegarde sera réelle")
                else:
                    print("\n[!] Sauvegarde terminée avec des avertissements")
            except Exception as e:
                print(f"\n[✗] Erreur : {e}")
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    def sauvegarde_sql_seule(self):
        """Sauvegarde SQL uniquement"""
        print("\n" + "=" * 80)
        print("SAUVEGARDE SQL")
        print("=" * 80)
        
        # Arguments personnalisés
        print("\n→ Configuration MySQL :")
        host = input("  Host [192.168.10.21] : ").strip() or "192.168.10.21"
        user = input("  User [root] : ").strip() or "root"
        db = input("  Database [wms_db] : ").strip() or "wms_db"
        
        print(f"\nSauvegarde de {db} depuis {host}...")
        print("[INFO] Fonctionnalité nécessite adaptation du module backup.py")
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    def sauvegarde_csv_personnalise(self):
        """Export CSV avec table personnalisée"""
        print("\n" + "=" * 80)
        print("EXPORT CSV PERSONNALISÉ")
        print("=" * 80)
        print("\nTables disponibles :")
        print("  • orders (commandes)")
        print("  • inventory (inventaire)")
        print("  • shipments (expéditions)")
        
        table = input("\n→ Nom de la table à exporter [orders] : ").strip() or "orders"
        
        print(f"\nExport de la table '{table}' en cours...")
        print("[INFO] Fonctionnalité nécessite adaptation du module backup.py")
        
        input("\n\nAppuyez sur Entrée pour continuer...")
    
    # ========== MODULE 3 : OBSOLESCENCE ==========
    
    def menu_obsolescence(self):
        """Menu interactif du module obsolescence"""
        if not modules_disponibles.get('obsolescence'):
            print("\n[!] Module obsolescence_audit non disponible")
            input("\nAppuyez sur Entrée...")
            return
        
        # Le module obsolescence a déjà son propre menu interactif complet
        # On l'appelle directement
        obsolescence_audit.menu_principal()
    
    # ========== BOUCLE PRINCIPALE ==========
    
    def run(self):
        """Boucle principale du menu"""
        while True:
            self.print_menu_principal()
            choix = input("→ Votre choix : ").strip()
            
            if choix == "1":
                self.menu_diagnostic()
            
            elif choix == "2":
                self.menu_sauvegarde()
            
            elif choix == "3":
                self.menu_obsolescence()
            
            elif choix == "0":
                self.clear_screen()
                print("\n" + "=" * 80)
                print(f"  Merci d'avoir utilisé NTL-SysToolbox")
                print(f"  {self.nom_entreprise}")
                print("=" * 80 + "\n")
                sys.exit(0)
            
            else:
                print("\n[!] Choix invalide. Veuillez réessayer.")
                input("\nAppuyez sur Entrée...")


def main():
    """Point d'entrée principal"""
    try:
        # Vérifier qu'au moins un module est disponible
        if not any(modules_disponibles.values()):
            print("\n" + "=" * 80)
            print("[ERREUR] Aucun module trouvé !")
            print("=" * 80)
            print("\nFichiers requis :")
            print("  • diagnostic.py")
            print("  • backup.py")
            print("  • obsolescence_audit.py")
            print("\nAssurez-vous que ces fichiers sont présents dans le même répertoire.")
            print("=" * 80 + "\n")
            sys.exit(1)
        
        # Lancer l'application
        toolbox = NTLSysToolbox()
        toolbox.run()
        
    except KeyboardInterrupt:
        print("\n\n[*] Interruption utilisateur (Ctrl+C). Au revoir !")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERREUR CRITIQUE] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 
