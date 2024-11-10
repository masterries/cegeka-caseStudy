import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid

class BusinessDataGenerator:
    def __init__(self, start_date='2023-01-01', end_date='2024-12-31', error_rate=0.15):
        self.fake = Faker('de_DE')
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.error_rate = error_rate  # Rate für Datenfehler
        
        # Konstante Listen für realistische Daten
        self.product_categories = ['Elektronik', 'Bürobedarf', 'Möbel', 'IT-Equipment', 'Verbrauchsmaterial']
        self.payment_terms = ['Net30', 'Net60', 'Immediate', 'Net45']
        self.departments = ['Vertrieb', 'IT', 'HR', 'Finanzen', 'Einkauf', 'Produktion']
        self.status_options = ['Neu', 'In Bearbeitung', 'Abgeschlossen', 'Storniert']
        self.shipping_methods = ['Standard', 'Express', 'Economy', 'Premium']
        
        # Generiere Basis-Produktdaten
        self.products = self._generate_product_master_data()
        
        # Generiere Basis-Kundendaten
        self.customers = self._generate_customer_master_data()

    def _generate_product_master_data(self, num_products=100):
        """Generiert Produktstammdaten"""
        products = []
        
        for _ in range(num_products):
            category = random.choice(self.product_categories)
            
            # Definiere kategoriespezifische Produkteigenschaften
            if category == 'Elektronik':
                name_parts = ['ThinkPad', 'ProBook', 'Latitude', 'Monitor', 'Drucker']
                price_range = (500, 2000)
            elif category == 'Bürobedarf':
                name_parts = ['Papier', 'Ordner', 'Stifte', 'Marker', 'Notizblöcke']
                price_range = (5, 50)
            elif category == 'Möbel':
                name_parts = ['Schreibtisch', 'Bürostuhl', 'Schrank', 'Regal', 'Lampe']
                price_range = (100, 1000)
            elif category == 'IT-Equipment':
                name_parts = ['Router', 'Switch', 'Kabel', 'Dockingstation', 'Webcam']
                price_range = (50, 500)
            else:  # Verbrauchsmaterial
                name_parts = ['Toner', 'Druckerpatrone', 'Batterien', 'USB-Sticks', 'Reinigungsmittel']
                price_range = (10, 200)

            # Generiere manchmal fehlerhafte oder fehlende Daten
            if random.random() < self.error_rate:
                min_stock = None
                max_stock = None
                supplier_id = None
            else:
                min_stock = random.randint(10, 50)
                max_stock = random.randint(100, 500)
                supplier_id = f'S{str(uuid.uuid4())[:8]}'

            product = {
                'product_id': f'P{str(uuid.uuid4())[:8]}',
                'name': f'{random.choice(name_parts)} {self.fake.unique.random_number(digits=3)}',
                'category': category,
                'unit_price': round(random.uniform(*price_range), 2),
                'min_stock': min_stock,
                'max_stock': max_stock,
                'supplier_id': supplier_id,
                'lead_time_days': random.randint(1, 30)
            }
            products.append(product)
        
        return pd.DataFrame(products)

    def _generate_customer_master_data(self, num_customers=200):
        """Generiert Kundenstammdaten"""
        customers = []
        
        for _ in range(num_customers):
            # Generiere manchmal fehlerhafte oder fehlende Daten
            if random.random() < self.error_rate:
                email = None
                phone = None
                credit_limit = None
            else:
                email = self.fake.company_email()
                phone = self.fake.phone_number()
                credit_limit = random.choice([5000, 10000, 25000, 50000, 100000])

            customer = {
                'customer_id': f'C{str(uuid.uuid4())[:8]}',
                'company_name': self.fake.company(),
                'contact_name': self.fake.name(),
                'email': email,
                'phone': phone,
                'address': self.fake.street_address(),
                'city': self.fake.city(),
                'postal_code': self.fake.postcode(),
                'country': 'Deutschland',
                'customer_since': self.fake.date_between(
                    start_date='-5y', 
                    end_date='today'
                ).strftime('%Y-%m-%d'),
                'credit_limit': credit_limit,
                'payment_terms': random.choice(self.payment_terms),
                'department': random.choice(self.departments)
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)

    def generate_sales_orders(self, num_orders=1000):
        orders = []
        
        # Generiere normale Bestellungen
        for _ in range(num_orders):
            order_date = self.fake.date_time_between(
                start_date=self.start_date,
                end_date=self.end_date
            )
            customer = self.customers.sample(1).iloc[0]
            
            # Manchmal fehlen Kundendaten
            if random.random() < self.error_rate * 0.5:
                customer_id = None
                shipping_address = None
                shipping_city = None
                shipping_postal_code = None
            else:
                customer_id = customer['customer_id']
                shipping_address = customer['address']
                shipping_city = customer['city']
                shipping_postal_code = customer['postal_code']
            
            order = {
                'order_id': f'SO{str(uuid.uuid4())[:8]}',
                'customer_id': customer_id,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'status': np.random.choice(
                    self.status_options,
                    p=[0.1, 0.2, 0.6, 0.1]
                ),
                'shipping_method': random.choice(self.shipping_methods),
                'payment_terms': customer['payment_terms'],
                'department': customer['department'],
                'shipping_address': shipping_address,
                'shipping_city': shipping_city,
                'shipping_postal_code': shipping_postal_code,
                'expected_delivery': (
                    order_date + timedelta(days=random.randint(3, 14))
                ).strftime('%Y-%m-%d')
            }
            orders.append(order)
        
        return pd.DataFrame(orders)

    def generate_order_items(self, sales_orders, items_per_order=(1, 5)):
        order_items = []
        
        for _, order in sales_orders.iterrows():
            # Manchmal fehlen komplette Bestellpositionen
            if random.random() < self.error_rate * 0.3:
                continue
                
            num_items = random.randint(*items_per_order)
            selected_products = self.products.sample(num_items)
            
            for _, product in selected_products.iterrows():
                # Manchmal fehlen einzelne Positionen
                if random.random() < self.error_rate * 0.1:
                    continue
                    
                quantity = random.randint(1, 10)
                unit_price = product['unit_price']
                discount = random.choice([0, 0, 0, 0.05, 0.1])
                
                # Manchmal Preisabweichungen
                if random.random() < self.error_rate:
                    unit_price *= (1 + random.uniform(-0.1, 0.1))
                
                item = {
                    'order_id': order['order_id'],
                    'product_id': product['product_id'],
                    'quantity': quantity,
                    'unit_price': round(unit_price, 2),
                    'discount': discount,
                    'line_total': round(quantity * unit_price * (1 - discount), 2)
                }
                order_items.append(item)
        
        return pd.DataFrame(order_items)

    def generate_financial_transactions(self, sales_orders, order_items):
        # Berechne tatsächliche Bestellsummen
        order_totals = order_items.groupby('order_id')['line_total'].sum().reset_index()
        orders_with_totals = sales_orders.merge(order_totals, on='order_id', how='left')
        
        financial_transactions = []
        
        for _, order in orders_with_totals.iterrows():
            # Manchmal fehlen Finanztransaktionen komplett
            if random.random() < self.error_rate * 0.2:
                continue
                
            # Basisinformationen
            invoice_date = pd.to_datetime(order['order_date'])
            due_date = invoice_date + timedelta(days={
                'Net30': 30, 'Net45': 45, 'Net60': 60, 'Immediate': 0
            }[order['payment_terms']])
            
            # Zeitliche Verschiebungen
            if random.random() < 0.3:
                invoice_date += timedelta(days=random.randint(1, 5))
            
            # Zufällige Zahlungsverzögerung
            payment_delay = random.choice([0, 0, 0, 5, 10, 15, 30])  # 60% pünktlich
            actual_payment_date = due_date + timedelta(days=payment_delay)
            
            # Manchmal Betragsabweichungen
            amount = order['line_total']
            if random.random() < self.error_rate:
                amount *= (1 + random.uniform(-0.05, 0.05))
            
            # Manchmal Split-Buchungen
            if random.random() < 0.1 and amount > 1000:
                # Teile den Betrag in zwei Transaktionen
                split_ratio = random.uniform(0.3, 0.7)
                amounts = [amount * split_ratio, amount * (1 - split_ratio)]
                dates = [actual_payment_date, actual_payment_date + timedelta(days=random.randint(1, 10))]
                
                for split_amount, split_date in zip(amounts, dates):
                    transaction = {
                        'transaction_id': f'FT{str(uuid.uuid4())[:8]}',
                        'order_id': order['order_id'],
                        'customer_id': order['customer_id'],
                        'invoice_date': invoice_date.strftime('%Y-%m-%d'),
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'amount': round(split_amount, 2),
                        'payment_date': split_date.strftime('%Y-%m-%d'),
                        'payment_method': random.choice(['Überweisung', 'Lastschrift', 'Kreditkarte']),
                        'status': 'Bezahlt' if split_date <= datetime.now() else 'Ausstehend',
                        'department': order['department'],
                        'currency': 'EUR'
                    }
                    financial_transactions.append(transaction)
            else:
                transaction = {
                    'transaction_id': f'FT{str(uuid.uuid4())[:8]}',
                    'order_id': order['order_id'],
                    'customer_id': order['customer_id'],
                    'invoice_date': invoice_date.strftime('%Y-%m-%d'),
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'payment_date': actual_payment_date.strftime('%Y-%m-%d'),
                    'payment_method': random.choice(['Überweisung', 'Lastschrift', 'Kreditkarte']),
                    'status': 'Bezahlt' if actual_payment_date <= datetime.now() else 'Ausstehend',
                    'department': order['department'],
                    'currency': 'EUR'
                }
                financial_transactions.append(transaction)
        
        return pd.DataFrame(financial_transactions)

    def generate_inventory_transactions(self, num_transactions=2000):
        transactions = []
        transaction_types = ['Eingang', 'Ausgang', 'Bestandskorrektur', 'Retoure']
        
        for _ in range(num_transactions):
            product = self.products.sample(1).iloc[0]
            trans_type = random.choice(transaction_types)
            
            # Manchmal fehlerhafte oder unvollständige Daten
            if random.random() < self.error_rate:
                product_id = None
                unit_cost = None
            else:
                product_id = product['product_id']
                unit_cost = product['unit_price'] * 0.7
            
            if trans_type == 'Eingang':
                quantity = random.randint(10, 100)
            elif trans_type == 'Ausgang':
                quantity = -random.randint(1, 20)
            elif trans_type == 'Bestandskorrektur':
                quantity = random.randint(-5, 5)
            else:  # Retoure
                quantity = random.randint(1, 5)
            
            transaction = {
                'transaction_id': f'T{str(uuid.uuid4())[:8]}',
                'product_id': product_id,
                'transaction_type': trans_type,
                'quantity': quantity,
                'transaction_date': self.fake.date_time_between(
                    start_date=self.start_date,
                    end_date=self.end_date
                ).strftime('%Y-%m-%d %H:%M:%S'),
                'unit_cost': unit_cost,
                'location': random.choice(['Hauptlager', 'Außenlager', 'Versand', 'Retouren']),
                'reference_document': f'REF{self.fake.unique.random_number(digits=6)}',
                'status': random.choice(['Abgeschlossen', 'In Bearbeitung', 'Geplant'])
            }
            transactions.append(transaction)
            
        return pd.DataFrame(transactions)

    def generate_all_data(self):
        """Generiert alle Datensätze mit realistischen Inkonsistenzen"""
        # Generiere Verkaufsaufträge
        sales_orders = self.generate_sales_orders()
        
        # Generiere Auftragspositionen mit fehlenden Daten
        order_items = self.generate_order_items(sales_orders)
        
        # Generiere Lagertransaktionen mit Inkonsistenzen
        inventory_transactions = self.generate_inventory_transactions()
        
        # Generiere Finanztransaktionen mit Abweichungen
        financial_transactions = self.generate_financial_transactions(sales_orders, order_items)
        
        return {
            'products': self.products,
            'customers': self.customers,
            'sales_orders': sales_orders,
            'order_items': order_items,
            'inventory_transactions': inventory_transactions,
            'financial_transactions': financial_transactions
        }

if __name__ == "__main__":
    # Generator mit 15% Fehlerrate initialisieren
    generator = BusinessDataGenerator(error_rate=0.15)
    
    # Alle Daten generieren
    data = generator.generate_all_data()
    
    # Speichere die Daten
    for name, df in data.items():
        df.to_csv(f'{name}.csv', index=False)
        
        # Zeige Statistiken
        print(f"\nStatistiken für {name}:")
        print(f"Anzahl Datensätze: {len(df)}")
        print(f"Fehlende Werte:")
        print(df.isnull().sum())
        
        if name in ['sales_orders', 'order_items', 'financial_transactions']:
            print("\nFinanzielle Übersicht:")
            if 'amount' in df.columns:
                print(f"Gesamtbetrag: {df['amount'].sum():,.2f}")
            elif 'line_total' in df.columns:
                print(f"Gesamtbetrag: {df['line_total'].sum():,.2f}")