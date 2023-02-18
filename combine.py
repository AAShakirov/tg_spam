import random
import asyncio
import json
import aiohttp
import random

from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.sync import TelegramClient, errors
from telethon.errors.rpcerrorlist import MessageTooLongError, PeerIdInvalidError
from telethon.errors.rpcerrorlist import ChannelPrivateError, UsernameInvalidError

from config import BOT_TOKEN


def start(account_number):
    with open('accounts.json', 'r') as file:
        accounts = json.load(file)
        api_id = accounts['Values'][account_number]['api_id']
        api_hash = accounts['Values'][account_number]['api_hash']
        client = TelegramClient('session_name',
                        api_id,
                        api_hash)
        return client
    # client.start()

async def join_channel(client, count_start):
    with open('chats.txt', 'r') as file:
        global count_join, count_none
        coefficient = 1
        for i in range(411):
            group = file.readline().split('\n')[0]
            if i < count_start: continue
            async with client:
                try:
                    await client(JoinChannelRequest(channel=group))
                    count_join += 1
                    print(f'Подключен [{group}]')
                    print(f'Добавлено чатов: {count_join}')
                    print(f'Отсутствует чатов: {count_none}')
                except ValueError:
                    count_none += 1
                    print(f'Отсутствует [{group}]')
                    print(f'Добавлено чатов: {count_join}')
                    print(f'Отсутствует чатов: {count_none}')
                except ChannelPrivateError:
                    print('Channel is private')
                except UsernameInvalidError:
                    print(f'Nobody is using {group}')
                except Exception as e:
                    print(f'Ошибка в join_channel: {e}')
                with open('count_start.txt', 'w') as file:
                    file.write(str(count_start))
                delay = random.randint(60, 120) * coefficient
                print(f'[-] sleep {delay}')
                await asyncio.sleep(delay)
            if i <= 10:
                coefficient += i / 10

def dialog_sort(dialog):
    # Сортирует диалоги по непрочитанным
    return dialog.unread_count

async def create_groups_list(groups=[]):
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            if dialog.unread_count >= 1:
                groups.append(dialog)
    return groups

async def spammer(client):
    global count_sent
    global all_chats
    k = 0

    coefficient = 1

    task_1 = asyncio.create_task(join_channel(client, count_start=count_start))
    task_2 = asyncio.create_task(send_message())

    async with client:
        count = 0
        while True:
            async for message in client.iter_messages('me', limit=2):
                groups = await asyncio.gather(create_groups_list())
                all_chats = len(groups[0])
                print(f'Подключено чатов: {all_chats}')
                groups[0].sort(key=dialog_sort, reverse=True)
                for group in groups[0]:
                    try:
                        await client.forward_messages(group, message, 'me')
                        k = k + 1
                    except errors.ForbiddenError as o:
                        await client.delete_dialog(group)
                        if group.entity.username != None:
                            print(f'Error: {o.message} Аккаунт покинул {group.entity.username}')
                        else:
                            print(f'Error: {o.message} Аккаунт покинул {group.name}')
                    except errors.FloodError as e:
                        print(f'Error: {e.message} Требуется ожидание {e.seconds} секунд')
                        await asyncio.sleep(e.seconds + 60)
                    except PeerIdInvalidError:
                        await client.delete_dialog(group)
                    except MessageTooLongError:
                        print(f'Message was too long ==> {group.name}')
                    except errors.BadRequestError as i:
                        print(f'Error: {i.message}')
                    except errors.RPCError as a:
                        print(f'Error: {a.message}')
                    except Exception as e:
                        print(f'При отправке сообщения в {group.name} возникло исключение: {e}')
                    delay = random.randint(60, 180) * coefficient
                    print(f'[-{group.name}-] sleep {delay}')
                    await asyncio.sleep(delay)
                count_sent= k + count_sent
                k = 0
                delay = random.randint(60, 180) * coefficient
                print(f'[+{count_sent}+] сообщений отправлено')
                print(f'sleep {delay}')
                await asyncio.sleep(delay)
                groups[0].clear()
                # await task_2
                # await task_1
            if count <= 10:
                count += 1
                coefficient = coefficient + count / 10
            # task_2 = asyncio.create_task(send_message())

async def send_message():
    emojis = ('✉️','📩','📨','📧','📪','📫','📬','📭','📮','📜','📃','📄','📑','🧾')
    while True:
        global count_sent, count_join, count_none, all_chats
        emoji = random.choice(emojis)
        message = f'{emoji} Статистика рассылки \n' \
            f'Отправлено сообщений: {count_sent} \n' \
            f'Добавлено чатов: {count_join} \n' \
            f'Отсутствует чатов: {count_none} \n' \
            f'Всего чатов: {all_chats} \n'
        for chat_id in (391421988, 1149861352):
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, data={"chat_id": chat_id, "text": message}) as response:
                        if response.status == 200:
                            print(f'Сообщение в диалог {chat_id} отправлено')
            except Exception as e:
                print('Не удалось отправить сообщение в телеграм. ', e)
        await asyncio.sleep((60 - datetime.now().minute) * 60)

if __name__ == '__main__':
    with open('count_start.txt', 'r') as file:
        count_start = int(file.read())
    account_number = 1
    client = start(account_number)
    count_sent, count_join, count_none, all_chats = 0, 0, 0, 0
    asyncio.run(spammer(client))
