#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Config 模块单元测试

测试范围:
- 从 config.json 读取凭据
- 从环境变量读取凭据
- 测试凭据缺失处理
"""

import unittest
import json
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加 scripts 目录到路径
import sys
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import config as config_module


class TestConfig(unittest.TestCase):
    """测试配置管理功能"""

    def setUp(self):
        """保存原始环境变量"""
        self.original_env = {
            'INTERVALS_ATHLETE_ID': os.environ.get('INTERVALS_ATHLETE_ID'),
            'INTERVALS_API_KEY': os.environ.get('INTERVALS_API_KEY'),
            'INTERVALS_EMAIL': os.environ.get('INTERVALS_EMAIL'),
            'INTERVALS_PASSWORD': os.environ.get('INTERVALS_PASSWORD'),
        }
        
        # 清除环境变量
        for key in self.original_env:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        """恢复原始环境变量"""
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

    def test_load_config_empty(self):
        """测试加载不存在的配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 临时修改 CONFIG_FILE
            original_config_file = config_module.CONFIG_FILE
            config_module.CONFIG_FILE = Path(temp_dir) / "nonexistent.json"
            
            try:
                result = config_module.load_config()
                self.assertEqual(result, {})
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_load_config_valid(self):
        """测试加载有效的配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_file = Path(temp_dir) / "config.json"
            config_module.CONFIG_FILE = config_file
            
            try:
                config_data = {
                    "athlete_id": "test_athlete_123",
                    "api_key": "test_api_key_456",
                    "email": "test@example.com",
                    "password": "test_password"
                }
                config_file.write_text(json.dumps(config_data))
                
                result = config_module.load_config()
                self.assertEqual(result["athlete_id"], "test_athlete_123")
                self.assertEqual(result["api_key"], "test_api_key_456")
                self.assertEqual(result["email"], "test@example.com")
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_load_config_invalid_json(self):
        """测试加载损坏的配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_file = Path(temp_dir) / "config.json"
            config_module.CONFIG_FILE = config_file
            
            try:
                config_file.write_text("invalid json")
                
                result = config_module.load_config()
                self.assertEqual(result, {})
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_from_config(self):
        """测试从配置文件读取凭据"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_file = Path(temp_dir) / "config.json"
            config_module.CONFIG_FILE = config_file
            
            try:
                config_data = {
                    "athlete_id": "config_athlete",
                    "api_key": "config_key"
                }
                config_file.write_text(json.dumps(config_data))
                
                athlete_id, api_key = config_module.get_credentials()
                self.assertEqual(athlete_id, "config_athlete")
                self.assertEqual(api_key, "config_key")
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_from_env(self):
        """测试从环境变量读取凭据"""
        os.environ['INTERVALS_ATHLETE_ID'] = "env_athlete"
        os.environ['INTERVALS_API_KEY'] = "env_key"
        
        result = config_module.get_credentials()
        self.assertEqual(result[0], "env_athlete")
        self.assertEqual(result[1], "env_key")

    def test_get_credentials_priority_env_over_config(self):
        """测试环境变量优先级高于配置文件"""
        os.environ['INTERVALS_ATHLETE_ID'] = "env_athlete"
        os.environ['INTERVALS_API_KEY'] = "env_key"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_file = Path(temp_dir) / "config.json"
            config_module.CONFIG_FILE = config_file
            
            try:
                config_data = {
                    "athlete_id": "config_athlete",
                    "api_key": "config_key"
                }
                config_file.write_text(json.dumps(config_data))
                
                result = config_module.get_credentials()
                # 环境变量应该优先
                self.assertEqual(result[0], "env_athlete")
                self.assertEqual(result[1], "env_key")
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_priority_args_over_env(self):
        """测试命令行参数优先级高于环境变量"""
        os.environ['INTERVALS_ATHLETE_ID'] = "env_athlete"
        os.environ['INTERVALS_API_KEY'] = "env_key"
        
        # 模拟命令行参数
        args = MagicMock()
        args.athlete_id = "arg_athlete"
        args.api_key = "arg_key"
        
        result = config_module.get_credentials(args)
        # 命令行参数应该优先
        self.assertEqual(result[0], "arg_athlete")
        self.assertEqual(result[1], "arg_key")

    def test_get_credentials_with_dict_args(self):
        """测试使用字典作为 args 参数"""
        args = {
            "athlete_id": "dict_athlete",
            "api_key": "dict_key"
        }
        
        result = config_module.get_credentials(args)
        self.assertEqual(result[0], "dict_athlete")
        self.assertEqual(result[1], "dict_key")

    def test_get_credentials_missing(self):
        """测试凭据缺失的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            # 使用不存在的配置文件路径
            config_module.CONFIG_FILE = Path(temp_dir) / "nonexistent.json"
            
            try:
                result = config_module.get_credentials()
                self.assertIsNone(result[0])
                self.assertIsNone(result[1])
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_partial_missing(self):
        """测试部分凭据缺失的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_module.CONFIG_FILE = Path(temp_dir) / "nonexistent.json"
            
            try:
                os.environ['INTERVALS_ATHLETE_ID'] = "partial_athlete"
                # api_key 未设置
                
                result = config_module.get_credentials()
                self.assertEqual(result[0], "partial_athlete")
                self.assertIsNone(result[1])
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_with_email_password(self):
        """测试包含 email/password 的凭据"""
        os.environ['INTERVALS_ATHLETE_ID'] = "athlete"
        os.environ['INTERVALS_API_KEY'] = "key"
        os.environ['INTERVALS_EMAIL'] = "test@example.com"
        os.environ['INTERVALS_PASSWORD'] = "password"
        
        result = config_module.get_credentials()
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], "athlete")
        self.assertEqual(result[1], "key")
        self.assertEqual(result[2], "test@example.com")
        self.assertEqual(result[3], "password")

    def test_get_credentials_email_password_from_config(self):
        """测试从配置文件读取 email/password"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_file = Path(temp_dir) / "config.json"
            config_module.CONFIG_FILE = config_file
            
            try:
                config_data = {
                    "athlete_id": "athlete",
                    "api_key": "key",
                    "email": "config@example.com",
                    "password": "config_pass"
                }
                config_file.write_text(json.dumps(config_data))
                
                result = config_module.get_credentials()
                self.assertEqual(len(result), 4)
                self.assertEqual(result[2], "config@example.com")
                self.assertEqual(result[3], "config_pass")
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_only_athlete_id_from_env(self):
        """测试仅从环境变量读取 athlete_id"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_module.CONFIG_FILE = Path(temp_dir) / "nonexistent.json"
            
            try:
                os.environ['INTERVALS_ATHLETE_ID'] = "only_athlete"
                
                result = config_module.get_credentials()
                self.assertEqual(result[0], "only_athlete")
                self.assertIsNone(result[1])
            finally:
                config_module.CONFIG_FILE = original_config_file

    def test_get_credentials_only_api_key_from_env(self):
        """测试仅从环境变量读取 api_key"""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_config_file = config_module.CONFIG_FILE
            config_module.CONFIG_FILE = Path(temp_dir) / "nonexistent.json"
            
            try:
                os.environ['INTERVALS_API_KEY'] = "only_key"
                
                result = config_module.get_credentials()
                self.assertIsNone(result[0])
                self.assertEqual(result[1], "only_key")
            finally:
                config_module.CONFIG_FILE = original_config_file


if __name__ == '__main__':
    unittest.main()
