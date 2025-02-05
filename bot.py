import asyncio
from telethon import TelegramClient, events
import re
import time

api_id = 23553289
api_hash = 'a79dd17affd330b2648c0e9a5f9ffde5'
phone_number = '+5533984639798'

client = TelegramClient('session', api_id, api_hash)

def save_approved_card(card):
    with open('lives.txt', 'a') as file:
        file.write(f"{card}\n")

async def check_card(card):
    print(f"Testando: {card}")
    start_time = time.time()
    await client.send_message('@testegatokobot', f'/chk {card}')
    await asyncio.sleep(15)
    messages = await client.get_messages('@testegatokobot', limit=1)
    response = messages[0].message
    if not messages[0].out:
        end_time = time.time()
        elapsed_time = end_time - start_time
        if "Cartão Aprovado!" in response:
            debit_value = re.search(r' Débito: R$\s*(\d+.\d+)', response)
            if debit_value:
                debit_value = debit_value.group(1)
            else:
                debit_value = "Valor não encontrado"
            print(f"Aprovada - {card} Response: Debitou R${debit_value} | Time: {elapsed_time:.2f}s")
            save_approved_card(card)
        elif "Reprovado!" in response:
            print(f"Reprovada - {card} Response: Não Debitou | Time: {elapsed_time:.2f}s")
        elif "Cartão Vencido!" in response:
            print(f"Vencido - {card} Response: {response} | Time: {elapsed_time:.2f}s")
        elif "CVV Inválido!" in response:
            print(f"CVV repetido - {card} Response: {response} | Time: {elapsed_time:.2f}s")
        elif "Cartão inválido!" in response or "Cartão já testado anteriormente" in response:
            print(f"Erro - {card} Response: {response} | Time: {elapsed_time:.2f}s")
        else:
            print(f"Resposta desconhecida - {card} Response: {response} | Time: {elapsed_time:.2f}s")
    else:
        print(f"Timeout - {card} Response: Cartão retestado (sem resposta em 15s) | Time: 15s")

async def main():
    await client.start(phone_number)
    print("Client Created")
    with open('db.txt', 'r') as file:
        cards = file.readlines()
    for card in cards:
        card = card.strip()
        if card:
            await check_card(card)
    await client.disconnect()

asyncio.run(main())in())