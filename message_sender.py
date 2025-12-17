import asyncio
from pathlib import Path
from typing import Optional
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat
import config


class MessageSender:
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.is_running = False
        self.message_delay = config.DEFAULT_MESSAGE_DELAY
        self.group_delay = config.DEFAULT_GROUP_DELAY
        self.loop_delay = config.DEFAULT_LOOP_DELAY
    
    def set_delays(
        self,
        message_delay: Optional[int] = None,
        group_delay: Optional[int] = None,
        loop_delay: Optional[int] = None
    ):
        if message_delay is not None:
            self.message_delay = message_delay
        if group_delay is not None:
            self.group_delay = group_delay
        if loop_delay is not None:
            self.loop_delay = loop_delay
    
    async def send_message(
        self,
        entity,
        message: str,
        image_path: Optional[str] = None
    ) -> tuple[bool, str]:
        try:
            if image_path:
                path = Path(image_path)
                if not path.exists():
                    return False, f"Resim bulunamadı: {image_path}"
                
                await self.client.send_file(
                    entity,
                    path,
                    caption=message
                )
            else:
                await self.client.send_message(entity, message)
            
            return True, "Mesaj gönderildi!"
            
        except Exception as e:
            error_msg = str(e)
            if "FloodWaitError" in error_msg:
                return False, f"Flood bekleme hatası: {error_msg}"
            elif "ChatWriteForbiddenError" in error_msg:
                return False, "Bu gruba mesaj gönderme izniniz yok."
            elif "UserBannedInChannelError" in error_msg:
                return False, "Bu gruptan banlandınız."
            elif "SlowModeWaitError" in error_msg:
                return False, "Yavaş mod aktif, beklemeniz gerekiyor."
            return False, f"Mesaj hatası: {error_msg}"
    
    async def send_to_groups(
        self,
        groups: list[dict],
        message: str,
        image_path: Optional[str] = None,
        loop: bool = False,
        callback=None
    ) -> dict:
        self.is_running = True
        results = {"success": 0, "failed": 0, "total": 0, "loop_count": 0}
        
        try:
            while self.is_running:
                results["loop_count"] += 1
                
                if callback:
                    callback(None, None, f"\n🔄 Döngü #{results['loop_count']} başlıyor...")
                
                for i, group in enumerate(groups):
                    if not self.is_running:
                        break
                    
                    entity = group.get("entity")
                    title = group.get("title", "Bilinmeyen")
                    
                    if callback:
                        callback(title, None, f"📤 Gönderiliyor: {title}")
                    
                    success, msg = await self.send_message(entity, message, image_path)
                    results["total"] += 1
                    
                    if success:
                        results["success"] += 1
                        if callback:
                            callback(title, True, f"✅ {title}: Başarılı")
                    else:
                        results["failed"] += 1
                        if callback:
                            callback(title, False, f"❌ {title}: {msg}")
                    
                    if i < len(groups) - 1 or loop:
                        if self.is_running:
                            await asyncio.sleep(self.group_delay)
                
                if not loop:
                    break
                
                if self.is_running:
                    if callback:
                        callback(None, None, f"⏳ Sonraki döngü için {self.loop_delay} saniye bekleniyor...")
                    await asyncio.sleep(self.loop_delay)
        
        except asyncio.CancelledError:
            pass
        
        self.is_running = False
        return results
    
    def stop(self):
        self.is_running = False
    
    async def send_single(
        self,
        group: dict,
        message: str,
        image_path: Optional[str] = None
    ) -> tuple[bool, str]:
        entity = group.get("entity")
        if not entity:
            return False, "Geçersiz grup."
        
        return await self.send_message(entity, message, image_path)
