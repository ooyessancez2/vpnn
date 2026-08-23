import aiohttp
from datetime import datetime, timedelta
from config import settings
from typing import Optional, Dict


class RemnawaveAPI:
    def __init__(self):
        self.base_url = settings.remnawave_api_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.remnawave_api_key}",
            "Content-Type": "application/json"
        }
    
    async def _request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Базовый метод для запросов к API"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api{endpoint}"
            async with session.request(method, url, headers=self.headers, json=data) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Remnawave API error {response.status}: {error_text}")
    
    async def create_user(self, telegram_id: int, username: str, days: int = 30) -> Dict:
        """Создать пользователя в Remnawave"""
        expire_at = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"
        data = {
            "username": f"tg_{telegram_id}",
            "status": "ACTIVE",
            "shortUuid": f"tg{telegram_id}",
            "trojanPassword": f"pass_{telegram_id}",
            "vlessUuid": f"vless_{telegram_id}",
            "ssPassword": f"ss_{telegram_id}",
            "description": f"Telegram bot user: @{username} (ID: {telegram_id})",
            "expireAt": expire_at,
            "activeUserInbounds": []  # Пустой массив = все инбаунды
        }
        return await self._request("POST", "/users", data)
    
    async def extend_subscription(self, remnawave_uuid: str, days: int) -> Dict:
        """Продлить подписку"""
        # Получаем текущие данные
        user_data = await self._request("GET", f"/users/{remnawave_uuid}")
        current_expire = datetime.fromisoformat(user_data["expireAt"].replace("Z", "+00:00"))
        
        # Если подписка уже истекла, начинаем с текущего момента
        if current_expire < datetime.now():
            new_expire = datetime.utcnow() + timedelta(days=days)
        else:
            new_expire = current_expire + timedelta(days=days)
        
        data = {
            **user_data,
            "expireAt": new_expire.isoformat() + "Z"
        }
        return await self._request("PATCH", f"/users/{remnawave_uuid}", data)
    
    async def get_user_status(self, remnawave_uuid: str) -> Dict:
        """Получить статус подписки"""
        return await self._request("GET", f"/users/{remnawave_uuid}")
    
    async def get_subscription_link(self, remnawave_uuid: str) -> str:
        """Получить ссылку для подключения (vless/vmess)"""
        data = await self._request("GET", f"/users/{remnawave_uuid}")
        return data.get("subscriptionUrl", "Ссылка недоступна")


remnawave = RemnawaveAPI()
