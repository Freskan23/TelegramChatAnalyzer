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
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QAction, QPainter, QPen, QBrush

from bs4 import BeautifulSoup


# ============================================================
# CONFIGURACIÓN DE ACTUALIZACIÓN
# ============================================================

APP_VERSION = "2.1.0"
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
        
        self.conn.commit()
        
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
        allowed = ['name', 'role', 'role_confidence', 'profile_summary', 'total_messages', 'is_me']
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
    
    def get_all_tasks(self, status: str = None) -> List[Dict]:
        if status:
            self.cursor.execute('''
                SELECT t.*, p.name as assigned_to_name
                FROM tasks t
                LEFT JOIN persons p ON t.assigned_to = p.id
                WHERE t.status = ?
                ORDER BY 
                    CASE t.priority 
                        WHEN 'urgent' THEN 1 
                        WHEN 'high' THEN 2 
                        WHEN 'medium' THEN 3 
                        ELSE 4 
                    END,
                    t.created_at DESC
            ''', (status,))
        else:
            self.cursor.execute('''
                SELECT t.*, p.name as assigned_to_name
                FROM tasks t
                LEFT JOIN persons p ON t.assigned_to = p.id
                ORDER BY 
                    CASE t.status WHEN 'completed' THEN 1 ELSE 0 END,
                    CASE t.priority 
                        WHEN 'urgent' THEN 1 
                        WHEN 'high' THEN 2 
                        WHEN 'medium' THEN 3 
                        ELSE 4 
                    END,
                    t.created_at DESC
            ''')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_my_tasks(self) -> List[Dict]:
        me = self.get_me()
        if not me:
            return []
        return self.get_tasks_for_person(me['id'])
    
    def get_tasks_grouped_by_category(self, status: str = None) -> Dict[str, List[Dict]]:
        tasks = self.get_all_tasks(status)
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
        tables = ['messages', 'person_skills', 'tasks', 'patterns', 'persons', 'skills', 'chats']
        for table in tables:
            self.cursor.execute(f'DELETE FROM {table}')
        self.conn.commit()


# ============================================================
# PARSER DE TELEGRAM
# ============================================================

class TelegramHTMLParser:
    def __init__(self):
        self.messages = []
        self.participants = {}
        self.chat_name = ""
        self.date_range = (None, None)
        
    def parse_file(self, file_path: str) -> Dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        self._extract_chat_name(soup)
        self._extract_messages(soup)
        self._calculate_date_range()
        self._clean_participants()
        
        return {
            'chat_name': self.chat_name,
            'messages': self.messages,
            'participants': self.participants,
            'date_range': self.date_range,
            'total_messages': len(self.messages)
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
        formats = [
            '%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M',
            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
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
        if self.provider == "gemini":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text
        else:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
    
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
    "skills": [
        {{"name": "nombre de habilidad", "category": "técnica|comunicación|liderazgo|organización|creatividad", "score": 0-100, "evidence": "evidencia del chat"}}
    ],
    "summary": "Resumen profesional en 2-3 oraciones",
    "strengths": ["fortaleza 1", "fortaleza 2", "fortaleza 3"],
    "areas_to_improve": ["área 1", "área 2"],
    "recommendations": ["recomendación accionable 1", "recomendación 2", "recomendación 3"]
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
                recommendations=data.get('recommendations', [])
            )
        except Exception as e:
            print(f"Error analizando persona {name}: {e}")
            return PersonProfile(name=name, role=PersonRole.UNKNOWN, 
                               role_confidence=0.0, skills=[], summary="")
    
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
    
    def _format_messages(self, messages: List[Dict], include_sender: bool = True) -> str:
        lines = []
        for msg in messages:
            timestamp = msg.get('timestamp', '')[:16] if msg.get('timestamp') else ''
            sender = msg.get('sender', 'Desconocido')
            content = msg.get('content', '')
            if include_sender:
                lines.append(f"[{timestamp}] {sender}: {content}")
            else:
                lines.append(f"[{timestamp}] {content}")
        return "\n".join(lines)
    
    def _extract_json(self, text: str) -> str:
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


class StatCard(QFrame):
    def __init__(self, icon: str, title: str, value: str, subtitle: str = "", 
                 color: str = None, parent=None):
        super().__init__(parent)
        self._setup_ui(icon, title, value, subtitle, color)
        
    def _setup_ui(self, icon: str, title: str, value: str, subtitle: str, color: str):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border: 1px solid {COLORS['border_light']};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con icono
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 24px;
            background-color: {color or COLORS['accent_soft']};
            padding: 12px;
            border-radius: 12px;
        """)
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-weight: 500;
        """)
        layout.addWidget(title_label)
        
        # Valor
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 32px;
            font-weight: 700;
        """)
        layout.addWidget(self.value_label)
        
        # Subtítulo
        if subtitle:
            sub_label = QLabel(subtitle)
            sub_label.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 12px;
            """)
            layout.addWidget(sub_label)
            
        self.setMinimumWidth(200)
        self.setMinimumHeight(160)
        
    def set_value(self, value: str):
        self.value_label.setText(value)


class PersonCard(Card):
    def __init__(self, person_id: int, name: str, role: str, skills: list = None,
                 message_count: int = 0, is_me: bool = False, parent=None):
        super().__init__(parent)
        self.person_id = person_id
        self._setup_ui(name, role, skills, message_count, is_me)
        
    def _setup_ui(self, name: str, role: str, skills: list, message_count: int, is_me: bool):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        
        # Avatar
        role_colors = ROLE_COLORS.get(role.lower(), ROLE_COLORS['desconocido'])
        avatar = QLabel(name[0].upper() if name else "?")
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            border-radius: 28px;
            font-size: 22px;
            font-weight: 700;
        """)
        header.addWidget(avatar)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_layout = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 16px;
            font-weight: 600;
        """)
        name_layout.addWidget(name_label)
        
        if is_me:
            me_badge = QLabel("TÚ")
            me_badge.setStyleSheet(f"""
                background-color: {COLORS['accent']};
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 700;
            """)
            name_layout.addWidget(me_badge)
        name_layout.addStretch()
        info_layout.addLayout(name_layout)
        
        # Role badge
        role_badge = QLabel(role.capitalize())
        role_badge.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        """)
        role_badge.setFixedWidth(role_badge.sizeHint().width() + 8)
        info_layout.addWidget(role_badge)
        
        header.addLayout(info_layout)
        header.addStretch()
        layout.addLayout(header)
        
        # Stats
        stats_label = QLabel(f"💬 {message_count} mensajes")
        stats_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
        """)
        layout.addWidget(stats_label)
        
        # Skills
        if skills:
            skills_layout = QHBoxLayout()
            skills_layout.setSpacing(8)
            for skill in skills[:3]:
                skill_badge = QLabel(skill.get('name', skill) if isinstance(skill, dict) else skill)
                skill_badge.setStyleSheet(f"""
                    background-color: {COLORS['bg_primary']};
                    color: {COLORS['text_secondary']};
                    padding: 6px 12px;
                    border-radius: 8px;
                    font-size: 12px;
                """)
                skills_layout.addWidget(skill_badge)
            skills_layout.addStretch()
            layout.addLayout(skills_layout)
            
        self.setMinimumWidth(320)
        self.setMinimumHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


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
        priority_colors = PRIORITY_COLORS.get(priority, PRIORITY_COLORS['medium'])
        category_colors = CATEGORY_COLORS.get(category.lower() if category else 'general', CATEGORY_COLORS['general'])
        
        # Fondo blanco puro con borde más visible
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border: 1px solid {COLORS['border']};
                border-left: 5px solid {priority_colors[0]};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {COLORS['accent']};
                border-left: 5px solid {priority_colors[0]};
                background-color: #FAFBFC;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(16)
        
        # Checkbox más grande y visible
        self.checkbox = QPushButton()
        self.checkbox.setFixedSize(32, 32)
        self.checkbox.setCheckable(True)
        self.checkbox.setChecked(status == "completed")
        self._update_checkbox_style()
        self.checkbox.clicked.connect(self._on_status_toggle)
        layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignTop)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)
        
        # Título con mejor contraste
        title_label = QLabel(title)
        if status == "completed":
            title_label.setStyleSheet(f"""
                color: {COLORS['text_muted']};
                font-size: 15px;
                font-weight: 500;
                text-decoration: line-through;
            """)
        else:
            title_label.setStyleSheet(f"""
                color: #1a1a2e;
                font-size: 15px;
                font-weight: 600;
            """)
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)
        
        # Descripción con mejor visibilidad
        if description:
            desc_text = description[:100] + "..." if len(description) > 100 else description
            desc_label = QLabel(desc_text)
            desc_label.setStyleSheet(f"""
                color: #4a5568;
                font-size: 13px;
                line-height: 1.4;
            """)
            desc_label.setWordWrap(True)
            content_layout.addWidget(desc_label)
            
        # Meta info con badges
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(10)
        
        # Responsable destacado
        if assigned_to:
            assigned_frame = QFrame()
            assigned_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['accent_soft']};
                    border-radius: 6px;
                    padding: 2px;
                }}
            """)
            assigned_inner = QHBoxLayout(assigned_frame)
            assigned_inner.setContentsMargins(8, 4, 10, 4)
            assigned_inner.setSpacing(6)
            
            # Avatar pequeño
            avatar = QLabel(assigned_to[0].upper() if assigned_to else "?")
            avatar.setFixedSize(22, 22)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet(f"""
                background-color: {COLORS['accent']};
                color: white;
                border-radius: 11px;
                font-size: 11px;
                font-weight: 700;
            """)
            assigned_inner.addWidget(avatar)
            
            name_label = QLabel(assigned_to)
            name_label.setStyleSheet(f"""
                color: {COLORS['accent']};
                font-size: 12px;
                font-weight: 600;
            """)
            assigned_inner.addWidget(name_label)
            meta_layout.addWidget(assigned_frame)
        
        # Badge de categoría
        if category and category.lower() != 'general':
            cat_badge = QLabel(category.capitalize())
            cat_badge.setStyleSheet(f"""
                background-color: {category_colors[1]};
                color: {category_colors[0]};
                padding: 4px 10px;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
            """)
            meta_layout.addWidget(cat_badge)
            
        # Badge de prioridad
        priority_names = {'low': 'Baja', 'medium': 'Media', 'high': 'Alta', 'urgent': 'Urgente'}
        priority_badge = QLabel(priority_names.get(priority, priority.capitalize()))
        priority_badge.setStyleSheet(f"""
            background-color: {priority_colors[1]};
            color: {priority_colors[0]};
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
        """)
        meta_layout.addWidget(priority_badge)
        
        meta_layout.addStretch()
        content_layout.addLayout(meta_layout)
        
        layout.addLayout(content_layout, 1)
        
    def _update_checkbox_style(self):
        if self.checkbox.isChecked():
            self.checkbox.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['success']};
                    border: none;
                    border-radius: 14px;
                    color: white;
                    font-size: 14px;
                }}
            """)
            self.checkbox.setText("✓")
        else:
            self.checkbox.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 2px solid {COLORS['border']};
                    border-radius: 14px;
                }}
                QPushButton:hover {{
                    border-color: {COLORS['accent']};
                }}
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
        
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack, 1)
        
        # Pages
        self.dashboard_page = self._create_dashboard_page()
        self.my_profile_page = self._create_my_profile_page()
        self.persons_page = self._create_persons_page()
        self.tasks_page = self._create_tasks_page()
        self.patterns_page = self._create_patterns_page()
        self.settings_page = self._create_settings_page()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.my_profile_page)
        self.content_stack.addWidget(self.persons_page)
        self.content_stack.addWidget(self.tasks_page)
        self.content_stack.addWidget(self.patterns_page)
        self.content_stack.addWidget(self.settings_page)
        
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()
        
        self._create_menu()
        
    def _create_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_sidebar']};
                border-right: 1px solid {COLORS['border_light']};
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 28, 20, 28)
        layout.setSpacing(8)
        
        # Logo/Title
        title_layout = QHBoxLayout()
        logo = QLabel("📊")
        logo.setStyleSheet("font-size: 28px;")
        title_layout.addWidget(logo)
        
        title = QLabel("Chat Analyzer")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 20px;
            font-weight: 700;
        """)
        title_layout.addWidget(title)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        layout.addSpacing(24)
        
        # Navigation
        nav_buttons = [
            ("🏠", "Dashboard", 0),
            ("👤", "Mi Perfil", 1),
            ("👥", "Personas", 2),
            ("✅", "Tareas", 3),
            ("🔍", "Patrones", 4),
            ("⚙️", "Configuración", 5),
        ]
        
        self.nav_buttons = []
        for icon, text, index in nav_buttons:
            btn = QPushButton(f"  {icon}   {text}")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    text-align: left;
                    padding: 14px 16px;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: 500;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: {COLORS['accent_soft']};
                    color: {COLORS['accent']};
                    font-weight: 600;
                }}
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self._navigate_to(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
            
        self.nav_buttons[0].setChecked(True)
        layout.addStretch()
        
        # Import button
        import_btn = QPushButton("📥  Importar Chat")
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                padding: 14px 20px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_light']};
            }}
        """)
        import_btn.clicked.connect(self._import_chat)
        layout.addWidget(import_btn)
        
        return sidebar
        
    def _navigate_to(self, index: int):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.content_stack.setCurrentIndex(index)
        
    def _create_dashboard_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(32)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("Dashboard")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Quick action
        analyze_btn = QPushButton("🔄  Analizar con IA")
        analyze_btn.clicked.connect(self._run_ai_analysis)
        header_layout.addWidget(analyze_btn)
        layout.addLayout(header_layout)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.stat_persons = StatCard("👥", "Personas", "0", "participantes activos", COLORS['accent_soft'])
        self.stat_pending = StatCard("📋", "Pendientes", "0", "tareas por hacer", COLORS['warning_soft'])
        self.stat_completed = StatCard("✅", "Completadas", "0", "tareas finalizadas", COLORS['success_soft'])
        self.stat_messages = StatCard("💬", "Mensajes", "0", "analizados", COLORS['border_light'])
        
        stats_layout.addWidget(self.stat_persons)
        stats_layout.addWidget(self.stat_pending)
        stats_layout.addWidget(self.stat_completed)
        stats_layout.addWidget(self.stat_messages)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Content grid
        content_layout = QHBoxLayout()
        content_layout.setSpacing(24)
        
        # Recent tasks
        tasks_card = Card()
        tasks_layout = QVBoxLayout(tasks_card)
        tasks_layout.setSpacing(16)
        
        tasks_header = QHBoxLayout()
        tasks_title = QLabel("📋 Tareas Recientes")
        tasks_title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: 600;
        """)
        tasks_header.addWidget(tasks_title)
        tasks_header.addStretch()
        
        view_all_btn = QPushButton("Ver todas →")
        view_all_btn.setProperty("class", "ghost")
        view_all_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['accent']};
                border: none;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: {COLORS['accent_light']};
            }}
        """)
        view_all_btn.clicked.connect(lambda: self._navigate_to(3))
        tasks_header.addWidget(view_all_btn)
        tasks_layout.addLayout(tasks_header)
        
        self.dashboard_tasks_container = QVBoxLayout()
        self.dashboard_tasks_container.setSpacing(12)
        tasks_layout.addLayout(self.dashboard_tasks_container)
        tasks_layout.addStretch()
        content_layout.addWidget(tasks_card, 2)
        
        # Active persons
        persons_card = Card()
        persons_layout = QVBoxLayout(persons_card)
        persons_layout.setSpacing(16)
        
        persons_header = QLabel("👥 Personas Activas")
        persons_header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 18px;
            font-weight: 600;
        """)
        persons_layout.addWidget(persons_header)
        
        self.dashboard_persons_container = QVBoxLayout()
        self.dashboard_persons_container.setSpacing(12)
        persons_layout.addLayout(self.dashboard_persons_container)
        persons_layout.addStretch()
        content_layout.addWidget(persons_card, 1)
        
        layout.addLayout(content_layout)
        layout.addStretch()
        
        return page
        
    def _create_my_profile_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("Mi Perfil")
        header.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        # Selector de usuario
        self.me_selector = QComboBox()
        self.me_selector.setFixedWidth(250)
        self.me_selector.setPlaceholderText("Selecciona tu usuario...")
        self.me_selector.currentIndexChanged.connect(self._on_me_selected)
        header_layout.addWidget(self.me_selector)
        layout.addLayout(header_layout)
        
        # Scroll area for profile content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.profile_layout = QVBoxLayout(scroll_content)
        self.profile_layout.setSpacing(24)
        self.profile_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Empty state
        self.profile_empty = EmptyState(
            "👤",
            "Selecciona tu usuario",
            "Elige tu nombre del selector para ver tu evaluación personal.",
        )
        self.profile_layout.addWidget(self.profile_empty)
        
        return page
        
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
        self._load_tasks()
        self._load_patterns()
        self._update_me_selector()
        self._load_my_profile()
        
    def _update_dashboard(self):
        stats = self.db.get_dashboard_stats()
        
        self.stat_persons.set_value(str(stats.get('total_persons', 0)))
        self.stat_pending.set_value(str(stats.get('pending_tasks', 0)))
        self.stat_completed.set_value(str(stats.get('completed_tasks', 0)))
        self.stat_messages.set_value(str(stats.get('total_messages', 0)))
        
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
            
        # Active persons
        self._clear_layout(self.dashboard_persons_container)
        persons = self.db.get_all_persons(min_messages=1)[:4]
        for person in persons:
            person_frame = QFrame()
            person_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_primary']};
                    border-radius: 10px;
                    padding: 12px;
                }}
            """)
            p_layout = QHBoxLayout(person_frame)
            p_layout.setContentsMargins(12, 8, 12, 8)
            
            role_colors = ROLE_COLORS.get(person.get('role', 'desconocido').lower(), ROLE_COLORS['desconocido'])
            avatar = QLabel(person['name'][0].upper())
            avatar.setFixedSize(36, 36)
            avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar.setStyleSheet(f"""
                background-color: {role_colors[1]};
                color: {role_colors[0]};
                border-radius: 18px;
                font-weight: 600;
            """)
            p_layout.addWidget(avatar)
            
            info = QVBoxLayout()
            info.setSpacing(2)
            name_label = QLabel(person['name'])
            name_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 500;")
            info.addWidget(name_label)
            
            role_label = QLabel(f"{person.get('role', 'desconocido').capitalize()} · {person.get('total_messages', 0)} msgs")
            role_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            info.addWidget(role_label)
            p_layout.addLayout(info)
            p_layout.addStretch()
            
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
        # Clear existing content
        self._clear_layout(self.profile_layout)
        
        me = self.db.get_me()
        if not me:
            self.profile_empty = EmptyState(
                "👤",
                "Selecciona tu usuario",
                "Elige tu nombre del selector para ver tu evaluación personal.",
            )
            self.profile_layout.addWidget(self.profile_empty)
            return
            
        me_data = self.db.get_person_with_skills(me['id'])
        me_stats = self.db.get_person_stats(me['id'])
        
        # Profile header card
        header_card = Card()
        header_layout = QHBoxLayout(header_card)
        header_layout.setSpacing(24)
        
        role_colors = ROLE_COLORS.get(me.get('role', 'desconocido').lower(), ROLE_COLORS['desconocido'])
        avatar = QLabel(me['name'][0].upper())
        avatar.setFixedSize(100, 100)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            border-radius: 50px;
            font-size: 40px;
            font-weight: 700;
        """)
        header_layout.addWidget(avatar)
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        
        name_label = QLabel(me['name'])
        name_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
        """)
        info_layout.addWidget(name_label)
        
        role_badge = QLabel(me.get('role', 'desconocido').capitalize())
        role_badge.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            padding: 6px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
        """)
        role_badge.setFixedWidth(role_badge.sizeHint().width() + 16)
        info_layout.addWidget(role_badge)
        
        if me_data and me_data.get('profile_summary'):
            summary = QLabel(me_data['profile_summary'])
            summary.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px;")
            summary.setWordWrap(True)
            info_layout.addWidget(summary)
            
        header_layout.addLayout(info_layout, 1)
        self.profile_layout.addWidget(header_card)
        
        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        
        stats_data = [
            ("💬", "Mensajes", str(me_stats.get('total_messages', 0))),
            ("📋", "Tareas", str(me_stats.get('total_tasks', 0))),
            ("✅", "Completadas", str(me_stats.get('completed_tasks', 0))),
            ("⭐", "Promedio Skills", f"{me_stats.get('avg_skill_score', 0):.0f}%"),
        ]
        
        for icon, label, value in stats_data:
            stat_card = QFrame()
            stat_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_secondary']};
                    border: 1px solid {COLORS['border_light']};
                    border-radius: 12px;
                    padding: 16px;
                }}
            """)
            stat_layout = QVBoxLayout(stat_card)
            stat_layout.setSpacing(4)
            
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 24px;")
            stat_layout.addWidget(icon_label)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 24px; font-weight: 700;")
            stat_layout.addWidget(value_label)
            
            label_label = QLabel(label)
            label_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            stat_layout.addWidget(label_label)
            
            stats_layout.addWidget(stat_card)
            
        stats_layout.addStretch()
        self.profile_layout.addLayout(stats_layout)
        
        # Two column layout for skills and recommendations
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(24)
        
        # Skills card
        if me_data and me_data.get('skills'):
            skills_card = Card()
            skills_layout = QVBoxLayout(skills_card)
            skills_layout.setSpacing(16)
            
            skills_header = QLabel("📊 Mis Habilidades")
            skills_header.setStyleSheet(f"""
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 600;
            """)
            skills_layout.addWidget(skills_header)
            
            for skill in me_data['skills']:
                skill_bar = SkillBar(skill['name'], skill['score'], skill.get('category', ''))
                skills_layout.addWidget(skill_bar)
                
            columns_layout.addWidget(skills_card, 1)
            
        # My tasks card
        my_tasks = self.db.get_my_tasks()
        if my_tasks:
            tasks_card = Card()
            tasks_layout = QVBoxLayout(tasks_card)
            tasks_layout.setSpacing(16)
            
            tasks_header = QLabel("📋 Mis Tareas Pendientes")
            tasks_header.setStyleSheet(f"""
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: 600;
            """)
            tasks_layout.addWidget(tasks_header)
            
            pending_tasks = [t for t in my_tasks if t['status'] != 'completed'][:5]
            for task in pending_tasks:
                task_item = TaskCard(
                    task['id'], task['title'], task.get('description', ''),
                    task.get('status', 'pending'), task.get('priority', 'medium')
                )
                task_item.status_changed.connect(self._on_task_status_changed)
                tasks_layout.addWidget(task_item)
                
            if not pending_tasks:
                done_label = QLabel("🎉 ¡No tienes tareas pendientes!")
                done_label.setStyleSheet(f"color: {COLORS['success']}; padding: 20px;")
                done_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                tasks_layout.addWidget(done_label)
                
            columns_layout.addWidget(tasks_card, 1)
            
        self.profile_layout.addLayout(columns_layout)
        self.profile_layout.addStretch()
        
    def _load_persons(self):
        self._clear_layout(self.persons_grid)
        persons = self.db.get_all_persons(min_messages=1)
        
        if not persons:
            self.persons_empty.show()
            return
        self.persons_empty.hide()
        
        me = self.db.get_me()
        col, row, max_cols = 0, 0, 3
        
        for person in persons:
            person_data = self.db.get_person_with_skills(person['id'])
            skills = person_data.get('skills', []) if person_data else []
            is_me = me and person['id'] == me['id']
            
            card = PersonCard(
                person['id'], person['name'], person.get('role', 'desconocido'),
                skills=skills, message_count=person.get('total_messages', 0),
                is_me=is_me
            )
            card.clicked.connect(lambda p=person: self._show_person_detail(p))
            self.persons_grid.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
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
        
        # Verificar si agrupación está activa
        group_by_category = hasattr(self, 'group_toggle') and self.group_toggle.isChecked()
        
        if group_by_category:
            grouped_tasks = self.db.get_tasks_grouped_by_category(status)
            
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
                
    def _import_chat(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo HTML de Telegram", "",
            "Archivos HTML (*.html);;Todos los archivos (*.*)"
        )
        
        if not path:
            return
            
        try:
            self.loading_overlay.show_indeterminate("Importando chat...")
            self.loading_overlay.show()
            QApplication.processEvents()
            
            parser = TelegramHTMLParser()
            data = parser.parse_file(path)
            self.current_chat_data = data
            
            chat_id = self.db.add_chat(data['chat_name'], 'group', path)
            
            for name, info in data['participants'].items():
                person_id = self.db.add_person(name)
                self.db.update_person(person_id, total_messages=info['message_count'])
                
            for msg in data['messages']:
                sender = msg.get('sender')
                if sender and sender in data['participants']:
                    person_id = self.db.add_person(sender)
                    self.db.add_message(chat_id, person_id, msg.get('content', ''), msg.get('timestamp'))
                    
            self.loading_overlay.hide()
            self._load_data()
            
            reply = QMessageBox.question(
                self, "Chat Importado",
                f"Se importaron {data['total_messages']} mensajes de {len(data['participants'])} participantes.\n\n¿Deseas analizar con IA ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._run_ai_analysis()
                
        except Exception as e:
            self.loading_overlay.hide()
            QMessageBox.critical(self, "Error", f"Error al importar:\n{str(e)}")
            
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
                profile_summary=profile.summary
            )
            for skill in profile.skills:
                skill_id = self.db.add_skill(skill.name, skill.category)
                self.db.add_person_skill(person_id, skill_id, skill.score, skill.evidence)
                
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
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Perfil: {person['name']}")
        dialog.setMinimumSize(600, 700)
        dialog.setStyleSheet(GLOBAL_STYLE + f"QDialog {{ background-color: {COLORS['bg_primary']}; }}")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(24)
        layout.setContentsMargins(32, 32, 32, 32)
        
        # Header
        header = QHBoxLayout()
        role_colors = ROLE_COLORS.get(person.get('role', 'desconocido').lower(), ROLE_COLORS['desconocido'])
        
        avatar = QLabel(person['name'][0].upper())
        avatar.setFixedSize(80, 80)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            border-radius: 40px;
            font-size: 32px;
            font-weight: 700;
        """)
        header.addWidget(avatar)
        
        info = QVBoxLayout()
        info.setSpacing(8)
        
        name_label = QLabel(person['name'])
        name_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 24px; font-weight: 700;")
        info.addWidget(name_label)
        
        role_badge = QLabel(person.get('role', 'Desconocido').capitalize())
        role_badge.setStyleSheet(f"""
            background-color: {role_colors[1]};
            color: {role_colors[0]};
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        """)
        role_badge.setFixedWidth(role_badge.sizeHint().width() + 8)
        info.addWidget(role_badge)
        
        header.addLayout(info)
        header.addStretch()
        layout.addLayout(header)
        
        # Stats
        stats_layout = QHBoxLayout()
        stats_data = [
            (f"💬 {person_stats.get('total_messages', 0)}", "mensajes"),
            (f"📋 {person_stats.get('total_tasks', 0)}", "tareas"),
            (f"✅ {person_stats.get('completed_tasks', 0)}", "completadas"),
        ]
        for value, label in stats_data:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                background-color: {COLORS['bg_secondary']};
                border-radius: 10px;
                padding: 12px;
            """)
            s_layout = QVBoxLayout(stat_frame)
            s_layout.setSpacing(2)
            
            v_label = QLabel(value)
            v_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 18px; font-weight: 600;")
            s_layout.addWidget(v_label)
            
            l_label = QLabel(label)
            l_label.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 12px;")
            s_layout.addWidget(l_label)
            
            stats_layout.addWidget(stat_frame)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Summary
        if person_data and person_data.get('profile_summary'):
            summary_card = Card()
            summary_layout = QVBoxLayout(summary_card)
            summary_label = QLabel(person_data['profile_summary'])
            summary_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 14px; line-height: 1.5;")
            summary_label.setWordWrap(True)
            summary_layout.addWidget(summary_label)
            layout.addWidget(summary_card)
            
        # Skills
        if person_data and person_data.get('skills'):
            skills_card = Card()
            skills_layout = QVBoxLayout(skills_card)
            skills_layout.setSpacing(12)
            
            skills_header = QLabel("📊 Habilidades")
            skills_header.setStyleSheet(f"color: {COLORS['text_primary']}; font-size: 16px; font-weight: 600;")
            skills_layout.addWidget(skills_header)
            
            for skill in person_data['skills']:
                skill_bar = SkillBar(skill['name'], skill['score'], skill.get('category', ''))
                skills_layout.addWidget(skill_bar)
            layout.addWidget(skills_card)
            
        layout.addStretch()
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
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
