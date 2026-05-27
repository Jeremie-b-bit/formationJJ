try:
    from kivymd.app import MDApp
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.properties import StringProperty
    from kivymd.uix.datatables import MDDataTable
    from kivymd.uix.snackbar import Snackbar
    from kivymd.uix.list import OneLineListItem
except ModuleNotFoundError as e:
    import sys
    missing = getattr(e, "name", str(e))
    print(f"Module manquant: {missing}.")
    print("Pour réparer, ouvrez PowerShell et exécutez :")
    print("  python -m pip install --upgrade pip")
    print("  python -m pip install \"kivy[base]\" kivymd")
    print("Si vous utilisez un environnement virtuel, activez-le d'abord (ex: .\\venv\\Scripts\\Activate)")
    sys.exit(1)

from datetime import datetime
import sqlite3
import os

DB_PATH = "stock.db"

KV = """
BoxLayout:
    orientation: "vertical"
    spacing: dp(10)
    padding: dp(12)

    MDTopAppBar:
        title: "Gestion Stock - Entrées/Sorties"
        elevation: 4
        size_hint_y: None
        height: dp(56)
        left_action_items: [['arrow-left', lambda x: None]]
        right_action_items: [['refresh', lambda x: app.refresh_all()]]

    ScrollView:
        do_scroll_x: False

        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(12)

            MDCard:
                size_hint_y: None
                height: dp(180)
                padding: dp(16)
                spacing: dp(12)
                elevation: 2

                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(10)

                    MDTextField:
                        id: product_name
                        hint_text: "Nom du produit"
                        mode: "rectangle"
                        icon_left: "cube-outline"
                        required: True

                    MDTextField:
                        id: qty
                        hint_text: "Quantité"
                        input_filter: "int"
                        mode: "rectangle"
                        icon_left: "numeric"
                        required: True

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(12)

                        MDRaisedButton:
                            text: "Entrée"
                            md_bg_color: app.theme_cls.primary_color
                            on_release: app.add_entry()

                        MDRaisedButton:
                            text: "Sortie"
                            md_bg_color: [0.85, 0.25, 0.25, 1]
                            on_release: app.add_exit()

            Widget:
                size_hint_y: None
                height: dp(8)

            MDCard:
                size_hint_y: None
                height: dp(220)
                padding: dp(12)
                spacing: dp(8)
                elevation: 1

                MDBoxLayout:
                    orientation: 'vertical'

                    MDLabel:
                        text: "Stock actuel"
                        font_style: 'H6'
                        size_hint_y: None
                        height: self.texture_size[1]

                    ScrollView:
                        do_scroll_x: False
                        MDList:
                            id: stock_box
                            size_hint_y: None
                            height: self.minimum_height

            Widget:
                size_hint_y: None
                height: dp(8)

            MDCard:
                size_hint_y: None
                height: dp(240)
                padding: dp(12)
                spacing: dp(8)
                elevation: 1

                MDBoxLayout:
                    orientation: 'vertical'

                    MDLabel:
                        text: "Historique"
                        font_style: 'H6'
                        size_hint_y: None
                        height: self.texture_size[1]

                    ScrollView:
                        do_scroll_x: False
                        MDList:
                            id: history_box
                            size_hint_y: None
                            height: self.minimum_height
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            qty INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

class StockApp(MDApp):
    search_text = StringProperty("")

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        init_db()
        root = Builder.load_string(KV)
        # initial refresh
        self.root = root
        self.refresh_all()
        return root

    def add_entry(self):
        print("DEBUG: add_entry called")
        try:
            name = self.root.ids.product_name.text.strip()
            qty_text = self.root.ids.qty.text.strip()
            print(f"DEBUG: name={name!r}, qty_text={qty_text!r}")
        except Exception as e:
            print("DEBUG: Error accessing fields in add_entry:", e)
            import traceback; traceback.print_exc()
            Snackbar(text="Erreur interne: impossible de lire les champs").open()
            return

        if not name:
            Snackbar(text="Entrez un nom de produit").open()
            return
        if not qty_text:
            Snackbar(text="Entrez une quantité").open()
            return

        try:
            qty = int(qty_text)
        except ValueError:
            Snackbar(text="Quantité invalide").open()
            return

        if qty <= 0:
            Snackbar(text="La quantité doit être > 0").open()
            return

        self.apply_movement(name=name, qty=qty, mtype="ENTREE")
        self.root.ids.qty.text = ""
        self.root.ids.product_name.focus = True
        self.refresh_all()
        print(f"DEBUG: add_entry completed for {qty} x {name}")
        Snackbar(text=f"Entrée: {qty} × {name}").open()

    def add_exit(self):
        print("DEBUG: add_exit called")
        try:
            name = self.root.ids.product_name.text.strip()
            qty_text = self.root.ids.qty.text.strip()
            print(f"DEBUG: name={name!r}, qty_text={qty_text!r}")
        except Exception as e:
            print("DEBUG: Error accessing fields in add_exit:", e)
            import traceback; traceback.print_exc()
            Snackbar(text="Erreur interne: impossible de lire les champs").open()
            return

        if not name:
            Snackbar(text="Entrez un nom de produit").open()
            return
        if not qty_text:
            Snackbar(text="Entrez une quantité").open()
            return

        try:
            qty = int(qty_text)
        except ValueError:
            Snackbar(text="Quantité invalide").open()
            return

        if qty <= 0:
            Snackbar(text="La quantité doit être > 0").open()
            return

        ok, msg = self.can_exit(name=name, qty=qty)
        if not ok:
            Snackbar(text=msg).open()
            return

        self.apply_movement(name=name, qty=qty, mtype="SORTIE")
        self.root.ids.qty.text = ""
        self.root.ids.product_name.focus = True
        self.refresh_all()
        print(f"DEBUG: add_exit completed for {qty} x {name}")
        Snackbar(text=f"Sortie: {qty} × {name}").open()

    def can_exit(self, name, qty):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, stock FROM products WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return False, "Produit introuvable (ajoutez d'abord une entrée)."

        product_id, stock = row
        if stock < qty:
            return False, f"Stock insuffisant. Stock actuel: {stock}"
        return True, ""

    def apply_movement(self, name, qty, mtype):
        conn = get_conn()
        cur = conn.cursor()

        # Get or create product
        cur.execute("SELECT id, stock FROM products WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            product_id, stock = row
        else:
            cur.execute("INSERT INTO products(name, stock) VALUES(?, 0)", (name,))
            product_id = cur.lastrowid
            stock = 0

        new_stock = stock + qty if mtype == "ENTREE" else stock - qty

        cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
        cur.execute(
            "INSERT INTO movements(product_id, type, qty, created_at) VALUES(?, ?, ?, ?)",
            (product_id, mtype, qty, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        conn.close()

    def refresh_all(self):
        try:
            self.refresh_stock()
            self.refresh_history()
        except Exception as e:
            print("Erreur lors du refresh:", e)

    def refresh_stock(self):
        box = self.root.ids.stock_box
        box.clear_widgets()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT name, stock
            FROM products
            ORDER BY name ASC
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            box.add_widget(OneLineListItem(text="Aucun produit pour le moment."))
            return

        for name, stock in rows:
            item = OneLineListItem(text=f"{name} : {stock}")
            box.add_widget(item)

    def refresh_history(self):
        box = self.root.ids.history_box
        box.clear_widgets()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.name, m.type, m.qty, m.created_at
            FROM movements m
            JOIN products p ON p.id = m.product_id
            ORDER BY m.id DESC
            LIMIT 50
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            box.add_widget(OneLineListItem(text="Aucun mouvement pour le moment."))
            return

        for name, mtype, qty, created_at in rows:
            sign = "+" if mtype == "ENTREE" else "-"
            ts = created_at.replace('T', ' ')
            box.add_widget(OneLineListItem(text=f"{ts} | {name} | {sign}{qty}"))


if __name__ == "__main__":
    StockApp().run(), sur cette application ajoute sur le chant de resultat le bouton pour supprimer l'article et modifier , tu me cree aussi un dashboad moderne avec les fonctionnalite qu'il faudra