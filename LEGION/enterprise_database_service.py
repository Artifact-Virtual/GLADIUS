#!/usr/bin/env python3
"""
Enterprise Database Service - Production Configuration
Provides database connection and query utilities for the Legion Enterprise system.
Enhanced with Phase 6 Database Schema Extensions and Production Backup/Recovery.
"""

import sqlite3
import json
import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import os
import shutil
import gzip
import threading

class EnterpriseDatabase:
    """Database service for Legion Enterprise operations with backup and recovery support."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection with backup configuration."""
        # Get current directory first for default paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if db_path is None:
            # Default to the enterprise operations database
            db_path = os.path.join(current_dir, 'data', 'enterprise_operations.db')
        
        self.db_path = db_path
        self.connection = None
        
        # Backup configuration
        self.backup_enabled = os.getenv('BACKUP_ENABLED', 'true').lower() == 'true'
        self.backup_interval = int(os.getenv('BACKUP_INTERVAL', '3600')) # 1 hour default
        self.backup_retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
        # Use relative path from current directory
        default_backup_location = os.path.join(current_dir, 'backups')
        self.backup_location = os.getenv('BACKUP_LOCATION', default_backup_location)
        
        # Initialize backup system
        if self.backup_enabled:
            self.initialize_backup_system()
    
    def initialize_backup_system(self):
        """Initialize automated backup system."""
        os.makedirs(self.backup_location, exist_ok=True)
        
        # Start backup thread
        backup_thread = threading.Thread(target=self._backup_scheduler, daemon=True)
        backup_thread.start()
        
        print(f"Backup system initialized - interval: {self.backup_interval}s, retention: {self.backup_retention_days} days")
    
    def _backup_scheduler(self):
        """Automated backup scheduler."""
        while self.backup_enabled:
            try:
                self.create_backup()
                self.cleanup_old_backups()
                threading.Event().wait(self.backup_interval)
            except Exception as e:
                print(f"Backup scheduler error: {e}")
                threading.Event().wait(60)  # Wait 1 minute on error
    
    def create_backup(self):
        """Create compressed database backup."""
        if not os.path.exists(self.db_path):
            return False
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"enterprise_db_backup_{timestamp}.db.gz"
        backup_path = os.path.join(self.backup_location, backup_filename)
        
        try:
            # Create compressed backup
            with open(self.db_path, 'rb') as source:
                with gzip.open(backup_path, 'wb') as backup:
                    shutil.copyfileobj(source, backup)
            
            print(f"Database backup created: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"Backup creation failed: {e}")
            return False
    
    def restore_backup(self, backup_filename: str):
        """Restore database from backup."""
        backup_path = os.path.join(self.backup_location, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"Backup file not found: {backup_filename}")
            return False
        
        try:
            # Close current connection
            if self.connection:
                self.disconnect()
            
            # Create backup of current database
            current_backup = f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db_path, os.path.join(self.backup_location, current_backup))
            
            # Restore from backup
            with gzip.open(backup_path, 'rb') as backup:
                with open(self.db_path, 'wb') as target:
                    shutil.copyfileobj(backup, target)
            
            print(f"Database restored from: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def cleanup_old_backups(self):
        """Remove old backup files based on retention policy."""
        if not os.path.exists(self.backup_location):
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
        removed_count = 0
        
        for filename in os.listdir(self.backup_location):
            if filename.startswith('enterprise_db_backup_') and filename.endswith('.db.gz'):
                file_path = os.path.join(self.backup_location, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except Exception as e:
                        print(f"Failed to remove old backup {filename}: {e}")
        
        if removed_count > 0:
            print(f"Cleaned up {removed_count} old backup files")
    
    def get_backup_status(self):
        """Get backup system status and statistics."""
        if not os.path.exists(self.backup_location):
            return {'status': 'disabled', 'backups': []}
        
        backups = []
        total_size = 0
        
        for filename in os.listdir(self.backup_location):
            if filename.startswith('enterprise_db_backup_') and filename.endswith('.db.gz'):
                file_path = os.path.join(self.backup_location, filename)
                file_stat = os.stat(file_path)
                
                backups.append({
                    'filename': filename,
                    'size': file_stat.st_size,
                    'created': datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                    'age_days': (datetime.now() - datetime.fromtimestamp(file_stat.st_ctime)).days
                })
                total_size += file_stat.st_size
        
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return {
            'status': 'enabled' if self.backup_enabled else 'disabled',
            'backup_count': len(backups),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'latest_backup': backups[0]['created'] if backups else None,
            'retention_days': self.backup_retention_days,
            'interval_hours': self.backup_interval / 3600,
            'backups': backups[:10]  # Return latest 10 backups
        }
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_extended_schema(self):
        """Create Phase 6 extended database schema tables."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # === TASK 20.1: Dashboard Configuration Tables ===
            
            # Dashboard configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_id TEXT UNIQUE NOT NULL,
                    dashboard_name TEXT NOT NULL,
                    layout_type TEXT NOT NULL DEFAULT 'grid',
                    theme TEXT DEFAULT 'dark',
                    auto_refresh_enabled BOOLEAN DEFAULT 1,
                    refresh_interval_seconds INTEGER DEFAULT 30,
                    widget_order TEXT, -- JSON array of widget IDs
                    custom_settings TEXT, -- JSON object for custom settings
                    user_id TEXT,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Widget configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS widget_configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    widget_id TEXT UNIQUE NOT NULL,
                    dashboard_config_id TEXT NOT NULL,
                    widget_type TEXT NOT NULL,
                    widget_name TEXT NOT NULL,
                    position_x INTEGER DEFAULT 0,
                    position_y INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 1,
                    height INTEGER DEFAULT 1,
                    data_source TEXT, -- API endpoint or data source
                    refresh_rate INTEGER DEFAULT 30,
                    display_options TEXT, -- JSON for chart type, colors, etc.
                    filter_settings TEXT, -- JSON for data filtering
                    is_visible BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dashboard_config_id) REFERENCES dashboard_configurations(config_id)
                )
            ''')
            
            # Dashboard themes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_themes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    theme_id TEXT UNIQUE NOT NULL,
                    theme_name TEXT NOT NULL,
                    primary_color TEXT DEFAULT '#1a1a1a',
                    secondary_color TEXT DEFAULT '#2d2d2d',
                    accent_color TEXT DEFAULT '#4a9eff',
                    text_color TEXT DEFAULT '#ffffff',
                    background_color TEXT DEFAULT '#0a0a0a',
                    border_color TEXT DEFAULT '#3d3d3d',
                    success_color TEXT DEFAULT '#28a745',
                    warning_color TEXT DEFAULT '#ffc107',
                    error_color TEXT DEFAULT '#dc3545',
                    info_color TEXT DEFAULT '#17a2b8',
                    custom_css TEXT,
                    is_system_theme BOOLEAN DEFAULT 0,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # === TASK 20.2: System Metrics Logging Tables ===
            
            # System performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT UNIQUE NOT NULL,
                    metric_type TEXT NOT NULL, -- cpu, memory, disk, network
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT NOT NULL,
                    component TEXT, -- which system component
                    threshold_warning REAL,
                    threshold_critical REAL,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    server_instance TEXT DEFAULT 'main'
                )
            ''')
            
            # Application performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS application_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT UNIQUE NOT NULL,
                    application_name TEXT NOT NULL,
                    metric_type TEXT NOT NULL, -- response_time, throughput, error_rate
                    metric_value REAL NOT NULL,
                    endpoint TEXT,
                    user_session TEXT,
                    request_id TEXT,
                    error_details TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Agent performance metrics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_id TEXT UNIQUE NOT NULL,
                    agent_id TEXT NOT NULL,
                    agent_domain TEXT NOT NULL,
                    metric_type TEXT NOT NULL, -- tasks_completed, response_time, success_rate
                    metric_value REAL NOT NULL,
                    task_id TEXT,
                    complexity_level TEXT,
                    resource_usage REAL,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # === TASK 20.3: User Preferences and Settings Tables ===
            
            # User profiles and preferences
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    email TEXT,
                    full_name TEXT,
                    role TEXT DEFAULT 'user',
                    department TEXT,
                    preferred_theme TEXT DEFAULT 'dark',
                    timezone TEXT DEFAULT 'UTC',
                    language TEXT DEFAULT 'en',
                    notification_preferences TEXT, -- JSON object
                    dashboard_preferences TEXT, -- JSON object
                    accessibility_settings TEXT, -- JSON object
                    last_login TIMESTAMP,
                    login_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User session management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    session_token TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    logout_time TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    session_duration_minutes INTEGER,
                    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id)
                )
            ''')
            
            # User settings and customizations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    setting_category TEXT NOT NULL, -- dashboard, notifications, performance
                    setting_name TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    setting_type TEXT DEFAULT 'string', -- string, number, boolean, json
                    is_system_setting BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id)
                )
            ''')
            
            # === TASK 20.4: Dashboard Usage Analytics Tables ===
            
            # Dashboard usage tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usage_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    dashboard_name TEXT NOT NULL,
                    session_id TEXT,
                    action_type TEXT NOT NULL, -- view, interact, export, configure
                    widget_id TEXT,
                    interaction_details TEXT, -- JSON object
                    duration_seconds INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id)
                )
            ''')
            
            # Widget interaction analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS widget_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interaction_id TEXT UNIQUE NOT NULL,
                    widget_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    interaction_type TEXT NOT NULL, -- click, hover, resize, configure
                    data_filters_applied TEXT, -- JSON object
                    time_spent_seconds INTEGER,
                    error_occurred BOOLEAN DEFAULT 0,
                    error_message TEXT,
                    performance_metrics TEXT, -- JSON object
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id)
                )
            ''')
            
            # Dashboard performance analytics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dashboard_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    performance_id TEXT UNIQUE NOT NULL,
                    dashboard_name TEXT NOT NULL,
                    user_id TEXT,
                    load_time_ms INTEGER NOT NULL,
                    render_time_ms INTEGER,
                    data_fetch_time_ms INTEGER,
                    widget_count INTEGER,
                    error_count INTEGER DEFAULT 0,
                    memory_usage_mb REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.connection.commit()
            print("Phase 6 Database Schema Extensions - Tasks 20.1-20.4 completed successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error creating extended schema: {e}")
            self.connection.rollback()
            return False
    
    def create_remaining_schema_extensions(self):
        """Create remaining Phase 6 database schema extensions (Tasks 20.5-20.8)."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            
            # === TASK 20.5: System Health Monitoring Tables ===
            
            # System health status tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_health_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    health_id TEXT UNIQUE NOT NULL,
                    component_name TEXT NOT NULL,
                    component_type TEXT NOT NULL, -- service, database, api, agent
                    health_status TEXT NOT NULL, -- healthy, warning, critical, down
                    health_score INTEGER DEFAULT 100, -- 0-100
                    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_time_ms INTEGER,
                    error_rate REAL DEFAULT 0.0,
                    uptime_percentage REAL DEFAULT 100.0,
                    details TEXT, -- JSON object with detailed status info
                    remediation_suggested TEXT,
                    auto_recovery_attempted BOOLEAN DEFAULT 0
                )
            ''')
            
            # Health monitoring alerts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_monitoring_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    component_name TEXT NOT NULL,
                    alert_type TEXT NOT NULL, -- performance, availability, error
                    severity TEXT NOT NULL, -- info, warning, critical
                    alert_message TEXT NOT NULL,
                    threshold_value REAL,
                    actual_value REAL,
                    alert_triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    alert_acknowledged BOOLEAN DEFAULT 0,
                    acknowledged_by TEXT,
                    acknowledged_at TIMESTAMP,
                    alert_resolved BOOLEAN DEFAULT 0,
                    resolved_at TIMESTAMP,
                    resolution_notes TEXT
                )
            ''')
            
            # System dependencies mapping
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dependency_id TEXT UNIQUE NOT NULL,
                    parent_component TEXT NOT NULL,
                    dependent_component TEXT NOT NULL,
                    dependency_type TEXT NOT NULL, -- service, data, network
                    criticality TEXT DEFAULT 'medium', -- low, medium, high, critical
                    health_impact_factor REAL DEFAULT 1.0,
                    last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # === TASK 20.6: Alert and Notification History Tables ===
            
            # Notification history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    notification_type TEXT NOT NULL, -- email, sms, push, in_app
                    category TEXT NOT NULL, -- alert, info, warning, success
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    priority TEXT DEFAULT 'medium', -- low, medium, high, urgent
                    delivery_channel TEXT NOT NULL,
                    delivery_status TEXT DEFAULT 'pending', -- pending, sent, delivered, failed
                    sent_at TIMESTAMP,
                    delivered_at TIMESTAMP,
                    read_at TIMESTAMP,
                    clicked_at TIMESTAMP,
                    related_entity_type TEXT, -- dashboard, agent, workflow, system
                    related_entity_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Alert escalation rules
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_escalation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_id TEXT UNIQUE NOT NULL,
                    rule_name TEXT NOT NULL,
                    alert_category TEXT NOT NULL,
                    severity_threshold TEXT NOT NULL,
                    escalation_delay_minutes INTEGER DEFAULT 15,
                    escalation_levels TEXT NOT NULL, -- JSON array of escalation steps
                    notification_channels TEXT NOT NULL, -- JSON array of channels
                    is_active BOOLEAN DEFAULT 1,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Notification preferences per user
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_id TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    notification_category TEXT NOT NULL,
                    channel_email BOOLEAN DEFAULT 1,
                    channel_sms BOOLEAN DEFAULT 0,
                    channel_push BOOLEAN DEFAULT 1,
                    channel_in_app BOOLEAN DEFAULT 1,
                    quiet_hours_start TEXT, -- HH:MM format
                    quiet_hours_end TEXT, -- HH:MM format
                    frequency_limit TEXT DEFAULT 'immediate', -- immediate, hourly, daily
                    is_enabled BOOLEAN DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id)
                )
            ''')
            
            # === TASK 20.7: Optimization Metrics Tracking Tables ===
            
            # Optimization execution history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT UNIQUE NOT NULL,
                    optimization_type TEXT NOT NULL,
                    target_component TEXT NOT NULL,
                    optimization_strategy TEXT NOT NULL,
                    parameters TEXT, -- JSON object
                    initiated_by TEXT,
                    initiated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'pending', -- pending, running, completed, failed, rolled_back
                    progress_percentage INTEGER DEFAULT 0,
                    performance_before TEXT, -- JSON object with metrics
                    performance_after TEXT, -- JSON object with metrics
                    improvement_achieved REAL,
                    cost_impact REAL,
                    rollback_available BOOLEAN DEFAULT 1,
                    rollback_executed BOOLEAN DEFAULT 0,
                    success_criteria_met BOOLEAN DEFAULT 0,
                    execution_logs TEXT
                )
            ''')
            
            # Optimization recommendations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS optimization_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recommendation_id TEXT UNIQUE NOT NULL,
                    recommendation_type TEXT NOT NULL,
                    target_area TEXT NOT NULL,
                    priority TEXT NOT NULL, -- low, medium, high, critical
                    impact_estimate TEXT NOT NULL, -- low, medium, high
                    effort_estimate TEXT NOT NULL, -- low, medium, high
                    description TEXT NOT NULL,
                    detailed_analysis TEXT,
                    expected_improvement REAL,
                    estimated_cost REAL,
                    estimated_savings REAL,
                    implementation_timeframe TEXT,
                    risk_level TEXT DEFAULT 'medium',
                    generated_by TEXT DEFAULT 'ai_analysis',
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'new', -- new, reviewed, approved, implemented, rejected
                    reviewed_by TEXT,
                    reviewed_at TIMESTAMP,
                    implementation_notes TEXT
                )
            ''')
            
            # Performance baseline tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    baseline_id TEXT UNIQUE NOT NULL,
                    component_name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    baseline_value REAL NOT NULL,
                    measurement_unit TEXT NOT NULL,
                    measurement_period TEXT NOT NULL, -- daily, weekly, monthly
                    confidence_level REAL DEFAULT 95.0,
                    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sample_size INTEGER,
                    standard_deviation REAL,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # === TASK 20.8: Audit Trail and Change Tracking Tables ===
            
            # System audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    audit_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    action_type TEXT NOT NULL, -- create, read, update, delete, execute
                    entity_type TEXT NOT NULL, -- dashboard, widget, user, configuration
                    entity_id TEXT NOT NULL,
                    entity_name TEXT,
                    action_description TEXT NOT NULL,
                    old_values TEXT, -- JSON object
                    new_values TEXT, -- JSON object
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    request_id TEXT
                )
            ''')
            
            # Configuration change history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuration_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_id TEXT UNIQUE NOT NULL,
                    configuration_type TEXT NOT NULL,
                    configuration_name TEXT NOT NULL,
                    change_type TEXT NOT NULL, -- create, update, delete, backup, restore
                    changed_by TEXT NOT NULL,
                    change_reason TEXT,
                    previous_configuration TEXT, -- JSON object
                    new_configuration TEXT, -- JSON object
                    validation_status TEXT DEFAULT 'pending', -- pending, valid, invalid
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rollback_available BOOLEAN DEFAULT 1,
                    rollback_configuration TEXT, -- JSON object
                    impact_assessment TEXT,
                    approval_required BOOLEAN DEFAULT 0,
                    approved_by TEXT,
                    approved_at TIMESTAMP
                )
            ''')
            
            # Data change tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_change_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_log_id TEXT UNIQUE NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL, -- INSERT, UPDATE, DELETE
                    field_name TEXT,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    source_application TEXT DEFAULT 'enterprise_dashboard'
                )
            ''')
            
            # Security event log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL, -- login, logout, failed_login, permission_denied
                    severity TEXT NOT NULL, -- info, warning, critical
                    user_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    endpoint TEXT,
                    event_description TEXT NOT NULL,
                    additional_data TEXT, -- JSON object
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    investigated BOOLEAN DEFAULT 0,
                    investigated_by TEXT,
                    investigation_notes TEXT,
                    false_positive BOOLEAN DEFAULT 0
                )
            ''')
            
            self.connection.commit()
            print("Phase 6 Database Schema Extensions - Tasks 20.5-20.8 completed successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error creating remaining schema extensions: {e}")
            self.connection.rollback()
            return False
    
    def initialize_complete_schema(self):
        """Initialize the complete database schema including Phase 6 extensions."""
        if not self.connection:
            self.connect()
        
        try:
            print("🚀 Initializing Complete Enterprise Database Schema...")
            
            # Create Phase 6 extended schema
            if self.create_extended_schema():
                print("✅ Phase 6 Schema Extensions (Tasks 20.1-20.4) created successfully!")
            else:
                print("❌ Failed to create Phase 6 initial schema extensions")
                return False
            
            # Create remaining schema extensions
            if self.create_remaining_schema_extensions():
                print("✅ Phase 6 Schema Extensions (Tasks 20.5-20.8) created successfully!")
            else:
                print("❌ Failed to create remaining Phase 6 schema extensions")
                return False
            
            # Populate default data
            self.populate_default_data()
            
            print("🎉 Complete Enterprise Database Schema initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Schema initialization error: {e}")
            return False
    
    def populate_default_data(self):
        """Populate database with default configuration data."""
        try:
            cursor = self.connection.cursor()
            
            # Insert default dashboard themes
            default_themes = [
                ('theme_dark', 'Dark Enterprise', '#1a1a1a', '#2d2d2d', '#4a9eff', 
                 '#ffffff', '#0a0a0a', '#3d3d3d', '#28a745', '#ffc107', '#dc3545', '#17a2b8', 1),
                ('theme_light', 'Light Enterprise', '#ffffff', '#f8f9fa', '#007bff', 
                 '#333333', '#ffffff', '#dee2e6', '#28a745', '#ffc107', '#dc3545', '#17a2b8', 1),
                ('theme_blue', 'Enterprise Blue', '#0d1421', '#1e2a3a', '#2196f3', 
                 '#ffffff', '#0a0f1c', '#2a3f54', '#4caf50', '#ff9800', '#f44336', '#03a9f4', 1)
            ]
            
            for theme in default_themes:
                cursor.execute('''
                    INSERT OR IGNORE INTO dashboard_themes 
                    (theme_id, theme_name, primary_color, secondary_color, accent_color,
                     text_color, background_color, border_color, success_color, warning_color,
                     error_color, info_color, is_system_theme)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', theme)
            
            # Insert default user with admin privileges
            cursor.execute('''
                INSERT OR IGNORE INTO user_preferences 
                (user_id, username, email, full_name, role, department, preferred_theme)
                VALUES ('admin_001', 'admin', 'admin@enterprise.ai', 'System Administrator', 
                        'admin', 'IT', 'theme_dark')
            ''')
            
            # Insert default dashboard configuration
            cursor.execute('''
                INSERT OR IGNORE INTO dashboard_configurations 
                (config_id, dashboard_name, layout_type, theme, user_id, is_default)
                VALUES ('dashboard_default', 'Enterprise Operations Dashboard', 'grid', 
                        'theme_dark', 'admin_001', 1)
            ''')
            
            # Insert default notification preferences
            cursor.execute('''
                INSERT OR IGNORE INTO notification_preferences 
                (preference_id, user_id, notification_category, channel_email, 
                 channel_push, channel_in_app)
                VALUES ('notif_admin_001', 'admin_001', 'system_alerts', 1, 1, 1)
            ''')
            
            # Insert default escalation rule
            cursor.execute('''
                INSERT OR IGNORE INTO alert_escalation_rules 
                (rule_id, rule_name, alert_category, severity_threshold, 
                 escalation_levels, notification_channels, created_by)
                VALUES ('rule_critical', 'Critical Alert Escalation', 'system', 'critical',
                        '["immediate", "15min", "30min"]', '["email", "sms", "push"]', 'admin_001')
            ''')
            
            self.connection.commit()
            print("✅ Default configuration data populated successfully!")
            
        except sqlite3.Error as e:
            print(f"Error populating default data: {e}")
            self.connection.rollback()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert sqlite3.Row objects to dictionaries
            result = []
            for row in rows:
                result.append(dict(row))
            
            return result
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an INSERT, UPDATE, or DELETE query."""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Update execution error: {e}")
            return False

class BusinessObjectivesService:
    """Service for business objectives operations."""
    
    def __init__(self, db: EnterpriseDatabase):
        self.db = db
    
    def get_all_objectives(self) -> List[Dict[str, Any]]:
        """Get all business objectives grouped by type."""
        query = """
        SELECT objective_type, description, target_value, current_value, 
               target_date, status, created_at
        FROM business_objectives 
        GROUP BY objective_type 
        ORDER BY target_date ASC
        """
        return self.db.execute_query(query)
    
    def get_objectives_progress(self) -> Dict[str, float]:
        """Calculate progress percentage for each objective."""
        objectives = self.get_all_objectives()
        progress = {}
        
        for obj in objectives:
            if obj['target_value'] > 0:
                progress[obj['objective_type']] = (obj['current_value'] / obj['target_value']) * 100
            else:
                progress[obj['objective_type']] = 0.0
        
        return progress
    
    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get objectives with deadlines in the next N days."""
        query = """
        SELECT objective_type, description, target_date, status
        FROM business_objectives 
        WHERE target_date <= date('now', '+{} days')
        AND status = 'active'
        GROUP BY objective_type
        ORDER BY target_date ASC
        """.format(days_ahead)
        
        return self.db.execute_query(query)

class DepartmentActivitiesService:
    """Service for department activities operations."""
    
    def __init__(self, db: EnterpriseDatabase):
        self.db = db
    
    def get_all_activities(self) -> List[Dict[str, Any]]:
        """Get all department activities grouped by department."""
        query = """
        SELECT department, activity_type, description, status, priority, created_at
        FROM department_activities 
        GROUP BY department, activity_type
        ORDER BY priority DESC, department
        """
        return self.db.execute_query(query)
    
    def get_department_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics by department."""
        activities = self.get_all_activities()
        summary = {}
        
        for activity in activities:
            dept = activity['department']
            if dept not in summary:
                summary[dept] = {
                    'total_activities': 0,
                    'active_activities': 0,
                    'avg_priority': 0,
                    'activities': []
                }
            
            summary[dept]['total_activities'] += 1
            if activity['status'] == 'active':
                summary[dept]['active_activities'] += 1
            summary[dept]['activities'].append(activity)
        
        # Calculate average priority
        for dept in summary:
            if summary[dept]['activities']:
                priorities = [act['priority'] for act in summary[dept]['activities']]
                summary[dept]['avg_priority'] = sum(priorities) / len(priorities)
        
        return summary

class RevenueTrackingService:
    """Service for revenue tracking operations."""
    
    def __init__(self, db: EnterpriseDatabase):
        self.db = db
    
    def get_revenue_data(self) -> List[Dict[str, Any]]:
        """Get all revenue tracking data ordered by date."""
        query = """
        SELECT month, year, target_revenue, actual_revenue, lead_value, conversion_rate, created_at
        FROM revenue_tracking 
        GROUP BY month, year
        ORDER BY year, month
        """
        return self.db.execute_query(query)
    
    def get_current_year_summary(self, year: int = None) -> Dict[str, float]:
        """Get revenue summary for current or specified year."""
        if year is None:
            year = datetime.now().year
        
        query = """
        SELECT 
            SUM(target_revenue) as total_target,
            SUM(actual_revenue) as total_actual,
            SUM(lead_value) as total_leads,
            AVG(conversion_rate) as avg_conversion
        FROM revenue_tracking 
        WHERE year = ?
        """
        
        result = self.db.execute_query(query, (year,))
        if result:
            return result[0]
        return {'total_target': 0, 'total_actual': 0, 'total_leads': 0, 'avg_conversion': 0}
    
    def get_monthly_performance(self, year: int = None) -> List[Dict[str, Any]]:
        """Get month-by-month performance data."""
        if year is None:
            year = datetime.now().year
        
        query = """
        SELECT month, target_revenue, actual_revenue, lead_value, conversion_rate
        FROM revenue_tracking 
        WHERE year = ?
        ORDER BY month
        """
        
        return self.db.execute_query(query, (year,))

class EnterpriseDataAPI:
    """Main API service for dashboard data."""
    
    def __init__(self, db_path: str = None):
        self.db = EnterpriseDatabase(db_path)
        self.objectives_service = BusinessObjectivesService(self.db)
        self.activities_service = DepartmentActivitiesService(self.db)
        self.revenue_service = RevenueTrackingService(self.db)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get complete dashboard data payload."""
        try:
            # Connect to database
            if not self.db.connect():
                return {"error": "Database connection failed"}
            
            # Gather all dashboard data
            dashboard_data = {
                "timestamp": datetime.now().isoformat(),
                "business_objectives": {
                    "objectives": self.objectives_service.get_all_objectives(),
                    "progress": self.objectives_service.get_objectives_progress(),
                    "upcoming_deadlines": self.objectives_service.get_upcoming_deadlines()
                },
                "department_activities": {
                    "activities": self.activities_service.get_all_activities(),
                    "summary": self.activities_service.get_department_summary()
                },
                "revenue_tracking": {
                    "data": self.revenue_service.get_revenue_data(),
                    "current_year": self.revenue_service.get_current_year_summary(),
                    "monthly_performance": self.revenue_service.get_monthly_performance()
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            return {"error": f"Data retrieval error: {str(e)}"}
        
        finally:
            self.db.disconnect()

def main():
    """Test the database services."""
    print("🔧 Testing Enterprise Database Services...")
    
    # Initialize API
    api = EnterpriseDataAPI()
    
    # Get dashboard data
    data = api.get_dashboard_data()
    
    if "error" in data:
        print(f"❌ Error: {data['error']}")
        return
    
    # Print summary
    print(f"✅ Database connection successful!")
    print(f"📊 Data retrieved at: {data['timestamp']}")
    print(f"🎯 Business Objectives: {len(data['business_objectives']['objectives'])}")
    print(f"🏢 Department Activities: {len(data['department_activities']['activities'])}")
    print(f"💰 Revenue Records: {len(data['revenue_tracking']['data'])}")
    
    # Show sample data
    print("\n📋 Sample Business Objectives:")
    for obj in data['business_objectives']['objectives'][:3]:
        print(f"  • {obj['objective_type']}: {obj['description']}")
    
    print("\n🏢 Active Departments:")
    for dept, info in data['department_activities']['summary'].items():
        print(f"  • {dept}: {info['active_activities']} active activities (Priority: {info['avg_priority']})")

if __name__ == "__main__":
    main()
