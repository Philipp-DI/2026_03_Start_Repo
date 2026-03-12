# Multiplayer Functionality
import json
import random as rd
import pathlib as p
import datetime as dt
import xml.etree.ElementTree as et
import yaml

class Player:
    def __init__(self, name: str):
        self.name: str = str(name)
        self.score: int = 0
        
    def update_score(self, points: int):
        self.score += points

    def __str__(self) -> str:
        return f"{self.name}: {self.score} Punkte"

class Dice:
    def __init__(self, face: int) -> None:
        self.face: int = int(face)
        

    def rolling(self, rolls: int, stats_object):
        for _ in range(rolls):
            result = rd.randint(1, self.face)
            stats_object.get_roll(result)
            self.last_result = result
        return rolls
        
class Statistics:
    SAVE_PATH = p.Path('saves')
    SAVE_PATH.mkdir(exist_ok=True)
    SAVE_FORMATS = {
        'json': json.dump,
        'yaml': yaml.safe_dump,
        'xml': et.Element
    }
    LOAD_FORMATS = {
        'json': lambda f: json.load(f),
        'yaml': lambda f: yaml.safe_load(f),
        'xml': lambda f: et.parse(f).getroot()
    }
    
    def __init__(self, save, results: dict) -> None:
        self.save: str = str(save)
        self.results: dict = dict(results)
        self.rolls_total: int = sum(results.values())
        self.dirty = False
        
    @property # Funktionen, die wie eine Variable genutzt werden können.
    def score(self):
        return sum((int(k) * v) for k, v in self.results.items())

    @property
    def relative(self):
        if self.rolls_total == 0: return {}
        return {k: v / self.rolls_total for k, v in sorted(self.results.items())}

    def get_roll(self, result: int):
        self.results[result] += 1
        self.rolls_total += 1
        self.dirty = True
    
    def display(self):
        print(f"\nStatistik: '{self.save}'")
        print(f"Gesamtrolls der Würfe: {self.rolls_total}")
        if self.rolls_total > 0:
            print(f" {'face':^5} | {'rolls':^7} | {'relative Häufigkeit':^8}")
            print("="*38)
            for k, v in self.results.items():
                rh = v / self.rolls_total
                print(f"  {k:^4} |  {v:^6} | {rh:^10.2%}")
                print("-"*38)
        else:
            print("Noch keine Daten vorhanden.")
    
    @classmethod
    def new_dice_face(cls, face):
        empty_dict = dict.fromkeys(range(1, face + 1), 0)
        return cls(f"{face}-Augen-Spiel", empty_dict)
        
    # Speichern bleibt Instanz, da es die aktuellen Objektdaten benötigt.
    def saving(self, filename: str, fileformat: str):
        full_path = self.SAVE_PATH / f'{filename}.{fileformat}'
        
        if fileformat == 'xml': # Speicherblock für XML
            root = et.Element('data')
            
            results_xml = et.SubElement(root, 'resultse')
            for w_seite, rolls in self.results.items():
                child = et.SubElement(results_xml, f"f{w_seite}")
                child.text = str(rolls)
                
            tree = et.ElementTree(root)
            et.indent(tree, space="  ")
            tree.write(f"{full_path}")
            
        elif fileformat in ['json', 'yaml']: # Struktur, damit .dump nicht wiederholt werden muss
            if (s_function := self.SAVE_FORMATS.get(fileformat)):
                with open(full_path, 'w') as f:
                    s_function(self.results, f, sort_keys=True, indent=4)
        self.dirty = False
        print(f"Erfolgreich unter '{full_path}' gespeichert.")

    # Laden als Klassenmethode (Fabrik) die ein neues Objekt erstellt anhand externer Daten
    @classmethod
    def laden(cls, filename: str):
        # Pfad robust machen:
        path = p.Path(filename)
        if not path.is_absolute() and cls.SAVE_PATH not in path.parents:
            path = cls.SAVE_PATH / path
        fileformat = path.suffix.lstrip('.')
        
        if (l_function := cls.LOAD_FORMATS.get(fileformat)):
            try:
                if fileformat == 'xml': # XML laden Block
                    with open(path, 'r') as f:
                        root = l_function(f)
                        result_node = root.find('results')
                        data = {int(n.tag[1:]): int(n.text or 0) for n in result_node} if result_node is not None else {}
                    
                elif fileformat in ['json', 'yaml']:
                    
                        with open(path, 'r') as f:
                            data = l_function(f)
                else:
                    data = {}
                            
                return cls(path.stem, data)
            
            except FileNotFoundError:
                print(f"Dateifehle.")
            except Exception as e:
                print(f"Unerwarteter Fehler: {e}")
            return None

timestring: str = str(dt.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss'))

if __name__ == '__main__':
    dice = Dice(6)
    empty_dict = dict.fromkeys(range(1, dice.face +1), 0)
    current_save = Statistics('neu', empty_dict)
    
    print(f"--- Willkommen im Würfel-Imperium! ---\n[Enter] zum Würfeln oder [Zahl] für Durchgänge, [S] Statistiken, [K] Würfel konfigurieren\n[D] Dateiverwaltung, [Q] Beenden:\n")
    while True:
        mainmenu_choice = input(">Hauptmenü< Warte auf Input: ").strip().lower()
        
        if mainmenu_choice == '':
            dice.rolling(1, current_save)
            print(f"{dice.face}-seitiger Würfel: 🎲 {dice.last_result}!\nWürfe insgesamt: {current_save.rolls_total}")
        elif mainmenu_choice == 'q':
            print("Mach's gut. Ciao!")
            exit()
        elif mainmenu_choice == 's':
            current_save.display()
            
        elif mainmenu_choice == 'd':
            save_load = input(f"Speichern [S] oder Laden [L]?\n")
            if save_load == 's':
                print(f"Zunächst das Format zum Speichern wählen! Verfügbare Formate: ", list(Statistics.SAVE_FORMATS.keys()))
                fileformat = input("Eingabe: ").strip().lower()
                if fileformat in Statistics.SAVE_FORMATS:
                    use_format: str = str(fileformat)
                    print(f"{use_format} gewählt!")
                    name = input(f"Dateinamen eingeben oder einfach [Enter] um automatisch zu generieren:\n").strip()
                    filename = name if name != '' else timestring
                    current_save.saving(filename, use_format)
                else: print("Ungültige Eingabe. Nix gespeichert.")
                
            elif save_load == 'l':
                saves = list(Statistics.SAVE_PATH.glob('*.*'))
                
                if not saves:
                    print("Keine Spielstände gefunden.")
                else:
                    print("\nVerfügbare Spielstände:")
                    for i, datei in enumerate(saves, 1):
                        print(f"[{i}] {datei.name}")
                    
                    choice = input("\nWelche Datei möchtest du laden? (Nummer eingeben):\n")
                    
                    if choice.isdigit() and 1 <= int(choice) <= len(saves):
                        chosen_file = saves[int(choice) - 1]
                        loaded = Statistics.laden(str(chosen_file))
                        if loaded is not None:
                            current_save = loaded
                            neue_face = max(current_save.results.keys())
                            dice = Dice(neue_face)
                            print(f"'{chosen_file}' wurde erfolgreich geladen. Würfel hat nun {neue_face} face.")
                        else:
                            print("Laden fehlgeschlagen!")
                    else: print("Ungültige Auswahl.")

def new_game(num_players: int):
    players = []
    for i in range(num_players):
        valid_name = False
        while not valid_name:
            name: str = str(input(f"Name Spieler {i + 1}: "))
            if name.isalpha():
                players.append(Player(name))
                print(f"'{name}' hinzugefügt.")
                valid_name = True
            else:
                print("Ungültiger Name. Nur Buchstaben erlaubt. Bitte erneut eingeben.")
                valid_name = False            
    return players
        
if __name__ == "__main__":
    menu = True
    while menu:
        loading = input("save laden? [L]aden oder [N]eu starten: ").strip().lower()
        if loading == 'l':
            players = Player.load()
            if players:
                print("save geladen:")
                for player in players:
                    print(f"{player.name}: {player.score} Punkte")
                game_loop(players)
                menu = False
        elif loading == 'n':
            print("Neues Spiel gestartet.")
            num_players = int(input("rolls der Spieler: "))
            if 99 > num_players > 0:
                players = new_game(num_players)
                if players:
                    print("Starte das Spiel mit folgenden Spielern:")
                    for player in players:
                        print(f"- {player.name}")
                    game_loop(players)
                    menu = False
            else: print("Ganze Zahl zwischen 1 und 99, du Nuss!")
        else: print("Ungültige Eingabe. [L] oder [N] du Nuss!")