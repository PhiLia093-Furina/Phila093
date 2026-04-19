import tomli as tomllib  # 内置：读取toml
import tomli_w   # 第三方：写入toml
import sys
from pathlib import Path
import os

# 配置文件路径
TOML_PATH = "config/config.toml"

def resource_path(relative_path):
    """获取资源的绝对路径，适用于开发和打包环境"""
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发模式下，从当前文件所在目录开始构建路径
        base_path = Path(__file__).parent
    
    return os.path.join(base_path, relative_path)

# ========== 读取 TOML 配置 ==========
def load_config(PATH = None) -> dict:
    file_path = PATH if PATH is not None else resource_path(TOML_PATH)

    try:
        with open(file_path, "rb") as f:
            config = tomllib.load(f)
        return config
    
    except FileNotFoundError:
        print("自动生成缓存文件")
        with open(file_path, "w", encoding="utf-8") as f:
            # 写入一个空的 TOML 结构（必须合法，不能是空文件）
            f.write("# 自动生成的配置文件\n games = []\n")

    except Exception as e:
        print(f"读取配置失败: {e}")

# ========== 写入/保存 TOML 配置 ==========
def save_config(data: dict, PATH=None):
    file_path = PATH if PATH is not None else resource_path(TOML_PATH)
    
    """写入字典数据到toml文件"""
    try:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)
        return True
    
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False