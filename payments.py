import aiohttp
from config import settings


class CryptoBotAPI:
    def __init__(self):
        self.token = settings.cryptobot_api_token
        self.base_url = "https://pay.crypt.bot/api" if settings.cryptobot_network == "mainnet" else "https://testnet-pay.crypt.bot/api"
        self.headers = {"Crypto-Pay-API-Token": self.token}
    
    async def create_invoice(self, amount: float, description: str, telegram_id: int) -> dict:
        """Создать инвойс в CryptoBot"""
        data = {
            "asset": "USDT",
            "amount": str(amount),
            "description": description,
            "hidden_message": f"Telegram ID: {telegram_id}",
            "paid_btn_name": "callback",
            "paid_btn_url": f"https://t.me/your_bot",
            "payload": str(telegram_id),
            "expires_in": 3600  # 1 час
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/createInvoice",
                headers=self.headers,
                json=data
            ) as response:
                result = await response.json()
                if result.get("ok"):
                    return result["result"]
                raise Exception(f"CryptoBot error: {result}")


cryptobot = CryptoBotAPI()
