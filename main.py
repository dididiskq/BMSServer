from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import os
import shutil
import uvicorn

# 创建数据库引擎
DATABASE_URL = "sqlite:///./bms.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型
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

# 创建数据表（在模型定义后创建）
Base.metadata.create_all(bind=engine)

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建FastAPI应用实例
app = FastAPI(
    title="BMS Server",
    description="电池管理系统服务器API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保uploads目录存在
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 用户管理API
@app.post("/users/")
async def create_user(
    username: str = Form(...),
    email: str = Form(...),
    password_hash: str = Form(...),
    full_name: str = Form(...),
    db: Session = Depends(get_db)
):
    # 检查用户名和邮箱是否已存在
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 创建新用户
    db_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        full_name=full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}

@app.get("/users/")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return [{"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name, "is_active": user.is_active} for user in users]

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name, "is_active": user.is_active}

@app.put("/users/{user_id}")
async def update_user(
    user_id: int,
    username: str = Form(None),
    email: str = Form(None),
    password_hash: str = Form(None),
    full_name: str = Form(None),
    is_active: bool = Form(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 更新字段
    if username is not None:
        if db.query(User).filter(User.username == username, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Username already in use")
        user.username = username
    if email is not None:
        if db.query(User).filter(User.email == email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = email
    if password_hash is not None:
        user.password_hash = password_hash
    if full_name is not None:
        user.full_name = full_name
    if is_active is not None:
        user.is_active = is_active
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email, "full_name": user.full_name, "is_active": user.is_active}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# OTA固件更新API
@app.post("/ota/upload")
async def upload_firmware(
    version: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 检查版本是否已存在
    if db.query(OTAUpdate).filter(OTAUpdate.version == version).first():
        raise HTTPException(status_code=400, detail="Version already exists")
    
    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 创建OTA更新记录
    ota_update = OTAUpdate(
        version=version,
        filename=file.filename,
        description=description
    )
    db.add(ota_update)
    db.commit()
    db.refresh(ota_update)
    
    return {"id": ota_update.id, "version": ota_update.version, "filename": ota_update.filename, "description": ota_update.description}

@app.get("/ota/updates")
async def get_ota_updates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    updates = db.query(OTAUpdate).offset(skip).limit(limit).all()
    return [{
        "id": update.id,
        "version": update.version,
        "filename": update.filename,
        "description": update.description,
        "release_date": update.release_date.isoformat(),
        "is_active": update.is_active
    } for update in updates]

@app.get("/ota/updates/{update_id}")
async def get_ota_update(update_id: int, db: Session = Depends(get_db)):
    update = db.query(OTAUpdate).filter(OTAUpdate.id == update_id).first()
    if not update:
        raise HTTPException(status_code=404, detail="OTA update not found")
    
    return {
        "id": update.id,
        "version": update.version,
        "filename": update.filename,
        "description": update.description,
        "release_date": update.release_date.isoformat(),
        "is_active": update.is_active
    }

@app.get("/ota/latest")
async def get_latest_firmware(db: Session = Depends(get_db)):
    # 获取最新的活跃固件版本
    update = db.query(OTAUpdate).filter(OTAUpdate.is_active == True).order_by(OTAUpdate.release_date.desc()).first()
    if not update:
        raise HTTPException(status_code=404, detail="No active firmware found")
    
    return {
        "id": update.id,
        "version": update.version,
        "filename": update.filename,
        "description": update.description,
        "release_date": update.release_date.isoformat(),
        "download_url": f"/ota/download/{update.id}"
    }

@app.get("/ota/download/{update_id}")
async def download_firmware(update_id: int, db: Session = Depends(get_db)):
    # 获取固件信息
    update = db.query(OTAUpdate).filter(OTAUpdate.id == update_id).first()
    if not update:
        raise HTTPException(status_code=404, detail="Firmware not found")
    
    # 检查文件是否存在
    file_path = os.path.join(UPLOAD_DIR, update.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Firmware file not found")
    
    # 读取文件内容
    with open(file_path, "rb") as file:
        content = file.read()
    
    # 返回文件响应
    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={update.filename}"
        }
    )

@app.put("/ota/updates/{update_id}/status")
async def update_firmware_status(update_id: int, is_active: bool = Form(...), db: Session = Depends(get_db)):
    update = db.query(OTAUpdate).filter(OTAUpdate.id == update_id).first()
    if not update:
        raise HTTPException(status_code=404, detail="OTA update not found")
    
    update.is_active = is_active
    db.commit()
    db.refresh(update)
    
    return {"id": update.id, "version": update.version, "is_active": update.is_active}

@app.delete("/ota/updates/{update_id}")
async def delete_ota_update(update_id: int, db: Session = Depends(get_db)):
    update = db.query(OTAUpdate).filter(OTAUpdate.id == update_id).first()
    if not update:
        raise HTTPException(status_code=404, detail="OTA update not found")
    
    # 删除文件
    file_path = os.path.join(UPLOAD_DIR, update.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.delete(update)
    db.commit()
    
    return {"message": "OTA update deleted successfully"}

# 根路径
@app.get("/")
async def root():
    return {"message": "BMS Server is running"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)