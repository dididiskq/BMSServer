from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
import os

# 数据库配置
DATABASE_URL = "sqlite:///./bms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型定义
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OTAUpdate(Base):
    __tablename__ = "ota_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True)
    filename = Column(String)
    description = Column(String)
    release_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# 确保uploads目录存在
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 创建示例固件文件
def create_sample_firmware_file(filename):
    """创建一个简单的示例固件文件"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "w") as f:
        f.write(f"Sample firmware content for {filename}\nVersion: {filename.split('.')[0]}\nCreated: {datetime.now()}")
    return filename

def seed_data():
    """向数据库中插入测试数据"""
    # 创建数据表（如果不存在）
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        existing_updates = db.query(OTAUpdate).count()
        
        if existing_users > 0 or existing_updates > 0:
            print("数据库中已存在数据，跳过数据填充。")
            print(f"当前用户数: {existing_users}")
            print(f"当前OTA更新数: {existing_updates}")
            return
        
        print("开始填充测试数据...")
        
        # 创建测试用户数据
        users_data = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                "full_name": "管理员",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=30)
            },
            {
                "username": "user1",
                "email": "user1@example.com",
                "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                "full_name": "测试用户一",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=15)
            },
            {
                "username": "user2",
                "email": "user2@example.com",
                "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                "full_name": "测试用户二",
                "is_active": True,
                "created_at": datetime.utcnow() - timedelta(days=10)
            },
            {
                "username": "user3",
                "email": "user3@example.com",
                "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                "full_name": "测试用户三",
                "is_active": False,
                "created_at": datetime.utcnow() - timedelta(days=5)
            }
        ]
        
        # 插入用户数据
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print(f"成功插入 {len(users_data)} 条用户数据")
        
        # 创建示例固件文件
        firmware_files = [
            create_sample_firmware_file("1.0.0.bin"),
            create_sample_firmware_file("1.0.1.bin"),
            create_sample_firmware_file("1.1.0.bin")
        ]
        
        # 创建OTA更新数据
        ota_updates_data = [
            {
                "version": "1.0.0",
                "filename": firmware_files[0],
                "description": "初始版本固件，基本功能实现",
                "release_date": datetime.utcnow() - timedelta(days=60),
                "is_active": False
            },
            {
                "version": "1.0.1",
                "filename": firmware_files[1],
                "description": "修复了系统稳定性问题，优化了电池管理算法",
                "release_date": datetime.utcnow() - timedelta(days=30),
                "is_active": False
            },
            {
                "version": "1.1.0",
                "filename": firmware_files[2],
                "description": "新增温度监控功能，改进了用户界面，提升了系统性能",
                "release_date": datetime.utcnow() - timedelta(days=7),
                "is_active": True
            }
        ]
        
        # 插入OTA更新数据
        for update_data in ota_updates_data:
            update = OTAUpdate(**update_data)
            db.add(update)
        
        db.commit()
        print(f"成功插入 {len(ota_updates_data)} 条OTA更新数据")
        print(f"成功创建 {len(firmware_files)} 个示例固件文件")
        
        print("数据填充完成！")
        
    except Exception as e:
        print(f"数据填充过程中出现错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()