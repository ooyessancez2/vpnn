<div align="center">

# ⚡ CYBER VPN BOT

### Быстро. Технологично. Надёжно.

![Python](https://img.shields.io/badge/python-3.11+-000?style=for-the-badge&logo=python&logoColor=00ccff)
![aiogram](https://img.shields.io/badge/aiogram-3.x-000?style=for-the-badge&logo=telegram&logoColor=00ccff)
![Docker](https://img.shields.io/badge/docker-ready-000?style=for-the-badge&logo=docker&logoColor=00ccff)
![Remnawave](https://img.shields.io/badge/remnawave-panel-000?style=for-the-badge&logo=shield&logoColor=00ccff)
![License](https://img.shields.io/badge/license-MIT-000?style=for-the-badge&logoColor=00ccff)

**Telegram-бот для продажи VPN-подписок через панель Remnawave.**
Без воды. Без логов. Без границ.

[Установка](#-быстрый-старт) • [Конфиг](#-конфигурация) • [Обновление](#-обновление) • [Проблемы](#-решение-проблем)

</div>

---

## 🎯 Что это

Автономный бот, который продаёт VPN-подписки, пока ты спишь.
Юзер жмёт три кнопки — получает ключ. Ты получаешь деньги.

- **Стиль:** строгий монохром, тёмная тема, высокий контраст. Ноль визуального шума.
- **Тон:** дерзко и неформально. Никаких корпоративных реверансов.
- **Безопасность:** секреты живут в `.env` (права 600) и больше нигде.

> ⚡ **СИСТЕМА ИНИЦИАЛИЗИРОВАНА.**
> Слышь, кибер-странник. Ты в зоне без цензуры и ограничений.
> Выбирай действие. Не тупи.

---

## ⚡ Функционал

| Модуль | Что делает | Статус |
|---|---|---|
| 🔐 Подписки | Тариф → оплата → выдача ключа за ~30 сек | ✅ |
| 📊 Статус | Срок, трафик, устройства | ✅ |
| 💰 Баланс | Пополнение + история транзакций | ✅ |
| 💳 CryptoBot | USDT / TON / BTC / ETH | ✅ |
| 🤝 Рефералка | Бонус с каждого друга | ✅ |
| 🎁 Промокоды | Разовые бонусы на баланс | ✅ |
| ⚠️ Уведомления | За 3 дня (бот) и за 24 ч (push) | ✅ |
| 💳 ЮMoney / QIWI | Фиат-приём | 🔜 |
| 🏦 Карты P2P | Банковские карты | 🔜 |

> ⚠️ Клиент Remnawave (`remnawave.py`) написан под общую схему API. Поля создания пользователя (`trojanPassword`, `vlessUuid`, `activeUserInbounds`) могут потребовать подгонки под твою версию панели и набор инбаундов.

---

## 🏗 Архитектура


    [ Пользователь Telegram ]
                │
                ▼
    [ aiogram 3.x :: main.py ]
      │          │          │
      ▼          ▼          ▼
 [handlers] [scheduler] [payments] ──▶ [ CryptoBot API ]
      │          │
      ▼          ▼
 [ database ]  (уведомления: 3 дн / 24 ч)
      │
      ▼
 [ remnawave.py ] ──▶ [ Панель Remnawave ] ──▶ [ VPN-ноды ]



 Контейнеры (docker compose):  bot  ·  postgres  ·  redis



 
---

## 📁 Структура

vpnn/
├── install.sh             # автономная установка/обновление (v3.0)
├── main.py                # точка входа
├── config.py              # конфиг из .env (pydantic-settings)
├── database.py            # SQLite (aiosqlite): юзеры, транзакции, промо
├── remnawave.py           # клиент API панели Remnawave
├── payments.py            # интеграция CryptoBot
├── scheduler.py           # уведомления 3 дн / 24 ч
├── texts.py               # все тексты (дерзкий тон — здесь)
├── handlers/
│   ├── start.py           # /start, главное меню
│   ├── subscription.py    # тарифы, покупка, статус
│   ├── balance.py         # баланс, пополнение
│   ├── referral.py        # реферальная схема
│   └── promo.py           # промокоды
├── keyboards/
│   └── inline.py          # inline-клавиатуры (монохром)
├── docker-compose.yml     # bot + postgres + redis
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore             # .env сюда не попадает. Никогда.




> Примечание по БД: бот хранит данные в **SQLite-файле** (`data/bot.db`, лежит в docker-volume). Контейнеры `postgres` и `redis` подняты как инфраструктурный запас под будущие модули (автоплатежи, кэш, веб-кабинет) и на текущую логику не влияют.

---

## 🚀 Быстрый старт

### Способ 1 — одна строка (рекомендуется)

Чистый VPS (Ubuntu/Debian) → одна команда → рабочая система:

```bash
curl -fsSL https://raw.githubusercontent.com/ooyessancez2/vpnn/main/install.sh | sudo bash


Скрипт сам:
- поставит Docker и зависимости (переждёт блокировку apt);
- склонирует репо в `/opt/cyber-vpn-bot`;
- спросит 5 параметров и сгенерирует защищённый `.env` (chmod 600, случайный пароль БД);
- соберёт и поднимет контейнеры;
- выведет хвост лога — сразу видно, живой бот или нет.

### Способ 2 — вручную

```bash
git clone https://github.com/ooyessancez2/vpnn.git
cd vpnn
cp .env.example .env
nano .env                                   # заполни переменные (см. ниже)
docker compose up -d --build
```

---

## ⚙️ Конфигурация

Все секреты — только в `.env`. В коде их нет и не будет.

```bash
# ===== TELEGRAM =====
BOT_TOKEN=123456789:AAF...          # от @BotFather
ADMIN_IDS=[123456789]               # ⚠️ строго JSON-список в скобках! Несколько: [111,222]

# ===== REMNAWAVE =====
REMNAWAVE_API_URL=https://panel.domain.com
REMNAWAVE_API_KEY=...               # для eGames-скрипта формат XXXXXXX:DDDDDDDD

# ===== CRYPTOBOT =====
CRYPTOBOT_API_TOKEN=123456:AA...    # от @CryptoBot
CRYPTOBOT_NETWORK=mainnet           # mainnet | testnet

# ===== ЦЕНЫ (руб) =====
PRICE_30_DAYS=100
PRICE_90_DAYS=270
PRICE_180_DAYS=500

# ===== УВЕДОМЛЕНИЯ =====
NOTIFY_3_DAYS_BEFORE=true           # сообщение в боте за 3 дня
NOTIFY_24_HOURS_BEFORE=true         # push за 24 часа

# ===== DATABASE (PostgreSQL-контейнер; бот пока на SQLite) =====
POSTGRES_DB=cyber_vpn_db
POSTGRES_USER=cyber_vpn_user
POSTGRES_PASSWORD=...               # install.sh сгенерирует сам

# ===== REFERRAL =====
REFERRAL_BONUS_RUB=50

# ===== SYSTEM =====
TZ=Europe/Moscow
LOG_LEVEL=INFO
```

---

## 🎛 Управление

```bash
docker compose ps                 # статус контейнеров
docker compose logs -f bot        # логи в реальном времени
docker compose restart bot        # перезапуск бота
docker compose down               # полная остановка
```

---

## 🔄 Обновление

После любых правок на GitHub — одна команда на сервере:

```bash
sudo bash /opt/cyber-vpn-bot/install.sh
```

Скрипт подтянет код (`git reset --hard origin/main`), **не тронет** `.env`, пересоберёт образ и перезапустит. Данные в volumes не теряются.

Откат:
```bash
git log --oneline -5
git checkout <hash>
docker compose up -d --build
```

---

## 🔒 Безопасность

1. Секреты только в `.env` — он в `.gitignore`.
2. Права 600 — `.env` читает только root.
3. Пароль БД генерируется (`openssl rand`), а не `password123`.
4. Изолированная сеть `cyber_net`.
5. Порты БД на `127.0.0.1` — снаружи не достучаться.

**Утёк ключ?**
```bash
docker compose down
nano .env                     # смени скомпрометированные ключи
docker compose up -d --build
```

---

## 🐛 Решение проблем

| Симптом | Причина | Лечение |
|---|---|---|
| `TokenValidationError` | кривой `BOT_TOKEN` | перепиши токен → `docker compose restart bot` |
| `ValidationError ... ADMIN_IDS` | ID без скобок / текст | пиши строго `[123456789]` |
| `Remnawave API error 4xx` | схема юзера не совпала с панелью | подгони поля в `remnawave.py` под свою версию |
| `Could not get lock /var/lib/dpkg/...` | фоновый apt | подожди 2–3 мин (скрипт переждёт сам) |
| `/bin/bash^M: bad interpreter` | CRLF из Windows | `sed -i 's/\r$//' install.sh` |
| `Permission denied` | нет +x | `chmod +x install.sh` |
| контейнер в рестарт-цикле | — | `docker compose logs --tail=50 bot` |

---

## 🗺 Roadmap

- [ ] ЮMoney / QIWI
- [ ] P2P-оплата картами
- [ ] Автопродление (autopay)
- [ ] Webhooks Remnawave (real-time)
- [ ] Мини-кабинет (Telegram WebApp)
- [ ] Мониторинг трафика и аномалий

---

## 📝 Лицензия

MIT. Делай что хочешь — на свой страх и риск.

---

<div align="center">

**Не тупи. Подключайся. Летай.** ⚡

</div>
```

---

### Что именно я починил

| # | Было | Стало |
|---|---|---|
| 1 | `${WHITE}$1${1}${NC}` — битый цвет в `log_warn` | `${WHITE}$1${NC}` |
| 2 | README врала про SQLite vs Postgres | Честно: бот на SQLite, postgres/redis — инфраструктурный запас |
| 3 | Схема показывала redis как рабочий | Добавлена сноска про назначение контейнеров |
| 4 | Remnawave помечен ✅ без оговорок | Добавлен warning про подгонку полей под версию панели |
| 5 | Ручной способ не генерил пароль БД | Уточнено, что install.sh генерит креды |
| 6 | Нет бейджа лицензии | Добавлен |
