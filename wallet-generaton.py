import asyncio
import requests
from pytoniq_core.crypto.keys import mnemonic_new
from tonutils.client import LiteserverClient
from tonutils.wallet import WalletV5R1
from colorama import Fore, Style, init
from tqdm import tqdm

# Инициализация цветного вывода
init(autoreset=True)

# Словарь замены похожих символов
SIMILAR_CHARS = {
    'l': ['1', '|'],
    '1': ['l', '|'],
    'o': ['0'],
    '0': ['o'],
    's': ['5', '$'],
    '5': ['s', '$'],
    '$': ['s', '5'],
    'a': ['@'],
    'e': ['3'],
    '3': ['e'],
    'w': ['vv'],
}

# Полный список популярных слов (300+)
POPULAR_WORDS = [
    # Основные крипто термины
    'ton', 'btc', 'eth', 'toncoin', 'solana', 'avax','link',
    'atom', 'cake',  'comp',
    'fil', 'near',
    'wallet', 'sand', 'mana',
    'audio', 'penis',
    'ocean',
    'pool', 'farm', 'node', 'mine', 'stack', 'hold',
    
    # Финансовые термины
    'moon', 'bull', 'bear', 'pump', 'dump', 'fomo', 'fud','gas', 'fee',
    'key', 'sign', 'hash', 'node', 'peer', 'smart',
    'code', 'byte', 'call','block', 'chain', 'fork', 'air', 'drop',
    'whale', 'bot', 'flash', 'front','scam', 'wrap',
    
    # Общие слова
    'bank', 'cash', 'pay', 'buy', 'sell', 'bid','swap', 'trade', 'fund',
    'rich', 'gold', 'coin', 'money', 'profit', 'loss', 'gain', 'risk', 'safe', 'vault',
    'credit', 'asset', 'stock', 'bond', 'deriv', 'margin',
    'short', 'long', 'lever','cost', 'price', 'value', 'cap',
    'share','mcap','supply', 'burn',
    
    # Технические термины
    'mint', 'issue', 'stake', 'slash', 'claim', 'vest', 'lock', 'unlock', 'withdraw',
    'deposit', 'transfer', 'convert', 'bridge', 'pool', 'pair', 'route', 'quote', 'slippage', 'impact',
    'order', 'book', 'depth', 'twap', 'vwap', 'limit', 'market', 'stop', 'take', 'cancel',
    
    # Дополнительные слова
    'tech', 'data', 'api', 'web',
    'edge', 'node', 'mesh', 'grid','graph','ledger',
    'soft', 'hard', 'upgrade', 'patch', 'bug', 'fix', 'test', 'dev', 'prod', 'stage',
    'deploy','audit', 'pentest', 'encrypt', 'decrypt', 'verify',
    'proof', 'work',
    'http', 'rest', 'json', 'xml', 'protobuf',
    
    # Дополнительные популярные слова
    'anon', 'alpha', 'beta', 'gamma', 'sigma', 'omega','dex', 'cex',
    'nft', 'defi', 'gamefi', 'web3', 'metaverse',
    'prod', 'test', 'mainnet', 'testnet',
    'notcoin', 'not','paws', 'memhash', 'arbitrum', 'polygon',
    'fantom', 'avalanche', 'cosmos', 'polkadot', 'kusama', 'cardano', 'solana', 'terra', 'near',
    'flow','harmony', 'icon',
    'waves',
    'audio', 'sex'
    'ocean',
]

def get_similar_variants(word):
    """Генерирует варианты слова с похожими символами"""
    variants = [word]
    for i, char in enumerate(word):
        if char.lower() in SIMILAR_CHARS:
            for similar in SIMILAR_CHARS[char.lower()]:
                new_word = word[:i] + similar + word[i+1:]
                variants.append(new_word)
    return variants

async def generate_wallets(batch_size, highlight_settings, custom_words, console_settings):
    liteserver_TU = LiteserverClient(requests.get('https://ton.org/global-config.json').json())
    
    # Подготовка списков слов с вариантами
    popular_words_with_variants = []
    for word in POPULAR_WORDS:
        popular_words_with_variants.extend(get_similar_variants(word))
    
    custom_words_with_variants = []
    for word in custom_words:
        custom_words_with_variants.extend(get_similar_variants(word))
    
    # Открываем все файлы для записи
    with open("all_wallets.txt", "a") as all_file, \
         open("repeat_wallets.txt", "a") as repeat_file, \
         open("sequence_wallets.txt", "a") as sequence_file, \
         open("popular_wallets.txt", "a") as popular_file, \
         open("custom_wallets.txt", "a") as custom_file:
         
        # Создаем прогресс-бар
        pbar = tqdm(desc="Генерация кошельков", unit=" кош", dynamic_ncols=True)
        
        while True:
            try:
                batch = []
                for _ in range(batch_size):
                    mnemo = mnemonic_new(24)
                    wallet = WalletV5R1.from_mnemonic(liteserver_TU, mnemo)
                    batch.append((wallet, mnemo))
                
                for wallet, mnemo in batch:
                    address = wallet[0].address.to_str(is_bounceable=False)
                    colored_chars = list(address)
                    lower_addr = address.lower()
                    
                    # Флаги для определения типа адреса
                    has_custom = False
                    has_popular = False
                    has_repeat_pair = False
                    has_sequence = False
                    
                    # Игнорируем первые 3 символа при проверке
                    address_to_check = address[3:]
                    lower_addr_to_check = lower_addr[3:]
                    
                    # 1. Проверяем пользовательские слова (КРАСНЫЙ) с вариантами
                    if custom_words_with_variants and highlight_settings['custom_words']:
                        for word in custom_words_with_variants:
                            word_lower = word.lower()
                            idx = lower_addr_to_check.find(word_lower)
                            if idx != -1:
                                actual_idx = idx + 3
                                for j in range(actual_idx, actual_idx+len(word)):
                                    if Fore.RED not in colored_chars[j]:
                                        colored_chars[j] = f"{Fore.RED}{address[j]}{Style.RESET_ALL}"
                                has_custom = True
                    
                    # 2. Проверяем популярные слова (ЗЕЛЕНЫЙ) с вариантами
                    if highlight_settings['popular_words']:
                        for word in popular_words_with_variants:
                            word_lower = word.lower()
                            idx = lower_addr_to_check.find(word_lower)
                            if idx != -1:
                                is_custom = any(
                                    custom_word.lower() in word_lower or 
                                    word_lower in custom_word.lower() 
                                    for custom_word in custom_words_with_variants
                                )
                                if not is_custom:
                                    actual_idx = idx + 3
                                    for j in range(actual_idx, actual_idx+len(word)):
                                        if not any(color in colored_chars[j] for color in [Fore.RED, Fore.YELLOW, Fore.BLUE]):
                                            colored_chars[j] = f"{Fore.GREEN}{address[j]}{Style.RESET_ALL}"
                                    has_popular = True
                    
                    # 3. Проверяем повторяющиеся пары (ЖЕЛТЫЙ)
                    if highlight_settings['repeat_pairs']:
                        for i in range(3, len(address)-3):
                            if address[i] == address[i+2] and address[i+1] == address[i+3]:
                                for j in range(i, i+4):
                                    if not any(color in colored_chars[j] for color in [Fore.RED, Fore.GREEN, Fore.BLUE]):
                                        colored_chars[j] = f"{Fore.YELLOW}{address[j]}{Style.RESET_ALL}"
                                has_repeat_pair = True
                    
                    # 4. Проверяем дубли символов (СИНИЙ)
                    if highlight_settings['duplicates']:
                        for i in range(4, len(address)):
                            if address[i] == address[i-1]:
                                if not any(color in colored_chars[i] for color in [Fore.RED, Fore.GREEN, Fore.YELLOW]):
                                    colored_chars[i-1] = f"{Fore.BLUE}{address[i-1]}{Style.RESET_ALL}"
                                    colored_chars[i] = f"{Fore.BLUE}{address[i]}{Style.RESET_ALL}"
                                has_sequence = True
                    
                    # Сохраняем во все файлы
                    wallet_info = f"{address} {mnemo}\n\n"
                    all_file.write(wallet_info)
                    
                    if has_custom:
                        custom_file.write(wallet_info)
                    if has_popular:
                        popular_file.write(wallet_info)
                    if has_repeat_pair:
                        repeat_file.write(wallet_info)
                    if has_sequence:
                        sequence_file.write(wallet_info)
                    
                    # Вывод в консоль в соответствии с настройками
                    should_print = (
                        (console_settings['all'] and not any([has_custom, has_popular, has_repeat_pair, has_sequence])) or
                        (console_settings['custom'] and has_custom) or
                        (console_settings['popular'] and has_popular) or
                        (console_settings['repeat'] and has_repeat_pair) or
                        (console_settings['sequence'] and has_sequence)
                    )
                    
                    if should_print:
                        colored_address = ''.join(colored_chars)
                        print(f"{colored_address}\n")
                
                # Обновляем прогресс-бар
                pbar.update(batch_size)
                
                # Сбрасываем буферы записи
                all_file.flush()
                repeat_file.flush()
                sequence_file.flush()
                popular_file.flush()
                custom_file.flush()
            
            except Exception as e:
                print(f"Ошибка: {str(e)[:50]}...\n")
                await asyncio.sleep(1)

def get_settings():
    print("Ton wallet generator by @yaklovn/@fatd0g64 fork by @steparikov")
    print("----------------------------------\n")
    
    batch_size = int(input("Сколько кошельков генерировать за пачку? (1-1000): ") or 20)
    batch_size = max(1, min(1000, batch_size))
    
    print("\nВыберите что подсвечивать:")
    highlight_settings = {
        'repeat_pairs': input("Повторяющиеся пары (ABAB)? [y/n]: ").lower() == 'y',
        'popular_words': input("Популярные слова? [y/n]: ").lower() == 'y',
        'duplicates': input("Дубли символов (AA, 11)? [y/n]: ").lower() == 'y',
        'custom_words': True  # Всегда включено, если есть пользовательские слова
    }
    
    custom_input = input("\nВведите свои слова для подсветки (красный), через пробел: ")
    custom_words = [word.strip() for word in custom_input.split() if word.strip()]
    
    print("\nНастройки вывода в консоль:")
    console_settings = {
        'all': input("Выводить все адреса? [y/n]: ").lower() == 'y',
        'custom': input("Выводить адреса с пользовательскими словами? [y/n]: ").lower() == 'y',
        'popular': input("Выводить адреса с популярными словами? [y/n]: ").lower() == 'y',
        'repeat': input("Выводить адреса с повторяющимися парами? [y/n]: ").lower() == 'y',
        'sequence': input("Выводить адреса с дублирующимися символами? [y/n]: ").lower() == 'y'
    }
    
    return batch_size, highlight_settings, custom_words, console_settings

if __name__ == "__main__":
    batch_size, highlight_settings, custom_words, console_settings = get_settings()
    print("\nЗапуск генератора... (Ctrl+C для остановки)\n")
    print(f"Цвета подсветки:")
    print(f"- Пользовательские слова: {Fore.RED}красный{Style.RESET_ALL}")
    print(f"- Популярные слова: {Fore.GREEN}зеленый{Style.RESET_ALL}")
    print(f"- Повторяющиеся пары: {Fore.YELLOW}желтый{Style.RESET_ALL}")
    print(f"- Последовательности: {Fore.BLUE}синий{Style.RESET_ALL}")
    print(f"\nПохожие символы будут учитываться (i/l/1, o/0, s/5 и др.)")
    print(f"\nВаши слова для подсветки: {', '.join(custom_words) or 'нет'}\n")
    asyncio.run(generate_wallets(batch_size, highlight_settings, custom_words, console_settings))