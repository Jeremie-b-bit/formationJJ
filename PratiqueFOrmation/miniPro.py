try:
    from kivymd.app import MDApp
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.properties import StringProperty, ObjectProperty
    from kivy.clock import Clock
    from kivymd.uix.snackbar import Snackbar
    from kivymd.uix.list import OneLineListItem, OneLineRightIconListItem
    from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
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

# Fonctions utilitaires pour PowerShell
def log_success(message):
    print(f"\033[92m✓ {message}\033[0m")  # Vert

def log_error(message):
    print(f"\033[91m✗ {message}\033[0m")  # Rouge

def log_warning(message):
    print(f"\033[93m⚠ {message}\033[0m")  # Jaune

def log_info(message):
    print(f"\033[94mℹ {message}\033[0m")  # Bleu

def init_db():
    """Initialiser la base de données"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Table des produits
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            stock INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table des mouvements
    cur.execute('''
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('ENTREE', 'SORTIE')),
            quantity INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    conn.commit()
    conn.close()
    log_success("Base de données initialisée")

def get_conn():
    """Obtenir une connexion à la base de données"""
    return sqlite3.connect(DB_PATH)

KV_DASHBOARD = """
#:kivy 2.0

<DashboardScreen>:
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(12)
        padding: dp(12)

        MDTopAppBar:
            title: "📊 Dashboard - Gestion Stock"
            elevation: 4
            size_hint_y: None
            height: dp(56)
            right_action_items: [['refresh', lambda x: app.load_dashboard()]]

        ScrollView:
            do_scroll_x: False
            bar_width: dp(8)
            bar_color: [0.3, 0.3, 0.3, 1]
            bar_inactive_color: [0.7, 0.7, 0.7, 1]

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)
                padding: dp(8)

                # Stats Cards
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(120)
                    spacing: dp(12)

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.95, 0.95, 0.95, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📦 Produits"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.3, 0.3, 0.3, 1]

                            MDLabel:
                                id: stat_products
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.2, 0.2, 0.2, 1]

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.95, 0.95, 0.95, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📊 Stock Total"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.3, 0.3, 0.3, 1]

                            MDLabel:
                                id: stat_stock
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.2, 0.2, 0.2, 1]

                # More Stats
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(120)
                    spacing: dp(12)

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.9, 0.95, 0.9, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📈 Entrées (24h)"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.2, 0.5, 0.2, 1]

                            MDLabel:
                                id: stat_entries
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.2, 0.8, 0.2, 1]

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.95, 0.9, 0.9, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📉 Sorties (24h)"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.5, 0.2, 0.2, 1]

                            MDLabel:
                                id: stat_exits
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.8, 0.2, 0.2, 1]

                # Action Buttons
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(100)
                    spacing: dp(12)

                    MDRaisedButton:
                        text: "📦 Gérer Stock"
                        md_bg_color: app.theme_cls.primary_color
                        on_release: app.show_screen("stock")

                    MDRaisedButton:
                        text: "➕ Enregistrer Mouvement"
                        md_bg_color: [0.1, 0.7, 0.3, 1]
                        on_release: app.show_screen("entry")

                # Recent Movements
                MDCard:
                    elevation: 2
                    padding: dp(12)
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(300)
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: dp(8)

                        MDLabel:
                            text: "🕒 Mouvements Récents"
                            font_style: "H6"
                            size_hint_y: None
                            height: dp(32)
                            color: [0.3, 0.3, 0.3, 1]

                        ScrollView:
                            do_scroll_x: False
                            bar_width: dp(6)
                            bar_color: [0.5, 0.5, 0.5, 1]
                            bar_inactive_color: [0.8, 0.8, 0.8, 1]
                            MDList:
                                id: recent_movements
                                size_hint_y: None
                                height: self.minimum_height


<StockScreen>:
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(12)

        MDTopAppBar:
            title: "📦 Gestion Stock - Entrées/Sorties"
            elevation: 4
            size_hint_y: None
            height: dp(56)
            left_action_items: [['arrow-left', lambda x: app.show_screen("dashboard")]]
            right_action_items: [['refresh', lambda x: app.refresh_all()]]

        ScrollView:
            do_scroll_x: False
            bar_width: dp(8)
            bar_color: [0.3, 0.3, 0.3, 1]
            bar_inactive_color: [0.7, 0.7, 0.7, 1]

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)

                MDCard:
                    size_hint_y: None
                    height: dp(200)
                    padding: dp(16)
                    spacing: dp(12)
                    elevation: 3
                    md_bg_color: [0.95, 0.95, 0.95, 1]

                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(10)

                        MDTextField:
                            id: product_name
                            hint_text: "📝 Nom du produit"
                            mode: "rectangle"
                            icon_left: "cube-outline"
                            required: True

                        MDTextField:
                            id: qty
                            hint_text: "🔢 Quantité"
                            input_filter: "int"
                            mode: "rectangle"
                            icon_left: "numeric"
                            required: True

                        MDBoxLayout:
                            size_hint_y: None
                            height: dp(48)
                            spacing: dp(12)

                            MDRaisedButton:
                                text: "➕ Entrée"
                                md_bg_color: [0.2, 0.8, 0.2, 1]
                                on_release: app.add_entry()

                            MDRaisedButton:
                                text: "➖ Sortie"
                                md_bg_color: [0.8, 0.2, 0.2, 1]
                                on_release: app.add_exit()

                Widget:
                    size_hint_y: None
                    height: dp(8)

                MDCard:
                    size_hint_y: None
                    height: dp(350)
                    padding: dp(12)
                    spacing: dp(8)
                    elevation: 2
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        orientation: 'vertical'

                        MDLabel:
                            text: "📦 Stock actuel"
                            font_style: 'H6'
                            size_hint_y: None
                            height: self.texture_size[1]
                            color: [0.3, 0.3, 0.3, 1]

                        ScrollView:
                            do_scroll_x: False
                            bar_width: dp(6)
                            bar_color: [0.5, 0.5, 0.5, 1]
                            bar_inactive_color: [0.8, 0.8, 0.8, 1]
                            MDList:
                                id: stock_box
                                size_hint_y: None
                                height: self.minimum_height

                Widget:
                    size_hint_y: None
                    height: dp(8)

                MDCard:
                    size_hint_y: None
                    height: dp(280)
                    padding: dp(12)
                    spacing: dp(8)
                    elevation: 2
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        orientation: 'vertical'

                        MDLabel:
                            text: "📋 Historique"
                            font_style: 'H6'
                            size_hint_y: None
                            height: self.texture_size[1]
                            color: [0.3, 0.3, 0.3, 1]

                        ScrollView:
                            do_scroll_x: False
                            bar_width: dp(6)
                            bar_color: [0.5, 0.5, 0.5, 1]
                            bar_inactive_color: [0.8, 0.8, 0.8, 1]
                            MDList:
                                id: history_box
                                size_hint_y: None
                                height: self.minimum_height
"""

class DashboardScreen(MDBoxLayout):
    pass

class StockScreen(MDBoxLayout):
    pass

class StockApp(MDApp):
    search_text = StringProperty("")

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        init_db()

        # Charger le KV
        Builder.load_string(KV_DASHBOARD)

        # Créer les écrans
        self.dashboard_screen = DashboardScreen()
        self.stock_screen = StockScreen()

        # Afficher le dashboard d'abord
        self.current_screen = "dashboard"
        self.root = self.dashboard_screen

        log_success("Application démarrée avec succès")
        self.load_dashboard()
        return self.root

    def show_screen(self, screen_name):
        """Basculer entre les écrans"""
        if screen_name == "dashboard":
            self.current_screen = "dashboard"
            self.root = self.dashboard_screen
            self.load_dashboard()
            log_info("Affichage du dashboard")
        elif screen_name == "stock":
            self.current_screen = "stock"
            self.root = self.stock_screen
            self.refresh_all()
            log_info("Affichage de la gestion stock")
        elif screen_name == "entry":
            self.current_screen = "stock"
            self.root = self.stock_screen
            self.refresh_all()
            log_info("Affichage du formulaire d'entrée")

    def load_dashboard(self):
        """Charger les statistiques du dashboard"""
        try:
            conn = get_conn()
            cur = conn.cursor()

            # Nombre de produits
            cur.execute("SELECT COUNT(*) FROM products")
            products_count = cur.fetchone()[0]

            # Stock total
            cur.execute("SELECT SUM(stock) FROM products")
            total_stock = cur.fetchone()[0] or 0

            # Entrées des dernières 24h
            cur.execute("""
                SELECT SUM(quantity) FROM movements
                WHERE type = 'ENTREE' AND created_at >= datetime('now', '-1 day')
            """)
            entries_24h = cur.fetchone()[0] or 0

            # Sorties des dernières 24h
            cur.execute("""
                SELECT SUM(quantity) FROM movements
                WHERE type = 'SORTIE' AND created_at >= datetime('now', '-1 day')
            """)
            exits_24h = cur.fetchone()[0] or 0

            conn.close()

            # Mettre à jour l'interface
            self.dashboard_screen.ids.stat_products.text = str(products_count)
            self.dashboard_screen.ids.stat_stock.text = str(total_stock)
            self.dashboard_screen.ids.stat_entries.text = str(entries_24h)
            self.dashboard_screen.ids.stat_exits.text = str(exits_24h)

            # Charger les mouvements récents
            self.load_recent_movements()

            log_success("Dashboard chargé")
        except Exception as e:
            log_error(f"Erreur chargement dashboard: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_recent_movements(self):
        """Charger les mouvements récents"""
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.name, m.type, m.quantity, m.created_at
                FROM movements m
                JOIN products p ON m.product_id = p.id
                ORDER BY m.created_at DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
            conn.close()

            box = self.dashboard_screen.ids.recent_movements
            box.clear_widgets()

            if not rows:
                box.add_widget(OneLineListItem(text="Aucun mouvement pour le moment."))
                return

            for name, mtype, qty, created_at in rows:
                sign = "➕" if mtype == "ENTREE" else "➖"
                ts = created_at.replace('T', ' ')
                box.add_widget(OneLineListItem(text=f"{ts} | {name} | {sign}{qty}"))

        except Exception as e:
            log_error(f"Erreur chargement mouvements: {str(e)}")

    def add_entry(self):
        """Ajouter une entrée en stock"""
        try:
            product_name = self.stock_screen.ids.product_name.text.strip()
            qty_text = self.stock_screen.ids.qty.text.strip()

            if not product_name or not qty_text:
                Snackbar(text="Veuillez remplir tous les champs").open()
                log_warning("Champs manquants pour entrée")
                return

            qty = int(qty_text)
            if qty <= 0:
                Snackbar(text="La quantité doit être positive").open()
                log_warning("Quantité invalide pour entrée")
                return

            conn = get_conn()
            cur = conn.cursor()

            # Créer ou mettre à jour le produit
            cur.execute("INSERT OR IGNORE INTO products (name, stock) VALUES (?, 0)", (product_name,))
            cur.execute("UPDATE products SET stock = stock + ? WHERE name = ?", (qty, product_name))

            # Récupérer l'ID du produit
            cur.execute("SELECT id FROM products WHERE name = ?", (product_name,))
            product_id = cur.fetchone()[0]

            # Enregistrer le mouvement
            cur.execute("INSERT INTO movements (product_id, type, quantity) VALUES (?, 'ENTREE', ?)",
                       (product_id, qty))

            conn.commit()
            conn.close()

            Snackbar(text=f"✅ Entrée ajoutée: {product_name} (+{qty})").open()
            log_success(f"Entrée ajoutée: {product_name} +{qty}")

            # Vider les champs
            self.stock_screen.ids.product_name.text = ""
            self.stock_screen.ids.qty.text = ""

            Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)

        except ValueError:
            Snackbar(text="Quantité invalide").open()
            log_error("Quantité invalide saisie")
        except Exception as e:
            Snackbar(text=f"Erreur: {str(e)}").open()
            log_error(f"Erreur ajout entrée: {str(e)}")
            import traceback
            traceback.print_exc()

    def add_exit(self):
        """Ajouter une sortie de stock"""
        try:
            product_name = self.stock_screen.ids.product_name.text.strip()
            qty_text = self.stock_screen.ids.qty.text.strip()

            if not product_name or not qty_text:
                Snackbar(text="Veuillez remplir tous les champs").open()
                log_warning("Champs manquants pour sortie")
                return

            qty = int(qty_text)
            if qty <= 0:
                Snackbar(text="La quantité doit être positive").open()
                log_warning("Quantité invalide pour sortie")
                return

            conn = get_conn()
            cur = conn.cursor()

            # Vérifier si le produit existe et a assez de stock
            cur.execute("SELECT id, stock FROM products WHERE name = ?", (product_name,))
            result = cur.fetchone()

            if not result:
                Snackbar(text=f"Produit '{product_name}' introuvable").open()
                log_warning(f"Produit introuvable: {product_name}")
                return

            product_id, current_stock = result
            if current_stock < qty:
                Snackbar(text=f"Stock insuffisant ({current_stock} disponible)").open()
                log_warning(f"Stock insuffisant: {product_name} ({current_stock} < {qty})")
                return

            # Mettre à jour le stock
            cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))

            # Enregistrer le mouvement
            cur.execute("INSERT INTO movements (product_id, type, quantity) VALUES (?, 'SORTIE', ?)",
                       (product_id, qty))

            conn.commit()
            conn.close()

            Snackbar(text=f"✅ Sortie enregistrée: {product_name} (-{qty})").open()
            log_success(f"Sortie enregistrée: {product_name} -{qty}")

            # Vider les champs
            self.stock_screen.ids.product_name.text = ""
            self.stock_screen.ids.qty.text = ""

            Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)

        except ValueError:
            Snackbar(text="Quantité invalide").open()
            log_error("Quantité invalide saisie")
        except Exception as e:
            Snackbar(text=f"Erreur: {str(e)}").open()
            log_error(f"Erreur ajout sortie: {str(e)}")
            import traceback
            traceback.print_exc()

    def refresh_stock(self):
        """Rafraîchir l'affichage du stock"""
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id, name, stock FROM products ORDER BY name")
            products = cur.fetchall()
            conn.close()

            box = self.stock_screen.ids.stock_box
            box.clear_widgets()

            if not products:
                box.add_widget(OneLineListItem(text="Aucun produit en stock."))
                return

            for product_id, name, stock in products:
                # Créer un item avec boutons modifier/supprimer
                item_layout = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(48),
                    padding=[dp(8), 0]
                )

                # Label du produit
                label = MDLabel(
                    text=f"{name}: {stock}",
                    size_hint_x=0.6,
                    valign="center"
                )
                label.bind(size=label.setter('text_size'))
                item_layout.add_widget(label)

                # Boutons d'action
                buttons_layout = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_x=0.4,
                    spacing=dp(4)
                )

                edit_btn = MDIconButton(
                    icon="pencil",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    md_bg_color=[0.2, 0.6, 0.9, 1],
                    on_release=lambda x, pid=product_id, pname=name: self.edit_product_qty(pid, pname)
                )

                delete_btn = MDIconButton(
                    icon="delete",
                    size_hint=(None, None),
                    size=(dp(36), dp(36)),
                    md_bg_color=[0.9, 0.2, 0.2, 1],
                    on_release=lambda x, pid=product_id, pname=name: self.delete_product(pid, pname)
                )

                buttons_layout.add_widget(edit_btn)
                buttons_layout.add_widget(delete_btn)
                item_layout.add_widget(buttons_layout)

                box.add_widget(item_layout)

        except Exception as e:
            log_error(f"Erreur refresh stock: {str(e)}")
            import traceback
            traceback.print_exc()

    def refresh_history(self):
        """Rafraîchir l'historique des mouvements"""
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT p.name, m.type, m.quantity, m.created_at
                FROM movements m
                JOIN products p ON m.product_id = p.id
                ORDER BY m.created_at DESC
                LIMIT 20
            """)
            rows = cur.fetchall()
            conn.close()

            box = self.stock_screen.ids.history_box
            box.clear_widgets()

            if not rows:
                box.add_widget(OneLineListItem(text="Aucun mouvement enregistré."))
                return

            for name, mtype, qty, created_at in rows:
                sign = "➕" if mtype == "ENTREE" else "➖"
                ts = created_at.replace('T', ' ')
                box.add_widget(OneLineListItem(text=f"{ts} | {name} | {sign}{qty}"))

        except Exception as e:
            log_error(f"Erreur refresh historique: {str(e)}")
            import traceback
            traceback.print_exc()

    def edit_product_qty(self, product_id, product_name):
        """Modifier la quantité d'un produit"""
        dialog = MDDialog(
            title=f"Modifier {product_name}",
            type="custom",
            content_cls=MDBoxLayout(),
            size_hint=(0.8, None),
            height=dp(200)
        )

        qty_input = MDTextField(
            hint_text="Nouvelle quantité",
            input_filter="int",
            text="",
            size_hint_y=None,
            height=dp(48)
        )

        dialog_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(12),
            size_hint_y=None,
            height=dp(120)
        )
        dialog_content.add_widget(qty_input)

        def confirm_edit(instance):
            try:
                new_qty = int(qty_input.text)
                if new_qty < 0:
                    Snackbar(text="La quantité ne peut pas être négative").open()
                    log_warning("Quantité négative refusée")
                    return

                conn = get_conn()
                cur = conn.cursor()
                cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_qty, product_id))
                conn.commit()
                conn.close()

                Snackbar(text=f"✅ {product_name} modifié ({new_qty})").open()
                log_success(f"Produit modifié: {product_name} -> {new_qty}")
                Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)
                dialog.dismiss()
            except Exception as e:
                Snackbar(text=f"Erreur: {str(e)}").open()
                log_error(f"Erreur modification: {str(e)}")
                import traceback
                traceback.print_exc()

        def cancel_edit(instance):
            dialog.dismiss()

        dialog.buttons = [
            MDFlatButton(text="Annuler", on_release=cancel_edit),
            MDRaisedButton(text="Modifier", on_release=confirm_edit)
        ]

        dialog.open()

    def delete_product(self, product_id, product_name):
        """Supprimer un produit"""
        def confirm_delete(instance):
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()

                Snackbar(text=f"🗑️ {product_name} supprimé").open()
                log_success(f"Produit supprimé: {product_name}")
                Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)
                dialog.dismiss()
            except Exception as e:
                Snackbar(text=f"Erreur: {str(e)}").open()
                log_error(f"Erreur suppression: {str(e)}")
                import traceback
                traceback.print_exc()

        def cancel_delete(instance):
            dialog.dismiss()

        dialog = MDDialog(
            title="Confirmer la suppression",
            text=f"Êtes-vous sûr de vouloir supprimer '{product_name}' ?",
            buttons=[
                MDFlatButton(text="Annuler", on_release=cancel_delete),
                MDRaisedButton(text="Supprimer", md_bg_color=[0.8, 0.2, 0.2, 1], on_release=confirm_delete)
            ]
        )
        dialog.open()

    def refresh_all(self):
        """Rafraîchir tous les éléments de l'interface"""
        try:
            self.refresh_stock()
            self.refresh_history()
        except Exception as e:
            log_error(f"Erreur refresh: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":

    from kivymd.app import MDApp
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.properties import StringProperty, ObjectProperty
    from kivy.clock import Clock
    from kivymd.uix.snackbar import Snackbar
    from kivymd.uix.list import OneLineListItem, OneLineRightIconListItem
    from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.gridlayout import GridLayout
    #except ModuleNotFoundError as e:
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

# Fonctions utilitaires pour PowerShell
def log_success(message):
    print(f"\033[92m✓ {message}\033[0m")  # Vert

def log_error(message):
    print(f"\033[91m✗ {message}\033[0m")  # Rouge

def log_warning(message):
    print(f"\033[93m⚠ {message}\033[0m")  # Jaune

def log_info(message):
    print(f"\033[94mℹ {message}\033[0m")  # Bleu

KV_DASHBOARD = """
#:kivy 2.0

<DashboardScreen>:
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(12)
        padding: dp(12)

        MDTopAppBar:
            title: "📊 Dashboard - Gestion Stock"
            elevation: 4
            size_hint_y: None
            height: dp(56)
            right_action_items: [['refresh', lambda x: app.load_dashboard()]]

        ScrollView:
            do_scroll_x: False
            bar_width: dp(8)
            bar_color: [0.3, 0.3, 0.3, 1]
            bar_inactive_color: [0.7, 0.7, 0.7, 1]

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)
                padding: dp(8)

                # Stats Cards
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(120)
                    spacing: dp(12)

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.95, 0.95, 0.95, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📦 Produits"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.3, 0.3, 0.3, 1]

                            MDLabel:
                                id: stat_products
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.2, 0.2, 0.2, 1]

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.95, 0.95, 0.95, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📊 Stock Total"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.3, 0.3, 0.3, 1]

                            MDLabel:
                                id: stat_stock
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.2, 0.2, 0.2, 1]

                # More Stats
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(120)
                    spacing: dp(12)

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.9, 0.95, 0.9, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📈 Entrées (24h)"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.2, 0.5, 0.2, 1]

                            MDLabel:
                                id: stat_entries
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.2, 0.8, 0.2, 1]

                    MDCard:
                        elevation: 3
                        padding: dp(12)
                        spacing: dp(8)
                        md_bg_color: [0.95, 0.9, 0.9, 1]

                        MDBoxLayout:
                            orientation: "vertical"

                            MDLabel:
                                text: "📉 Sorties (24h)"
                                font_style: "Caption"
                                size_hint_y: None
                                height: dp(20)
                                color: [0.5, 0.2, 0.2, 1]

                            MDLabel:
                                id: stat_exits
                                text: "0"
                                font_style: "H5"
                                bold: True
                                size_hint_y: None
                                height: dp(40)
                                color: [0.8, 0.2, 0.2, 1]

                # Action Buttons
                GridLayout:
                    cols: 2
                    size_hint_y: None
                    height: dp(100)
                    spacing: dp(12)

                    MDRaisedButton:
                        text: "📦 Gérer Stock"
                        md_bg_color: app.theme_cls.primary_color
                        on_release: app.show_screen("stock")

                    MDRaisedButton:
                        text: "➕ Enregistrer Mouvement"
                        md_bg_color: [0.1, 0.7, 0.3, 1]
                        on_release: app.show_screen("entry")

                # Recent Movements
                MDCard:
                    elevation: 2
                    padding: dp(12)
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(300)
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        orientation: "vertical"
                        spacing: dp(8)

                        MDLabel:
                            text: "🕒 Mouvements Récents"
                            font_style: "H6"
                            size_hint_y: None
                            height: dp(32)
                            color: [0.3, 0.3, 0.3, 1]

                        ScrollView:
                            do_scroll_x: False
                            bar_width: dp(6)
                            bar_color: [0.5, 0.5, 0.5, 1]
                            bar_inactive_color: [0.8, 0.8, 0.8, 1]
                            MDList:
                                id: recent_movements
                                size_hint_y: None
                                height: self.minimum_height


<StockScreen>:
    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(10)
        padding: dp(12)

        MDTopAppBar:
            title: "📦 Gestion Stock - Entrées/Sorties"
            elevation: 4
            size_hint_y: None
            height: dp(56)
            left_action_items: [['arrow-left', lambda x: app.show_screen("dashboard")]]
            right_action_items: [['refresh', lambda x: app.refresh_all()]]

        ScrollView:
            do_scroll_x: False
            bar_width: dp(8)
            bar_color: [0.3, 0.3, 0.3, 1]
            bar_inactive_color: [0.7, 0.7, 0.7, 1]

            MDBoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(12)

                MDCard:
                    size_hint_y: None
                    height: dp(200)
                    padding: dp(16)
                    spacing: dp(12)
                    elevation: 3
                    md_bg_color: [0.95, 0.95, 0.95, 1]

                    MDBoxLayout:
                        orientation: 'vertical'
                        spacing: dp(10)

                        MDTextField:
                            id: product_name
                            hint_text: "📝 Nom du produit"
                            mode: "rectangle"
                            icon_left: "cube-outline"
                            required: True

                        MDTextField:
                            id: qty
                            hint_text: "🔢 Quantité"
                            input_filter: "int"
                            mode: "rectangle"
                            icon_left: "numeric"
                            required: True

                        MDBoxLayout:
                            size_hint_y: None
                            height: dp(48)
                            spacing: dp(12)

                            MDRaisedButton:
                                text: "➕ Entrée"
                                md_bg_color: [0.2, 0.8, 0.2, 1]
                                on_release: app.add_entry()

                            MDRaisedButton:
                                text: "➖ Sortie"
                                md_bg_color: [0.8, 0.2, 0.2, 1]
                                on_release: app.add_exit()

                Widget:
                    size_hint_y: None
                    height: dp(8)

                MDCard:
                    size_hint_y: None
                    height: dp(350)
                    padding: dp(12)
                    spacing: dp(8)
                    elevation: 2
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        orientation: 'vertical'

                        MDLabel:
                            text: "📦 Stock actuel"
                            font_style: 'H6'
                            size_hint_y: None
                            height: self.texture_size[1]
                            color: [0.3, 0.3, 0.3, 1]

                        ScrollView:
                            do_scroll_x: False
                            bar_width: dp(6)
                            bar_color: [0.5, 0.5, 0.5, 1]
                            bar_inactive_color: [0.8, 0.8, 0.8, 1]
                            MDList:
                                id: stock_box
                                size_hint_y: None
                                height: self.minimum_height

                Widget:
                    size_hint_y: None
                    height: dp(8)

                MDCard:
                    size_hint_y: None
                    height: dp(280)
                    padding: dp(12)
                    spacing: dp(8)
                    elevation: 2
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        orientation: 'vertical'

                        MDLabel:
                            text: "📋 Historique"
                            font_style: 'H6'
                            size_hint_y: None
                            height: self.texture_size[1]
                            color: [0.3, 0.3, 0.3, 1]

                        ScrollView:
                            do_scroll_x: False
                            bar_width: dp(6)
                            bar_color: [0.5, 0.5, 0.5, 1]
                            bar_inactive_color: [0.8, 0.8, 0.8, 1]
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

class DashboardScreen(MDBoxLayout):
    pass

class StockScreen(MDBoxLayout):
    pass

class StockApp(MDApp):
    search_text = StringProperty("")

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "500"
        init_db()

        # Charger le KV
        self.root = Builder.load_string(KV_DASHBOARD)
        self.root.clear_widgets()

        # Créer les écrans
        self.dashboard_screen = DashboardScreen()
        self.stock_screen = StockScreen()

        Builder.load_string(KV_DASHBOARD)
        self.dashboard_screen = DashboardScreen()
        self.stock_screen = StockScreen()

        # Afficher le dashboard d'abord
        self.current_screen = "dashboard"
        self.root.add_widget(self.dashboard_screen)

        log_success("Application démarrée avec succès")
        self.load_dashboard()
        return self.root

    def show_screen(self, screen_name):
        """Basculer entre les écrans"""
        self.root.clear_widgets()

        if screen_name == "dashboard":
            self.current_screen = "dashboard"
            self.root.add_widget(self.dashboard_screen)
            self.load_dashboard()
            log_info("Affichage du dashboard")
        elif screen_name == "stock":
            self.current_screen = "stock"
            self.root.add_widget(self.stock_screen)
            self.refresh_all()
            log_info("Affichage de la gestion stock")
        elif screen_name == "entry":
            self.current_screen = "stock"
            self.root.add_widget(self.stock_screen)
            self.refresh_all()
            log_info("Affichage du formulaire d'entrée")

    def load_dashboard(self):
        """Charger les données du dashboard"""
        try:
            conn = get_conn()
            cur = conn.cursor()

            # Nombre de produits
            cur.execute("SELECT COUNT(*) FROM products")
            nb_products = cur.fetchone()[0]

            # Stock total
            cur.execute("SELECT SUM(stock) FROM products")
            total_stock = cur.fetchone()[0] or 0

            # Entrées du jour
            cur.execute("""
                SELECT SUM(qty) FROM movements
                WHERE type = 'ENTREE' AND DATE(created_at) = DATE('now')
            """)
            entries_today = cur.fetchone()[0] or 0

            # Sorties du jour
            cur.execute("""
                SELECT SUM(qty) FROM movements
                WHERE type = 'SORTIE' AND DATE(created_at) = DATE('now')
            """)
            exits_today = cur.fetchone()[0] or 0

            # Mouvements récents
            cur.execute("""
                SELECT p.name, m.type, m.qty, m.created_at
                FROM movements m
                JOIN products p ON p.id = m.product_id
                ORDER BY m.id DESC
                LIMIT 10
            """)
            movements = cur.fetchall()
            conn.close()

            # Mettre à jour les labels
            self.dashboard_screen.ids.stat_products.text = str(nb_products)
            self.dashboard_screen.ids.stat_stock.text = str(total_stock)
            self.dashboard_screen.ids.stat_entries.text = str(entries_today)
            self.dashboard_screen.ids.stat_exits.text = str(exits_today)

            # Mettre à jour les mouvements récents
            box = self.dashboard_screen.ids.recent_movements
            box.clear_widgets()

            if not movements:
                box.add_widget(OneLineListItem(text="Aucun mouvement récent"))
                return

            for name, mtype, qty, created_at in movements:
                sign = "➕" if mtype == "ENTREE" else "➖"
                ts = created_at.replace('T', ' ')[:16]
                box.add_widget(OneLineListItem(text=f"{ts} | {name} | {sign}{qty}"))

            log_success(f"Dashboard mis à jour: {nb_products} produits, {total_stock} en stock")

        except Exception as e:
            log_error(f"Erreur load_dashboard: {e}")
            import traceback
            traceback.print_exc()

    def add_entry(self):
        try:
            name = self.stock_screen.ids.product_name.text.strip()
            qty_text = self.stock_screen.ids.qty.text.strip()

            if not name:
                Snackbar(text="Entrez un nom de produit").open()
                log_warning("Nom de produit manquant")
                return
            if not qty_text:
                Snackbar(text="Entrez une quantité").open()
                log_warning("Quantité manquante")
                return

            qty = int(qty_text)
            if qty <= 0:
                Snackbar(text="La quantité doit être > 0").open()
                log_warning("Quantité invalide")
                return

            self.apply_movement(name=name, qty=qty, mtype="ENTREE")
            self.stock_screen.ids.qty.text = ""
            self.stock_screen.ids.product_name.text = ""
            self.stock_screen.ids.product_name.focus = True
            self.refresh_all()
            log_success(f"Entrée ajoutée: {qty} × {name}")
            Snackbar(text=f"➕ Entrée: {qty} × {name}").open()

        except ValueError as e:
            log_error(f"Erreur de valeur: {e}")
            Snackbar(text="Quantité invalide").open()
        except Exception as e:
            log_error(f"Erreur add_entry: {e}")
            import traceback
            traceback.print_exc()
            Snackbar(text="Erreur interne").open()

    def add_exit(self):
        try:
            name = self.stock_screen.ids.product_name.text.strip()
            qty_text = self.stock_screen.ids.qty.text.strip()

            if not name:
                Snackbar(text="Entrez un nom de produit").open()
                log_warning("Nom de produit manquant")
                return
            if not qty_text:
                Snackbar(text="Entrez une quantité").open()
                log_warning("Quantité manquante")
                return

            qty = int(qty_text)
            if qty <= 0:
                Snackbar(text="La quantité doit être > 0").open()
                log_warning("Quantité invalide")
                return

            ok, msg = self.can_exit(name=name, qty=qty)
            if not ok:
                Snackbar(text=msg).open()
                log_warning(f"Sortie impossible: {msg}")
                return

            self.apply_movement(name=name, qty=qty, mtype="SORTIE")
            self.stock_screen.ids.qty.text = ""
            self.stock_screen.ids.product_name.text = ""
            self.stock_screen.ids.product_name.focus = True
            self.refresh_all()
            log_success(f"Sortie ajoutée: {qty} × {name}")
            Snackbar(text=f"➖ Sortie: {qty} × {name}").open()

        except ValueError as e:
            log_error(f"Erreur de valeur: {e}")
            Snackbar(text="Quantité invalide").open()
        except Exception as e:
            log_error(f"Erreur add_exit: {e}")
            import traceback
            traceback.print_exc()
            Snackbar(text="Erreur interne").open()

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

    def delete_product(self, product_id, product_name):
        """Supprimer un produit"""
        def confirm_delete(instance):
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM movements WHERE product_id = ?", (product_id,))
                cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()
                Snackbar(text=f"✓ {product_name} supprimé").open()
                log_success(f"Produit supprimé: {product_name}")
                Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)
                dialog.dismiss()
            except Exception as e:
                log_error(f"Erreur delete: {e}")
                import traceback
                traceback.print_exc()
                Snackbar(text=f"Erreur: {str(e)}").open()
                dialog.dismiss()

        try:
            dialog = MDDialog(
                title=f"Supprimer {product_name}?",
                text="Cette action ne peut pas être annulée.",
                buttons=[
                    MDFlatButton(text="Annuler", on_release=lambda x: dialog.dismiss()),
                    MDRaisedButton(text="Supprimer", on_release=confirm_delete)
                ]
            )
            dialog.open()
        except Exception as e:
            log_error(f"Erreur dialog: {e}")
            import traceback
            traceback.print_exc()

    def edit_product_qty(self, product_id, product_name, current_qty):
        """Modifier la quantité d'un produit"""
        try:
            qty_input = MDTextField(
                hint_text="Nouvelle quantité",
                mode="rectangle",
                input_filter="int",
                text=str(current_qty),
                size_hint_y=None,
                height=dp(56)
            )

            dialog_content = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                padding=dp(12),
                size_hint_y=None,
                height=dp(120)
            )
            dialog_content.add_widget(qty_input)

            def confirm_edit(instance):
                try:
                    new_qty = int(qty_input.text)
                    if new_qty < 0:
                        Snackbar(text="La quantité ne peut pas être négative").open()
                        log_warning("Quantité négative refusée")
                        return

                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("UPDATE products SET stock = ? WHERE id = ?", (new_qty, product_id))
                    conn.commit()
                    conn.close()

                    Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)
                    dialog.dismiss()
                except Exception as e:
                    Snackbar(text=f"Erreur: {str(e)}").open()
                    log_error(f"Erreur modification: {str(e)}")
                    import traceback
                    traceback.print_exc()

            def cancel_edit(instance):
                dialog.dismiss()

            dialog.buttons = [
                MDFlatButton(text="Annuler", on_release=cancel_edit),
                MDRaisedButton(text="Modifier", on_release=confirm_edit)
            ]

            dialog.open()

    def delete_product(self, product_id, product_name):
        """Supprimer un produit"""
        def confirm_delete(instance):
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()

                Snackbar(text=f"??? {product_name} supprim�").open()
                log_success(f"Produit supprim�: {product_name}")
                Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)
                dialog.dismiss()
            except Exception as e:
                Snackbar(text=f"Erreur: {str(e)}").open()
                log_error(f"Erreur suppression: {str(e)}")
                import traceback
                traceback.print_exc()

        def cancel_delete(instance):
            dialog.dismiss()

        dialog = MDDialog(
            title="Confirmer la suppression",
            text=f"�tes-vous s�r de vouloir supprimer '{product_name}' ?",
            buttons=[
                MDFlatButton(text="Annuler", on_release=cancel_delete),
                MDRaisedButton(text="Supprimer", md_bg_color=[0.8, 0.2, 0.2, 1], on_release=confirm_delete)
            ]
        )
        dialog.open()

    def refresh_all(self):
        """Rafra�chir tous les �l�ments de l'interface"""
        try:
            self.refresh_stock()
            self.refresh_history()
        except Exception as e:
            log_error(f"Erreur refresh: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    StockApp().run()
                    Clock.schedule_once(lambda dt: self.refresh_all(), 0.1)
                    dialog.dismiss()
                except ValueError as e:
                    log_error(f"ValueError edit: {e}")
                    Snackbar(text="Quantité invalide").open()
                except Exception as e:
                    log_error(f"Erreur edit: {e}")
                    import traceback
                    traceback.print_exc()
                    Snackbar(text=f"Erreur: {str(e)}").open()

            dialog = MDDialog(
                title=f"Modifier {product_name}",
                type="custom",
                content_cls=dialog_content,
                buttons=[
                    MDFlatButton(text="Annuler", on_release=lambda x: dialog.dismiss()),
                    MDRaisedButton(text="Modifier", on_release=confirm_edit)
                ]
            )
            dialog.open()
        except Exception as e:
            log_error(f"Erreur dialog edit: {e}")
            import traceback
            traceback.print_exc()

    def refresh_all(self):
        try:
            if self.current_screen == "stock":
                self.refresh_stock()
                self.refresh_history()
            else:
                self.load_dashboard()
        except Exception as e:
            log_error(f"Erreur refresh_all: {e}")

    def refresh_stock(self):
        box = self.stock_screen.ids.stock_box
        box.clear_widgets()

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, stock
            FROM products
            ORDER BY name ASC
        """)
        rows = cur.fetchall()
        conn.close()

        if not rows:
            box.add_widget(OneLineListItem(text="Aucun produit pour le moment."))
            return

        for product_id, name, stock in rows:
            # Créer un layout horizontal avec le texte à gauche et les boutons à droite
            item_layout = MDBoxLayout(
                size_hint_y=None,
                height=dp(48),
                padding=dp(8),
                spacing=dp(4)
            )

            # Texte du produit à gauche
            label = MDLabel(
                text=f"{name}  :  {stock} unités",
                size_hint_x=0.7,
                valign="center"
            )
            item_layout.add_widget(label)

            # Bouton modifier (bleu)
            btn_edit = MDIconButton(
                icon="pencil",
                theme_text_color="Custom",
                text_color=[0.2, 0.6, 1, 1],
                size_hint_x=0.15,
                icon_size="24sp"
            )
            btn_edit.bind(on_release=lambda x, pid=product_id, pn=name, q=stock: self.edit_product_qty(pid, pn, q))
            item_layout.add_widget(btn_edit)

            # Bouton supprimer (rouge)
            btn_delete = MDIconButton(
                icon="delete",
                theme_text_color="Custom",
                text_color=[1, 0.3, 0.3, 1],
                size_hint_x=0.15,
                icon_size="24sp"
            )
            btn_delete.bind(on_release=lambda x, pid=product_id, pn=name: self.delete_product(pid, pn))
            item_layout.add_widget(btn_delete)

            # Ajouter le layout à la boîte
            box.add_widget(item_layout)

    def refresh_history(self):
        box = self.stock_screen.ids.history_box
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
            sign = "➕" if mtype == "ENTREE" else "➖"
            ts = created_at.replace('T', ' ')
            box.add_widget(OneLineListItem(text=f"{ts} | {name} | {sign}{qty}"))


if __name__ == "__main__":
    StockApp().run()try:
    
