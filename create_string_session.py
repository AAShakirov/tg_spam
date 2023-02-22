import json
import python_socks
from typing import Literal, Generator
from telethon import TelegramClient
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from exceptions import CantGetProxyType

def get_proxy(index: int = 0) -> dict[Literal['hostname', 'port'], str | int]:
    with open('proxy_list.txt', 'r') as file:
        proxy_list = file.readlines()
    ip: str = proxy_list[index].split(';')[0]
    port = int(proxy_list[index].split(';')[1])
    protocol: str = proxy_list[index].split(';')[2].split('\n')[0]
    if protocol == 'SOCKS4':
        proxy_type = python_socks.ProxyType.SOCKS4
    elif protocol == 'SOCKS5':
        proxy_type = python_socks.ProxyType.SOCKS5
    else:
        raise CantGetProxyType('Error in determining the proxy type', f'It may be SOCKS4 or SOCKS5 only. Not {protocol}')
    proxy = (proxy_type, ip, port)
    return proxy

def get_accounts() -> dict[Literal['Values'], list[dict, ]]:
    with open('accounts.json', 'r') as file:
        accounts = json.load(file)
    return accounts

def get_client(account_number: int) -> TelegramClient:
    accounts = get_accounts()
    api_id: int = accounts['Values'][account_number]['api_id']
    api_hash: str = accounts['Values'][account_number]['api_hash']
    # string: str = accounts['Values'][account_number]['string']
    # session = StringSession(string)
    proxy = get_proxy()
    client = TelegramClient(StringSession(), api_id=api_id, api_hash=api_hash, proxy=proxy)
    return client

def change_accounts(account_number: int) -> None:
    client = get_client(account_number)
    accounts = get_accounts()
    with client:
        string = client.session.save()
    for account in accounts['Values']:
        if account['api_id'] == client.api_id:
            account['string'] = string
    write_string_session_json(accounts)

def write_string_session_json(accounts: dict[Literal['Values'], list[dict, ]]) -> None:
    with open('accounts.json', 'w') as file:
        accounts = json.dumps(accounts)
        accounts = json.loads(str(accounts))
        json.dump(accounts, file, indent = 4)

def choice_the_account() -> Generator:
    accounts = get_accounts()
    account_number = 0
    for account in accounts['Values']:
        if account['phone'] == '+7 952 225 4258': break
        if 'string' not in account.keys():
            phone = account['phone']
            print(f'account: {account_number}; phone: {phone}')
            yield account_number
        account_number += 1

def change_select_account():
    account_numbers = choice_the_account()
    for account_number in account_numbers:
        change_accounts(account_number)

if __name__ == '__main__':
    change_select_account()
