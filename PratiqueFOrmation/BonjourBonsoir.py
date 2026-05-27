# Version compacte avec thème personnalisé
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from datetime import datetime

class BonjourAppCompacte(App):
    def build(self):
        # Configuration de la fenêtre
        from kivy.core.window import Window
        Window.clearcolor = (0.2, 0.4, 0.7, 1)  # Bleu profond
        Window.size = (600, 400)

        layout = FloatLayout()

        # Horloge en haut à droite
        horloge = Label(font_size='20sp', color=(1, 1, 0.8, 1),
                        pos_hint={'right': 0.98, 'top': 0.98})
        Clock.schedule_interval(lambda dt: setattr(horloge, 'text',
                               datetime.now().strftime("%H:%M:%S")), 1)

        # Message principal
        h = datetime.now().hour
        if 6 <= h < 12: msg = "🌅 Bonjour Monsieur"
        elif 12 <= h < 18: msg = "☀️ Bon après-midi Monsieur"
        elif 18 <= h < 22: msg = "🌙 Bonsoir Monsieur"
        else: msg = "🌙 Bonne nuit Monsieur"

        texte = Label(text=msg, font_size='35sp', bold=True, color=(1,1,1,1),
                      pos_hint={'center_x': 0.5, 'center_y': 0.6})

        # Emoji animé
        main = Label(text="👋", font_size='70sp',
                     pos_hint={'center_x': 0.5, 'center_y': 0.35})
        anim = Animation(pos_hint={'center_x': 0.55, 'center_y': 0.35}, duration=0.25) + \
               Animation(pos_hint={'center_x': 0.45, 'center_y': 0.35}, duration=0.25)
        anim.repeat = True
        anim.start(main)

        layout.add_widget(horloge)
        layout.add_widget(texte)
        layout.add_widget(main)

        return layout

BonjourAppCompacte().run()