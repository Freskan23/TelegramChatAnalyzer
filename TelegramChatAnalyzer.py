#!/usr/bin/env python3
"""
Telegram Chat Analyzer v2.0 - Diseño Zen 2025
Analiza chats exportados de Telegram con estilo minimalista y claro
"""

import sys
import os
import sqlite3
import json
import re
import subprocess
import urllib.request
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QScrollArea, QGridLayout, QFrame,
    QFileDialog, QMessageBox, QSplitter, QStackedWidget,
    QLineEdit, QComboBox, QTextEdit, QDialog, QDialogButtonBox,
    QFormLayout, QSpinBox, QApplication, QProgressBar,
    QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QAction, QPainter, QPen, QBrush, QPixmap

from bs4 import BeautifulSoup


# ============================================================
# CONFIGURACIÓN DE ACTUALIZACIÓN
# ============================================================

APP_VERSION = "3.1.5"
GITHUB_REPO = "Freskan23/TelegramChatAnalyzer"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/TelegramChatAnalyzer.py"
GITHUB_VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/VERSION"

# ============================================================
# PALETA DE COLORES ZEN 2025 - TEMA CLARO
# ============================================================

COLORS = {
    # Fondos
    'bg_primary': '#FAFBFC',      # Fondo principal - casi blanco
    'bg_secondary': '#FFFFFF',     # Tarjetas - blanco puro
    'bg_sidebar': '#F8F9FA',       # Sidebar - gris muy suave
    'bg_hover': '#F0F4F8',         # Hover - gris suave
    
    # Acentos
    'accent': '#6366F1',           # Indigo moderno
    'accent_light': '#818CF8',     # Indigo claro
    'accent_soft': '#EEF2FF',      # Indigo muy suave para fondos
    'success': '#10B981',          # Verde esmeralda
    'success_soft': '#D1FAE5',     # Verde suave
    'warning': '#F59E0B',          # Ámbar
    'warning_soft': '#FEF3C7',     # Ámbar suave
    'error': '#EF4444',            # Rojo suave
    'error_soft': '#FEE2E2',       # Rojo muy suave
    
    # Textos
    'text_primary': '#1F2937',     # Gris oscuro - texto principal
    'text_secondary': '#6B7280',   # Gris medio - texto secundario
    'text_muted': '#9CA3AF',       # Gris claro - texto deshabilitado
    
    # Bordes y sombras
    'border': '#E5E7EB',           # Borde suave
    'border_light': '#F3F4F6',     # Borde muy suave
    'shadow': 'rgba(0, 0, 0, 0.05)', # Sombra suave
}

# Roles con colores
ROLE_COLORS = {
    'profesor': ('#8B5CF6', '#EDE9FE'),    # Violeta
    'alumno': ('#3B82F6', '#DBEAFE'),      # Azul
    'colaborador': ('#10B981', '#D1FAE5'), # Verde
    'cliente': ('#F59E0B', '#FEF3C7'),     # Ámbar
    'manager': ('#EC4899', '#FCE7F3'),     # Rosa
    'desconocido': ('#6B7280', '#F3F4F6'), # Gris
}

PRIORITY_COLORS = {
    'low': ('#6B7280', '#F3F4F6'),
    'medium': ('#F59E0B', '#FEF3C7'),
    'high': ('#F97316', '#FFEDD5'),
    'urgent': ('#EF4444', '#FEE2E2'),
}

GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'SF Pro Display', -apple-system, sans-serif;
    font-size: 14px;
}}

QLabel {{
    color: {COLORS['text_primary']};
    background: transparent;
}}

QPushButton {{
    background-color: {COLORS['accent']};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 600;
    font-size: 14px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['accent']};
    transform: scale(0.98);
}}

QPushButton:disabled {{
    background-color: {COLORS['border']};
    color: {COLORS['text_muted']};
}}

QPushButton[class="secondary"] {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
}}

QPushButton[class="secondary"]:hover {{
    background-color: {COLORS['bg_hover']};
    border-color: {COLORS['accent']};
}}

QPushButton[class="ghost"] {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    border: none;
    padding: 8px 16px;
}}

QPushButton[class="ghost"]:hover {{
    background-color: {COLORS['bg_hover']};
    color: {COLORS['text_primary']};
}}

QLineEdit, QTextEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 2px solid {COLORS['accent']};
    outline: none;
}}

QLineEdit::placeholder {{
    color: {COLORS['text_muted']};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    margin: 4px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border']};
    border-radius: 4px;
    min-height: 40px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QProgressBar {{
    background-color: {COLORS['border_light']};
    border: none;
    border-radius: 6px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-weight: 600;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 6px;
}}

QComboBox {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
}}

QComboBox:hover {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    width: 12px;
    height: 12px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    selection-background-color: {COLORS['accent_soft']};
    selection-color: {COLORS['accent']};
}}

QMenuBar {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_hover']};
    border-radius: 6px;
}}

QMenu {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
    padding: 8px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 6px;
}}

QMenu::item:selected {{
    background-color: {COLORS['accent_soft']};
    color: {COLORS['accent']};
}}
"""


# ============================================================
# BASE DE DATOS
# ============================================================

class Database:
    """Clase para gestionar la base de datos SQLite local"""
    
    def __init__(self, db_path: str = "telegram_analyzer.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def close(self):
        if self.conn:
            self.conn.close()
            
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'group',
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                total_messages INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT,
                role TEXT DEFAULT 'unknown',
                role_confidence REAL DEFAULT 0.0,
                profile_summary TEXT,
                total_messages INTEGER DEFAULT 0,
                is_me INTEGER DEFAULT 0,
                ai_analyzed INTEGER DEFAULT 0,
                ai_analyzed_at TIMESTAMP,
                sentiment TEXT DEFAULT 'neutral',
                sentiment_score REAL DEFAULT 0.0,
                avatar_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT,
                description TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS person_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                score REAL DEFAULT 0.0,
                evidence TEXT,
                FOREIGN KEY (person_id) REFERENCES persons(id),
                FOREIGN KEY (skill_id) REFERENCES skills(id),
                UNIQUE(person_id, skill_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                category TEXT DEFAULT 'general',
                assigned_to INTEGER,
                source_message TEXT,
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (assigned_to) REFERENCES persons(id)
            )
        ''')
        
        # Migrar tabla existente si no tiene category
        try:
            self.cursor.execute('ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT "general"')
            self.conn.commit()
        except:
            pass
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                person_id INTEGER,
                content TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id),
                FOREIGN KEY (person_id) REFERENCES persons(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pattern_type TEXT,
                description TEXT,
                persons_involved TEXT,
                examples TEXT,
                recommendations TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Tabla de enlaces compartidos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                link_type TEXT DEFAULT 'general',
                context TEXT,
                shared_by INTEGER,
                mention_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shared_by) REFERENCES persons(id)
            )
        ''')
        
        # Tabla de objetivos personales
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS objectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_value REAL,
                current_value REAL DEFAULT 0,
                unit TEXT,
                status TEXT DEFAULT 'in_progress',
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES persons(id)
            )
        ''')
        
        # Tabla de proyectos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'active',
                client_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES persons(id)
            )
        ''')
        
        # Tabla de alertas de comportamiento
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                title TEXT NOT NULL,
                description TEXT,
                evidence TEXT,
                message_examples TEXT,
                recommendation TEXT,
                is_dismissed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES persons(id)
            )
        ''')
        
        # Tabla de compromisos/promesas detectados
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commitments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER NOT NULL,
                commitment_type TEXT DEFAULT 'promise',
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'pending',
                evidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (person_id) REFERENCES persons(id)
            )
        ''')
        
        # Tabla de resumen de conversaciones
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                summary_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                main_topics TEXT,
                key_decisions TEXT,
                action_items TEXT,
                participants_involved TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id)
            )
        ''')
        
        self.conn.commit()
        
        # Migraciones automáticas para bases de datos existentes
        self._run_migrations()
    
    def _run_migrations(self):
        """Ejecuta migraciones para actualizar esquema de BD existentes"""
        # Obtener columnas existentes en persons
        self.cursor.execute("PRAGMA table_info(persons)")
        existing_columns = {row[1] for row in self.cursor.fetchall()}
        
        # Migración: añadir ai_analyzed si no existe
        if 'ai_analyzed' not in existing_columns:
            try:
                self.cursor.execute('ALTER TABLE persons ADD COLUMN ai_analyzed INTEGER DEFAULT 0')
                self.conn.commit()
            except:
                pass
        
        # Migración: añadir ai_analyzed_at si no existe
        if 'ai_analyzed_at' not in existing_columns:
            try:
                self.cursor.execute('ALTER TABLE persons ADD COLUMN ai_analyzed_at TIMESTAMP')
                self.conn.commit()
            except:
                pass
        
        # Migración: añadir sentiment si no existe
        if 'sentiment' not in existing_columns:
            try:
                self.cursor.execute("ALTER TABLE persons ADD COLUMN sentiment TEXT DEFAULT 'neutral'")
                self.conn.commit()
            except:
                pass
        
        # Migración: añadir sentiment_score si no existe
        if 'sentiment_score' not in existing_columns:
            try:
                self.cursor.execute('ALTER TABLE persons ADD COLUMN sentiment_score REAL DEFAULT 0.0')
                self.conn.commit()
            except:
                pass
        
        # Migración: añadir avatar_path si no existe
        if 'avatar_path' not in existing_columns:
            try:
                self.cursor.execute('ALTER TABLE persons ADD COLUMN avatar_path TEXT')
                self.conn.commit()
            except:
                pass
        
    def add_chat(self, name: str, chat_type: str = 'group', file_path: str = None) -> int:
        self.cursor.execute(
            'INSERT INTO chats (name, type, file_path) VALUES (?, ?, ?)',
            (name, chat_type, file_path)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_chats(self) -> List[Dict]:
        self.cursor.execute('SELECT * FROM chats ORDER BY import_date DESC')
        return [dict(row) for row in self.cursor.fetchall()]
        
    def add_person(self, name: str, username: str = None) -> int:
        self.cursor.execute('SELECT id FROM persons WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result['id']
        self.cursor.execute(
            'INSERT INTO persons (name, username) VALUES (?, ?)',
            (name, username)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_person(self, person_id: int) -> Optional[Dict]:
        self.cursor.execute('SELECT * FROM persons WHERE id = ?', (person_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_person_by_name(self, name: str) -> Optional[Dict]:
        """Obtiene una persona por su nombre"""
        self.cursor.execute('SELECT * FROM persons WHERE name = ?', (name,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_persons(self, min_messages: int = 1) -> List[Dict]:
        self.cursor.execute(
            'SELECT * FROM persons WHERE total_messages >= ? ORDER BY total_messages DESC',
            (min_messages,)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_me(self) -> Optional[Dict]:
        self.cursor.execute('SELECT * FROM persons WHERE is_me = 1')
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def set_me(self, person_id: int):
        self.cursor.execute('UPDATE persons SET is_me = 0')
        self.cursor.execute('UPDATE persons SET is_me = 1 WHERE id = ?', (person_id,))
        self.conn.commit()
    
    def update_person(self, person_id: int, **kwargs):
        allowed = ['name', 'role', 'role_confidence', 'profile_summary', 'total_messages', 'is_me', 'ai_analyzed', 'ai_analyzed_at', 'sentiment', 'sentiment_score', 'avatar_path']
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed:
                updates.append(f"{key} = ?")
                values.append(value)
        if updates:
            values.append(person_id)
            self.cursor.execute(
                f"UPDATE persons SET {', '.join(updates)} WHERE id = ?",
                values
            )
            self.conn.commit()
    
    def delete_person(self, person_id: int):
        """Elimina una persona y todos sus datos asociados"""
        # Eliminar mensajes de la persona
        self.cursor.execute('DELETE FROM messages WHERE person_id = ?', (person_id,))
        # Eliminar skills asociados
        self.cursor.execute('DELETE FROM person_skills WHERE person_id = ?', (person_id,))
        # Eliminar alertas de comportamiento
        self.cursor.execute('DELETE FROM behavior_alerts WHERE person_id = ?', (person_id,))
        # Eliminar compromisos
        self.cursor.execute('DELETE FROM commitments WHERE person_id = ?', (person_id,))
        # Eliminar tareas asignadas (poner assigned_to en NULL)
        self.cursor.execute('UPDATE tasks SET assigned_to = NULL WHERE assigned_to = ?', (person_id,))
        # Eliminar la persona
        self.cursor.execute('DELETE FROM persons WHERE id = ?', (person_id,))
        self.conn.commit()
            
    def get_person_with_skills(self, person_id: int) -> Optional[Dict]:
        person = self.get_person(person_id)
        if not person:
            return None
        self.cursor.execute('''
            SELECT s.name, s.category, ps.score, ps.evidence
            FROM person_skills ps
            JOIN skills s ON ps.skill_id = s.id
            WHERE ps.person_id = ?
            ORDER BY ps.score DESC
        ''', (person_id,))
        person['skills'] = [dict(row) for row in self.cursor.fetchall()]
        return person
        
    def add_skill(self, name: str, category: str = None, description: str = None) -> int:
        self.cursor.execute('SELECT id FROM skills WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        if result:
            return result['id']
        self.cursor.execute(
            'INSERT INTO skills (name, category, description) VALUES (?, ?, ?)',
            (name, category, description)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def add_person_skill(self, person_id: int, skill_id: int, score: float, evidence: str = None):
        self.cursor.execute('''
            INSERT INTO person_skills (person_id, skill_id, score, evidence)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(person_id, skill_id) 
            DO UPDATE SET score = ?, evidence = ?
        ''', (person_id, skill_id, score, evidence, score, evidence))
        self.conn.commit()
        
    def add_task(self, title: str, description: str = None, status: str = 'pending',
                 priority: str = 'medium', category: str = 'general', assigned_to: int = None, 
                 source_message: str = None, due_date: str = None) -> int:
        self.cursor.execute('''
            INSERT INTO tasks (title, description, status, priority, category, assigned_to, source_message, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, status, priority, category, assigned_to, source_message, due_date))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_tasks(self, status: str = None, person_id: int = None) -> List[Dict]:
        conditions = []
        params = []
        
        if status:
            conditions.append("t.status = ?")
            params.append(status)
        
        if person_id:
            conditions.append("t.assigned_to = ?")
            params.append(person_id)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        query = f'''
            SELECT t.*, p.name as assigned_to_name
            FROM tasks t
            LEFT JOIN persons p ON t.assigned_to = p.id
            {where_clause}
            ORDER BY 
                CASE t.status WHEN 'completed' THEN 1 ELSE 0 END,
                CASE t.priority 
                    WHEN 'urgent' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    ELSE 4 
                END,
                t.created_at DESC
        '''
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_my_tasks(self) -> List[Dict]:
        me = self.get_me()
        if not me:
            return []
        return self.get_tasks_for_person(me['id'])
    
    def get_tasks_grouped_by_category(self, status: str = None, person_id: int = None) -> Dict[str, List[Dict]]:
        tasks = self.get_all_tasks(status, person_id)
        grouped = {}
        for task in tasks:
            category = task.get('category', 'general') or 'general'
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(task)
        return grouped
    
    def get_task_categories(self) -> List[str]:
        self.cursor.execute('SELECT DISTINCT category FROM tasks WHERE category IS NOT NULL')
        return [row['category'] for row in self.cursor.fetchall()]
    
    def get_tasks_for_person(self, person_id: int) -> List[Dict]:
        self.cursor.execute('''
            SELECT t.*, p.name as assigned_to_name
            FROM tasks t
            LEFT JOIN persons p ON t.assigned_to = p.id
            WHERE t.assigned_to = ?
            ORDER BY t.status, t.priority DESC, t.created_at DESC
        ''', (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_task_status(self, task_id: int, status: str):
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        self.cursor.execute(
            'UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?', 
            (status, completed_at, task_id)
        )
        self.conn.commit()
        
    def add_message(self, chat_id: int, person_id: int, content: str, timestamp: str) -> int:
        self.cursor.execute('''
            INSERT INTO messages (chat_id, person_id, content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, person_id, content, timestamp))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_messages_for_person(self, person_id: int) -> List[Dict]:
        """Obtiene todos los mensajes de una persona"""
        self.cursor.execute('''
            SELECT m.*, p.name as sender_name
            FROM messages m
            JOIN persons p ON m.person_id = p.id
            WHERE m.person_id = ?
            ORDER BY m.timestamp ASC
        ''', (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_messages(self) -> List[Dict]:
        """Obtiene todos los mensajes con información del remitente"""
        self.cursor.execute('''
            SELECT m.*, p.name as sender_name
            FROM messages m
            JOIN persons p ON m.person_id = p.id
            ORDER BY m.timestamp ASC
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
        
    def add_pattern(self, name: str, pattern_type: str, description: str = None,
                    persons_involved: List[str] = None, examples: List[str] = None,
                    recommendations: str = None) -> int:
        self.cursor.execute('''
            INSERT INTO patterns (name, pattern_type, description, persons_involved, examples, recommendations)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, pattern_type, description,
              json.dumps(persons_involved) if persons_involved else None,
              json.dumps(examples) if examples else None,
              recommendations))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_patterns(self) -> List[Dict]:
        self.cursor.execute('SELECT * FROM patterns')
        patterns = []
        for row in self.cursor.fetchall():
            pattern = dict(row)
            if pattern['persons_involved']:
                pattern['persons_involved'] = json.loads(pattern['persons_involved'])
            if pattern['examples']:
                pattern['examples'] = json.loads(pattern['examples'])
            patterns.append(pattern)
        return patterns
    
    def get_dashboard_stats(self) -> Dict:
        stats = {}
        self.cursor.execute('SELECT COUNT(*) as count FROM persons WHERE total_messages > 0')
        stats['total_persons'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT status, COUNT(*) as count FROM tasks GROUP BY status')
        stats['tasks_by_status'] = {row['status']: row['count'] for row in self.cursor.fetchall()}
        
        self.cursor.execute('SELECT COUNT(*) as count FROM tasks')
        stats['total_tasks'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM messages')
        stats['total_messages'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM patterns')
        stats['total_patterns'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "pending"')
        stats['pending_tasks'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "completed"')
        stats['completed_tasks'] = self.cursor.fetchone()['count']
        
        return stats
    
    def get_person_stats(self, person_id: int) -> Dict:
        stats = {}
        self.cursor.execute('SELECT COUNT(*) as count FROM messages WHERE person_id = ?', (person_id,))
        stats['total_messages'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE assigned_to = ?', (person_id,))
        stats['total_tasks'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE assigned_to = ? AND status = "completed"', (person_id,))
        stats['completed_tasks'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE assigned_to = ? AND status = "pending"', (person_id,))
        stats['pending_tasks'] = self.cursor.fetchone()['count']
        
        self.cursor.execute('SELECT AVG(score) as avg FROM person_skills WHERE person_id = ?', (person_id,))
        result = self.cursor.fetchone()
        stats['avg_skill_score'] = result['avg'] if result['avg'] else 0
        
        return stats
    
    def set_setting(self, key: str, value: str):
        self.cursor.execute('''
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = ?
        ''', (key, value, value))
        self.conn.commit()
        
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        self.cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = self.cursor.fetchone()
        return result['value'] if result else default
    
    def clear_all_data(self):
        tables = ['messages', 'person_skills', 'tasks', 'patterns', 'persons', 'skills', 'chats', 'links', 'objectives', 'projects']
        for table in tables:
            try:
                self.cursor.execute(f'DELETE FROM {table}')
            except:
                pass
        self.conn.commit()
    
    # === FUNCIONES DE ENLACES ===
    def add_link(self, url: str, title: str = None, link_type: str = 'general', 
                 context: str = None, shared_by: int = None, mention_count: int = 1) -> int:
        # Verificar si ya existe
        self.cursor.execute('SELECT id, mention_count FROM links WHERE url = ?', (url,))
        existing = self.cursor.fetchone()
        if existing:
            self.cursor.execute('''
                UPDATE links SET mention_count = mention_count + 1, last_seen = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (existing['id'],))
            self.conn.commit()
            return existing['id']
        else:
            self.cursor.execute('''
                INSERT INTO links (url, title, link_type, context, shared_by, mention_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, title, link_type, context, shared_by, mention_count))
            self.conn.commit()
            return self.cursor.lastrowid
    
    def get_all_links(self) -> List[Dict]:
        self.cursor.execute('''
            SELECT l.*, p.name as shared_by_name
            FROM links l
            LEFT JOIN persons p ON l.shared_by = p.id
            ORDER BY l.mention_count DESC, l.last_seen DESC
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_links_by_type(self, link_type: str) -> List[Dict]:
        self.cursor.execute('''
            SELECT l.*, p.name as shared_by_name
            FROM links l
            LEFT JOIN persons p ON l.shared_by = p.id
            WHERE l.link_type = ?
            ORDER BY l.mention_count DESC
        ''', (link_type,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_links_by_person(self, person_id: int) -> List[Dict]:
        self.cursor.execute('''
            SELECT * FROM links WHERE shared_by = ?
            ORDER BY mention_count DESC, last_seen DESC
        ''', (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # === FUNCIONES DE COMPROMISOS ===
    def add_commitment(self, person_id: int, title: str, commitment_type: str = 'promise',
                       description: str = None, due_date: str = None, evidence: str = None) -> int:
        self.cursor.execute('''
            INSERT INTO commitments (person_id, commitment_type, title, description, due_date, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (person_id, commitment_type, title, description, due_date, evidence))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_commitments(self, status: str = None) -> List[Dict]:
        if status:
            self.cursor.execute('''
                SELECT c.*, p.name as person_name
                FROM commitments c
                JOIN persons p ON c.person_id = p.id
                WHERE c.status = ?
                ORDER BY c.created_at DESC
            ''', (status,))
        else:
            self.cursor.execute('''
                SELECT c.*, p.name as person_name
                FROM commitments c
                JOIN persons p ON c.person_id = p.id
                ORDER BY c.created_at DESC
            ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_commitments_by_person(self, person_id: int) -> List[Dict]:
        self.cursor.execute('''
            SELECT * FROM commitments WHERE person_id = ?
            ORDER BY created_at DESC
        ''', (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_commitment_status(self, commitment_id: int, status: str):
        self.cursor.execute('UPDATE commitments SET status = ? WHERE id = ?', (status, commitment_id))
        self.conn.commit()
    
    # === FUNCIONES DE RESUMEN DE CONVERSACIONES ===
    def add_conversation_summary(self, chat_id: int, main_topics: str, key_decisions: str = None,
                                  action_items: str = None, participants: str = None) -> int:
        self.cursor.execute('''
            INSERT INTO conversation_summary (chat_id, main_topics, key_decisions, action_items, participants_involved)
            VALUES (?, ?, ?, ?, ?)
        ''', (chat_id, main_topics, key_decisions, action_items, participants))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_latest_summary(self, chat_id: int = None) -> Optional[Dict]:
        if chat_id:
            self.cursor.execute('''
                SELECT * FROM conversation_summary WHERE chat_id = ?
                ORDER BY summary_date DESC LIMIT 1
            ''', (chat_id,))
        else:
            self.cursor.execute('SELECT * FROM conversation_summary ORDER BY summary_date DESC LIMIT 1')
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # === FUNCIONES DE PROYECTOS ===
    def add_project(self, name: str, description: str = None, client_id: int = None) -> int:
        self.cursor.execute('''
            INSERT INTO projects (name, description, client_id)
            VALUES (?, ?, ?)
        ''', (name, description, client_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_projects(self) -> List[Dict]:
        self.cursor.execute('''
            SELECT p.*, c.name as client_name
            FROM projects p
            LEFT JOIN persons c ON p.client_id = c.id
            ORDER BY p.created_at DESC
        ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    # === FUNCIONES DE OBJETIVOS ===
    def add_objective(self, person_id: int, title: str, description: str = None,
                      target_value: float = 100, unit: str = '%', due_date: str = None) -> int:
        self.cursor.execute('''
            INSERT INTO objectives (person_id, title, description, target_value, unit, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (person_id, title, description, target_value, unit, due_date))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_objectives_for_person(self, person_id: int) -> List[Dict]:
        self.cursor.execute('''
            SELECT * FROM objectives WHERE person_id = ?
            ORDER BY status ASC, due_date ASC
        ''', (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_objective_progress(self, objective_id: int, current_value: float):
        self.cursor.execute('''
            UPDATE objectives SET current_value = ? WHERE id = ?
        ''', (current_value, objective_id))
        self.conn.commit()
    
    # === FUNCIONES DE ALERTAS DE COMPORTAMIENTO ===
    def add_behavior_alert(self, person_id: int, alert_type: str, title: str,
                           description: str = None, severity: str = 'medium',
                           evidence: str = None, message_examples: str = None,
                           recommendation: str = None) -> int:
        self.cursor.execute('''
            INSERT INTO behavior_alerts 
            (person_id, alert_type, title, description, severity, evidence, message_examples, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (person_id, alert_type, title, description, severity, evidence, message_examples, recommendation))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_alerts_for_person(self, person_id: int, include_dismissed: bool = False) -> List[Dict]:
        if include_dismissed:
            self.cursor.execute('''
                SELECT * FROM behavior_alerts WHERE person_id = ?
                ORDER BY severity DESC, created_at DESC
            ''', (person_id,))
        else:
            self.cursor.execute('''
                SELECT * FROM behavior_alerts WHERE person_id = ? AND is_dismissed = 0
                ORDER BY severity DESC, created_at DESC
            ''', (person_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_alerts(self, include_dismissed: bool = False) -> List[Dict]:
        if include_dismissed:
            self.cursor.execute('''
                SELECT ba.*, p.name as person_name
                FROM behavior_alerts ba
                JOIN persons p ON ba.person_id = p.id
                ORDER BY ba.severity DESC, ba.created_at DESC
            ''')
        else:
            self.cursor.execute('''
                SELECT ba.*, p.name as person_name
                FROM behavior_alerts ba
                JOIN persons p ON ba.person_id = p.id
                WHERE ba.is_dismissed = 0
                ORDER BY ba.severity DESC, ba.created_at DESC
            ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def dismiss_alert(self, alert_id: int):
        self.cursor.execute('UPDATE behavior_alerts SET is_dismissed = 1 WHERE id = ?', (alert_id,))
        self.conn.commit()
    
    def get_alerts_summary(self) -> Dict:
        self.cursor.execute('''
            SELECT 
                alert_type,
                severity,
                COUNT(*) as count
            FROM behavior_alerts
            WHERE is_dismissed = 0
            GROUP BY alert_type, severity
        ''')
        results = self.cursor.fetchall()
        summary = {'total': 0, 'by_type': {}, 'by_severity': {'high': 0, 'medium': 0, 'low': 0}}
        for row in results:
            summary['total'] += row['count']
            if row['alert_type'] not in summary['by_type']:
                summary['by_type'][row['alert_type']] = 0
            summary['by_type'][row['alert_type']] += row['count']
            summary['by_severity'][row['severity']] += row['count']
        return summary
    
    # === FUNCIONES DE ACTIVIDAD ===
    def get_activity_by_date(self, person_id: int = None) -> List[Dict]:
        if person_id:
            self.cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM messages WHERE person_id = ?
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            ''', (person_id,))
        else:
            self.cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM messages
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 30
            ''')
        return [dict(row) for row in self.cursor.fetchall()]


# ============================================================
# PARSER DE TELEGRAM
# ============================================================

class TelegramHTMLParser:
    def __init__(self):
        self.messages = []
        self.participants = {}
        self.chat_name = ""
        self.date_range = (None, None)
        self.links = []  # Lista de enlaces encontrados
        
    def parse_file(self, file_path: str) -> Dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        self._extract_chat_name(soup)
        self._extract_messages(soup)
        self._extract_links()  # Extraer enlaces de los mensajes
        self._calculate_date_range()
        self._clean_participants()
        
        return {
            'chat_name': self.chat_name,
            'messages': self.messages,
            'participants': self.participants,
            'date_range': self.date_range,
            'total_messages': len(self.messages),
            'links': self.links  # Incluir enlaces
        }
    
    def _extract_chat_name(self, soup):
        name_element = soup.select_one('.page_header .text')
        if name_element:
            self.chat_name = name_element.get_text(strip=True)
            return
        name_element = soup.select_one('.page_header')
        if name_element:
            self.chat_name = name_element.get_text(strip=True)
            return
        title = soup.find('title')
        if title:
            self.chat_name = title.get_text(strip=True)
            
    def _extract_messages(self, soup):
        message_elements = soup.select('.message')
        if not message_elements:
            message_elements = soup.select('.message_default')
            
        current_sender = None
        
        for msg_elem in message_elements:
            message_data = self._parse_message_element(msg_elem, current_sender)
            if message_data:
                self.messages.append(message_data)
                current_sender = message_data.get('sender')
                
                sender = message_data.get('sender')
                if sender:
                    if sender not in self.participants:
                        self.participants[sender] = {
                            'name': sender,
                            'message_count': 0,
                            'first_message': message_data.get('timestamp'),
                            'last_message': message_data.get('timestamp')
                        }
                    self.participants[sender]['message_count'] += 1
                    self.participants[sender]['last_message'] = message_data.get('timestamp')
    
    def _parse_message_element(self, element, previous_sender: str = None) -> Optional[Dict]:
        message = {
            'sender': None,
            'content': '',
            'timestamp': None,
            'type': 'text'
        }
        
        sender_elem = element.select_one('.from_name')
        if sender_elem:
            message['sender'] = sender_elem.get_text(strip=True)
        else:
            message['sender'] = previous_sender
            
        date_elem = element.select_one('.date')
        if date_elem:
            date_str = date_elem.get('title', '') or date_elem.get_text(strip=True)
            message['timestamp'] = self._parse_date(date_str)
            
        text_elem = element.select_one('.text')
        if text_elem:
            message['content'] = text_elem.get_text(strip=True)
            
        if message['content']:
            return message
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        
        # Limpiar zona horaria UTC+XX:XX o UTC-XX:XX
        clean_date = re.sub(r'\s*UTC[+-]\d{2}:\d{2}', '', date_str.strip())
        
        formats = [
            '%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',
            '%d %B %Y',  # Para fechas de servicio como "4 April 2021"
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(clean_date.strip(), fmt)
                return dt.isoformat()
            except ValueError:
                continue
        return date_str
    
    def _calculate_date_range(self):
        if not self.messages:
            return
        dates = [m['timestamp'] for m in self.messages if m.get('timestamp')]
        if dates:
            self.date_range = (min(dates), max(dates))
            
    def _clean_participants(self):
        # Eliminar participantes con nombres que parecen combinados o con 0 mensajes
        to_remove = []
        for name, info in self.participants.items():
            # Eliminar si tiene 0 mensajes
            if info['message_count'] == 0:
                to_remove.append(name)
            # Eliminar si parece un nombre combinado (contiene coma)
            elif ',' in name:
                to_remove.append(name)
            # Eliminar si el nombre es muy largo (probablemente error)
            elif len(name) > 50:
                to_remove.append(name)
                
        for name in to_remove:
            del self.participants[name]
    
    def _extract_links(self):
        """Extrae todos los enlaces de los mensajes"""
        import re
        url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+'
        )
        
        link_counts = {}  # Para contar ocurrencias
        
        for msg in self.messages:
            content = msg.get('content', '')
            sender = msg.get('sender', '')
            timestamp = msg.get('timestamp', '')
            
            # Buscar URLs en el contenido
            urls = url_pattern.findall(content)
            
            for url in urls:
                # Limpiar URL (quitar puntuación final)
                url = url.rstrip('.,;:!?)"\'')
                
                if url not in link_counts:
                    link_counts[url] = {
                        'url': url,
                        'shared_by': [],
                        'contexts': [],
                        'count': 0,
                        'first_shared': timestamp,
                        'last_shared': timestamp
                    }
                
                link_counts[url]['count'] += 1
                link_counts[url]['last_shared'] = timestamp
                
                if sender and sender not in link_counts[url]['shared_by']:
                    link_counts[url]['shared_by'].append(sender)
                
                # Guardar contexto (el mensaje donde aparece)
                if len(link_counts[url]['contexts']) < 3:  # Max 3 contextos
                    link_counts[url]['contexts'].append({
                        'message': content[:200],  # Primeros 200 chars
                        'sender': sender,
                        'timestamp': timestamp
                    })
        
        self.links = list(link_counts.values())


# ============================================================
# ANALIZADOR CON IA
# ============================================================

class PersonRole(Enum):
    COLLABORATOR = "colaborador"
    CLIENT = "cliente"
    STUDENT = "alumno"
    TEACHER = "profesor"
    MANAGER = "manager"
    UNKNOWN = "desconocido"


@dataclass
class TaskExtracted:
    title: str
    description: str = ""
    status: str = "pending"
    priority: str = "medium"
    category: str = "general"
    assigned_to: str = None
    source_message: str = ""
    confidence: float = 0.0


@dataclass
class SkillDetected:
    name: str
    category: str
    score: float
    evidence: str


@dataclass
class PersonProfile:
    name: str
    role: PersonRole
    role_confidence: float
    skills: List[SkillDetected]
    summary: str
    strengths: List[str] = None
    areas_to_improve: List[str] = None
    recommendations: List[str] = None
    sentiment: str = 'neutral'
    sentiment_score: float = 0.0
    commitments: List[Dict] = None


class AIAnalyzer:
    def __init__(self, api_key: str = None, provider: str = "gemini"):
        self.provider = provider
        self.client = None
        self.model = None
        
        if provider == "gemini":
            self._init_gemini(api_key)
        else:
            self._init_openai(api_key)
            
    def _init_gemini(self, api_key: str = None):
        try:
            from google import genai
            api_key = api_key or os.environ.get('GEMINI_API_KEY')
            self.client = genai.Client(api_key=api_key)
            self.model = "gemini-2.5-flash"
        except ImportError:
            raise ImportError("Instala google-genai: pip install google-genai")
            
    def _init_openai(self, api_key: str = None):
        try:
            from openai import OpenAI
            self.client = OpenAI()
            self.model = "gpt-4.1-mini"
        except ImportError:
            raise ImportError("Instala openai: pip install openai")
    
    def _call_ai(self, prompt: str, system_prompt: str = None) -> str:
        try:
            if self.provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt
                )
                result = response.text
            else:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                result = response.choices[0].message.content
            
            # Asegurar que nunca retornamos None
            return result if result else '{}'
        except Exception as e:
            print(f"Error en _call_ai: {e}")
            return '{}'
    
    def extract_tasks(self, messages: List[Dict]) -> List[TaskExtracted]:
        messages_text = self._format_messages(messages)
        
        system_prompt = """Eres un experto en análisis de conversaciones y gestión de proyectos.
Identifica TODAS las tareas, compromisos, pendientes y acciones mencionados en la conversación.
Sé muy detallado y no te pierdas ninguna tarea implícita o explícita.

CATEGORÍAS DISPONIBLES:
- mentoría: Tareas relacionadas con enseñanza, coaching, formación
- técnico: Desarrollo, programación, configuración técnica
- marketing: Publicidad, redes sociales, contenido promocional
- ventas: Clientes, leads, propuestas comerciales
- negocio: Estrategia, planificación, modelo de negocio
- diseño: Gráficos, UI/UX, branding
- contenido: Blogs, videos, material educativo
- administrativo: Documentos, facturas, trámites
- general: Otras tareas

Responde SOLO con JSON válido:
{
    "tasks": [
        {
            "title": "Título breve y accionable",
            "description": "Descripción detallada de la tarea",
            "status": "pending|in_progress|completed",
            "priority": "low|medium|high|urgent",
            "category": "mentoría|técnico|marketing|ventas|negocio|diseño|contenido|administrativo|general",
            "assigned_to": "nombre de la persona responsable o null",
            "source_message": "mensaje original donde se menciona",
            "confidence": 0.0-1.0
        }
    ]
}

IMPORTANTE: En assigned_to, indica claramente QUIÉN debe realizar la tarea, no quién la mencionó."""

        prompt = f"Analiza esta conversación y extrae TODAS las tareas:\n\n{messages_text}\n\nResponde SOLO con JSON válido."

        try:
            response = self._call_ai(prompt, system_prompt)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            tasks = []
            for t in data.get('tasks', []):
                task = TaskExtracted(
                    title=t.get('title', ''),
                    description=t.get('description', ''),
                    status=t.get('status', 'pending'),
                    priority=t.get('priority', 'medium'),
                    category=t.get('category', 'general'),
                    assigned_to=t.get('assigned_to'),
                    source_message=t.get('source_message', ''),
                    confidence=float(t.get('confidence', 0.5))
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            print(f"Error extrayendo tareas: {e}")
            return []
    
    def analyze_person(self, name: str, messages: List[Dict], is_me: bool = False) -> PersonProfile:
        messages_text = self._format_messages(messages, include_sender=False)
        
        extra_instructions = ""
        if is_me:
            extra_instructions = """
Este es el perfil del USUARIO PRINCIPAL. Sé especialmente detallado en:
- Identificar fortalezas claras
- Áreas de mejora constructivas
- Recomendaciones accionables para mejorar
"""
        
        system_prompt = f"""Analiza los mensajes de una persona y genera un perfil profesional detallado.
{extra_instructions}
Responde SOLO con JSON válido:
{{
    "role": "colaborador|cliente|alumno|profesor|manager|desconocido",
    "role_confidence": 0.0-1.0,
    "sentiment": "positive|neutral|negative",
    "sentiment_score": -1.0 a 1.0 (negativo a positivo),
    "skills": [
        {{"name": "nombre de habilidad", "category": "técnica|comunicación|liderazgo|organización|creatividad", "score": 0-100, "evidence": "evidencia del chat"}}
    ],
    "summary": "Resumen profesional en 2-3 oraciones",
    "strengths": ["fortaleza 1", "fortaleza 2", "fortaleza 3"],
    "areas_to_improve": ["área 1", "área 2"],
    "recommendations": ["recomendación accionable 1", "recomendación 2", "recomendación 3"],
    "commitments": [
        {{"title": "descripción corta del compromiso", "type": "promise|agreement|deadline", "due_date": "fecha si se menciona o null", "evidence": "cita del mensaje"}}
    ]
}}"""

        prompt = f"Analiza el perfil profesional de {name} basándote en sus mensajes:\n\n{messages_text}\n\nResponde SOLO con JSON válido."

        try:
            response = self._call_ai(prompt, system_prompt)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            skills = []
            for s in data.get('skills', []):
                skill = SkillDetected(
                    name=s.get('name', ''),
                    category=s.get('category', 'otro'),
                    score=float(s.get('score', 50)),
                    evidence=s.get('evidence', '')
                )
                skills.append(skill)
            
            role_str = data.get('role', 'desconocido')
            try:
                role = PersonRole(role_str)
            except ValueError:
                role = PersonRole.UNKNOWN
                
            return PersonProfile(
                name=name,
                role=role,
                role_confidence=float(data.get('role_confidence', 0.5)),
                skills=skills,
                summary=data.get('summary', ''),
                strengths=data.get('strengths', []),
                areas_to_improve=data.get('areas_to_improve', []),
                recommendations=data.get('recommendations', []),
                sentiment=data.get('sentiment', 'neutral'),
                sentiment_score=float(data.get('sentiment_score', 0.0)),
                commitments=data.get('commitments', [])
            )
        except Exception as e:
            print(f"Error analizando persona {name}: {e}")
            return PersonProfile(name=name, role=PersonRole.UNKNOWN, 
                               role_confidence=0.0, skills=[], summary="",
                               sentiment='neutral', sentiment_score=0.0, commitments=[])
    
    def detect_patterns(self, messages: List[Dict], participants: Dict) -> List[Dict]:
        messages_text = self._format_messages(messages[:200])
        
        system_prompt = """Identifica patrones de comunicación, dinámicas de grupo y temas recurrentes.
Sé específico y proporciona recomendaciones accionables.

Responde SOLO con JSON válido:
{
    "patterns": [
        {
            "name": "Nombre descriptivo del patrón",
            "type": "comunicación|temas|dinámicas|flujos|problemas|oportunidades",
            "description": "Descripción detallada del patrón observado",
            "persons_involved": ["persona1", "persona2"],
            "examples": ["ejemplo concreto del chat"],
            "recommendations": "Recomendación accionable para mejorar o aprovechar este patrón"
        }
    ]
}"""

        prompt = f"Analiza los patrones de comunicación en esta conversación:\n\n{messages_text}\n\nResponde SOLO con JSON válido."

        try:
            response = self._call_ai(prompt, system_prompt)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            return data.get('patterns', [])
        except Exception as e:
            print(f"Error detectando patrones: {e}")
            return []
    
    def detect_behavior_alerts(self, messages: List[Dict], person_name: str, my_name: str = None) -> List[Dict]:
        """Detecta comportamientos problemáticos de una persona hacia el usuario"""
        messages_text = self._format_messages(messages[:150])
        
        system_prompt = f"""Eres un experto en psicología y comunicación interpersonal.
Analiza los mensajes de {person_name} para detectar comportamientos problemáticos hacia {my_name or 'el usuario'}.

DETECTA ESTOS TIPOS DE ALERTAS:

1. INCONSISTENCIAS (inconsistency): Cuando dice una cosa y luego otra diferente, promesas rotas, contradicciones
2. ABUSO_CONOCIMIENTO (knowledge_abuse): Pide ayuda constantemente sin dar nada a cambio, extrae información valiosa sin compensación, usa como "consultor gratis"
3. MANIPULACION_EMOCIONAL (emotional_manipulation): Cumplidos excesivos fuera de contexto, intentos de ligar, cambios de tema hacia lo personal, frases manipuladoras
4. POSIBLES_MENTIRAS (possible_lies): Excusas repetitivas, historias que no cuadran, evasión de preguntas directas
5. RED_FLAGS (red_flags): Presión para tomar decisiones rápidas, victimismo constante, falta de reciprocidad, comportamiento tóxico

SÉ MUY CUIDADOSO: Solo reporta alertas cuando hay evidencia clara. No inventes alertas.
Si no hay comportamientos problemáticos, devuelve una lista vacía.

Responde SOLO con JSON válido:
{{
    "alerts": [
        {{
            "alert_type": "inconsistency|knowledge_abuse|emotional_manipulation|possible_lies|red_flags",
            "severity": "low|medium|high",
            "title": "Título breve y descriptivo de la alerta",
            "description": "Descripción detallada del comportamiento detectado",
            "evidence": "Evidencia concreta del chat que justifica esta alerta",
            "message_examples": ["mensaje ejemplo 1", "mensaje ejemplo 2"],
            "recommendation": "Qué debería hacer el usuario ante esta situación",
            "confidence": 0.0-1.0
        }}
    ]
}}

IMPORTANTE: Solo incluye alertas con confidence >= 0.6. Mejor pocos alertas certeras que muchos falsos positivos."""

        prompt = f"Analiza los mensajes de {person_name} y detecta comportamientos problemáticos:\n\n{messages_text}\n\nResponde SOLO con JSON válido."

        try:
            response = self._call_ai(prompt, system_prompt)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            
            # Filtrar por confidence
            alerts = [a for a in data.get('alerts', []) if float(a.get('confidence', 0)) >= 0.6]
            return alerts
        except Exception as e:
            print(f"Error detectando alertas para {person_name}: {e}")
            return []
    
    def _format_messages(self, messages: List[Dict], include_sender: bool = True) -> str:
        lines = []
        for msg in messages:
            timestamp = msg.get('timestamp', '')[:16] if msg.get('timestamp') else ''
            sender = msg.get('sender', 'Desconocido') or 'Desconocido'
            content = msg.get('content', '') or ''  # Manejar None
            if not content:  # Saltar mensajes vacíos
                continue
            if include_sender:
                lines.append(f"[{timestamp}] {sender}: {content}")
            else:
                lines.append(f"[{timestamp}] {content}")
        return "\n".join(lines)
    
    def _extract_json(self, text: str) -> str:
        if not text:
            return '{}'
        text = str(text)  # Asegurar que es string
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if json_match:
            return json_match.group(1).strip()
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json_match.group(0)
        return text


# ============================================================
# COMPONENTES DE UI - DISEÑO ZEN 2025
# ============================================================

class Card(QFrame):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("zenCard")
        self._setup_style()
        
    def _setup_style(self):
        self.setStyleSheet(f"""
            #zenCard {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 16px;
                padding: 20px;
            }}
            #zenCard:hover {{
                border-color: {COLORS['border']};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class MiniGraph(QWidget):
    """Mini gráfico de línea decorativo"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setMinimumWidth(80)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dibujar línea ondulada decorativa
        pen = QPen(QColor("#CBD5E1"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        width = self.width()
        height = self.height()
        
        # Puntos para la línea ondulada
        points = [
            (0, height * 0.6),
            (width * 0.15, height * 0.4),
            (width * 0.3, height * 0.7),
            (width * 0.45, height * 0.3),
            (width * 0.6, height * 0.5),
            (width * 0.75, height * 0.2),
            (width * 0.9, height * 0.4),
            (width, height * 0.3),
        ]
        
        from PyQt6.QtCore import QPointF
        from PyQt6.QtGui import QPainterPath
        
        path = QPainterPath()
        path.moveTo(QPointF(points[0][0], points[0][1]))
        for x, y in points[1:]:
            path.lineTo(QPointF(x, y))
        
        painter.drawPath(path)


class StatCard(QFrame):
    def __init__(self, icon: str, title: str, value: str, subtitle: str = "", 
                 color: str = None, parent=None):
        super().__init__(parent)
        self.icon_color = color
        self._setup_ui(icon, title, value, subtitle, color)
        
    def _setup_ui(self, icon: str, title: str, value: str, subtitle: str, color: str):
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #F1F5F9;
                border-radius: 16px;
            }
            QFrame:hover {
                border-color: #E2E8F0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 8))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(20, 18, 20, 18)
        
        # Título arriba (como en el mockup)
        title_label = QLabel(f"{title}:")
        title_label.setStyleSheet("""
            color: #64748B;
            font-size: 13px;
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        # Valor - GRANDE
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            color: #1E293B;
            font-size: 32px;
            font-weight: 700;
        """)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
        
        # Mini gráfico decorativo
        mini_graph = MiniGraph()
        layout.addWidget(mini_graph)
            
        self.setMinimumWidth(180)
        self.setFixedHeight(130)
        
    def set_value(self, value: str):
        self.value_label.setText(value)
        self.value_label.setStyleSheet("""
            color: #1E293B;
            font-size: 32px;
            font-weight: 700;
        """)


class PersonCard(Card):
    analyze_clicked = pyqtSignal(int)  # Señal para solicitar análisis de persona
    edit_clicked = pyqtSignal(int, str)  # person_id, nombre actual
    delete_clicked = pyqtSignal(int, str)  # person_id, nombre
    avatar_clicked = pyqtSignal(int)  # person_id para cambiar avatar
    
    def __init__(self, person_id: int, name: str, role: str, skills: list = None,
                 message_count: int = 0, is_me: bool = False, ai_analyzed: bool = False,
                 sentiment: str = 'neutral', sentiment_score: float = 0.0, 
                 avatar_path: str = None, parent=None):
        super().__init__(parent)
        self.person_id = person_id
        self.name = name
        self.ai_analyzed = ai_analyzed
        self.sentiment = sentiment
        self.sentiment_score = sentiment_score
        self.avatar_path = avatar_path
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self._setup_ui(name, role, skills, message_count, is_me, ai_analyzed, sentiment, sentiment_score, avatar_path)
    
    def _show_context_menu(self, pos):
        """Muestra menú contextual con opciones de edición"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #F1F5F9;
            }
        """)
        
        edit_action = menu.addAction("✏️ Editar nombre")
        avatar_action = menu.addAction("🖼️ Cambiar foto")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Eliminar persona")
        delete_action.setStyleSheet("color: #EF4444;")
        
        action = menu.exec(self.mapToGlobal(pos))
        
        if action == edit_action:
            self.edit_clicked.emit(self.person_id, self.name)
        elif action == avatar_action:
            self.avatar_clicked.emit(self.person_id)
        elif action == delete_action:
            self.delete_clicked.emit(self.person_id, self.name)
        
    def _setup_ui(self, name: str, role: str, skills: list, message_count: int, is_me: bool, ai_analyzed: bool,
                   sentiment: str = 'neutral', sentiment_score: float = 0.0, avatar_path: str = None):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Header con avatar e info
        header = QHBoxLayout()
        header.setSpacing(12)
        
        # Avatar (más pequeño) - con soporte para imagen personalizada
        role_colors = ROLE_COLORS.get(role.lower(), ROLE_COLORS['desconocido'])
        avatar = QLabel()
        avatar.setFixedSize(48, 48)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if avatar_path and os.path.exists(avatar_path):
            # Cargar imagen personalizada
            pixmap = QPixmap(avatar_path)
            pixmap = pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            # Crear máscara circular
            mask = QPixmap(48, 48)
            mask.fill(Qt.GlobalColor.transparent)
            painter = QPainter(mask)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(0, 0, 48, 48)
            painter.end()
            pixmap.setMask(mask.mask())
            avatar.setPixmap(pixmap)
            avatar.setStyleSheet("border-radius: 24px;")
        else:
            # Avatar con inicial
            avatar.setText(name[0].upper() if name else "?")
            avatar.setStyleSheet(f"""
                background-color: {role_colors[1]};
                color: {role_colors[0]};
                border-radius: 24px;
                font-size: 20px;
                font-weight: 700;
            """)
        header.addWidget(avatar)
        
        # Info container
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Nombre con badges en fila
        name_row = QHBoxLayout()
        name_row.setSpacing(6)
        
        # Nombre (con elipsis si es muy largo)
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 15px;
            font-weight: 600;
        """)
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(180)
        name_row.addWidget(name_label, 1)
        
        # Badges en contenedor horizontal
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(4)
        
        if is_me:
            me_badge = QLabel("TÚ")
            me_badge.setStyleSheet(f"""
                background-color: {COLORS['accent']};
                color: white;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 9px;
                font-weight: 700;
            """)
            me_badge.setFixedHeight(18)
            badges_layout.addWidget(me_badge)
        
        if ai_analyzed:
            ai_badge = QLabel("✓ IA")
            ai_badge.setStyleSheet(f"""
                background-color: {COLORS['success_soft']};
                color: {COLORS['success']};
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 9px;
                font-weight: 700;
            """)
            ai_badge.setFixedHeight(18)
            ai_badge.setToolTip("Esta persona ya fue analizada con IA")
            badges_layout.addWidget(ai_badge)
            
            # Badge de sentimiento (solo si ya fue analizado)
            sentiment_config = {
                'positive': ('😊', '#10B981', '#D1FAE5', 'Sentimiento positivo'),
                'neutral': ('😐', '#6B7280', '#F3F4F6', 'Sentimiento neutro'),
                'negative': ('😟', '#EF4444', '#FEE2E2', 'Sentimiento negativo')
            }
            emoji, color, bg_color, tooltip = sentiment_config.get(sentiment, sentiment_config['neutral'])
            sentiment_badge = QLabel(emoji)
            sentiment_badge.setStyleSheet(f"""
                background-color: {bg_color};
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 12px;
            """)
            sentiment_badge.setFixedHeight(18)
            sentiment_badge.setToolTip(f"{tooltip} ({sentiment_score:.1%})")
            badges_layout.addWidget(sentiment_badge)
        
        name_row.addLayout(badges_layout)
        name_row.addStretch()
        info_layout.addLayout(name_row)
        
        # Role badge
        role_badge = QLabel(role.capitalize())
        role_badge.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            padding: 3px 10px;
            border-radius: 5px;
            font-size: 11px;
            font-weight: 600;
        """)
        role_badge.setFixedWidth(role_badge.sizeHint().width() + 6)
        info_layout.addWidget(role_badge)
        
        header.addLayout(info_layout, 1)
        layout.addLayout(header)
        
        # Stats
        stats_label = QLabel(f"💬 {message_count} mensajes")
        stats_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 12px;
        """)
        layout.addWidget(stats_label)
        
        # Skills (con flow layout simulado - wrapping)
        if skills:
            skills_container = QWidget()
            skills_layout = QHBoxLayout(skills_container)
            skills_layout.setContentsMargins(0, 0, 0, 0)
            skills_layout.setSpacing(6)
            
            for skill in skills[:3]:
                skill_name = skill.get('name', skill) if isinstance(skill, dict) else skill
                # Truncar skill si es muy largo
                if len(skill_name) > 12:
                    skill_name = skill_name[:10] + "..."
                skill_badge = QLabel(skill_name)
                skill_badge.setStyleSheet(f"""
                    background-color: {COLORS['bg_primary']};
                    color: {COLORS['text_secondary']};
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 11px;
                """)
                skill_badge.setToolTip(skill.get('name', skill) if isinstance(skill, dict) else skill)
                skills_layout.addWidget(skill_badge)
            skills_layout.addStretch()
            layout.addWidget(skills_container)
        
        # Botón de analizar (siempre visible, cambia texto si ya analizado)
        btn_text = "🔄 Re-analizar" if ai_analyzed else "🤖 Analizar con IA"
        btn_color = COLORS['text_muted'] if ai_analyzed else COLORS['accent']
        btn_bg = COLORS['bg_secondary'] if ai_analyzed else COLORS['accent_soft']
        
        analyze_btn = QPushButton(btn_text)
        analyze_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_color};
                border: 1px solid {btn_color};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
                color: white;
                border-color: {COLORS['accent']};
            }}
        """)
        analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        analyze_btn.clicked.connect(self._on_analyze_clicked)
        layout.addWidget(analyze_btn)
        
        # Espaciador para empujar contenido arriba
        layout.addStretch()
        
        # Tamaño mínimo más flexible
        self.setMinimumWidth(280)
        self.setMinimumHeight(180)  # Siempre hay botón de analizar
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _on_analyze_clicked(self):
        self.analyze_clicked.emit(self.person_id)


# Colores para categorías de tareas
CATEGORY_COLORS = {
    'mentoría': ('#8B5CF6', '#EDE9FE'),      # Violeta
    'mentoria': ('#8B5CF6', '#EDE9FE'),      # Violeta (sin tilde)
    'técnico': ('#3B82F6', '#DBEAFE'),       # Azul
    'tecnico': ('#3B82F6', '#DBEAFE'),       # Azul (sin tilde)
    'marketing': ('#EC4899', '#FCE7F3'),     # Rosa
    'ventas': ('#10B981', '#D1FAE5'),        # Verde
    'negocio': ('#F59E0B', '#FEF3C7'),       # Ámbar
    'administrativo': ('#6B7280', '#F3F4F6'), # Gris
    'diseño': ('#06B6D4', '#CFFAFE'),        # Cyan
    'contenido': ('#F97316', '#FFEDD5'),     # Naranja
    'general': ('#6366F1', '#EEF2FF'),       # Indigo
}


class TaskCard(QFrame):
    status_changed = pyqtSignal(int, str)
    
    def __init__(self, task_id: int, title: str, description: str = "",
                 status: str = "pending", priority: str = "medium",
                 category: str = "general", assigned_to: str = None, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.status = status
        self._setup_ui(title, description, status, priority, category, assigned_to)
        
    def _setup_ui(self, title: str, description: str, status: str, 
                  priority: str, category: str, assigned_to: str):
        # Colores de prioridad estilo mockup
        priority_badge_colors = {
            'low': ('#10B981', '#D1FAE5'),      # Verde
            'medium': ('#F59E0B', '#FEF3C7'),   # Naranja
            'high': ('#F97316', '#FFEDD5'),     # Naranja fuerte
            'urgent': ('#EF4444', '#FEE2E2'),   # Rojo
        }
        p_colors = priority_badge_colors.get(priority, priority_badge_colors['medium'])
        
        # Estilo simple con borde izquierdo de color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #F1F5F9;
                border-left: 4px solid {p_colors[0]};
                border-radius: 10px;
            }}
            QFrame:hover {{
                background-color: #F8FAFC;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)
        
        # Checkbox cuadrado con bordes redondeados (estilo mockup)
        self.checkbox = QPushButton()
        self.checkbox.setFixedSize(22, 22)
        self.checkbox.setCheckable(True)
        self.checkbox.setChecked(status == "completed")
        self._update_checkbox_style()
        self.checkbox.clicked.connect(self._on_status_toggle)
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Content - título y asignado
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        # Título
        title_label = QLabel(title)
        if status == "completed":
            title_label.setStyleSheet("""
                color: #94A3B8;
                font-size: 14px;
                font-weight: 500;
                text-decoration: line-through;
            """)
        else:
            title_label.setStyleSheet("""
                color: #334155;
                font-size: 14px;
                font-weight: 500;
            """)
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)
        
        # Asignado a (estilo mockup: "Asignado: Nombre")
        if assigned_to:
            assigned_label = QLabel(f"Asignado: {assigned_to}")
            assigned_label.setStyleSheet("""
                color: #94A3B8;
                font-size: 12px;
            """)
            content_layout.addWidget(assigned_label)
        
        layout.addLayout(content_layout, 1)
        
        # Badge de prioridad a la derecha (estilo mockup)
        priority_names = {'low': 'Baja', 'medium': 'Media', 'high': 'Alta', 'urgent': 'Urgente'}
        priority_badge = QLabel(priority_names.get(priority, 'Media'))
        priority_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {p_colors[0]};
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(priority_badge, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        # Botón de menú (3 puntos)
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(24, 24)
        menu_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #94A3B8;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                border-radius: 12px;
            }
        """)
        layout.addWidget(menu_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        
    def _update_checkbox_style(self):
        if self.checkbox.isChecked():
            self.checkbox.setStyleSheet("""
                QPushButton {
                    background-color: #3B82F6;
                    border: 2px solid #3B82F6;
                    border-radius: 6px;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
            """)
            self.checkbox.setText("✓")
        else:
            self.checkbox.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #E2E8F0;
                    border-radius: 6px;
                    color: transparent;
                }
                QPushButton:hover {
                    border-color: #3B82F6;
                }
            """)
            self.checkbox.setText("")
            
    def _on_status_toggle(self):
        self._update_checkbox_style()
        new_status = "completed" if self.checkbox.isChecked() else "pending"
        self.status_changed.emit(self.task_id, new_status)


class SkillBar(QWidget):
    def __init__(self, skill_name: str, score: float, category: str = "", parent=None):
        super().__init__(parent)
        self._setup_ui(skill_name, score, category)
        
    def _setup_ui(self, skill_name: str, score: float, category: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 12)
        
        # Header
        header = QHBoxLayout()
        name_label = QLabel(skill_name)
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 500;
        """)
        header.addWidget(name_label)
        
        score_label = QLabel(f"{int(score)}%")
        score_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 14px;
            font-weight: 600;
        """)
        header.addWidget(score_label)
        layout.addLayout(header)
        
        # Progress bar
        progress = QProgressBar()
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        progress.setValue(int(score))
        
        # Color based on score
        if score >= 80:
            bar_color = COLORS['success']
        elif score >= 60:
            bar_color = COLORS['accent']
        elif score >= 40:
            bar_color = COLORS['warning']
        else:
            bar_color = COLORS['text_muted']
            
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['border_light']};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(progress)


class PatternCard(Card):
    def __init__(self, name: str, pattern_type: str, description: str,
                 persons: list = None, recommendations: str = None, parent=None):
        super().__init__(parent)
        self._setup_ui(name, pattern_type, description, persons, recommendations)
        
    def _setup_ui(self, name: str, pattern_type: str, description: str,
                  persons: list, recommendations: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Type badge
        type_colors = {
            'comunicación': (COLORS['accent'], COLORS['accent_soft']),
            'temas': ('#8B5CF6', '#EDE9FE'),
            'dinámicas': ('#EC4899', '#FCE7F3'),
            'flujos': ('#10B981', '#D1FAE5'),
            'problemas': ('#EF4444', '#FEE2E2'),
            'oportunidades': ('#F59E0B', '#FEF3C7'),
        }
        colors = type_colors.get(pattern_type.lower(), (COLORS['text_secondary'], COLORS['border_light']))
        
        type_badge = QLabel(pattern_type.upper())
        type_badge.setStyleSheet(f"""
            background-color: {colors[1]};
            color: {colors[0]};
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        """)
        type_badge.setFixedWidth(type_badge.sizeHint().width() + 8)
        layout.addWidget(type_badge)
        
        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 16px;
            font-weight: 600;
        """)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            line-height: 1.5;
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Persons
        if persons:
            persons_label = QLabel(f"👥 {', '.join(persons[:3])}")
            persons_label.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 12px;
            """)
            layout.addWidget(persons_label)
            
        # Recommendations
        if recommendations:
            rec_frame = QFrame()
            rec_frame.setStyleSheet(f"""
                background-color: {COLORS['success_soft']};
                border-radius: 8px;
                padding: 12px;
            """)
            rec_layout = QVBoxLayout(rec_frame)
            rec_layout.setContentsMargins(12, 12, 12, 12)
            
            rec_title = QLabel("💡 Recomendación")
            rec_title.setStyleSheet(f"""
                color: {COLORS['success']};
                font-size: 12px;
                font-weight: 600;
            """)
            rec_layout.addWidget(rec_title)
            
            rec_text = QLabel(recommendations)
            rec_text.setStyleSheet(f"""
                color: {COLORS['text_primary']};
                font-size: 13px;
            """)
            rec_text.setWordWrap(True)
            rec_layout.addWidget(rec_text)
            
            layout.addWidget(rec_frame)
            
        self.setMinimumWidth(350)


class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: rgba(250, 251, 252, 0.95);")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spinner placeholder
        spinner_label = QLabel("⏳")
        spinner_label.setStyleSheet("font-size: 48px;")
        spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(spinner_label)
        
        self.message_label = QLabel("Procesando...")
        self.message_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 16px;
            font-weight: 500;
            margin-top: 16px;
        """)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(300)
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        
    def set_progress(self, value: int, message: str = None):
        self.progress.setValue(value)
        if message:
            self.message_label.setText(message)
            
    def show_indeterminate(self, message: str = "Procesando..."):
        self.progress.setRange(0, 0)
        self.message_label.setText(message)
        self.show()


class EmptyState(QWidget):
    action_clicked = pyqtSignal()
    
    def __init__(self, icon: str, title: str, description: str, 
                 action_text: str = None, parent=None):
        super().__init__(parent)
        self._setup_ui(icon, title, description, action_text)
        
    def _setup_ui(self, icon: str, title: str, description: str, action_text: str):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 64px;
            color: {COLORS['text_muted']};
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 20px;
            font-weight: 600;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 14px;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(400)
        layout.addWidget(desc_label)
        
        if action_text:
            action_btn = QPushButton(action_text)
            action_btn.setFixedWidth(200)
            action_btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(action_btn, alignment=Qt.AlignmentFlag.AlignCenter)


# ============================================================
# WORKER THREAD
# ============================================================

class AnalysisWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, messages: List[Dict], participants: Dict, 
                 api_key: str = None, me_name: str = None):
        super().__init__()
        self.messages = messages
        self.participants = participants
        self.api_key = api_key
        self.me_name = me_name
        
    def run(self):
        try:
            analyzer = AIAnalyzer(api_key=self.api_key)
            results = {'tasks': [], 'person_profiles': {}, 'patterns': []}
            
            total_steps = len(self.participants) + 2
            current_step = 0
            
            # Extract tasks
            self.progress.emit(current_step, total_steps, "Extrayendo tareas...")
            results['tasks'] = analyzer.extract_tasks(self.messages[:150])
            current_step += 1
            
            # Analyze persons
            for name in self.participants.keys():
                self.progress.emit(current_step, total_steps, f"Analizando a {name}...")
                person_messages = [m for m in self.messages if m.get('sender') == name]
                if person_messages:
                    is_me = (name == self.me_name) if self.me_name else False
                    profile = analyzer.analyze_person(name, person_messages[:80], is_me=is_me)
                    results['person_profiles'][name] = profile
                current_step += 1
                
            # Detect patterns
            self.progress.emit(current_step, total_steps, "Detectando patrones...")
            results['patterns'] = analyzer.detect_patterns(self.messages, self.participants)
            
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class BehaviorAnalysisWorker(QThread):
    """Worker para analizar comportamientos en segundo plano"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, api_key: str, persons: List[Dict], me_name: str, db_path: str):
        super().__init__()
        self.api_key = api_key
        self.persons = persons
        self.me_name = me_name
        self.db_path = db_path
        
    def run(self):
        try:
            # Crear conexión a BD en este thread
            db = Database(self.db_path)
            db.connect()
            analyzer = AIAnalyzer(api_key=self.api_key)
            
            total_alerts = 0
            total_persons = len(self.persons)
            
            for i, person in enumerate(self.persons):
                self.progress.emit(f"Analizando {person['name']} ({i+1}/{total_persons})...")
                
                messages = db.get_messages_for_person(person['id'])
                if len(messages) < 5:
                    continue
                
                alerts = analyzer.detect_behavior_alerts(messages, person['name'], self.me_name)
                
                for alert in alerts:
                    db.add_behavior_alert(
                        person_id=person['id'],
                        alert_type=alert.get('alert_type', 'red_flags'),
                        title=alert.get('title', 'Alerta detectada'),
                        description=alert.get('description'),
                        severity=alert.get('severity', 'medium'),
                        evidence=alert.get('evidence'),
                        message_examples=json.dumps(alert.get('message_examples', [])),
                        recommendation=alert.get('recommendation')
                    )
                    total_alerts += 1
            
            db.close()
            self.finished.emit(total_alerts)
        except Exception as e:
            self.error.emit(str(e))


class PersonAnalysisThread(QThread):
    """Worker para analizar una persona individual en segundo plano"""
    finished = pyqtSignal(int, dict)  # person_id, result
    error = pyqtSignal(str)
    
    def __init__(self, api_key: str, person_id: int, person_name: str, messages_text: str, db: 'Database'):
        super().__init__()
        self.api_key = api_key
        self.person_id = person_id
        self.person_name = person_name
        self.messages_text = messages_text
        self.db_path = db.db_path if hasattr(db, 'db_path') else 'telegram_analyzer.db'
        
    def run(self):
        try:
            analyzer = AIAnalyzer(api_key=self.api_key)
            
            # Analizar rol, skills, sentimiento y compromisos
            prompt = f"""Analiza los siguientes mensajes de {self.person_name} y extrae:

1. ROL: ¿Qué rol tiene esta persona? (profesor, alumno, colaborador, cliente, manager, desconocido)
2. SKILLS: Lista de habilidades detectadas con nivel estimado (1-100) y categoría
3. SENTIMIENTO: Tono general de la comunicación (positive, neutral, negative) y score (-1.0 a 1.0)
4. COMPROMISOS: Promesas, acuerdos o fechas límite mencionadas

Mensajes:
{self.messages_text[:12000]}

Responde SOLO con JSON válido en este formato:
{{
    "role": "colaborador",
    "role_confidence": 0.8,
    "sentiment": "positive",
    "sentiment_score": 0.6,
    "skills": [
        {{"name": "Diseño Web", "level": 85, "category": "técnica"}},
        {{"name": "Comunicación", "level": 70, "category": "comunicación"}}
    ],
    "commitments": [
        {{"title": "Entregar propuesta", "type": "promise", "due_date": "2024-01-15", "evidence": "Te lo envío mañana"}},
        {{"title": "Reunión de seguimiento", "type": "agreement", "due_date": null, "evidence": "Quedamos en vernos la próxima semana"}}
    ],
    "summary": "Resumen profesional en 2-3 oraciones"
}}

IMPORTANTE:
- Busca TODOS los compromisos, promesas, acuerdos y fechas límite mencionados
- Si no hay compromisos claros, devuelve un array vacío
- El sentimiento debe reflejar el tono general de la persona"""
            
            result = analyzer._call_ai(prompt)
            
            # Intentar parsear JSON - proteger contra None
            try:
                if not result:
                    result = '{}'
                result = str(result)  # Asegurar que es string
                # Buscar JSON en la respuesta
                json_match = re.search(r'\{[\s\S]*\}', result)
                if json_match:
                    result_dict = json.loads(json_match.group())
                else:
                    result_dict = {'role': 'desconocido', 'skills': [], 'patterns': []}
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Error parseando JSON: {e}")
                result_dict = {'role': 'desconocido', 'skills': [], 'patterns': []}
            
            self.finished.emit(self.person_id, result_dict)
            
        except Exception as e:
            self.error.emit(str(e))


class ImportWorker(QThread):
    """Worker para importar chats en segundo plano sin bloquear la UI"""
    progress = pyqtSignal(str)  # Mensaje de progreso
    finished = pyqtSignal(dict)  # Resultado con estadísticas
    error = pyqtSignal(str)
    
    def __init__(self, paths: list, db_path: str = 'telegram_analyzer.db'):
        super().__init__()
        self.paths = sorted(paths)  # Ordenar por nombre
        self.db_path = db_path
        
    def run(self):
        try:
            # Crear conexión a BD en este thread (SQLite requiere conexión por thread)
            db = Database(self.db_path)
            db.connect()  # Abrir conexión
            
            parser = TelegramHTMLParser()
            combined_data = None
            total_files = len(self.paths)
            
            # Fase 1: Parsear todos los archivos
            for idx, path in enumerate(self.paths):
                self.progress.emit(f"Leyendo archivo {idx + 1} de {total_files}...")
                
                data = parser.parse_file(path)
                
                if combined_data is None:
                    combined_data = data
                else:
                    # Combinar mensajes
                    combined_data['messages'].extend(data['messages'])
                    combined_data['total_messages'] += data['total_messages']
                    
                    # Combinar participantes
                    for name, info in data['participants'].items():
                        if name in combined_data['participants']:
                            combined_data['participants'][name]['message_count'] += info['message_count']
                        else:
                            combined_data['participants'][name] = info
                    
                    # Combinar enlaces
                    existing_urls = {link['url'] for link in combined_data.get('links', [])}
                    for link in data.get('links', []):
                        if link['url'] not in existing_urls:
                            combined_data.setdefault('links', []).append(link)
                            existing_urls.add(link['url'])
                        else:
                            for existing_link in combined_data['links']:
                                if existing_link['url'] == link['url']:
                                    existing_link['count'] += link['count']
                                    break
            
            # Fase 2: Guardar en base de datos
            self.progress.emit("Guardando chat en base de datos...")
            chat_id = db.add_chat(combined_data['chat_name'], 'group', self.paths[0])
            
            # Guardar participantes
            self.progress.emit("Guardando participantes...")
            person_ids = {}  # Cache de IDs para evitar búsquedas repetidas
            for name, info in combined_data['participants'].items():
                person_id = db.add_person(name)
                db.update_person(person_id, total_messages=info['message_count'])
                person_ids[name] = person_id
            
            # Guardar mensajes en lotes
            total_msgs = len(combined_data['messages'])
            self.progress.emit(f"Guardando 0/{total_msgs} mensajes...")
            
            for idx, msg in enumerate(combined_data['messages']):
                sender = msg.get('sender')
                if sender and sender in person_ids:
                    db.add_message(chat_id, person_ids[sender], msg.get('content', ''), msg.get('timestamp'))
                
                # Actualizar progreso cada 200 mensajes
                if (idx + 1) % 200 == 0:
                    self.progress.emit(f"Guardando {idx + 1}/{total_msgs} mensajes...")
            
            # Guardar enlaces
            self.progress.emit("Guardando enlaces...")
            links_count = 0
            for link_data in combined_data.get('links', []):
                shared_by_id = None
                if link_data['shared_by']:
                    shared_by_id = person_ids.get(link_data['shared_by'][0])
                
                db.add_link(
                    url=link_data['url'],
                    link_type='general',
                    context=link_data['contexts'][0]['message'] if link_data['contexts'] else '',
                    shared_by=shared_by_id,
                    mention_count=link_data['count']
                )
                links_count += 1
            
            db.close()
            
            # Emitir resultado con estadísticas
            result = {
                'total_files': total_files,
                'total_messages': combined_data['total_messages'],
                'total_participants': len(combined_data['participants']),
                'total_links': links_count,
                'chat_name': combined_data['chat_name']
            }
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


# ============================================================
# VENTANA PRINCIPAL
# ============================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.db = None
        self.current_chat_data = None
        self.analysis_results = None
        
        self._init_ui()
        self._init_database()
        self._load_data()
        
    def _init_ui(self):
        self.setWindowTitle("Telegram Chat Analyzer")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(GLOBAL_STYLE)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Right side with header and content
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        header = self._create_header()
        right_layout.addWidget(header)
        
        self.content_stack = QStackedWidget()
        right_layout.addWidget(self.content_stack, 1)
        
        main_layout.addWidget(right_container, 1)
        
        # Pages
        self.dashboard_page = self._create_dashboard_page()
        self.my_profile_page = self._create_my_profile_page()
        self.persons_page = self._create_persons_page()
        self.tasks_page = self._create_tasks_page()
        self.patterns_page = self._create_patterns_page()
        self.settings_page = self._create_settings_page()
        self.commitments_page = self._create_commitments_page()
        
        self.content_stack.addWidget(self.dashboard_page)  # 0
        self.content_stack.addWidget(self.my_profile_page)  # 1
        self.content_stack.addWidget(self.persons_page)     # 2
        self.content_stack.addWidget(self.tasks_page)       # 3
        self.content_stack.addWidget(self.patterns_page)    # 4
        self.content_stack.addWidget(self.settings_page)    # 5
        self.content_stack.addWidget(self.commitments_page) # 6
        
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()
        
        self._create_menu()
        
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-right: 1px solid #F1F5F9;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(4)
        
        # Logo/Title
        title_layout = QHBoxLayout()
        title_layout.setSpacing(10)
        
        logo = QLabel("💬")
        logo.setStyleSheet("""
            font-size: 24px;
            background-color: #3B82F6;
            border-radius: 8px;
            padding: 6px;
        """)
        logo.setFixedSize(36, 36)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(logo)
        
        title = QLabel("Chat Analyzer")
        title.setStyleSheet("""
            color: #1E293B;
            font-size: 18px;
            font-weight: 700;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        layout.addSpacing(32)
        
        # Navigation items con iconos outline style
        nav_items = [
            ("◎", "Dashboard", 0),
            ("☺", "Mi Perfil", 1),
            ("☰", "Usuarios", 2),
            ("☐", "Tareas", 3),
            ("≡", "Patrones", 4),
            ("🤝", "Compromisos", 6),
            ("⚙", "Configuración", 5),
        ]
        
        self.nav_buttons = []
        for icon, text, index in nav_items:
            btn = QPushButton(f"  {icon}    {text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #64748B;
                    text-align: left;
                    padding: 12px 16px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 500;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #F8FAFC;
                    color: #334155;
                }
                QPushButton:checked {
                    background-color: #3B82F6;
                    color: white;
                    font-weight: 600;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self._navigate_to(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        self.nav_buttons[0].setChecked(True)
        layout.addStretch()
        
        # Import button - estilo outline
        import_btn = QPushButton("+ Importar Chat")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                padding: 14px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        import_btn.clicked.connect(self._import_chat)
        layout.addWidget(import_btn)
        
        return sidebar
    
    def _create_header(self) -> QWidget:
        """Crear header con barra de búsqueda y avatar"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #F1F5F9;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(20)
        
        # Search bar
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(16, 0, 16, 0)
        search_layout.setSpacing(10)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #94A3B8; font-size: 16px;")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #334155;
                font-size: 14px;
                padding: 12px 0;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
            }
        """)
        self.search_input.setMinimumWidth(300)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_container)
        layout.addStretch()
        
        # Notifications
        notif_btn = QPushButton("🔔")
        notif_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #F8FAFC;
                border-radius: 8px;
            }
        """)
        layout.addWidget(notif_btn)
        
        # User avatar
        self.header_avatar = QLabel("E")
        self.header_avatar.setFixedSize(40, 40)
        self.header_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_avatar.setStyleSheet("""
            background-color: #E2E8F0;
            color: #475569;
            border-radius: 20px;
            font-weight: 600;
            font-size: 16px;
        """)
        layout.addWidget(self.header_avatar)
        
        return header
        
    def _navigate_to(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.content_stack.setCurrentIndex(index)
        
    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background-color: #FAFBFC;")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(24)
        
        # Stats cards - 3 tarjetas como en el mockup
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        self.stat_messages = StatCard("", "Mensajes", "0")
        self.stat_pending = StatCard("", "Tareas Pendientes", "0")
        self.stat_time = StatCard("", "Tiempo Promedio", "--")
        
        stats_layout.addWidget(self.stat_messages)
        stats_layout.addWidget(self.stat_pending)
        stats_layout.addWidget(self.stat_time)
        stats_layout.addStretch()
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Content grid
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        
        # Recent tasks - estilo mockup
        tasks_card = QFrame()
        tasks_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #F1F5F9;
                border-radius: 16px;
            }
        """)
        tasks_layout = QVBoxLayout(tasks_card)
        tasks_layout.setSpacing(8)
        tasks_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header de tareas
        tasks_header = QVBoxLayout()
        tasks_title = QLabel("Tareas Recientes")
        tasks_title.setStyleSheet("""
            color: #1E293B;
            font-size: 18px;
            font-weight: 700;
        """)
        tasks_header.addWidget(tasks_title)
        
        view_all_btn = QPushButton("Ver Todas")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748B;
                border: none;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                padding: 0;
            }
            QPushButton:hover {
                color: #3B82F6;
            }
        """)
        view_all_btn.clicked.connect(lambda: self._navigate_to(3))
        tasks_header.addWidget(view_all_btn)
        tasks_layout.addLayout(tasks_header)
        
        tasks_layout.addSpacing(12)
        
        self.dashboard_tasks_container = QVBoxLayout()
        self.dashboard_tasks_container.setSpacing(8)
        tasks_layout.addLayout(self.dashboard_tasks_container)
        tasks_layout.addStretch()
        content_layout.addWidget(tasks_card, 3)
        
        # Top Usuarios - estilo mockup
        persons_card = QFrame()
        persons_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #F1F5F9;
                border-radius: 16px;
            }
        """)
        persons_layout = QVBoxLayout(persons_card)
        persons_layout.setSpacing(16)
        persons_layout.setContentsMargins(20, 20, 20, 20)
        
        persons_header = QLabel("Top Usuarios")
        persons_header.setStyleSheet("""
            color: #1E293B;
            font-size: 18px;
            font-weight: 700;
        """)
        persons_layout.addWidget(persons_header)
        
        self.dashboard_persons_container = QVBoxLayout()
        self.dashboard_persons_container.setSpacing(12)
        persons_layout.addLayout(self.dashboard_persons_container)
        persons_layout.addStretch()
        content_layout.addWidget(persons_card, 2)
        
        layout.addLayout(content_layout, 1)
        
        return page
        
    def _create_my_profile_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(16)
        
        # Header con selector
        header_layout = QHBoxLayout()
        header = QLabel("Mi Perfil")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 24px;
            font-weight: 700;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Selector de usuario
        self.me_selector = QComboBox()
        self.me_selector.setFixedWidth(200)
        self.me_selector.setPlaceholderText("Selecciona tu usuario...")
        self.me_selector.currentIndexChanged.connect(self._on_me_selected)
        header_layout.addWidget(self.me_selector)
        layout.addLayout(header_layout)
        
        # Sistema de pestañas
        self.profile_tabs_container = QHBoxLayout()
        self.profile_tabs_container.setSpacing(0)
        
        self.profile_tab_buttons = []
        tab_names = [
            ("📊", "Resumen"),
            ("⭐", "Valoraciones"),
            ("📋", "Tareas"),
            ("📁", "Proyectos"),
            ("🔗", "Enlaces"),
            ("📈", "Actividad"),
            ("🎯", "Objetivos"),
            ("🛡️", "Alertas")
        ]
        
        for i, (icon, name) in enumerate(tab_names):
            btn = QPushButton(f"{icon} {name}")
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.clicked.connect(lambda checked, idx=i: self._switch_profile_tab(idx))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #64748B;
                    border: none;
                    border-bottom: 2px solid transparent;
                    padding: 12px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    color: #3B82F6;
                }
                QPushButton:checked {
                    color: #3B82F6;
                    border-bottom: 2px solid #3B82F6;
                    font-weight: 600;
                }
            """)
            self.profile_tab_buttons.append(btn)
            self.profile_tabs_container.addWidget(btn)
        
        self.profile_tabs_container.addStretch()
        layout.addLayout(self.profile_tabs_container)
        
        # Línea separadora
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #E2E8F0;")
        layout.addWidget(separator)
        
        # Contenedor de contenido de pestañas
        self.profile_content_stack = QStackedWidget()
        self.profile_content_stack.setStyleSheet("background: transparent;")
        
        # Crear las 8 páginas de pestañas
        self.profile_tab_pages = []
        for i in range(8):
            tab_page = QWidget()
            tab_page.setStyleSheet("background: transparent;")
            tab_layout = QVBoxLayout(tab_page)
            tab_layout.setContentsMargins(0, 16, 0, 0)
            tab_layout.setSpacing(16)
            self.profile_tab_pages.append(tab_layout)
            self.profile_content_stack.addWidget(tab_page)
        
        layout.addWidget(self.profile_content_stack, 1)
        
        # Estado vacío inicial
        self.profile_empty = EmptyState(
            "👤",
            "Selecciona tu usuario",
            "Elige tu nombre del selector para ver tu evaluación personal.",
        )
        self.profile_tab_pages[0].addWidget(self.profile_empty)
        
        return page
    
    def _switch_profile_tab(self, index: int):
        # Actualizar botones
        for i, btn in enumerate(self.profile_tab_buttons):
            btn.setChecked(i == index)
        # Cambiar página
        self.profile_content_stack.setCurrentIndex(index)
        # Cargar contenido si es necesario
        self._load_profile_tab_content(index)
    
    def _load_profile_tab_content(self, tab_index: int):
        me = self.db.get_me()
        if not me:
            return
        
        # Limpiar contenido anterior
        layout = self.profile_tab_pages[tab_index]
        self._clear_layout(layout)
        
        if tab_index == 0:
            self._load_profile_resumen(layout, me)
        elif tab_index == 1:
            self._load_profile_valoraciones(layout, me)
        elif tab_index == 2:
            self._load_profile_tareas(layout, me)
        elif tab_index == 3:
            self._load_profile_proyectos(layout, me)
        elif tab_index == 4:
            self._load_profile_enlaces(layout, me)
        elif tab_index == 5:
            self._load_profile_actividad(layout, me)
        elif tab_index == 6:
            self._load_profile_objetivos(layout, me)
        elif tab_index == 7:
            self._load_profile_alertas(layout, me)
    
    def _load_profile_resumen(self, layout: QVBoxLayout, me: dict):
        me_data = self.db.get_person_with_skills(me['id'])
        me_stats = self.db.get_person_stats(me['id'])
        
        # Tarjeta de perfil compacta
        profile_card = QFrame()
        profile_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        profile_layout = QHBoxLayout(profile_card)
        profile_layout.setContentsMargins(20, 20, 20, 20)
        profile_layout.setSpacing(16)
        
        # Avatar
        role_colors = ROLE_COLORS.get(me.get('role', 'desconocido').lower(), ROLE_COLORS['desconocido'])
        avatar = QLabel(me['name'][0].upper())
        avatar.setFixedSize(60, 60)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            border-radius: 30px;
            font-size: 24px;
            font-weight: 700;
        """)
        profile_layout.addWidget(avatar)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_row = QHBoxLayout()
        name_label = QLabel(me['name'])
        name_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        name_row.addWidget(name_label)
        
        you_badge = QLabel("TÚ")
        you_badge.setStyleSheet("""
            background-color: #3B82F6;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
        """)
        name_row.addWidget(you_badge)
        name_row.addStretch()
        info_layout.addLayout(name_row)
        
        role_label = QLabel(me.get('role', 'Desconocido').capitalize())
        role_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        info_layout.addWidget(role_label)
        
        profile_layout.addLayout(info_layout, 1)
        
        # Stats en el header
        stats_data = [
            (str(me_stats.get('total_messages', 0)), "Mensajes"),
            (str(me_stats.get('total_tasks', 0)), "Tareas"),
            (str(me_stats.get('completed_tasks', 0)), "Completadas"),
            (f"{me_stats.get('avg_skill_score', 0):.0f}%", "Promedio")
        ]
        for value, label in stats_data:
            stat_box = QVBoxLayout()
            stat_box.setSpacing(0)
            v = QLabel(value)
            v.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 20px; font-weight: 700;")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_box.addWidget(v)
            l = QLabel(label)
            l.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_box.addWidget(l)
            profile_layout.addLayout(stat_box)
        
        layout.addWidget(profile_card)
        
        # Descripción
        if me_data and me_data.get('profile_summary'):
            desc_card = QFrame()
            desc_card.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                }
            """)
            desc_layout = QVBoxLayout(desc_card)
            desc_layout.setContentsMargins(20, 16, 20, 16)
            desc_text = QLabel(me_data['profile_summary'])
            desc_text.setWordWrap(True)
            desc_text.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; line-height: 1.5;")
            desc_layout.addWidget(desc_text)
            layout.addWidget(desc_card)
        
        # Grid de resumen rápido
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(16)
        
        # Top 3 habilidades
        skills_card = QFrame()
        skills_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        skills_layout = QVBoxLayout(skills_card)
        skills_layout.setContentsMargins(16, 16, 16, 16)
        skills_layout.setSpacing(12)
        
        skills_header = QLabel("⭐ Top Habilidades")
        skills_header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
        skills_layout.addWidget(skills_header)
        
        if me_data and me_data.get('skills'):
            for skill in me_data['skills'][:3]:
                skill_row = QHBoxLayout()
                skill_name = QLabel(skill['name'])
                skill_name.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
                skill_row.addWidget(skill_name)
                skill_score = QLabel(f"{skill['score']:.0f}%")
                skill_score.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 600;")
                skill_row.addWidget(skill_score)
                skills_layout.addLayout(skill_row)
        else:
            no_skills = QLabel("Sin habilidades aún")
            no_skills.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            skills_layout.addWidget(no_skills)
        
        skills_layout.addStretch()
        grid_layout.addWidget(skills_card)
        
        # Tareas pendientes
        tasks_card = QFrame()
        tasks_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)
        tasks_layout = QVBoxLayout(tasks_card)
        tasks_layout.setContentsMargins(16, 16, 16, 16)
        tasks_layout.setSpacing(12)
        
        tasks_header = QLabel("📋 Tareas Pendientes")
        tasks_header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
        tasks_layout.addWidget(tasks_header)
        
        my_tasks = self.db.get_tasks_for_person(me['id'])
        pending_tasks = [t for t in my_tasks if t['status'] != 'completed'][:3]
        if pending_tasks:
            for task in pending_tasks:
                task_label = QLabel(f"• {task['title'][:40]}..." if len(task['title']) > 40 else f"• {task['title']}")
                task_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
                tasks_layout.addWidget(task_label)
        else:
            no_tasks = QLabel("🎉 Sin tareas pendientes")
            no_tasks.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            tasks_layout.addWidget(no_tasks)
        
        tasks_layout.addStretch()
        grid_layout.addWidget(tasks_card)
        
        layout.addLayout(grid_layout)
        layout.addStretch()
    
    def _load_profile_valoraciones(self, layout: QVBoxLayout, me: dict):
        me_data = self.db.get_person_with_skills(me['id'])
        
        header = QLabel("⭐ Mis Habilidades y Valoraciones")
        header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        layout.addWidget(header)
        
        if me_data and me_data.get('skills'):
            # Scroll para habilidades
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            
            scroll_content = QWidget()
            scroll_content.setStyleSheet("background: transparent;")
            skills_layout = QVBoxLayout(scroll_content)
            skills_layout.setSpacing(12)
            
            for skill in me_data['skills']:
                skill_card = QFrame()
                skill_card.setStyleSheet("""
                    QFrame {
                        background-color: #FFFFFF;
                        border: 1px solid #E2E8F0;
                        border-radius: 10px;
                    }
                """)
                skill_layout = QVBoxLayout(skill_card)
                skill_layout.setContentsMargins(16, 12, 16, 12)
                skill_layout.setSpacing(8)
                
                # Nombre y score
                row = QHBoxLayout()
                name = QLabel(skill['name'])
                name.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
                row.addWidget(name)
                
                score = QLabel(f"{skill['score']:.0f}%")
                score_color = "#10B981" if skill['score'] >= 80 else "#F59E0B" if skill['score'] >= 60 else "#EF4444"
                score.setStyleSheet(f"color: {score_color}; font-size: 14px; font-weight: 700;")
                row.addWidget(score)
                skill_layout.addLayout(row)
                
                # Barra de progreso
                progress_bg = QFrame()
                progress_bg.setFixedHeight(8)
                progress_bg.setStyleSheet("background-color: #E2E8F0; border-radius: 4px;")
                progress_layout = QHBoxLayout(progress_bg)
                progress_layout.setContentsMargins(0, 0, 0, 0)
                
                progress_fill = QFrame()
                progress_fill.setFixedHeight(8)
                progress_fill.setFixedWidth(int(skill['score'] * 3))  # Max 300px
                progress_fill.setStyleSheet(f"background-color: {score_color}; border-radius: 4px;")
                progress_layout.addWidget(progress_fill)
                progress_layout.addStretch()
                
                skill_layout.addWidget(progress_bg)
                skills_layout.addWidget(skill_card)
            
            skills_layout.addStretch()
            scroll.setWidget(scroll_content)
            layout.addWidget(scroll, 1)
        else:
            empty = EmptyState("⭐", "Sin valoraciones", "Importa un chat y análiza con IA para obtener valoraciones.")
            layout.addWidget(empty)
    
    def _load_profile_tareas(self, layout: QVBoxLayout, me: dict):
        header_row = QHBoxLayout()
        header = QLabel("📋 Mis Tareas")
        header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        header_row.addWidget(header)
        header_row.addStretch()
        
        # Filtros
        filter_btns = QHBoxLayout()
        filter_btns.setSpacing(8)
        filters = [("Todas", "all"), ("Pendientes", "pending"), ("Completadas", "completed")]
        for label, status in filters:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #64748B;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                }
            """)
            filter_btns.addLayout(filter_btns)
        header_row.addLayout(filter_btns)
        layout.addLayout(header_row)
        
        # Lista de tareas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        tasks_layout = QVBoxLayout(scroll_content)
        tasks_layout.setSpacing(8)
        
        my_tasks = self.db.get_tasks_for_person(me['id'])
        if my_tasks:
            for task in my_tasks:
                task_card = self._create_task_item(task)
                tasks_layout.addWidget(task_card)
        else:
            empty = EmptyState("📋", "Sin tareas", "No tienes tareas asignadas aún.")
            tasks_layout.addWidget(empty)
        
        tasks_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
    
    def _create_task_item(self, task: dict) -> QFrame:
        card = QFrame()
        is_completed = task['status'] == 'completed'
        priority = task.get('priority', 'medium')
        priority_colors = {
            'urgent': '#DC2626',
            'high': '#F59E0B',
            'medium': '#3B82F6',
            'low': '#10B981'
        }
        border_color = priority_colors.get(priority, '#3B82F6')
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 4px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Checkbox
        checkbox = QLabel("✓" if is_completed else "")
        checkbox.setFixedSize(24, 24)
        checkbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox.setStyleSheet(f"""
            background-color: {'#10B981' if is_completed else '#FFFFFF'};
            border: 2px solid {'#10B981' if is_completed else '#E2E8F0'};
            border-radius: 6px;
            color: white;
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(checkbox)
        
        # Info
        info = QVBoxLayout()
        info.setSpacing(4)
        
        title = QLabel(task['title'])
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 14px;
            font-weight: 500;
            {'text-decoration: line-through;' if is_completed else ''}
        """)
        info.addWidget(title)
        
        if task.get('description'):
            desc = QLabel(task['description'][:80] + '...' if len(task.get('description', '')) > 80 else task.get('description', ''))
            desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            info.addWidget(desc)
        
        layout.addLayout(info, 1)
        
        # Badge de prioridad
        priority_labels = {'urgent': 'Urgente', 'high': 'Alta', 'medium': 'Media', 'low': 'Baja'}
        priority_bg = {'urgent': '#FEE2E2', 'high': '#FEF3C7', 'medium': '#DBEAFE', 'low': '#D1FAE5'}
        badge = QLabel(priority_labels.get(priority, 'Media'))
        badge.setStyleSheet(f"""
            background-color: {priority_bg.get(priority, '#DBEAFE')};
            color: {border_color};
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
        """)
        layout.addWidget(badge)
        
        return card
    
    def _load_profile_proyectos(self, layout: QVBoxLayout, me: dict):
        header = QLabel("📁 Mis Proyectos")
        header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        layout.addWidget(header)
        
        projects = self.db.get_all_projects()
        if projects:
            for project in projects:
                project_card = QFrame()
                project_card.setStyleSheet("""
                    QFrame {
                        background-color: #FFFFFF;
                        border: 1px solid #E2E8F0;
                        border-radius: 12px;
                    }
                """)
                p_layout = QVBoxLayout(project_card)
                p_layout.setContentsMargins(16, 16, 16, 16)
                
                name = QLabel(project['name'])
                name.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 600;")
                p_layout.addWidget(name)
                
                if project.get('description'):
                    desc = QLabel(project['description'])
                    desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
                    desc.setWordWrap(True)
                    p_layout.addWidget(desc)
                
                layout.addWidget(project_card)
        else:
            empty = EmptyState("📁", "Sin proyectos", "Los proyectos se detectarán automáticamente de tus conversaciones.")
            layout.addWidget(empty)
        
        layout.addStretch()
    
    def _load_profile_enlaces(self, layout: QVBoxLayout, me: dict):
        header = QLabel("🔗 Enlaces Compartidos")
        header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        layout.addWidget(header)
        
        # Filtros por tipo
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        link_types = [("Todos", "all"), ("🛠️ Herramientas", "tool"), ("📚 Recursos", "resource"), 
                      ("🎓 Tutoriales", "tutorial"), ("📰 Artículos", "article")]
        for label, ltype in link_types:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F1F5F9;
                    color: #64748B;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #E2E8F0;
                }
            """)
            filter_row.addWidget(btn)
        filter_row.addStretch()
        layout.addLayout(filter_row)
        
        # Lista de enlaces
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        links_layout = QVBoxLayout(scroll_content)
        links_layout.setSpacing(8)
        
        links = self.db.get_all_links()
        if links:
            for link in links:
                link_card = QFrame()
                link_card.setStyleSheet("""
                    QFrame {
                        background-color: #FFFFFF;
                        border: 1px solid #E2E8F0;
                        border-radius: 10px;
                    }
                    QFrame:hover {
                        border-color: #3B82F6;
                    }
                """)
                l_layout = QVBoxLayout(link_card)
                l_layout.setContentsMargins(16, 12, 16, 12)
                l_layout.setSpacing(6)
                
                # URL y tipo
                top_row = QHBoxLayout()
                url_label = QLabel(link['url'][:60] + '...' if len(link['url']) > 60 else link['url'])
                url_label.setStyleSheet("color: #3B82F6; font-size: 13px; font-weight: 500;")
                top_row.addWidget(url_label)
                
                type_badge = QLabel(link.get('link_type', 'general').capitalize())
                type_badge.setStyleSheet("""
                    background-color: #EEF2FF;
                    color: #4F46E5;
                    padding: 2px 8px;
                    border-radius: 6px;
                    font-size: 10px;
                """)
                top_row.addWidget(type_badge)
                l_layout.addLayout(top_row)
                
                # Contexto
                if link.get('context'):
                    context = QLabel(link['context'])
                    context.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
                    context.setWordWrap(True)
                    l_layout.addWidget(context)
                
                # Info
                info_row = QHBoxLayout()
                shared_by = QLabel(f"👤 {link.get('shared_by_name', 'Desconocido')}")
                shared_by.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
                info_row.addWidget(shared_by)
                
                mentions = QLabel(f"🔁 {link.get('mention_count', 1)} veces")
                mentions.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
                info_row.addWidget(mentions)
                info_row.addStretch()
                l_layout.addLayout(info_row)
                
                links_layout.addWidget(link_card)
        else:
            empty = EmptyState("🔗", "Sin enlaces", "Los enlaces se extraerán automáticamente de tus conversaciones.")
            links_layout.addWidget(empty)
        
        links_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
    
    def _load_profile_actividad(self, layout: QVBoxLayout, me: dict):
        header = QLabel("📈 Mi Actividad")
        header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        layout.addWidget(header)
        
        activity = self.db.get_activity_by_date(me['id'])
        
        if activity:
            # Gráfico simple de actividad
            chart_card = QFrame()
            chart_card.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 12px;
                }
            """)
            chart_layout = QVBoxLayout(chart_card)
            chart_layout.setContentsMargins(20, 20, 20, 20)
            
            chart_header = QLabel("Mensajes por día (últimos 30 días)")
            chart_header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
            chart_layout.addWidget(chart_header)
            
            # Barras simples
            bars_layout = QHBoxLayout()
            bars_layout.setSpacing(2)
            max_count = max([a['count'] for a in activity]) if activity else 1
            
            for day in activity[:14]:  # Últimos 14 días
                bar_container = QVBoxLayout()
                bar_container.setSpacing(2)
                
                bar = QFrame()
                height = int((day['count'] / max_count) * 60) if max_count > 0 else 0
                bar.setFixedSize(16, max(height, 4))
                bar.setStyleSheet("background-color: #3B82F6; border-radius: 2px;")
                bar_container.addStretch()
                bar_container.addWidget(bar)
                
                bars_layout.addLayout(bar_container)
            
            bars_layout.addStretch()
            chart_layout.addLayout(bars_layout)
            
            layout.addWidget(chart_card)
            
            # Lista de actividad reciente
            for day in activity[:7]:
                day_label = QLabel(f"📅 {day['date']}: {day['count']} mensajes")
                day_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; padding: 8px 0;")
                layout.addWidget(day_label)
        else:
            empty = EmptyState("📈", "Sin actividad", "Importa un chat para ver tu actividad.")
            layout.addWidget(empty)
        
        layout.addStretch()
    
    def _load_profile_objetivos(self, layout: QVBoxLayout, me: dict):
        header_row = QHBoxLayout()
        header = QLabel("🎯 Mis Objetivos")
        header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 700;")
        header_row.addWidget(header)
        header_row.addStretch()
        
        add_btn = QPushButton("+ Nuevo Objetivo")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
        add_btn.clicked.connect(lambda: self._add_objective(me['id']))
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)
        
        objectives = self.db.get_objectives_for_person(me['id'])
        
        if objectives:
            for obj in objectives:
                obj_card = QFrame()
                obj_card.setStyleSheet("""
                    QFrame {
                        background-color: #FFFFFF;
                        border: 1px solid #E2E8F0;
                        border-radius: 12px;
                    }
                """)
                o_layout = QVBoxLayout(obj_card)
                o_layout.setContentsMargins(16, 16, 16, 16)
                o_layout.setSpacing(10)
                
                # Título
                title = QLabel(obj['title'])
                title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 600;")
                o_layout.addWidget(title)
                
                # Progreso
                progress = (obj['current_value'] / obj['target_value'] * 100) if obj['target_value'] > 0 else 0
                progress_row = QHBoxLayout()
                
                progress_bg = QFrame()
                progress_bg.setFixedHeight(10)
                progress_bg.setStyleSheet("background-color: #E2E8F0; border-radius: 5px;")
                progress_inner = QHBoxLayout(progress_bg)
                progress_inner.setContentsMargins(0, 0, 0, 0)
                
                progress_fill = QFrame()
                progress_fill.setFixedHeight(10)
                progress_fill.setFixedWidth(int(progress * 2))  # Max 200px
                progress_color = "#10B981" if progress >= 100 else "#3B82F6"
                progress_fill.setStyleSheet(f"background-color: {progress_color}; border-radius: 5px;")
                progress_inner.addWidget(progress_fill)
                progress_inner.addStretch()
                
                progress_row.addWidget(progress_bg, 1)
                
                progress_label = QLabel(f"{obj['current_value']:.0f}/{obj['target_value']:.0f} {obj.get('unit', '')}")
                progress_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px; margin-left: 8px;")
                progress_row.addWidget(progress_label)
                
                o_layout.addLayout(progress_row)
                layout.addWidget(obj_card)
        else:
            empty = EmptyState("🎯", "Sin objetivos", "Crea objetivos para hacer seguimiento de tu progreso.")
            layout.addWidget(empty)
        
        layout.addStretch()
    
    def _add_objective(self, person_id: int):
        from PyQt6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Nuevo Objetivo", "Título del objetivo:")
        if ok and title:
            self.db.add_objective(person_id, title)
            self._load_profile_tab_content(6)  # Recargar pestaña de objetivos
        
    def _load_profile_alertas(self, layout: QVBoxLayout, me: dict):
        """Carga la pestaña de alertas de comportamiento - Diseño según mockup"""
        try:
            # Obtener alertas primero para contar por tipo
            all_alerts = self.db.get_all_alerts(include_dismissed=False)
            
            # Contar alertas por tipo
            type_counts = {'all': len(all_alerts) if all_alerts else 0}
            type_names = {
                'inconsistency': 'Inconsistencias',
                'knowledge_abuse': 'Abuso de conocimiento', 
                'emotional_manipulation': 'Manipulación emocional',
                'possible_lies': 'Posibles mentiras',
                'red_flags': 'Señales de alerta'
            }
            for t in type_names.keys():
                type_counts[t] = len([a for a in all_alerts if a.get('alert_type') == t]) if all_alerts else 0
            
            # === TABS POR TIPO DE ALERTA ===
            tabs_row = QHBoxLayout()
            tabs_row.setSpacing(8)
            
            self.alert_type_buttons = {}
            
            # Tab "Todas"
            all_btn = QPushButton(f"Todas ({type_counts['all']})")
            all_btn.setCheckable(True)
            all_btn.setChecked(True)
            all_btn.setStyleSheet(self._get_tab_style(True))
            all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            all_btn.clicked.connect(lambda: self._filter_alerts_by_type('all'))
            tabs_row.addWidget(all_btn)
            self.alert_type_buttons['all'] = all_btn
            
            # Tabs por tipo
            for type_id, type_name in type_names.items():
                if type_counts[type_id] > 0:
                    btn = QPushButton(f"{type_name} ({type_counts[type_id]})")
                    btn.setCheckable(True)
                    btn.setStyleSheet(self._get_tab_style(False))
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.clicked.connect(lambda checked, tid=type_id: self._filter_alerts_by_type(tid))
                    tabs_row.addWidget(btn)
                    self.alert_type_buttons[type_id] = btn
            
            tabs_row.addStretch()
            layout.addLayout(tabs_row)
            layout.addSpacing(12)
            
            # === DESCRIPCIÓN Y ORDENAR ===
            desc_row = QHBoxLayout()
            desc = QLabel("Este sistema analiza los chats para detectar comportamientos problemáticos como inconsistencias, abuso de conocimiento, manipulación emocional, posibles mentiras y otras señales de alerta.")
            desc.setWordWrap(True)
            desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            desc_row.addWidget(desc, 1)
            
            # Ordenar por
            sort_label = QLabel("Ordenar por:")
            sort_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;")
            desc_row.addWidget(sort_label)
            
            self.alert_sort_combo = QComboBox()
            self.alert_sort_combo.addItems(['Riesgo', 'Usuario', 'Fecha'])
            self.alert_sort_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: white;
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    padding: 6px 12px;
                    min-width: 100px;
                    font-size: 12px;
                }}
            """)
            desc_row.addWidget(self.alert_sort_combo)
            
            sort_order = QComboBox()
            sort_order.addItems(['Descendente', 'Ascendente'])
            sort_order.setStyleSheet(f"""
                QComboBox {{
                    background-color: white;
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    padding: 6px 12px;
                    min-width: 100px;
                    font-size: 12px;
                }}
            """)
            desc_row.addWidget(sort_order)
            
            layout.addLayout(desc_row)
            layout.addSpacing(16)
            
            # === LISTA DE ALERTAS ===
            if all_alerts:
                # DEBUG: Imprimir datos de alertas
                print(f"\n=== DEBUG ALERTAS ===")
                for i, a in enumerate(all_alerts[:3]):
                    print(f"Alerta {i+1}: id={a.get('id')}, type={a.get('alert_type')}, severity={a.get('severity')}")
                    print(f"  title={repr(a.get('title'))}")
                    print(f"  description={repr(a.get('description')[:50] if a.get('description') else None)}")
                    print(f"  person_name={repr(a.get('person_name'))}")
                print(f"=== FIN DEBUG ===\n")
                
                # Ordenar por severidad: high > medium > low
                severity_order = {'high': 0, 'medium': 1, 'low': 2}
                sorted_alerts = sorted(all_alerts, key=lambda a: severity_order.get(a.get('severity', 'medium'), 1))
                
                self.alert_cards_container = QVBoxLayout()
                self.alert_cards_container.setSpacing(0)
                
                for alert in sorted_alerts:
                    alert_card = self._create_alert_card(alert)
                    self.alert_cards_container.addWidget(alert_card)
                
                layout.addLayout(self.alert_cards_container)
            else:
                # Controles de análisis cuando no hay alertas
                controls_card = QFrame()
                controls_card.setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS['bg_secondary']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 12px;
                    }}
                """)
                controls_layout = QVBoxLayout(controls_card)
                controls_layout.setContentsMargins(16, 16, 16, 16)
                controls_layout.setSpacing(12)
                
                person_row = QHBoxLayout()
                person_label = QLabel("👤 Analizar a:")
                person_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px; font-weight: 600;")
                person_row.addWidget(person_label)
                
                self.alert_person_combo = QComboBox()
                self.alert_person_combo.setStyleSheet(f"""
                    QComboBox {{
                        background-color: white;
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                        padding: 8px 12px;
                        min-width: 200px;
                    }}
                """)
                self.alert_person_combo.addItem("-- Selecciona una persona --", None)
                persons = self.db.get_all_persons(min_messages=1)
                for p in persons:
                    if p['name'] != me.get('name', ''):
                        self.alert_person_combo.addItem(p['name'], p['id'])
                person_row.addWidget(self.alert_person_combo)
                person_row.addStretch()
                controls_layout.addLayout(person_row)
                
                btn_row = QHBoxLayout()
                self.analyze_selected_btn = QPushButton("🔍 Analizar")
                self.analyze_selected_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3B82F6;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover { background-color: #2563EB; }
                """)
                self.analyze_selected_btn.clicked.connect(self._analyze_selected_person)
                btn_row.addWidget(self.analyze_selected_btn)
                
                self.alert_progress_label = QLabel("")
                self.alert_progress_label.hide()
                btn_row.addWidget(self.alert_progress_label)
                btn_row.addStretch()
                controls_layout.addLayout(btn_row)
                
                layout.addWidget(controls_card)
                layout.addSpacing(16)
                
                empty = EmptyState(
                    "✅",
                    "Sin alertas detectadas",
                    "No se han detectado comportamientos problemáticos. Selecciona una persona y haz clic en 'Analizar'."
                )
                layout.addWidget(empty)
            
            layout.addStretch()
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_label = QLabel(f"❌ Error al cargar alertas: {str(e)}")
            error_label.setStyleSheet("color: #DC2626; font-size: 13px;")
            error_label.setWordWrap(True)
            layout.addWidget(error_label)
            layout.addStretch()
    
    def _get_tab_style(self, is_active: bool) -> str:
        """Devuelve el estilo para los tabs de alertas"""
        if is_active:
            return """
                QPushButton {
                    background-color: #3B82F6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                }
            """
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: rgba(0,0,0,0.05);
            }}
        """
    
    def _filter_alerts_by_type(self, type_id: str):
        """Filtra las alertas por tipo"""
        # Actualizar estado visual de tabs
        for tid, btn in self.alert_type_buttons.items():
            btn.setChecked(tid == type_id)
            btn.setStyleSheet(self._get_tab_style(tid == type_id))
        
        # Recargar pestaña (en el futuro: filtrar sin recargar)
        self._load_profile_tab_content(7)
    
    def _create_alert_card(self, alert: dict) -> QFrame:
        """Genera widget de alerta usando QWidget puro sin stylesheets complejos"""
        # Crear contenedor principal
        container = QFrame()
        container.setMinimumHeight(120)
        container.setMaximumHeight(200)
        
        # Obtener datos de la alerta
        aid = alert.get('id', 0)
        atype = alert.get('alert_type', 'red_flags') or 'red_flags'
        sev = (alert.get('severity', 'medium') or 'medium').lower()
        quien = alert.get('person_name', 'Usuario') or 'Usuario'
        titulo = alert.get('title', '') or ''
        detalle = alert.get('description', '') or ''
        pid = alert.get('person_id')
        
        # Si no hay titulo, usar uno generico segun tipo
        if not titulo:
            titulos_default = {
                'inconsistency': 'Se detectaron inconsistencias',
                'knowledge_abuse': 'Posible aprovechamiento',
                'emotional_manipulation': 'Patron de manipulacion',
                'possible_lies': 'Informacion dudosa',
                'red_flags': 'Comportamiento inusual'
            }
            titulo = titulos_default.get(atype, 'Alerta de comportamiento')
        
        if not detalle:
            detalle = 'Se ha identificado un patron que podria requerir tu atencion.'
        
        # Colores segun severidad
        if sev == 'high':
            color_fondo = '#FFEBEE'
            color_borde = '#E53935'
            texto_badge = 'ALTA'
        elif sev == 'low':
            color_fondo = '#FFFDE7'
            color_borde = '#FBC02D'
            texto_badge = 'BAJA'
        else:
            color_fondo = '#FFF3E0'
            color_borde = '#FB8C00'
            texto_badge = 'MEDIA'
        
        # Aplicar fondo y borde al contenedor
        container.setAutoFillBackground(True)
        pal = container.palette()
        pal.setColor(container.backgroundRole(), QColor(color_fondo))
        container.setPalette(pal)
        container.setFrameShape(QFrame.Shape.Box)
        container.setLineWidth(1)
        container.setStyleSheet(f"border-left: 4px solid {color_borde}; border-radius: 6px;")
        
        # Layout principal vertical
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(6)
        
        # -- Linea superior: badge y nombre --
        linea_sup = QWidget()
        hbox_sup = QHBoxLayout(linea_sup)
        hbox_sup.setContentsMargins(0, 0, 0, 0)
        hbox_sup.setSpacing(10)
        
        # Badge severidad
        lbl_badge = QLabel(texto_badge)
        lbl_badge.setFixedHeight(22)
        font_badge = lbl_badge.font()
        font_badge.setBold(True)
        font_badge.setPointSize(9)
        lbl_badge.setFont(font_badge)
        lbl_badge.setAutoFillBackground(True)
        pal_badge = lbl_badge.palette()
        pal_badge.setColor(lbl_badge.backgroundRole(), QColor(color_borde))
        pal_badge.setColor(lbl_badge.foregroundRole(), QColor('white'))
        lbl_badge.setPalette(pal_badge)
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_badge.setFixedWidth(60)
        hbox_sup.addWidget(lbl_badge)
        
        hbox_sup.addStretch()
        
        # Nombre persona
        lbl_quien = QLabel(quien)
        font_quien = lbl_quien.font()
        font_quien.setPointSize(10)
        lbl_quien.setFont(font_quien)
        pal_quien = lbl_quien.palette()
        pal_quien.setColor(lbl_quien.foregroundRole(), QColor('#555555'))
        lbl_quien.setPalette(pal_quien)
        hbox_sup.addWidget(lbl_quien)
        
        vbox.addWidget(linea_sup)
        
        # -- Titulo --
        lbl_titulo = QLabel(titulo)
        font_titulo = lbl_titulo.font()
        font_titulo.setBold(True)
        font_titulo.setPointSize(11)
        lbl_titulo.setFont(font_titulo)
        lbl_titulo.setWordWrap(True)
        pal_titulo = lbl_titulo.palette()
        pal_titulo.setColor(lbl_titulo.foregroundRole(), QColor('#212121'))
        lbl_titulo.setPalette(pal_titulo)
        vbox.addWidget(lbl_titulo)
        
        # -- Descripcion --
        texto_corto = detalle if len(detalle) <= 120 else detalle[:120] + '...'
        lbl_desc = QLabel(texto_corto)
        font_desc = lbl_desc.font()
        font_desc.setPointSize(10)
        lbl_desc.setFont(font_desc)
        lbl_desc.setWordWrap(True)
        pal_desc = lbl_desc.palette()
        pal_desc.setColor(lbl_desc.foregroundRole(), QColor('#424242'))
        lbl_desc.setPalette(pal_desc)
        vbox.addWidget(lbl_desc)
        
        # -- Botones --
        linea_btns = QWidget()
        hbox_btns = QHBoxLayout(linea_btns)
        hbox_btns.setContentsMargins(0, 4, 0, 0)
        hbox_btns.setSpacing(8)
        
        if pid:
            btn_ver = QPushButton('Ver chat')
            btn_ver.setFixedHeight(28)
            btn_ver.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ver.clicked.connect(lambda: self._view_person_chat(pid))
            hbox_btns.addWidget(btn_ver)
        
        btn_ok = QPushButton('Marcar revisada')
        btn_ok.setFixedHeight(28)
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.clicked.connect(lambda: self._dismiss_alert(aid))
        hbox_btns.addWidget(btn_ok)
        
        hbox_btns.addStretch()
        vbox.addWidget(linea_btns)
        
        return container
    
    def _get_alert_type_tooltip(self, alert_type: str) -> str:
        """Devuelve tooltip explicativo para cada tipo de alerta"""
        tooltips = {
            'inconsistency': 'Cuando hay contradicciones entre lo que dice y lo que hace.',
            'knowledge_abuse': 'Cuando alguien intenta aprovechar tu experiencia sin compensación adecuada.',
            'emotional_manipulation': 'Uso de emociones para influir en decisiones o comportamientos.',
            'possible_lies': 'Información que podría no ser veraz o verificable.',
            'red_flags': 'Patrones de comportamiento que requieren atención.'
        }
        return tooltips.get(alert_type, 'Alerta de comportamiento detectada.')
    
    def _view_person_chat(self, person_id: int):
        """Navega al perfil de la persona para ver sus mensajes"""
        # Ir a Mi Perfil y seleccionar la persona
        self._navigate_to(1)  # Índice de Mi Perfil
        # TODO: Implementar selección automática de persona
    
    def _filter_alerts(self, filter_id: str):
        """Filtra las alertas por severidad"""
        # Actualizar estado de botones
        for btn_id, btn in self.alert_filter_buttons.items():
            btn.setChecked(btn_id == filter_id)
        
        # Recargar pestaña de alertas con filtro
        self._load_profile_tab_content(7)  # Esto recarga todo, podríamos optimizar
    
    def _sort_alerts(self, sort_by: str):
        """Ordena las alertas según criterio seleccionado"""
        # Por ahora solo recarga, el ordenamiento ya está por prioridad por defecto
        self._load_profile_tab_content(7)
    
    def _dismiss_alert(self, alert_id: int):
        """Descarta una alerta"""
        self.db.dismiss_alert(alert_id)
        self._load_profile_tab_content(7)  # Recargar pestaña de alertas
    
    def _analyze_selected_person(self):
        """Analiza comportamientos de la persona seleccionada (requiere selección individual)"""
        api_key = self.db.get_setting('api_key')
        if not api_key:
            QMessageBox.warning(self, "API Key requerida", 
                "Configura tu API Key de Gemini en Configuración para usar el análisis de comportamiento.")
            return
        
        me = self.db.get_me()
        if not me:
            QMessageBox.warning(self, "Usuario no seleccionado",
                "Selecciona tu usuario en el selector de 'Mi Perfil' primero.")
            return
        
        # Obtener persona seleccionada - REQUIERE selección individual
        selected_person_id = self.alert_person_combo.currentData()
        
        if not selected_person_id:
            QMessageBox.warning(self, "Selecciona una persona",
                "Debes seleccionar una persona específica para analizar.\n\n"
                "Analizar a todas las personas consumiría muchos créditos de IA.\n"
                "Selecciona una persona del desplegable.")
            return
        
        person = self.db.get_person(selected_person_id)
        if not person:
            QMessageBox.warning(self, "Error", "No se encontró la persona seleccionada.")
            return
        
        # Contar mensajes para mostrar confirmación
        messages = self.db.get_messages_for_person(person['id'])
        msg_count = len(messages)
        
        if msg_count < 5:
            QMessageBox.information(self, "Pocos mensajes",
                f"{person['name']} solo tiene {msg_count} mensajes.\n"
                "Se necesitan al menos 5 mensajes para analizar comportamientos.")
            return
        
        # Confirmación antes de analizar
        reply = QMessageBox.question(self, "Confirmar análisis con IA",
            f"Vas a analizar {msg_count} mensajes de {person['name']}.\n\n"
            f"Esto consumirá créditos de tu API de IA.\n\n"
            f"¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        persons_to_analyze = [person]
        target_name = person['name']
        
        # Deshabilitar botón y mostrar progreso
        self.analyze_selected_btn.setEnabled(False)
        self.analyze_selected_btn.setText("⏳ Analizando...")
        self.alert_progress_label.setText(f"Analizando {target_name}...")
        self.alert_progress_label.show()
        
        # Crear worker thread
        self.alert_worker = BehaviorAnalysisWorker(
            api_key=api_key,
            persons=persons_to_analyze,
            me_name=me['name'],
            db_path=self.db.db_path
        )
        self.alert_worker.progress.connect(self._on_alert_progress)
        self.alert_worker.finished.connect(self._on_alert_analysis_finished)
        self.alert_worker.error.connect(self._on_alert_analysis_error)
        self.alert_worker.start()
    
    def _on_alert_progress(self, message: str):
        """Actualiza el progreso del análisis"""
        self.alert_progress_label.setText(message)
    
    def _on_alert_analysis_finished(self, total_alerts: int):
        """Callback cuando termina el análisis"""
        self.analyze_selected_btn.setEnabled(True)
        self.analyze_selected_btn.setText("🔍 Analizar")
        self.alert_progress_label.hide()
        
        # Notificación
        QMessageBox.information(self, "✅ Análisis completado",
            f"Se detectaron {total_alerts} alertas de comportamiento.\n\n"
            "Puedes seguir trabajando mientras se analizan más personas.")
        
        # Recargar pestaña de alertas
        self._load_profile_tab_content(7)
    
    def _on_alert_analysis_error(self, error_msg: str):
        """Callback cuando hay error en el análisis"""
        self.analyze_selected_btn.setEnabled(True)
        self.analyze_selected_btn.setText("🔍 Analizar")
        self.alert_progress_label.hide()
        QMessageBox.critical(self, "Error", f"Error al analizar: {error_msg}")
    
    def _analyze_behavior_alerts(self):
        """Método legacy - redirige al nuevo"""
        self._analyze_selected_person()
    
    def _create_persons_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("Personas")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.persons_grid = QGridLayout(scroll_content)
        self.persons_grid.setSpacing(20)
        self.persons_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.persons_empty = EmptyState(
            "👥",
            "No hay personas",
            "Importa un chat de Telegram para ver los perfiles de los participantes.",
            "Importar Chat"
        )
        self.persons_empty.action_clicked.connect(self._import_chat)
        self.persons_empty.hide()
        layout.addWidget(self.persons_empty)
        
        return page
        
    def _create_tasks_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("Tareas")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Filtro de estado
        self.task_filter = QComboBox()
        self.task_filter.addItems(["Todas", "Pendientes", "En progreso", "Completadas"])
        self.task_filter.setFixedWidth(150)
        self.task_filter.currentTextChanged.connect(self._filter_tasks)
        header_layout.addWidget(self.task_filter)
        
        # Filtro por persona
        self.task_person_filter = QComboBox()
        self.task_person_filter.addItem("Todas las personas", None)
        self.task_person_filter.setFixedWidth(180)
        self.task_person_filter.currentIndexChanged.connect(self._filter_tasks_by_person)
        header_layout.addWidget(self.task_person_filter)
        
        # Toggle agrupación
        self.group_toggle = QPushButton("📂 Agrupar")
        self.group_toggle.setCheckable(True)
        self.group_toggle.setChecked(True)
        self.group_toggle.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_soft']};
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                padding: 8px 16px;
            }}
            QPushButton:checked {{
                background-color: {COLORS['accent']};
                color: white;
            }}
        """)
        self.group_toggle.clicked.connect(self._toggle_task_grouping)
        header_layout.addWidget(self.group_toggle)
        
        add_btn = QPushButton("+ Nueva Tarea")
        add_btn.clicked.connect(self._add_task_dialog)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.tasks_list = QVBoxLayout(scroll_content)
        self.tasks_list.setSpacing(16)
        self.tasks_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tasks_empty = EmptyState(
            "✅",
            "No hay tareas",
            "Las tareas se extraerán automáticamente al analizar un chat con IA.",
            "Importar Chat"
        )
        self.tasks_empty.action_clicked.connect(self._import_chat)
        self.tasks_empty.hide()
        layout.addWidget(self.tasks_empty)
        
        return page
        
    def _create_patterns_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header = QLabel("Patrones Detectados")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.patterns_grid = QGridLayout(scroll_content)
        self.patterns_grid.setSpacing(20)
        self.patterns_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.patterns_empty = EmptyState(
            "🔍",
            "No hay patrones",
            "Los patrones de comunicación se detectarán al analizar con IA.",
            "Importar Chat"
        )
        self.patterns_empty.action_clicked.connect(self._import_chat)
        self.patterns_empty.hide()
        layout.addWidget(self.patterns_empty)
        
        return page
    
    def _create_commitments_page(self) -> QWidget:
        """Crea la página de compromisos detectados"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("🤝 Compromisos Detectados")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Filtro de estado
        self.commitment_filter = QComboBox()
        self.commitment_filter.addItems(["Todos", "Pendientes", "Completados", "Cancelados"])
        self.commitment_filter.setStyleSheet(f"""
            QComboBox {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 150px;
            }}
        """)
        self.commitment_filter.currentTextChanged.connect(self._load_commitments)
        header_layout.addWidget(self.commitment_filter)
        
        layout.addLayout(header_layout)
        
        # Descripción
        desc = QLabel("Promesas, acuerdos y compromisos detectados automáticamente en las conversaciones.")
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        layout.addWidget(desc)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.commitments_list = QVBoxLayout(scroll_content)
        self.commitments_list.setSpacing(12)
        self.commitments_list.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll, 1)
        
        # Estado vacío
        self.commitments_empty = EmptyState(
            "🤝",
            "No hay compromisos detectados",
            "Los compromisos se detectan automáticamente al analizar personas con IA.",
        )
        self.commitments_empty.hide()
        layout.addWidget(self.commitments_empty)
        
        return page
    
    def _load_commitments(self, filter_text: str = None):
        """Carga los compromisos en la lista"""
        self._clear_layout(self.commitments_list)
        
        # Mapear filtro a estado
        status_map = {
            "Pendientes": "pending",
            "Completados": "completed",
            "Cancelados": "cancelled"
        }
        status = status_map.get(filter_text)
        
        commitments = self.db.get_all_commitments(status)
        
        if not commitments:
            self.commitments_empty.show()
            return
        
        self.commitments_empty.hide()
        
        for commitment in commitments:
            card = self._create_commitment_card(commitment)
            self.commitments_list.addWidget(card)
        
        self.commitments_list.addStretch()
    
    def _create_commitment_card(self, commitment: dict) -> QFrame:
        """Crea una tarjeta de compromiso"""
        card = QFrame()
        
        # Color según tipo
        type_colors = {
            'promise': ('#EFF6FF', '#BFDBFE', '#3B82F6'),
            'agreement': ('#F0FDF4', '#BBF7D0', '#10B981'),
            'deadline': ('#FEF3C7', '#FDE68A', '#F59E0B')
        }
        bg, border, accent = type_colors.get(commitment.get('commitment_type', 'promise'), type_colors['promise'])
        
        # Estado
        status = commitment.get('status', 'pending')
        status_styles = {
            'pending': ('⏳', 'Pendiente', '#F59E0B'),
            'completed': ('✅', 'Completado', '#10B981'),
            'cancelled': ('❌', 'Cancelado', '#EF4444')
        }
        status_icon, status_text, status_color = status_styles.get(status, status_styles['pending'])
        
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-left: 4px solid {accent};
                border-radius: 12px;
            }}
        """)
        
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 16, 20, 16)
        c_layout.setSpacing(10)
        
        # Header
        header = QHBoxLayout()
        
        # Tipo
        type_names = {'promise': '💬 Promesa', 'agreement': '🤝 Acuerdo', 'deadline': '📅 Fecha límite'}
        type_label = QLabel(type_names.get(commitment.get('commitment_type', 'promise'), '💬 Promesa'))
        type_label.setStyleSheet(f"color: {accent}; font-size: 12px; font-weight: 600;")
        header.addWidget(type_label)
        
        header.addStretch()
        
        # Persona
        person_label = QLabel(f"👤 {commitment.get('person_name', 'Desconocido')}")
        person_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        header.addWidget(person_label)
        
        # Estado badge
        status_badge = QLabel(f"{status_icon} {status_text}")
        status_badge.setStyleSheet(f"""
            color: {status_color};
            font-size: 11px;
            font-weight: 600;
            padding: 4px 8px;
            background: rgba(255,255,255,0.7);
            border-radius: 6px;
        """)
        header.addWidget(status_badge)
        
        c_layout.addLayout(header)
        
        # Título
        title = QLabel(commitment.get('title', 'Sin título'))
        title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 15px; font-weight: 600;")
        title.setWordWrap(True)
        c_layout.addWidget(title)
        
        # Evidencia
        if commitment.get('evidence'):
            evidence = QLabel(f'"{commitment["evidence"]}"')
            evidence.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; font-style: italic;")
            evidence.setWordWrap(True)
            c_layout.addWidget(evidence)
        
        # Fecha límite
        if commitment.get('due_date'):
            due_label = QLabel(f"📅 Fecha límite: {commitment['due_date']}")
            due_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            c_layout.addWidget(due_label)
        
        # Botones de acción
        if status == 'pending':
            actions = QHBoxLayout()
            actions.addStretch()
            
            complete_btn = QPushButton("✓ Completar")
            complete_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['success']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background: #059669; }}
            """)
            complete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            complete_btn.clicked.connect(lambda _, cid=commitment['id']: self._update_commitment(cid, 'completed'))
            actions.addWidget(complete_btn)
            
            cancel_btn = QPushButton("✕ Cancelar")
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {COLORS['text_muted']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                }}
                QPushButton:hover {{ background: #FEE2E2; color: #EF4444; }}
            """)
            cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            cancel_btn.clicked.connect(lambda _, cid=commitment['id']: self._update_commitment(cid, 'cancelled'))
            actions.addWidget(cancel_btn)
            
            c_layout.addLayout(actions)
        
        return card
    
    def _update_commitment(self, commitment_id: int, status: str):
        """Actualiza el estado de un compromiso"""
        self.db.update_commitment_status(commitment_id, status)
        self._load_commitments(self.commitment_filter.currentText())
        
    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)
        
        # Header
        header = QLabel("Configuración")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        layout.addWidget(header)
        
        # API Settings Card
        api_card = Card()
        api_layout = QVBoxLayout(api_card)
        api_layout.setSpacing(20)
        
        api_header = QLabel("🔑 Configuración de IA")
        api_header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: 600;
        """)
        api_layout.addWidget(api_header)
        
        api_desc = QLabel("Configura tu API key para habilitar el análisis inteligente con IA.")
        api_desc.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        api_layout.addWidget(api_desc)
        
        # Provider
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Proveedor:")
        provider_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        provider_label.setFixedWidth(100)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Gemini (Recomendado)", "OpenAI"])
        self.provider_combo.setFixedWidth(250)
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        api_layout.addLayout(provider_layout)
        
        # API Key
        key_layout = QHBoxLayout()
        key_label = QLabel("API Key:")
        key_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
        key_label.setFixedWidth(100)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Ingresa tu API key...")
        self.api_key_input.setFixedWidth(400)
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.api_key_input)
        key_layout.addStretch()
        api_layout.addLayout(key_layout)
        
        # Help text
        help_text = QLabel("💡 Obtén tu API key gratis en ai.google.dev (Gemini) o platform.openai.com (OpenAI)")
        help_text.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        api_layout.addWidget(help_text)
        
        # Save button
        save_btn = QPushButton("Guardar Configuración")
        save_btn.setFixedWidth(200)
        save_btn.clicked.connect(self._save_api_settings)
        api_layout.addWidget(save_btn)
        
        layout.addWidget(api_card)
        
        # Data Management Card
        data_card = Card()
        data_layout = QVBoxLayout(data_card)
        data_layout.setSpacing(16)
        
        data_header = QLabel("🗄️ Gestión de Datos")
        data_header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: 600;
        """)
        data_layout.addWidget(data_header)
        
        clear_btn = QPushButton("🗑️ Limpiar todos los datos")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error_soft']};
                color: {COLORS['error']};
                border: 1px solid {COLORS['error']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
                color: white;
            }}
        """)
        clear_btn.setFixedWidth(250)
        clear_btn.clicked.connect(self._clear_all_data)
        data_layout.addWidget(clear_btn)
        
        layout.addWidget(data_card)
        
        # Update Card
        update_card = Card()
        update_layout = QVBoxLayout(update_card)
        update_layout.setSpacing(16)
        
        update_header = QLabel("🔄 Actualización")
        update_header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: 600;
        """)
        update_layout.addWidget(update_header)
        
        version_label = QLabel(f"Versión actual: {APP_VERSION}")
        version_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
        update_layout.addWidget(version_label)
        
        self.update_status_label = QLabel("")
        self.update_status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
        update_layout.addWidget(self.update_status_label)
        
        update_buttons = QHBoxLayout()
        
        check_update_btn = QPushButton("🔍 Buscar actualizaciones")
        check_update_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent_soft']};
                color: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent']};
                color: white;
            }}
        """)
        check_update_btn.setFixedWidth(200)
        check_update_btn.clicked.connect(self._check_for_updates)
        update_buttons.addWidget(check_update_btn)
        
        self.download_update_btn = QPushButton("⬇️ Descargar e instalar")
        self.download_update_btn.setFixedWidth(200)
        self.download_update_btn.clicked.connect(self._download_and_install_update)
        self.download_update_btn.setEnabled(False)
        update_buttons.addWidget(self.download_update_btn)
        
        update_buttons.addStretch()
        update_layout.addLayout(update_buttons)
        
        layout.addWidget(update_card)
        layout.addStretch()
        
        return page
        
    def _check_for_updates(self):
        """Busca actualizaciones en GitHub"""
        try:
            self.update_status_label.setText("Buscando actualizaciones...")
            self.update_status_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px;")
            QApplication.processEvents()
            
            # Try to get VERSION file first
            try:
                with urllib.request.urlopen(GITHUB_VERSION_URL, timeout=10) as response:
                    remote_version = response.read().decode('utf-8').strip()
            except:
                # If VERSION file doesn't exist, get version from the Python file
                with urllib.request.urlopen(GITHUB_RAW_URL, timeout=10) as response:
                    content = response.read().decode('utf-8')
                    match = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        remote_version = match.group(1)
                    else:
                        remote_version = APP_VERSION
            
            self.remote_version = remote_version
            
            if self._compare_versions(remote_version, APP_VERSION) > 0:
                self.update_status_label.setText(f"✅ Nueva versión disponible: {remote_version}")
                self.update_status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px; font-weight: 500;")
                self.download_update_btn.setEnabled(True)
            else:
                self.update_status_label.setText("✅ Ya tienes la última versión")
                self.update_status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px;")
                self.download_update_btn.setEnabled(False)
                
        except Exception as e:
            self.update_status_label.setText(f"❌ Error al buscar actualizaciones: {str(e)}")
            self.update_status_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 13px;")
            
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compara dos versiones. Retorna >0 si v1 > v2, <0 si v1 < v2, 0 si iguales"""
        def parse_version(v):
            return [int(x) for x in re.findall(r'\d+', v)]
        
        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0
        
    def _download_and_install_update(self):
        """Descarga e instala la actualización"""
        try:
            self.update_status_label.setText("Descargando actualización...")
            self.update_status_label.setStyleSheet(f"color: {COLORS['accent']}; font-size: 13px;")
            QApplication.processEvents()
            
            # Get current script path
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                QMessageBox.warning(
                    self, "Actualización Manual",
                    "Estás usando la versión compilada (.exe).\n\n"
                    "Para actualizar:\n"
                    "1. Descarga el nuevo TelegramChatAnalyzer.py desde GitHub\n"
                    "2. Recompila con PyInstaller\n\n"
                    f"URL: https://github.com/{GITHUB_REPO}"
                )
                return
            
            current_file = os.path.abspath(__file__)
            backup_file = current_file + ".backup"
            
            # Download new version
            with urllib.request.urlopen(GITHUB_RAW_URL, timeout=30) as response:
                new_content = response.read()
            
            # Create backup
            shutil.copy2(current_file, backup_file)
            
            # Write new version
            with open(current_file, 'wb') as f:
                f.write(new_content)
            
            self.update_status_label.setText("✅ Actualización instalada. Reinicia la aplicación.")
            self.update_status_label.setStyleSheet(f"color: {COLORS['success']}; font-size: 13px; font-weight: 500;")
            self.download_update_btn.setEnabled(False)
            
            reply = QMessageBox.question(
                self, "Actualización Completada",
                f"Se ha actualizado a la versión {getattr(self, 'remote_version', 'nueva')}.\n\n"
                "¿Deseas reiniciar la aplicación ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._restart_application()
                
        except Exception as e:
            self.update_status_label.setText(f"❌ Error al actualizar: {str(e)}")
            self.update_status_label.setStyleSheet(f"color: {COLORS['error']}; font-size: 13px;")
            
            # Try to restore backup
            if os.path.exists(backup_file):
                try:
                    shutil.copy2(backup_file, current_file)
                except:
                    pass
                    
    def _restart_application(self):
        """Reinicia la aplicación"""
        python = sys.executable
        script = os.path.abspath(__file__)
        
        if self.db:
            self.db.close()
        
        subprocess.Popen([python, script])
        QApplication.quit()
        
    def _create_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Archivo")
        
        import_action = QAction("Importar Chat...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self._import_chat)
        file_menu.addAction(import_action)
        
        analyze_action = QAction("Analizar con IA", self)
        analyze_action.setShortcut("Ctrl+A")
        analyze_action.triggered.connect(self._run_ai_analysis)
        file_menu.addAction(analyze_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    def _init_database(self):
        self.db = Database()
        self.db.connect()
        
        api_key = self.db.get_setting('api_key')
        provider = self.db.get_setting('provider', 'gemini')
        
        if api_key:
            self.api_key_input.setText(api_key)
        if provider == 'openai':
            self.provider_combo.setCurrentIndex(1)
        
    def _load_data(self):
        self._update_dashboard()
        self._load_persons()
        self._populate_person_filter()  # Llenar filtro de personas
        self._load_tasks()
        self._load_patterns()
        self._load_commitments()
        self._update_me_selector()
        self._load_my_profile()
        
    def _update_dashboard(self):
        stats = self.db.get_dashboard_stats()
        
        # Actualizar las 3 tarjetas de estadísticas
        self.stat_messages.set_value(str(stats.get('total_messages', 0)))
        self.stat_pending.set_value(str(stats.get('pending_tasks', 0)))
        self.stat_time.set_value("2 min")  # Tiempo promedio placeholder
        
        # Recent tasks
        self._clear_layout(self.dashboard_tasks_container)
        tasks = self.db.get_all_tasks()[:5]
        for task in tasks:
            item = TaskCard(
                task['id'], task['title'], task.get('description', ''),
                task.get('status', 'pending'), task.get('priority', 'medium'),
                task.get('category', 'general'), task.get('assigned_to_name')
            )
            item.status_changed.connect(self._on_task_status_changed)
            self.dashboard_tasks_container.addWidget(item)
            
        if not tasks:
            empty_label = QLabel("No hay tareas aún")
            empty_label.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 20px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dashboard_tasks_container.addWidget(empty_label)
            
        # Top Usuarios - estilo mockup
        self._clear_layout(self.dashboard_persons_container)
        persons = self.db.get_all_persons(min_messages=1)[:4]
        for person in persons:
            person_frame = QFrame()
            person_frame.setStyleSheet("""
                QFrame {
                    background-color: transparent;
                    border: none;
                }
                QFrame:hover {
                    background-color: #F8FAFC;
                    border-radius: 8px;
                }
            """)
            p_layout = QHBoxLayout(person_frame)
            p_layout.setContentsMargins(8, 8, 8, 8)
            p_layout.setSpacing(12)
            
            # Avatar circular con foto placeholder (color basado en rol)
            role_colors = ROLE_COLORS.get(person.get('role', 'desconocido').lower(), ROLE_COLORS['desconocido'])
            avatar = QLabel(person['name'][0].upper())
            avatar.setFixedSize(44, 44)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet(f"""
                background-color: #E2E8F0;
                color: #475569;
                border-radius: 22px;
                font-weight: 700;
                font-size: 18px;
            """)
            p_layout.addWidget(avatar)
            
            # Info: nombre y rol en badge
            info = QVBoxLayout()
            info.setSpacing(4)
            
            name_label = QLabel(person['name'])
            name_label.setStyleSheet("""
                color: #1E293B;
                font-weight: 600;
                font-size: 14px;
            """)
            info.addWidget(name_label)
            
            # Badge de rol
            role_text = person.get('role', 'Desconocido').capitalize()
            role_badge = QLabel(role_text)
            role_badge.setStyleSheet("""
                background-color: #F1F5F9;
                color: #64748B;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 500;
            """)
            role_badge.setFixedWidth(role_badge.sizeHint().width() + 16)
            info.addWidget(role_badge)
            
            p_layout.addLayout(info)
            p_layout.addStretch()
            
            # Punto verde de actividad
            activity_dot = QLabel("●")
            activity_dot.setStyleSheet("""
                color: #10B981;
                font-size: 12px;
            """)
            p_layout.addWidget(activity_dot)
            
            self.dashboard_persons_container.addWidget(person_frame)
            
    def _update_me_selector(self):
        self.me_selector.clear()
        self.me_selector.addItem("Selecciona tu usuario...", None)
        
        persons = self.db.get_all_persons(min_messages=1)
        me = self.db.get_me()
        
        for person in persons:
            self.me_selector.addItem(person['name'], person['id'])
            if me and person['id'] == me['id']:
                self.me_selector.setCurrentIndex(self.me_selector.count() - 1)
                
    def _on_me_selected(self, index: int):
        if index <= 0:
            return
        person_id = self.me_selector.currentData()
        if person_id:
            self.db.set_me(person_id)
            self._load_my_profile()
            
    def _load_my_profile(self):
        # Cargar la primera pestaña (Resumen) por defecto
        me = self.db.get_me()
        if not me:
            # Limpiar todas las pestañas y mostrar estado vacío
            for i, tab_layout in enumerate(self.profile_tab_pages):
                self._clear_layout(tab_layout)
                if i == 0:
                    empty_state = EmptyState(
                        "👤",
                        "Selecciona tu usuario",
                        "Elige tu nombre del selector para ver tu evaluación personal.",
                    )
                    tab_layout.addWidget(empty_state)
            return
        
        # Cargar contenido de la pestaña actual
        current_tab = self.profile_content_stack.currentIndex()
        self._load_profile_tab_content(current_tab)
        
    def _load_persons(self):
        self._clear_layout(self.persons_grid)
        persons = self.db.get_all_persons(min_messages=1)
        
        if not persons:
            self.persons_empty.show()
            return
        self.persons_empty.hide()
        
        me = self.db.get_me()
        # Calcular número de columnas basado en el ancho disponible
        # Mínimo 1 columna, máximo 4
        available_width = self.content_stack.width() - 100  # Margen
        card_width = 300  # Ancho aproximado de tarjeta
        max_cols = max(1, min(4, available_width // card_width)) if available_width > 0 else 3
        
        col, row = 0, 0
        
        for person in persons:
            person_data = self.db.get_person_with_skills(person['id'])
            skills = person_data.get('skills', []) if person_data else []
            is_me = me and person['id'] == me['id']
            ai_analyzed = bool(person.get('ai_analyzed', 0))
            sentiment = person.get('sentiment', 'neutral')
            sentiment_score = float(person.get('sentiment_score', 0.0) or 0.0)
            
            avatar_path = person.get('avatar_path')
            
            card = PersonCard(
                person['id'], person['name'], person.get('role', 'desconocido'),
                skills=skills, message_count=person.get('total_messages', 0),
                is_me=is_me, ai_analyzed=ai_analyzed,
                sentiment=sentiment, sentiment_score=sentiment_score,
                avatar_path=avatar_path
            )
            card.clicked.connect(lambda p=person: self._show_person_detail(p))
            card.analyze_clicked.connect(self._analyze_person_from_card)
            card.edit_clicked.connect(self._edit_person_name)
            card.delete_clicked.connect(self._delete_person)
            card.avatar_clicked.connect(self._change_person_avatar)
            self.persons_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configurar stretch para que las columnas se expandan uniformemente
        for i in range(max_cols):
            self.persons_grid.setColumnStretch(i, 1)
    
    def _analyze_person_from_card(self, person_id: int):
        """Analiza una persona desde el botón de la tarjeta"""
        person = self.db.get_person(person_id)
        if not person:
            return
        
        # Verificar API key
        api_key = self.api_key_input.text() or os.environ.get('GEMINI_API_KEY')
        if not api_key:
            QMessageBox.warning(
                self, "API Key requerida",
                "Configura tu API key en Configuración para usar el análisis con IA."
            )
            self._navigate_to(5)  # Ir a configuración
            return
        
        # Obtener mensajes de la persona
        messages = self.db.get_messages_for_person(person_id)
        if not messages:
            QMessageBox.warning(self, "Sin mensajes", f"No hay mensajes de {person['name']} para analizar.")
            return
        
        # Confirmación
        reply = QMessageBox.question(
            self, "Confirmar análisis con IA",
            f"Vas a analizar a {person['name']}:\n\n"
            f"• {len(messages)} mensajes\n\n"
            f"Esto consumirá créditos de tu API de IA.\n\n"
            f"¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Preparar datos para el análisis
        self.loading_overlay.show_indeterminate(f"Analizando a {person['name']}...")
        self.loading_overlay.show()
        QApplication.processEvents()
        
        # Crear thread de análisis para esta persona - filtrar mensajes vacíos/None
        valid_messages = []
        for m in messages:
            content = m.get('content')
            if content is not None and str(content).strip():
                valid_messages.append(m)
        
        if not valid_messages:
            self.loading_overlay.hide()
            QMessageBox.warning(self, "Sin contenido", f"Los mensajes de {person['name']} no tienen contenido válido para analizar.")
            return
        
        # Muestreo inteligente: tomar mensajes de diferentes períodos
        # Para obtener una visión más representativa
        total_valid = len(valid_messages)
        max_messages = 300  # Aumentado de 100 a 300
        
        if total_valid <= max_messages:
            sampled_messages = valid_messages
        else:
            # Tomar mensajes distribuidos: inicio, medio y final
            step = total_valid // max_messages
            sampled_messages = []
            # 40% más recientes (al final)
            recent_count = int(max_messages * 0.4)
            sampled_messages.extend(valid_messages[-recent_count:])
            # 30% del medio
            middle_count = int(max_messages * 0.3)
            middle_start = total_valid // 3
            sampled_messages.extend(valid_messages[middle_start:middle_start + middle_count])
            # 30% más antiguos (al inicio)
            old_count = max_messages - len(sampled_messages)
            sampled_messages.extend(valid_messages[:old_count])
        
        # Construir texto de mensajes con protección extra
        messages_lines = []
        for m in sampled_messages:
            content = str(m.get('content', '') or '').strip()
            timestamp = m.get('timestamp', '')[:10] if m.get('timestamp') else ''
            if content:
                if timestamp:
                    messages_lines.append(f"[{timestamp}] {person['name']}: {content}")
                else:
                    messages_lines.append(f"{person['name']}: {content}")
        
        if not messages_lines:
            self.loading_overlay.hide()
            QMessageBox.warning(self, "Sin contenido", f"No se pudo procesar ningún mensaje de {person['name']}.")
            return
            
        messages_text = "\n".join(messages_lines)
        
        self.person_analysis_thread = PersonAnalysisThread(
            api_key, person_id, person['name'], messages_text, self.db
        )
        self.person_analysis_thread.finished.connect(self._on_person_analysis_finished)
        self.person_analysis_thread.error.connect(self._on_person_analysis_error)
        self.person_analysis_thread.start()
    
    def _on_person_analysis_finished(self, person_id: int, result: dict):
        """Callback cuando termina el análisis de una persona"""
        self.loading_overlay.hide()
        
        # Marcar como analizado
        self.db.update_person(person_id, ai_analyzed=1, ai_analyzed_at=datetime.now().isoformat())
        
        # Actualizar rol si se detectó
        if result.get('role'):
            self.db.update_person(person_id, role=result['role'], role_confidence=result.get('role_confidence', 0.8))
        
        # Actualizar sentimiento
        if result.get('sentiment'):
            self.db.update_person(
                person_id, 
                sentiment=result.get('sentiment', 'neutral'),
                sentiment_score=result.get('sentiment_score', 0.0)
            )
        
        # Guardar skills
        if result.get('skills'):
            for skill in result['skills']:
                skill_id = self.db.add_skill(skill.get('name', ''), skill.get('category', 'otro'))
                self.db.add_person_skill(person_id, skill_id, skill.get('score', 50), skill.get('evidence', ''))
        
        # Guardar compromisos detectados
        commitments_count = 0
        if result.get('commitments'):
            for commitment in result['commitments']:
                self.db.add_commitment(
                    person_id=person_id,
                    title=commitment.get('title', ''),
                    commitment_type=commitment.get('type', 'promise'),
                    due_date=commitment.get('due_date'),
                    evidence=commitment.get('evidence')
                )
                commitments_count += 1
        
        # Recargar datos
        self._load_data()
        
        sentiment_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😟'}.get(result.get('sentiment', 'neutral'), '😐')
        
        QMessageBox.information(
            self, "✅ Análisis Completado",
            f"Se analizó el perfil:\n\n"
            f"• Rol detectado: {result.get('role', 'No detectado')}\n"
            f"• Sentimiento: {sentiment_emoji} {result.get('sentiment', 'neutral')}\n"
            f"• Skills: {len(result.get('skills', []))}\n"
            f"• Compromisos: {commitments_count}"
        )
    
    def _on_person_analysis_error(self, error_msg: str):
        """Callback cuando hay error en el análisis"""
        self.loading_overlay.hide()
        QMessageBox.critical(self, "Error de análisis", f"Error al analizar:\n{error_msg}")
    
    def _edit_person_name(self, person_id: int, current_name: str):
        """Edita el nombre de una persona"""
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self, "Editar nombre", 
            "Nuevo nombre:", 
            text=current_name
        )
        if ok and new_name and new_name != current_name:
            self.db.update_person(person_id, name=new_name)
            self._load_data()
            QMessageBox.information(self, "✅ Actualizado", f"Nombre cambiado a: {new_name}")
    
    def _delete_person(self, person_id: int, name: str):
        """Elimina una persona y todos sus datos asociados"""
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de eliminar a '{name}'?\n\n"
            "Se eliminarán también:\n"
            "• Todos sus mensajes\n"
            "• Skills asociados\n"
            "• Alertas de comportamiento\n"
            "• Compromisos\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_person(person_id)
            self._load_data()
            QMessageBox.information(self, "✅ Eliminado", f"'{name}' ha sido eliminado.")
    
    def _change_person_avatar(self, person_id: int):
        """Cambia el avatar de una persona"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            # Crear directorio de avatares si no existe
            avatars_dir = os.path.join(os.path.dirname(self.db.db_path), 'avatars')
            os.makedirs(avatars_dir, exist_ok=True)
            
            # Copiar imagen al directorio de avatares
            ext = os.path.splitext(file_path)[1]
            avatar_filename = f"avatar_{person_id}{ext}"
            avatar_path = os.path.join(avatars_dir, avatar_filename)
            
            import shutil
            shutil.copy2(file_path, avatar_path)
            
            # Guardar ruta en BD
            self.db.update_person(person_id, avatar_path=avatar_path)
            self._load_data()
            QMessageBox.information(self, "✅ Avatar actualizado", "La foto de perfil ha sido actualizada.")
                
    def _load_tasks(self, status_filter: str = None):
        self._clear_layout(self.tasks_list)
        
        # Obtener estado del filtro
        if status_filter == "Pendientes":
            status = "pending"
        elif status_filter == "En progreso":
            status = "in_progress"
        elif status_filter == "Completadas":
            status = "completed"
        else:
            status = None
        
        # Obtener filtro por persona
        person_id = None
        if hasattr(self, 'task_person_filter'):
            person_id = self.task_person_filter.currentData()
        
        # Verificar si agrupación está activa
        group_by_category = hasattr(self, 'group_toggle') and self.group_toggle.isChecked()
        
        if group_by_category:
            grouped_tasks = self.db.get_tasks_grouped_by_category(status, person_id)
            
            if not grouped_tasks:
                self.tasks_empty.show()
                return
            self.tasks_empty.hide()
            
            # Orden de categorías
            category_order = ['mentoría', 'mentoria', 'técnico', 'tecnico', 'marketing', 
                            'ventas', 'negocio', 'diseño', 'contenido', 'administrativo', 'general']
            
            # Ordenar categorías
            sorted_categories = sorted(grouped_tasks.keys(), 
                key=lambda x: category_order.index(x.lower()) if x.lower() in category_order else 999)
            
            for category in sorted_categories:
                tasks = grouped_tasks[category]
                if not tasks:
                    continue
                    
                # Header de categoría
                cat_colors = CATEGORY_COLORS.get(category.lower(), CATEGORY_COLORS['general'])
                
                cat_header = QFrame()
                cat_header.setStyleSheet(f"""
                    QFrame {{
                        background-color: {cat_colors[1]};
                        border-radius: 10px;
                        margin-top: 8px;
                    }}
                """)
                cat_layout = QHBoxLayout(cat_header)
                cat_layout.setContentsMargins(16, 12, 16, 12)
                
                cat_icon = QLabel("📁")
                cat_icon.setStyleSheet("font-size: 18px;")
                cat_layout.addWidget(cat_icon)
                
                cat_name = QLabel(category.capitalize())
                cat_name.setStyleSheet(f"""
                    color: {cat_colors[0]};
                    font-size: 16px;
                    font-weight: 700;
                """)
                cat_layout.addWidget(cat_name)
                
                cat_count = QLabel(f"{len(tasks)} tareas")
                cat_count.setStyleSheet(f"""
                    color: {cat_colors[0]};
                    font-size: 13px;
                    opacity: 0.8;
                """)
                cat_layout.addWidget(cat_count)
                cat_layout.addStretch()
                
                self.tasks_list.addWidget(cat_header)
                
                # Tareas de esta categoría
                for task in tasks:
                    item = TaskCard(
                        task['id'], task['title'], task.get('description', ''),
                        task.get('status', 'pending'), task.get('priority', 'medium'),
                        task.get('category', 'general'), task.get('assigned_to_name')
                    )
                    item.status_changed.connect(self._on_task_status_changed)
                    self.tasks_list.addWidget(item)
        else:
            # Sin agrupación - lista plana
            tasks = self.db.get_all_tasks(status)
            
            if not tasks:
                self.tasks_empty.show()
                return
            self.tasks_empty.hide()
            
            for task in tasks:
                item = TaskCard(
                    task['id'], task['title'], task.get('description', ''),
                    task.get('status', 'pending'), task.get('priority', 'medium'),
                    task.get('category', 'general'), task.get('assigned_to_name')
                )
                item.status_changed.connect(self._on_task_status_changed)
                self.tasks_list.addWidget(item)
    
    def _toggle_task_grouping(self):
        """Alternar entre vista agrupada y lista plana"""
        current_filter = self.task_filter.currentText()
        self._load_tasks(current_filter if current_filter != "Todas" else None)
            
    def _filter_tasks(self, filter_text: str):
        self._load_tasks(filter_text if filter_text != "Todas" else None)
    
    def _filter_tasks_by_person(self, index: int):
        """Filtra tareas por persona seleccionada"""
        status_filter = self.task_filter.currentText()
        status = status_filter if status_filter != "Todas" else None
        self._load_tasks(status)
    
    def _populate_person_filter(self):
        """Llena el filtro de personas con los usuarios disponibles"""
        if not hasattr(self, 'task_person_filter'):
            return
        
        current_data = self.task_person_filter.currentData()
        self.task_person_filter.blockSignals(True)
        self.task_person_filter.clear()
        self.task_person_filter.addItem("Todas las personas", None)
        
        persons = self.db.get_all_persons(min_messages=0)
        for person in persons:
            self.task_person_filter.addItem(person['name'], person['id'])
        
        # Restaurar selección si existía
        if current_data:
            for i in range(self.task_person_filter.count()):
                if self.task_person_filter.itemData(i) == current_data:
                    self.task_person_filter.setCurrentIndex(i)
                    break
        
        self.task_person_filter.blockSignals(False)
                
    def _load_patterns(self):
        self._clear_layout(self.patterns_grid)
        patterns = self.db.get_all_patterns()
        
        if not patterns:
            self.patterns_empty.show()
            return
        self.patterns_empty.hide()
        
        col, row, max_cols = 0, 0, 2
        for pattern in patterns:
            card = PatternCard(
                pattern['name'], pattern.get('pattern_type', 'otro'),
                pattern.get('description', ''), pattern.get('persons_involved', []),
                pattern.get('recommendations')
            )
            self.patterns_grid.addWidget(card, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
                
    def _import_chat(self):
        # Permitir selección múltiple de archivos HTML
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos HTML de Telegram (puedes seleccionar varios)", "",
            "Archivos HTML (*.html);;Todos los archivos (*.*)"
        )
        
        if not paths:
            return
        
        # Mostrar overlay de carga
        self.loading_overlay.show_indeterminate(f"Importando {len(paths)} archivo(s)...")
        self.loading_overlay.show()
        
        # Crear worker para importación en segundo plano (incluye guardado en BD)
        db_path = self.db.db_path if hasattr(self.db, 'db_path') else 'telegram_analyzer.db'
        self.import_worker = ImportWorker(paths, db_path)
        self.import_worker.progress.connect(self._on_import_progress)
        self.import_worker.finished.connect(self._on_import_finished)
        self.import_worker.error.connect(self._on_import_error)
        self.import_worker.start()
    
    def _on_import_progress(self, message: str):
        """Actualiza el mensaje de progreso durante la importación"""
        self.loading_overlay.show_indeterminate(message)
    
    def _on_import_finished(self, result: dict):
        """Callback cuando termina la importación (todo ya guardado en BD)"""
        self.loading_overlay.hide()
        self._load_data()  # Recargar datos desde BD
        
        # Mostrar resumen
        total_files = result.get('total_files', 1)
        files_text = f"{total_files} archivos" if total_files > 1 else "1 archivo"
        
        QMessageBox.information(
            self, "Chat Importado",
            f"Se importaron ({files_text}):\n\n"
            f"• {result.get('total_messages', 0)} mensajes\n"
            f"• {result.get('total_participants', 0)} participantes\n"
            f"• {result.get('total_links', 0)} enlaces\n\n"
            f"Para analizar con IA, haz clic en el botón\n"
            f"'🤖 Analizar con IA' en cada tarjeta de persona."
        )
    
    def _on_import_error(self, error_msg: str):
        """Callback cuando hay error en la importación"""
        self.loading_overlay.hide()
        QMessageBox.critical(self, "Error", f"Error al importar:\n{error_msg}")
            
    def _run_ai_analysis(self):
        if not self.current_chat_data:
            QMessageBox.warning(self, "Sin datos", "Primero importa un chat de Telegram.")
            return
            
        api_key = self.api_key_input.text() or os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            QMessageBox.warning(
                self, "API Key requerida", 
                "Configura tu API key en la sección de Configuración para usar el análisis con IA."
            )
            self._navigate_to(5)
            return
        
        # Contar mensajes y participantes para confirmación
        msg_count = len(self.current_chat_data.get('messages', []))
        participants_count = len(self.current_chat_data.get('participants', []))
        
        # Confirmación antes de analizar
        reply = QMessageBox.question(self, "Confirmar análisis con IA",
            f"Vas a analizar:\n\n"
            f"• {msg_count} mensajes\n"
            f"• {participants_count} participantes\n\n"
            f"Esto consumirá créditos de tu API de IA.\n\n"
            f"¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        me = self.db.get_me()
        me_name = me['name'] if me else None
            
        self.loading_overlay.progress.setRange(0, 100)
        self.loading_overlay.progress.setValue(0)
        self.loading_overlay.message_label.setText("Iniciando análisis con IA...")
        self.loading_overlay.show()
        
        self.analysis_worker = AnalysisWorker(
            self.current_chat_data['messages'],
            self.current_chat_data['participants'],
            api_key,
            me_name
        )
        self.analysis_worker.progress.connect(self._on_analysis_progress)
        self.analysis_worker.finished.connect(self._on_analysis_finished)
        self.analysis_worker.error.connect(self._on_analysis_error)
        self.analysis_worker.start()
        
    def _on_analysis_progress(self, current: int, total: int, message: str):
        progress = int((current / total) * 100) if total > 0 else 0
        self.loading_overlay.set_progress(progress, message)
        
    def _on_analysis_finished(self, results: dict):
        self.loading_overlay.hide()
        
        # Save tasks
        for task in results.get('tasks', []):
            assigned_to_id = None
            if task.assigned_to:
                assigned_to_id = self.db.add_person(task.assigned_to)
            self.db.add_task(
                task.title, task.description, task.status,
                task.priority, task.category, assigned_to_id, task.source_message
            )
            
        # Save person profiles
        for name, profile in results.get('person_profiles', {}).items():
            person_id = self.db.add_person(name)
            self.db.update_person(
                person_id, role=profile.role.value,
                role_confidence=profile.role_confidence,
                profile_summary=profile.summary,
                sentiment=profile.sentiment,
                sentiment_score=profile.sentiment_score
            )
            for skill in profile.skills:
                skill_id = self.db.add_skill(skill.name, skill.category)
                self.db.add_person_skill(person_id, skill_id, skill.score, skill.evidence)
            
            # Guardar compromisos detectados
            if profile.commitments:
                for commitment in profile.commitments:
                    self.db.add_commitment(
                        person_id=person_id,
                        title=commitment.get('title', ''),
                        commitment_type=commitment.get('type', 'promise'),
                        due_date=commitment.get('due_date'),
                        evidence=commitment.get('evidence')
                    )
                
        # Save patterns
        for pattern in results.get('patterns', []):
            self.db.add_pattern(
                pattern.get('name', ''), pattern.get('type', 'otro'),
                pattern.get('description', ''), pattern.get('persons_involved', []),
                pattern.get('examples', []), pattern.get('recommendations', '')
            )
            
        self._load_data()
        
        QMessageBox.information(
            self, "✅ Análisis Completado",
            f"Se extrajeron:\n\n"
            f"• {len(results.get('tasks', []))} tareas\n"
            f"• {len(results.get('person_profiles', {}))} perfiles analizados\n"
            f"• {len(results.get('patterns', []))} patrones detectados"
        )
        
    def _on_analysis_error(self, error: str):
        self.loading_overlay.hide()
        QMessageBox.critical(self, "Error en Análisis", f"Error:\n{error}")
        
    def _on_task_status_changed(self, task_id: int, new_status: str):
        self.db.update_task_status(task_id, new_status)
        self._update_dashboard()
        self._load_my_profile()
        
    def _add_task_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Tarea")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(GLOBAL_STYLE + f"QDialog {{ background-color: {COLORS['bg_secondary']}; }}")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title_label = QLabel("Título")
        title_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(title_label)
        title_input = QLineEdit()
        title_input.setPlaceholderText("¿Qué necesitas hacer?")
        layout.addWidget(title_input)
        
        # Description
        desc_label = QLabel("Descripción (opcional)")
        desc_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(desc_label)
        desc_input = QTextEdit()
        desc_input.setPlaceholderText("Añade más detalles...")
        desc_input.setMaximumHeight(80)
        layout.addWidget(desc_input)
        
        # Row for category and priority
        row_layout = QHBoxLayout()
        row_layout.setSpacing(16)
        
        # Category
        cat_col = QVBoxLayout()
        cat_label = QLabel("Categoría")
        cat_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        cat_col.addWidget(cat_label)
        category_combo = QComboBox()
        category_combo.addItems(["General", "Mentoría", "Técnico", "Marketing", "Ventas", "Negocio", "Diseño", "Contenido", "Administrativo"])
        cat_col.addWidget(category_combo)
        row_layout.addLayout(cat_col)
        
        # Priority
        pri_col = QVBoxLayout()
        priority_label = QLabel("Prioridad")
        priority_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        pri_col.addWidget(priority_label)
        priority_combo = QComboBox()
        priority_combo.addItems(["Baja", "Media", "Alta", "Urgente"])
        priority_combo.setCurrentIndex(1)
        pri_col.addWidget(priority_combo)
        row_layout.addLayout(pri_col)
        
        layout.addLayout(row_layout)
        
        # Assigned to
        assigned_label = QLabel("Asignar a")
        assigned_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        layout.addWidget(assigned_label)
        assigned_combo = QComboBox()
        assigned_combo.addItem("Sin asignar", None)
        persons = self.db.get_all_persons(min_messages=1)
        for person in persons:
            assigned_combo.addItem(person['name'], person['id'])
        layout.addWidget(assigned_combo)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        cancel_btn.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Crear Tarea")
        save_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and title_input.text().strip():
            priority_map = {"Baja": "low", "Media": "medium", "Alta": "high", "Urgente": "urgent"}
            category_map = {"General": "general", "Mentoría": "mentoría", "Técnico": "técnico", 
                          "Marketing": "marketing", "Ventas": "ventas", "Negocio": "negocio",
                          "Diseño": "diseño", "Contenido": "contenido", "Administrativo": "administrativo"}
            
            assigned_id = assigned_combo.currentData()
            
            self.db.add_task(
                title_input.text().strip(),
                desc_input.toPlainText().strip(),
                "pending",
                priority_map[priority_combo.currentText()],
                category_map[category_combo.currentText()],
                assigned_id
            )
            self._load_tasks()
            self._update_dashboard()
            
    def _show_person_detail(self, person: dict):
        person_data = self.db.get_person_with_skills(person['id'])
        person_stats = self.db.get_person_stats(person['id'])
        person_tasks = self.db.get_tasks_for_person(person['id'])
        me = self.db.get_me()
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Perfil: {person['name']}")
        dialog.setMinimumSize(900, 700)
        dialog.setStyleSheet(GLOBAL_STYLE + f"QDialog {{ background-color: {COLORS['bg_primary']}; }}")
        
        main_layout = QVBoxLayout(dialog)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(32, 32, 32, 32)
        
        # Header compacto
        header = QHBoxLayout()
        role_colors = ROLE_COLORS.get(person.get('role', 'desconocido').lower(), ROLE_COLORS['desconocido'])
        
        avatar = QLabel(person['name'][0].upper())
        avatar.setFixedSize(60, 60)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            border-radius: 30px;
            font-size: 24px;
            font-weight: 700;
        """)
        header.addWidget(avatar)
        
        info = QVBoxLayout()
        info.setSpacing(4)
        
        name_label = QLabel(person['name'])
        name_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 20px; font-weight: 700;")
        info.addWidget(name_label)
        
        role_badge = QLabel(person.get('role', 'Desconocido').capitalize())
        role_badge.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        """)
        role_badge.setFixedWidth(role_badge.sizeHint().width() + 8)
        info.addWidget(role_badge)
        
        header.addLayout(info)
        header.addStretch()
        
        # Stats compactos en header
        stats_data = [
            ("💬", str(person_stats.get('total_messages', 0)), "msgs"),
            ("📋", str(person_stats.get('total_tasks', 0)), "tareas"),
            ("✅", str(person_stats.get('completed_tasks', 0)), "hechas"),
        ]
        for icon, value, label in stats_data:
            stat_box = QVBoxLayout()
            stat_box.setSpacing(0)
            stat_value = QLabel(f"{icon} {value}")
            stat_value.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 600;")
            stat_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_box.addWidget(stat_value)
            stat_label = QLabel(label)
            stat_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 10px;")
            stat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stat_box.addWidget(stat_label)
            header.addLayout(stat_box)
            header.addSpacing(16)
        
        main_layout.addLayout(header)
        
        # Scroll area para contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)
        
        # === SECCIÓN DE TAREAS (PROMINENTE) ===
        tasks_section = QFrame()
        tasks_section.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border_light']};
                border-radius: 12px;
            }}
        """)
        tasks_section_layout = QVBoxLayout(tasks_section)
        tasks_section_layout.setSpacing(16)
        tasks_section_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header de tareas
        tasks_header = QHBoxLayout()
        tasks_title = QLabel(f"📋 Tareas de {person['name']}")
        tasks_title.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 700;")
        tasks_header.addWidget(tasks_title)
        
        pending_count = len([t for t in person_tasks if t['status'] != 'completed'])
        if pending_count > 0:
            pending_badge = QLabel(f"{pending_count} pendientes")
            pending_badge.setStyleSheet("""
                background-color: #FEF3C7;
                color: #D97706;
                padding: 4px 10px;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 600;
            """)
            tasks_header.addWidget(pending_badge)
        tasks_header.addStretch()
        tasks_section_layout.addLayout(tasks_header)
        
        # Lista de tareas de esta persona
        if person_tasks:
            for task in person_tasks[:8]:  # Mostrar hasta 8 tareas
                task_item = QFrame()
                task_item.setStyleSheet(f"""
                    QFrame {{
                        background-color: {COLORS['bg_secondary']};
                        border-radius: 8px;
                        border-left: 3px solid {'#10B981' if task['status'] == 'completed' else '#F59E0B' if task.get('priority') == 'high' else '#3B82F6'};
                    }}
                """)
                task_layout = QHBoxLayout(task_item)
                task_layout.setContentsMargins(12, 10, 12, 10)
                
                # Checkbox
                checkbox = QLabel("✓" if task['status'] == 'completed' else "")
                checkbox.setFixedSize(20, 20)
                checkbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox.setStyleSheet(f"""
                    background-color: {'#10B981' if task['status'] == 'completed' else '#FFFFFF'};
                    border: 2px solid {'#10B981' if task['status'] == 'completed' else '#E2E8F0'};
                    border-radius: 4px;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                """)
                task_layout.addWidget(checkbox)
                
                # Info de tarea
                task_info = QVBoxLayout()
                task_info.setSpacing(2)
                
                task_title = QLabel(task['title'])
                task_title.setStyleSheet(f"""
                    color: {COLORS['text_primary']};
                    font-size: 13px;
                    font-weight: 500;
                    {'text-decoration: line-through;' if task['status'] == 'completed' else ''}
                """)
                task_info.addWidget(task_title)
                
                if task.get('description'):
                    desc = QLabel(task['description'][:60] + '...' if len(task.get('description', '')) > 60 else task.get('description', ''))
                    desc.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
                    task_info.addWidget(desc)
                
                task_layout.addLayout(task_info, 1)
                
                # Badge de prioridad
                priority = task.get('priority', 'medium')
                priority_colors = {
                    'urgent': ('#DC2626', '#FEE2E2'),
                    'high': ('#F59E0B', '#FEF3C7'),
                    'medium': ('#3B82F6', '#DBEAFE'),
                    'low': ('#10B981', '#D1FAE5')
                }
                p_color = priority_colors.get(priority, priority_colors['medium'])
                priority_badge = QLabel(priority.capitalize())
                priority_badge.setStyleSheet(f"""
                    background-color: {p_color[1]};
                    color: {p_color[0]};
                    padding: 2px 8px;
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: 600;
                """)
                task_layout.addWidget(priority_badge)
                
                tasks_section_layout.addWidget(task_item)
        else:
            no_tasks = QLabel("🎉 No tiene tareas asignadas")
            no_tasks.setStyleSheet(f"color: {COLORS['text_muted']}; padding: 20px; font-size: 13px;")
            no_tasks.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tasks_section_layout.addWidget(no_tasks)
        
        content_layout.addWidget(tasks_section)
        
        # === MIS TAREAS RELACIONADAS (si soy yo diferente) ===
        if me and me['id'] != person['id']:
            # Buscar tareas donde yo tengo que hacer algo relacionado con esta persona
            my_tasks = self.db.get_my_tasks()
            related_tasks = [t for t in my_tasks if person['name'].lower() in (t.get('title', '') + t.get('description', '')).lower()]
            
            if related_tasks:
                my_section = QFrame()
                my_section.setStyleSheet(f"""
                    QFrame {{
                        background-color: #EEF2FF;
                        border: 1px solid #C7D2FE;
                        border-radius: 12px;
                    }}
                """)
                my_section_layout = QVBoxLayout(my_section)
                my_section_layout.setSpacing(12)
                my_section_layout.setContentsMargins(20, 20, 20, 20)
                
                my_header = QLabel(f"👤 Mis tareas relacionadas con {person['name']}")
                my_header.setStyleSheet(f"color: #4F46E5; font-size: 14px; font-weight: 700;")
                my_section_layout.addWidget(my_header)
                
                for task in related_tasks[:5]:
                    task_label = QLabel(f"• {task['title']}")
                    task_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 13px;")
                    my_section_layout.addWidget(task_label)
                
                content_layout.addWidget(my_section)
        
        # === HABILIDADES (compacto) ===
        if person_data and person_data.get('skills'):
            skills_section = QFrame()
            skills_section.setStyleSheet(f"""
                QFrame {{
                    background-color: #FFFFFF;
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 12px;
                }}
            """)
            skills_layout = QVBoxLayout(skills_section)
            skills_layout.setSpacing(12)
            skills_layout.setContentsMargins(20, 20, 20, 20)
            
            skills_header = QLabel("📊 Habilidades")
            skills_header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 14px; font-weight: 600;")
            skills_layout.addWidget(skills_header)
            
            skills_grid = QHBoxLayout()
            skills_grid.setSpacing(8)
            for skill in person_data['skills'][:6]:
                skill_badge = QLabel(f"{skill['name']} ({skill['score']:.0f}%)")
                skill_badge.setStyleSheet(f"""
                    background-color: {COLORS['bg_secondary']};
                    color: {COLORS['text_secondary']};
                    padding: 6px 12px;
                    border-radius: 8px;
                    font-size: 11px;
                """)
                skills_grid.addWidget(skill_badge)
            skills_grid.addStretch()
            skills_layout.addLayout(skills_grid)
            
            content_layout.addWidget(skills_section)
        
        content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
        
        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #2563EB;
            }}
        """)
        close_btn.clicked.connect(dialog.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        dialog.exec()
        
    def _save_api_settings(self):
        api_key = self.api_key_input.text()
        provider = "openai" if self.provider_combo.currentIndex() == 1 else "gemini"
        
        self.db.set_setting('api_key', api_key)
        self.db.set_setting('provider', provider)
        
        QMessageBox.information(self, "✅ Guardado", "Configuración guardada correctamente.")
        
    def _clear_all_data(self):
        reply = QMessageBox.warning(
            self, "⚠️ Confirmar",
            "¿Estás seguro de que quieres eliminar TODOS los datos?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.clear_all_data()
            self.current_chat_data = None
            self._load_data()
            QMessageBox.information(self, "✅ Completado", "Todos los datos han sido eliminados.")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.loading_overlay.setGeometry(self.rect())
        
    def closeEvent(self, event):
        if self.db:
            self.db.close()
        event.accept()


# ============================================================
# PUNTO DE ENTRADA
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set light palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['bg_primary']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS['bg_secondary']))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS['bg_secondary']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS['accent']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#FFFFFF'))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
