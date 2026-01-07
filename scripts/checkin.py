import os
import sys
import asyncio
import random
import uuid
from typing import List, Tuple
import aiohttp
from aiohttp_socks import ProxyConnector
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# Constants
API_BASE_URL = "https://be.nexira.ai/api/web-game-air-drop-token"
IP_CHECK_URL = "https://api.ipify.org?format=json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "Content-Type": "application/json",
    "Origin": "https://www.nexira.ai",
    "Referer": "https://www.nexira.ai/",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}

# Configuration
CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 5,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 5,
    "THREADS": 4,
    "BYPASS_SSL": True,
    "TIMEOUT": 30,
    "SEASON": 2,
}

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'NEXIRA SS2 NEW YEAR - DAILY CHECK-IN',
        'info': 'Thông tin',
        'found': 'Tìm thấy',
        'tokens': 'token',
        'processing_accounts': '⚙ ĐANG XỬ LÝ {count} TÀI KHOẢN',
        'checking_in': 'Đang check-in...',
        'checkin_success': 'Check-in thành công!',
        'getting_activities': 'Đang lấy thông tin hoạt động...',
        'activities_success': 'Đã lấy thông tin hoạt động!',
        'success': '✅ Check-in thành công cho tài khoản {index}',
        'points_earned': 'Điểm nhận được',
        'total_checkins': 'Tổng số lần check-in',
        'request_time': 'Thời gian',
        'account_info': 'Thông tin tài khoản',
        'failure': '❌ Check-in thất bại: {error}',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': '✅ HOÀN THÀNH: {successful}/{total} CHECK-IN THÀNH CÔNG',
        'error': 'Lỗi',
        'token_not_found': '❌ Không tìm thấy tệp token.txt',
        'token_empty': '❌ Không tìm thấy token hợp lệ',
        'token_error': '❌ Không thể đọc token.txt',
        'invalid_token': 'không hợp lệ, đã bỏ qua',
        'warning_line': 'Cảnh báo: Dòng',
        'found_proxies': 'Tìm thấy {count} proxy trong proxies.txt',
        'found_tokens': 'Thông tin: Tìm thấy {count} token',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': '🔄 Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': '⚠ Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': '⚠ Không thể kiểm tra IP công khai: {error}',
        'confirm_start': 'Tìm thấy {count} token, bạn có muốn bắt đầu check-in không? (y/n): ',
        'user_cancelled': 'ℹ Người dùng đã hủy thao tác',
        'rate_limit': '⚠ Đạt giới hạn yêu cầu (HTTP 429). Đang thử lại sau {delay} giây...',
        'already_checked': '⚠ Đã check-in hôm nay rồi',
        'daily_limit_reached': '⚠ Ví này đã checkin rồi! Vui lòng thực hiện lại hôm sau...',
    },
    'en': {
        'title': 'NEXIRA SS2 NEW YEAR - DAILY CHECK-IN',
        'info': 'Information',
        'found': 'Found',
        'tokens': 'tokens',
        'processing_accounts': '⚙ PROCESSING {count} ACCOUNTS',
        'checking_in': 'Checking in...',
        'checkin_success': 'Check-in successful!',
        'getting_activities': 'Getting activities info...',
        'activities_success': 'Got activities info!',
        'success': '✅ Check-in successful for account {index}',
        'points_earned': 'Points Earned',
        'total_checkins': 'Total Check-ins',
        'request_time': 'Request Time',
        'account_info': 'Account Info',
        'failure': '❌ Check-in failed: {error}',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': '✅ COMPLETED: {successful}/{total} CHECK-INS SUCCESSFUL',
        'error': 'Error',
        'token_not_found': '❌ token.txt file not found',
        'token_empty': '❌ No valid tokens found',
        'token_error': '❌ Failed to read token.txt',
        'invalid_token': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'found_proxies': 'Found {count} proxies in proxies.txt',
        'found_tokens': 'Info: Found {count} tokens',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': '🔄 Using Proxy - [{proxy}] with Public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': '⚠ Invalid or unresponsive proxy: {proxy}',
        'ip_check_failed': '⚠ Failed to check public IP: {error}',
        'user_cancelled': 'ℹ User cancelled operation',
        'rate_limit': '⚠ Rate limit reached (HTTP 429). Retrying after {delay} seconds...',
        'already_checked': '⚠ Already checked in today',
        'daily_limit_reached': '⚠ This wallet has already checked in! Please try again tomorrow...',
    }
}

def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH, language: str = 'en'):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_separator(color=Fore.MAGENTA, language: str = 'en'):
    print(f"{color}{'═' * BORDER_WIDTH}{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW, language: str = 'en'):
    print(f"{color}  {message}{Style.RESET_ALL}")

def print_accounts_summary(count: int, language: str = 'en'):
    print_border(
        LANG[language]['processing_accounts'].format(count=count),
        Fore.MAGENTA, language=language
    )
    print()

def is_valid_token(token: str) -> bool:
    token = token.strip()
    parts = token.split('.')
    return len(parts) == 3 and token.startswith('eyJ')

def load_tokens(file_path: str = "token.txt", language: str = 'en') -> List[Tuple[int, str]]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ✖ {LANG[language]['token_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add Bearer tokens here, one per line\n# Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...\n")
            sys.exit(1)
        
        valid_tokens = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                token = line.strip()
                if token and not token.startswith('#'):
                    if is_valid_token(token):
                        valid_tokens.append((i, token))
                    else:
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['warning_line']} {i} {LANG[language]['invalid_token']}: {token[:20]}...{Style.RESET_ALL}")
        
        if not valid_tokens:
            print(f"{Fore.RED}  ✖ {LANG[language]['token_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_tokens
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['token_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

def load_proxies(file_path: str = "proxies.txt", language: str = 'en') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not line.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW}  ⚠ {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            return []
        
        print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_proxies'].format(count=len(proxies))}{Style.RESET_ALL}")
        return proxies
    except Exception as e:
        print(f"{Fore.RED}  ✖ {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'en') -> str:
    try:
        if proxy:
            if proxy.startswith(('socks5://', 'socks4://', 'http://', 'https://')):
                connector = ProxyConnector.from_url(proxy)
            else:
                parts = proxy.split(':')
                if len(parts) == 4:
                    proxy_url = f"socks5://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
                    connector = ProxyConnector.from_url(proxy_url)
                elif len(parts) == 3 and '@' in proxy:
                    connector = ProxyConnector.from_url(f"socks5://{proxy}")
                else:
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['invalid_proxy'].format(proxy=proxy)}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
        else:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('ip', LANG[language]['unknown'])
                    print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

async def daily_checkin(token: str, index: int, proxy: str = None, language: str = 'en') -> bool:
    print_border(f"Daily Check-in for Account {index}", Fore.YELLOW, language=language)

    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN}🔄 {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                print(f"{Fore.CYAN}  > {LANG[language]['checking_in']}{Style.RESET_ALL}")
                
                headers = HEADERS.copy()
                headers["authorization"] = f"Bearer {token}"
                
                checkin_payload = {
                    "season": CONFIG['SEASON']
                }
                
                async with session.post(
                    f"{API_BASE_URL}/daily-checkin",
                    json=checkin_payload,
                    headers=headers,
                    ssl=not CONFIG['BYPASS_SSL']
                ) as response:
                    if response.status == 429:
                        delay = CONFIG['RETRY_DELAY'] * (attempt + 1)
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['rate_limit'].format(delay=delay)}{Style.RESET_ALL}")
                        await asyncio.sleep(delay)
                        continue
                    
                    if response.status == 500:
                        response_text = await response.text()
                        if "DATABASE_AIR_DROP_TOKEN_DAILY_LIMIT" in response_text:
                            print(f"{Fore.YELLOW}  {LANG[language]['daily_limit_reached']}{Style.RESET_ALL}")
                            print()
                            return True
                    
                    if response.status != 201:
                        response_text = await response.text()
                        print(f"{Fore.RED}  ✖ Check-in failed: HTTP {response.status} - {response_text}{Style.RESET_ALL}")
                        if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                            await asyncio.sleep(CONFIG['RETRY_DELAY'])
                            continue
                        return False
                    
                    data = await response.json()
                    checkin_data = data.get("data", {})
                    
                    if not checkin_data.get("updated"):
                        print(f"{Fore.YELLOW}  ⚠ {LANG[language]['already_checked']}{Style.RESET_ALL}")
                        print()
                        return True
                    
                    print(f"{Fore.GREEN}  ✓ {LANG[language]['checkin_success']}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['points_earned']}: {checkin_data.get('pointEarned', 0)}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}  - {LANG[language]['request_time']}: {checkin_data.get('requestTime', 'N/A')}{Style.RESET_ALL}")
                    print()
                
                print(f"{Fore.CYAN}  > {LANG[language]['getting_activities']}{Style.RESET_ALL}")
                
                async with session.get(
                    f"{API_BASE_URL}/activities/season?season={CONFIG['SEASON']}",
                    headers=headers,
                    ssl=not CONFIG['BYPASS_SSL']
                ) as response:
                    if response.status == 200:
                        activities_data = await response.json()
                        daily_login = activities_data.get("activities", {}).get("DAILY_LOGIN", {})
                        count = daily_login.get("count", 0)
                        
                        print(f"{Fore.GREEN}  ✓ {LANG[language]['activities_success']}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}  - {LANG[language]['total_checkins']}: {count}{Style.RESET_ALL}")
                        print()
                    else:
                        print(f"{Fore.YELLOW}  ⚠ Failed to get activities: HTTP {response.status}{Style.RESET_ALL}")
                        print()
                
                return True

        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                delay = CONFIG['RETRY_DELAY']
                print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}  ℹ {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}{Style.RESET_ALL}")
                await asyncio.sleep(delay)
                continue
            print(f"{Fore.RED}  ✖ {LANG[language]['failure'].format(error=str(e))}{Style.RESET_ALL}")
            return False
    return False

async def run_checkin(language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN, language=language)
    print()

    proxies = load_proxies(language=language)
    print()

    tokens = load_tokens(language=language)
    print(f"{Fore.YELLOW}  ℹ {LANG[language]['found_tokens'].format(count=len(tokens))}{Style.RESET_ALL}")
    print()

    if not tokens:
        return

    print_separator(language=language)
    random.shuffle(tokens)
    print_accounts_summary(len(tokens), language)

    total_checkins = 0
    successful_checkins = 0

    async def process_account(index, profile_num, token):
        nonlocal successful_checkins, total_checkins
        proxy = proxies[index % len(proxies)] if proxies else None
        
        async with semaphore:
            success = await daily_checkin(token, profile_num, proxy, language)
            total_checkins += 1
            if success:
                successful_checkins += 1
            if index < len(tokens) - 1:
                print_message(f"{LANG[language]['pausing']} {CONFIG['DELAY_BETWEEN_ACCOUNTS']:.2f} {LANG[language]['seconds']}", Fore.YELLOW, language)
                await asyncio.sleep(CONFIG['DELAY_BETWEEN_ACCOUNTS'])

    semaphore = asyncio.Semaphore(CONFIG['THREADS'])
    tasks = [process_account(i, profile_num, token) for i, (profile_num, token) in enumerate(tokens)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(
        LANG[language]['completed'].format(successful=successful_checkins, total=total_checkins),
        Fore.GREEN, language=language
    )
    print()

if __name__ == "__main__":
    asyncio.run(run_checkin('vi'))
