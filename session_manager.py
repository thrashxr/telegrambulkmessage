import asyncio
from pathlib import Path
from typing import Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import config


class SessionManager:
    
    def __init__(self):
        self.clients: dict[str, TelegramClient] = {}
        self.active_client: Optional[TelegramClient] = None
        self.active_phone: Optional[str] = None
    
    def get_session_path(self, phone: str) -> Path:
        clean_phone = phone.replace("+", "").replace(" ", "")
        return config.SESSIONS_DIR / clean_phone
    
    def list_saved_sessions(self) -> list[str]:
        sessions = []
        for session_file in config.SESSIONS_DIR.glob("*.session"):
            sessions.append(session_file.stem)
        return sessions
    
    def create_client(self, phone: str) -> TelegramClient:
        session_path = self.get_session_path(phone)
        client = TelegramClient(
            str(session_path),
            config.API_ID,
            config.API_HASH
        )
        return client
    
    async def login(self, phone: str) -> tuple[bool, str]:
        client = self.create_client(phone)
        
        try:
            await client.connect()
            
            if await client.is_user_authorized():
                self.clients[phone] = client
                self.active_client = client
                self.active_phone = phone
                return True, "Önceki oturum ile giriş yapıldı."
            
            await client.send_code_request(phone)
            
            print("\n📱 Telegram'dan gelen doğrulama kodunu girin:")
            code = input("Kod: ").strip()
            
            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                print("\n🔐 2FA şifresi gerekli:")
                password = input("Şifre: ").strip()
                await client.sign_in(password=password)
            
            self.clients[phone] = client
            self.active_client = client
            self.active_phone = phone
            
            me = await client.get_me()
            return True, f"Giriş başarılı! Hoş geldin, {me.first_name}!"
            
        except Exception as e:
            await client.disconnect()
            return False, f"Giriş hatası: {str(e)}"
    
    async def load_session(self, phone: str) -> tuple[bool, str]:
        session_path = self.get_session_path(phone)
        
        if not session_path.with_suffix(".session").exists():
            return False, "Session dosyası bulunamadı."
        
        client = self.create_client(phone)
        
        try:
            await client.connect()
            
            if await client.is_user_authorized():
                self.clients[phone] = client
                self.active_client = client
                self.active_phone = phone
                
                me = await client.get_me()
                return True, f"Session yüklendi! Hoş geldin, {me.first_name}!"
            else:
                await client.disconnect()
                return False, "Session geçersiz, yeniden giriş gerekli."
                
        except Exception as e:
            await client.disconnect()
            return False, f"Session yükleme hatası: {str(e)}"
    
    async def logout(self, phone: str) -> tuple[bool, str]:
        if phone in self.clients:
            client = self.clients[phone]
            try:
                await client.log_out()
                await client.disconnect()
            except:
                pass
            del self.clients[phone]
        
        session_path = self.get_session_path(phone)
        session_file = session_path.with_suffix(".session")
        if session_file.exists():
            session_file.unlink()
        
        if self.active_phone == phone:
            self.active_client = None
            self.active_phone = None
        
        return True, "Çıkış yapıldı ve session silindi."
    
    async def disconnect_all(self):
        for phone, client in self.clients.items():
            try:
                await client.disconnect()
            except:
                pass
        self.clients.clear()
        self.active_client = None
        self.active_phone = None
    
    def get_active_client(self) -> Optional[TelegramClient]:
        return self.active_client
    
    def get_active_phone(self) -> Optional[str]:
        return self.active_phone
