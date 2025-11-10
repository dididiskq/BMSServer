from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

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
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class OTAUpdate(Base):
    __tablename__ = "ota_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True)
    filename = Column(String)
    description = Column(String)
    release_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

def verify_data():
    """验证数据库中的数据是否正确插入"""
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        print("=== 数据库验证结果 ===")
        
        # 查询用户数据
        users = db.query(User).all()
        print(f"\n总用户数: {len(users)}")
        print("用户列表:")
        print("{:<5} {:<15} {:<25} {:<20} {:<10}".format(
            "ID", "用户名", "邮箱", "姓名", "状态"
        ))
        print("-" * 80)
        
        for user in users:
            status = "激活" if user.is_active else "禁用"
            print("{:<5} {:<15} {:<25} {:<20} {:<10}".format(
                user.id, user.username, user.email, user.full_name, status
            ))
        
        # 查询OTA更新数据
        updates = db.query(OTAUpdate).all()
        print(f"\n总OTA更新数: {len(updates)}")
        print("OTA更新列表:")
        print("{:<5} {:<10} {:<15} {:<15} {:<10}".format(
            "ID", "版本", "文件名", "发布日期", "状态"
        ))
        print("-" * 80)
        
        for update in updates:
            status = "激活" if update.is_active else "禁用"
            release_date = update.release_date.strftime("%Y-%m-%d")
            print("{:<5} {:<10} {:<15} {:<15} {:<10}".format(
                update.id, update.version, update.filename, release_date, status
            ))
        
        # 查询最新固件
        latest_update = db.query(OTAUpdate).filter(
            OTAUpdate.is_active == True
        ).order_by(OTAUpdate.release_date.desc()).first()
        
        if latest_update:
            print(f"\n最新激活的固件版本: {latest_update.version}")
            print(f"描述: {latest_update.description}")
        
        print("\n=== 验证完成 ===")
        
    except Exception as e:
        print(f"验证过程中出现错误: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_data()