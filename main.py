import sqlite3
import datetime
from dateutil import parser
from tabulate import tabulate

class VintedManager:
    def __init__(self):
        self.conn = sqlite3.connect('vinted.db')
        self.cursor = self.conn.cursor()
        self.setup_database()
        self.load_tax_rate()

    def setup_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            marque TEXT,
            taille TEXT,
            couleur TEXT,
            etat TEXT,
            description TEXT,
            prix_achat REAL,
            date_achat DATE,
            estimation REAL,
            prix_vente REAL,
            date_vente DATE
        )''')
        
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        self.conn.commit()

    def load_tax_rate(self):
        self.cursor.execute('SELECT value FROM settings WHERE key = "tax_rate"')
        result = self.cursor.fetchone()
        self.tax_rate = float(result[0]) if result else 0.0

    def set_tax_rate(self, rate):
        self.tax_rate = rate
        self.cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                          ('tax_rate', str(rate)))
        self.conn.commit()

    def add_product(self):
        print("\n=== Ajouter un produit ===")
        product = {}
        
        # Champs texte simples
        text_fields = {
            'type': "Type: ",
            'marque': "Marque: ",
            'taille': "Taille: ",
            'couleur': "Couleur: ",
            'etat': "État: ",
            'description': "Description: ",
            'date_achat': "Date d'achat (JJ/MM/AAAA): "
        }
        
        for field, prompt in text_fields.items():
            product[field] = input(prompt)
        
        # Champs numériques avec gestion d'erreur
        numeric_fields = {
            'prix_achat': "Prix d'achat: ",
            'estimation': "Estimation: "
        }
        
        for field, prompt in numeric_fields.items():
            while True:
                try:
                    value = input(prompt)
                    # Remplacer la virgule par un point pour la conversion
                    value = value.replace(',', '.')
                    product[field] = float(value)
                    break
                except ValueError:
                    print("Erreur: Veuillez entrer un nombre valide (utilisez le point ou la virgule comme séparateur décimal)")
        
        self.cursor.execute('''
        INSERT INTO products (type, marque, taille, couleur, etat, description, 
                            prix_achat, date_achat, estimation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product['type'], product['marque'], product['taille'], product['couleur'],
              product['etat'], product['description'], product['prix_achat'],
              product['date_achat'], product['estimation']))
        self.conn.commit()
        print("Produit ajouté avec succès!")

    def view_stock(self):
        print("\n=== Stock actuel ===")
        self.cursor.execute('''
        SELECT * FROM products WHERE prix_vente IS NULL
        ''')
        products = self.cursor.fetchall()
        headers = ['ID', 'Type', 'Marque', 'Taille', 'Couleur', 'État', 'Description',
                  "Prix d'achat", "Date d'achat", 'Estimation', 'Prix de vente', 'Date de vente']
        print(tabulate(products, headers=headers, tablefmt='grid'))

    def modify_product(self):
        print("\n=== Modifier un produit ===")
        self.view_stock()
        product_id = input("\nID du produit à modifier: ")
        print("\nQue souhaitez-vous modifier ?")
        print("1. Type")
        print("2. Marque")
        print("3. Taille")
        print("4. Couleur")
        print("5. État")
        print("6. Description")
        print("7. Prix d'achat")
        print("8. Date d'achat")
        print("9. Estimation")
        print("10. Prix de vente")
        print("11. Date de vente")
        print("12. Supprimer ce produit")
        choice = input("Votre choix: ")

        if choice == '12':
            confirmation = input("Êtes-vous sûr de vouloir supprimer ce produit ? (o/n): ")
            if confirmation.lower() == 'o':
                self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                self.conn.commit()
                print("Produit supprimé avec succès!")
            return

        # Dictionnaire des champs et leurs types
        fields = {
            '1': ('type', str),
            '2': ('marque', str),
            '3': ('taille', str),
            '4': ('couleur', str),
            '5': ('etat', str),
            '6': ('description', str),
            '7': ('prix_achat', float),
            '8': ('date_achat', str),
            '9': ('estimation', float),
            '10': ('prix_vente', float),
            '11': ('date_vente', str)
        }

        if choice in fields:
            field, type_conv = fields[choice]
            try:
                if type_conv == float:
                    new_value = float(input(f"Nouveau {field}: "))
                else:
                    new_value = input(f"Nouveau {field}: ")
                
                self.cursor.execute(f'UPDATE products SET {field} = ? WHERE id = ?',
                                  (new_value, product_id))
                self.conn.commit()
                print("Produit modifié avec succès!")
            except ValueError:
                print("Erreur: Valeur invalide")

    def calculate_metrics(self, period=None):
        where_clause = ''
        if period:
            start_date = period
            end_date = (parser.parse(period) + datetime.timedelta(days=31)).strftime('%d/%m/%Y')
            where_clause = f" WHERE date_vente BETWEEN '{start_date}' AND '{end_date}'"

        # Chiffre d'affaires
        self.cursor.execute(f'''
        SELECT SUM(prix_vente) FROM products 
        WHERE prix_vente IS NOT NULL{where_clause}
        ''')
        ca = self.cursor.fetchone()[0] or 0

        # Bénéfice brut
        self.cursor.execute(f'''
        SELECT SUM(prix_vente - prix_achat) FROM products 
        WHERE prix_vente IS NOT NULL{where_clause}
        ''')
        benefice_brut = self.cursor.fetchone()[0] or 0

        # Bénéfice net
        benefice_net = benefice_brut * (1 - self.tax_rate/100)

        return ca, benefice_brut, benefice_net

    def calculate_estimated_metrics(self):
        self.cursor.execute('''
        SELECT SUM(estimation) FROM products 
        WHERE prix_vente IS NULL
        ''')
        ca_estime = self.cursor.fetchone()[0] or 0

        self.cursor.execute('''
        SELECT SUM(estimation - prix_achat) FROM products 
        WHERE prix_vente IS NULL
        ''')
        benefice_brut_estime = self.cursor.fetchone()[0] or 0
        benefice_net_estime = benefice_brut_estime * (1 - self.tax_rate/100)

        return ca_estime, benefice_brut_estime, benefice_net_estime

def main_menu():
    manager = VintedManager()
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1. Ajouter un produit")
        print("2. Modifier/Supprimer un produit")
        print("3. Voir le stock")
        print("4. Voir les métriques")
        print("5. Modifier le taux d'imposition")
        print("6. Quitter")
        
        choice = input("\nVotre choix: ")
        
        if choice == '1':
            manager.add_product()
        elif choice == '2':
            manager.modify_product()
        elif choice == '3':
            manager.view_stock()
        elif choice == '4':
            print("\n=== Métriques ===")
            period = input("Entrez le mois (MM/AAAA) pour les métriques mensuelles ou appuyez sur Entrée pour le total: ")
            
            if period:
                period = f"01/{period}"
                ca, bb, bn = manager.calculate_metrics(period)
                print(f"\nMétriques pour {period}:")
            else:
                ca, bb, bn = manager.calculate_metrics()
                print("\nMétriques totales:")
            
            print(f"Chiffre d'affaires: {ca:.2f}€")
            print(f"Bénéfice brut: {bb:.2f}€")
            print(f"Bénéfice net: {bn:.2f}€")
            
            print("\nEstimations:")
            ca_est, bb_est, bn_est = manager.calculate_estimated_metrics()
            print(f"Chiffre d'affaires estimé: {ca_est:.2f}€")
            print(f"Bénéfice brut estimé: {bb_est:.2f}€")
            print(f"Bénéfice net estimé: {bn_est:.2f}€")
        elif choice == '5':
            new_rate = float(input("Nouveau taux d'imposition (%): "))
            manager.set_tax_rate(new_rate)
            print(f"Taux d'imposition mis à jour à {new_rate}%")
        elif choice == '6':
            print("Au revoir!")
            break

if __name__ == "__main__":
    main_menu() 