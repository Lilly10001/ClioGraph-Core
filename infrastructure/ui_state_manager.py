# -*- coding: utf-8 -*-
"""
ClioGraph - UI State Manager (Synchronized Undo / Redo)
Verwaltet Snapshots des UI-Schemas UND der physischen JSON-Sprachdateien.
Garantiert, dass Sprach-IDs und GUI-Elemente immer synchron zurückgesetzt werden.
"""
import copy
import os
import json
import infrastructure.cfg as cfg

class UIStateManager:
    def __init__(self, translation_service=None):
        self._undo_stack = []
        self._redo_stack = []
        self._i18n = translation_service
        self.save_checkpoint()

    def save_checkpoint(self):
        """Schiesst ein synchronisiertes Backup-Foto von Schema und Übersetzungen."""
        snapshot = {
            "ui_schema": copy.deepcopy(cfg.UI_SCHEMA),
            "translations": {}
        }
        
        # Falls der Übersetzungsservice bereitsteht, sichern wir den aktuellen RAM-Zustand der Sprachen
        if self._i18n and hasattr(self._i18n, "_translations"):
            snapshot["translations"] = copy.deepcopy(self._i18n._translations)
            
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    def undo_action(self):
        """Geht exakt einen Schritt im System-Designer zurück (Sichert den Live-Zustand)."""
        if self._undo_stack:
            # 1. Sichere den AKTUELLEN Live-Zustand vom Bildschirm für das Redo
            current_live = {
                "ui_schema": copy.deepcopy(cfg.UI_SCHEMA),
                "translations": copy.deepcopy(self._i18n._translations) if self._i18n else {}
            }
            self._redo_stack.append(current_live)
            
            # 2. Hole den exakt vorherigen Zustand vom Undo-Stapel
            previous = self._undo_stack.pop()
            
            # 3. Überschreibe das Schema ohne Referenzverlust
            cfg.UI_SCHEMA.clear()
            cfg.UI_SCHEMA.update(copy.deepcopy(previous["ui_schema"]))
            
            # Synchronisiere Sprachdateien
            if self._i18n and previous["translations"]:
                self._i18n._translations = copy.deepcopy(previous["translations"])
                self._write_translations_to_disk()
            
            return True
        return False

    def redo_action(self):
        """Wiederholt exakt einen Layout-Schritt (Sichert den Live-Zustand)."""
        if self._redo_stack:
            # 1. Sichere den aktuellen Zustand vor dem Sprung auf den Undo-Stapel
            current_live = {
                "ui_schema": copy.deepcopy(cfg.UI_SCHEMA),
                "translations": copy.deepcopy(self._i18n._translations) if self._i18n else {}
            }
            self._undo_stack.append(current_live)
            
            # 2. Hole den Zustand aus der Zukunft
            future = self._redo_stack.pop()
            
            # 3. Überschreibe das Schema ohne Referenzverlust
            cfg.UI_SCHEMA.clear()
            cfg.UI_SCHEMA.update(copy.deepcopy(future["ui_schema"]))
            
            # Synchronisiere Sprachdateien
            if self._i18n and future["translations"]:
                self._i18n._translations = copy.deepcopy(future["translations"])
                self._write_translations_to_disk()
            
            return True
        return False

    
    def _write_translations_to_disk(self):
        """Hilfsfunktion: Schreibt den wiederhergestellten Sprachpool physisch in die JSON-Dateien."""
        if not self._i18n or not hasattr(self._i18n, "_locales_dir"): return
        
        for lang in ["de", "en"]:
            if lang in self._i18n._translations:
                file_path = os.path.join(self._i18n._locales_dir, f"{lang}.json")
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(self._i18n._translations[lang], f, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(f"❌ Synchronisations-Fehler beim Schreiben von {lang}.json: {e}")
