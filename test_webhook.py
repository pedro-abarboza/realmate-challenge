#!/usr/bin/env python
import requests
import json
import uuid
from datetime import datetime, timedelta
import time

# URL base para os webhooks
BASE_URL = "http://localhost:8000/webhook/"

# Função para gerar um timestamp
def get_timestamp(seconds_offset=0):
    dt = datetime.now() + timedelta(seconds=seconds_offset)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")

# Função para enviar um evento para o webhook
def send_webhook_event(event_data):
    response = requests.post(BASE_URL, json=event_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def main():
    # Gerar um ID único para a conversa
    conversation_id = str(uuid.uuid4())
    print(f"ID da conversa gerada: {conversation_id}")
    
    # 1. Criar uma nova conversa
    new_conversation_event = {
        "type": "NEW_CONVERSATION",
        "timestamp": get_timestamp(),
        "data": {
            "id": conversation_id
        }
    }
    print("\n1. Enviando evento de nova conversa...")
    send_webhook_event(new_conversation_event)
    
    # Aguardar um segundo
    time.sleep(1)
    
    # 2. Adicionar uma mensagem recebida
    message_received_event = {
        "type": "NEW_MESSAGE",
        "timestamp": get_timestamp(1),
        "data": {
            "id": str(uuid.uuid4()),
            "direction": "RECEIVED",
            "content": "Olá, tudo bem?",
            "conversation_id": conversation_id
        }
    }
    print("\n2. Enviando evento de mensagem recebida...")
    send_webhook_event(message_received_event)
    
    # Aguardar um segundo
    time.sleep(1)
    
    # 3. Adicionar uma mensagem enviada
    message_sent_event = {
        "type": "NEW_MESSAGE",
        "timestamp": get_timestamp(2),
        "data": {
            "id": str(uuid.uuid4()),
            "direction": "SENT",
            "content": "Tudo ótimo e você?",
            "conversation_id": conversation_id
        }
    }
    print("\n3. Enviando evento de mensagem enviada...")
    send_webhook_event(message_sent_event)
    
    # Aguardar um segundo
    time.sleep(1)
    
    # 4. Fechar a conversa
    close_conversation_event = {
        "type": "CLOSE_CONVERSATION",
        "timestamp": get_timestamp(3),
        "data": {
            "id": conversation_id
        }
    }
    print("\n4. Enviando evento de fechamento de conversa...")
    send_webhook_event(close_conversation_event)
    
    # 5. Tentar adicionar uma mensagem a uma conversa fechada (deve falhar)
    failed_message_event = {
        "type": "NEW_MESSAGE",
        "timestamp": get_timestamp(4),
        "data": {
            "id": str(uuid.uuid4()),
            "direction": "RECEIVED",
            "content": "Esta mensagem não deve ser adicionada porque a conversa está fechada.",
            "conversation_id": conversation_id
        }
    }
    print("\n5. Tentando enviar mensagem para uma conversa fechada (deve falhar)...")
    send_webhook_event(failed_message_event)
    
    print(f"\nURL para visualizar a conversa: http://localhost:8000/conversations/{conversation_id}/view/")
    print(f"URL da API para a conversa: http://localhost:8000/conversations/{conversation_id}/")

if __name__ == "__main__":
    main() 