#!/bin/bash
# ============================================================
#  CYBER VPN BOT - АВТОНОМНАЯ УСТАНОВКА И ОБНОВЛЕНИЕ
#  Версия: 3.0.0
#
#  Первичная установка (одной строкой):
#    curl -fsSL https://raw.githubusercontent.com/USER/REPO/main/install.sh | sudo bash
#
#  Обновление:
#    sudo bash /opt/cyber-vpn-bot/install.sh
# ============================================================

set -e
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# ====== НАСТРОЙКИ (ИЗМЕНИ ПЕРЕД ПУШЕМ В GITHUB!) ======
GITHUB_USER="ooyessancez2"   # твой логин GitHub
GITHUB_REPO="vpnn"          # имя репозитория
GITHUB_TOKEN=""                      # токен ghp_... ТОЛЬКО для приватных репо
BRANCH="main"
INSTALL_DIR="/opt/cyber-vpn-bot"
# ======================================================

CYAN='\033[1;36m'; WHITE='\033[1;37m'; RED='\033[1;31m'
GREEN='\033[1;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

log_info()    { echo -e "${CYAN}[*]${NC} ${WHITE}$1${NC}"; }
log_success() { echo -e "${GREEN}[+]${NC} ${WHITE}$1${NC}"; }
log_warn()    { echo -e "${YELLOW}[!]${NC} ${WHITE}$1${1}${NC}"; }
log_error()   { echo -e "${RED}[-]${NC} ${WHITE}$1${NC}"; exit 1; }

echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}  CYBER VPN BOT :: ПРОТОКОЛ РАЗВЕРТЫВАНИЯ v3.0                 ${NC}"
echo -e "${CYAN}  Быстро. Технологично. Надежно.                               ${NC}"
echo -e "${CYAN}================================================================${NC}"

# ---------- 0. ПРОВЕРКИ ----------
[ "$EUID" -ne 0 ] && log_error "Нет прав. Запускай: sudo bash install.sh"

# ---------- 1. ЗАВИСИМОСТИ (с ожиданием блокировки apt) ----------
apt_safe() {
    local attempt=1
    while [ $attempt -le 3 ]; do
        if apt-get "$@" -y -qq > /dev/null 2>&1; then return 0; fi
        log_warn "apt занят (фоновые обновления). Жду 20 сек... (попытка $attempt/3)"
        sleep 20
        attempt=$((attempt + 1))
    done
    log_error "apt заблокирован. Подожди пару минут и запусти скрипт снова."
}

log_info "Проверка зависимостей (curl, git)..."
apt_safe update
apt_safe install curl git

if ! command -v docker &> /dev/null; then
    log_info "Docker не найден. Устанавливаю..."
    curl -fsSL https://get.docker.com | bash > /dev/null 2>&1
    systemctl enable --now docker
    log_success "Docker установлен."
else
    log_success "Docker на месте."
fi

if ! docker compose version &> /dev/null 2>&1; then
    log_info "Ставлю Docker Compose..."
    apt_safe install docker-compose-plugin
fi

# ---------- 2. КОД (клон или обновление) ----------
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

if [ -d ".git" ]; then
    log_info "Существующая установка. Синхронизация с GitHub..."
    GIT_TERMINAL_PROMPT=0 git fetch origin "$BRANCH"
    GIT_TERMINAL_PROMPT=0 git reset --hard "origin/$BRANCH"
    git clean -fd > /dev/null 2>&1
    log_success "Код обновлен."
else
    if [ "$GITHUB_USER" = "YOUR_GITHUB_USERNAME" ]; then
        log_error "В скрипте не указан GITHUB_USER. Отредактируй install.sh на GitHub."
    fi
    if [ -n "$GITHUB_TOKEN" ]; then
        REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
    else
        REPO_URL="https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
    fi
    log_info "Клонирование репозитория..."
    GIT_TERMINAL_PROMPT=0 git clone -b "$BRANCH" "$REPO_URL" . \
        || log_error "Не удалось склонировать. Проверь URL/токен/права."
    log_success "Код загружен."
fi

# ---------- 3. КОНФИГУРАЦИЯ .env ----------
if [ ! -f ".env" ]; then
    log_info "Первичная настройка. Отвечай на вопросы:"

    # читаем с /dev/tty, чтобы работало и через curl | bash
    read -p "BOT_TOKEN (от @BotFather): " BOT_TOKEN < /dev/tty
    read -p "Твой Telegram ID (число, можно несколько через запятую): " ADMIN_RAW < /dev/tty
    read -p "REMNAWAVE_API_URL (https://panel.domain.com): " RW_URL < /dev/tty
    read -p "REMNAWAVE_API_KEY: " RW_KEY < /dev/tty
    read -p "CRYPTOBOT_API_TOKEN (Enter - пропустить): " CB_TOKEN < /dev/tty

    # авто-формат ID в JSON-список для pydantic: 123 -> [123]
    case "$ADMIN_RAW" in
        \[*\]) ADMIN_IDS="$ADMIN_RAW" ;;
        *)     ADMIN_IDS="[${ADMIN_RAW}]" ;;
    esac

    DB_PASS=$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 32)

    cat <<EOF > .env
# Сгенерировано install.sh v3.0 | $(date '+%Y-%m-%d %H:%M')
# НЕ ПУБЛИКУЙ ЭТОТ ФАЙЛ.

# ===== TELEGRAM =====
BOT_TOKEN=${BOT_TOKEN}
ADMIN_IDS=${ADMIN_IDS}

# ===== REMNAWAVE =====
REMNAWAVE_API_URL=${RW_URL}
REMNAWAVE_API_KEY=${RW_KEY}

# ===== CRYPTOBOT =====
CRYPTOBOT_API_TOKEN=${CB_TOKEN}
CRYPTOBOT_NETWORK=mainnet

# ===== ЦЕНЫ (руб) =====
PRICE_30_DAYS=100
PRICE_90_DAYS=270
PRICE_180_DAYS=500

# ===== УВЕДОМЛЕНИЯ =====
NOTIFY_3_DAYS_BEFORE=true
NOTIFY_24_HOURS_BEFORE=true

# ===== DATABASE =====
POSTGRES_DB=cyber_vpn_db
POSTGRES_USER=cyber_vpn_user
POSTGRES_PASSWORD=${DB_PASS}

# ===== REFERRAL =====
REFERRAL_BONUS_RUB=50

# ===== SYSTEM =====
TZ=Europe/Moscow
LOG_LEVEL=INFO
EOF

    chmod 600 .env
    log_success ".env создан и защищен (chmod 600)."
else
    log_success ".env уже на месте. Не трогаю."
fi

# ---------- 4. ЗАПУСК ----------
log_info "Сборка и запуск контейнеров..."
docker compose down > /dev/null 2>&1 || true
docker compose up -d --build --remove-orphans

# ---------- 5. ПРОВЕРКА ----------
sleep 5
if docker compose ps | grep -q "Up"; then
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${GREEN}  СИСТЕМА РАЗВЕРНУТА. ДОСТУП РАЗРЕШЕН.                         ${NC}"
    echo -e "${CYAN}----------------------------------------------------------------${NC}"
    echo -e "${WHITE}  Логи:        ${CYAN}docker compose logs -f bot${NC}"
    echo -e "${WHITE}  Статус:      ${CYAN}docker compose ps${NC}"
    echo -e "${WHITE}  Обновление:  ${CYAN}sudo bash install.sh${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${WHITE}Последние строки лога бота:${NC}"
    docker compose logs --tail=10 bot
else
    log_error "Контейнеры не поднялись. Смотри: docker compose logs bot"
fi
