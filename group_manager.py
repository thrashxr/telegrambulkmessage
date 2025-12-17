from typing import Optional
from telethon import TelegramClient
from telethon.tl.types import Chat, Channel, User
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest


class GroupManager:
    
    def __init__(self, client: TelegramClient):
        self.client = client
        self.groups: list[dict] = []
    
    async def fetch_groups(self) -> list[dict]:
        self.groups = []
        
        async for dialog in self.client.iter_dialogs():
            entity = dialog.entity
            
            if isinstance(entity, (Chat, Channel)):
                if isinstance(entity, Channel) and entity.broadcast and not entity.megagroup:
                    if not entity.creator and not entity.admin_rights:
                        continue
                
                group_info = {
                    "id": entity.id,
                    "title": dialog.title,
                    "entity": entity,
                    "type": self._get_group_type(entity),
                    "members": getattr(entity, "participants_count", None)
                }
                self.groups.append(group_info)
        
        return self.groups
    
    def _get_group_type(self, entity) -> str:
        if isinstance(entity, Chat):
            return "Grup"
        elif isinstance(entity, Channel):
            if entity.megagroup:
                return "Süper Grup"
            elif entity.broadcast:
                return "Kanal"
            else:
                return "Kanal"
        return "Bilinmiyor"
    
    def list_groups(self) -> list[dict]:
        return self.groups
    
    async def join_by_username(self, username: str) -> tuple[bool, str]:
        try:
            username = username.lstrip("@")
            
            await self.client(JoinChannelRequest(username))
            
            await self.fetch_groups()
            
            return True, f"@{username} grubuna katıldınız!"
            
        except Exception as e:
            error_msg = str(e)
            if "Cannot find any entity" in error_msg:
                return False, f"'{username}' kullanıcısı veya grubu bulunamadı."
            if "UsernameInvalidError" in error_msg:
                return False, "Geçersiz kullanıcı adı formatı."
            return False, f"Katılım hatası: {error_msg}"
    
    async def join_by_invite(self, invite_link: str) -> tuple[bool, str]:
        try:
            invite_hash = invite_link
            
            if "t.me/+" in invite_link:
                invite_hash = invite_link.split("t.me/+")[-1]
            elif "t.me/joinchat/" in invite_link:
                invite_hash = invite_link.split("t.me/joinchat/")[-1]
            elif "joinchat/" in invite_link:
                invite_hash = invite_link.split("joinchat/")[-1]
            
            invite_hash = invite_hash.strip().rstrip("/")
            
            await self.client(ImportChatInviteRequest(invite_hash))
            
            await self.fetch_groups()
            
            return True, "Gruba katıldınız!"
            
        except Exception as e:
            error_msg = str(e)
            if "UserAlreadyParticipantError" in error_msg:
                return False, "Zaten bu grubun üyesisiniz."
            return False, f"Katılım hatası: {error_msg}"
    
    async def join_group(self, link_or_username: str) -> tuple[bool, str]:
        link = link_or_username.strip()
        
        if not link or len(link) < 4:
            return False, "Geçersiz format: Link veya kullanıcı adı en az 4 karakter olmalıdır."
        
        if "t.me/+" in link or "joinchat" in link:
            return await self.join_by_invite(link)
        
        if link.startswith("@") or link.startswith("t.me/"):
            username = link.replace("t.me/", "").lstrip("@")
            return await self.join_by_username(username)
        
        if link.isdigit():
             return False, "Geçersiz format: Kullanıcı adı sadece rakamlardan oluşamaz."
             
        return await self.join_by_username(link)
    
    def get_group_by_index(self, index: int) -> Optional[dict]:
        if 0 <= index < len(self.groups):
            return self.groups[index]
        return None
    
    def get_group_by_id(self, group_id: int) -> Optional[dict]:
        for group in self.groups:
            if group["id"] == group_id:
                return group
        return None
