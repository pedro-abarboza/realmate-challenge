from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import Conversation, Message
from .serializers import ConversationSerializer

# Create your views here.

class WebhookView(APIView):
    def post(self, request):
        try:
            event_type = request.data.get('type')
            timestamp = request.data.get('timestamp')
            data = request.data.get('data')
            
            if not all([event_type, timestamp, data]):
                return Response(
                    {'error': 'Dados incompletos no webhook'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Processar evento de nova conversa
            if event_type == 'NEW_CONVERSATION':
                try:    
                    conversation_id = data.get('id')
                except Exception as e:
                    return Response(
                        {'error': f'Erro ao processar webhook: Falha na identificação do ID da conversa'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Verificar se a conversa já existe
                if Conversation.objects.filter(id=conversation_id).exists():
                    return Response(
                        {'error': 'Conversa já existe'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Criar nova conversa
                conversation = Conversation.objects.create(
                    id=conversation_id,
                    status='OPEN'
                )
                
                return Response(
                    {'message': 'Conversa criada com sucesso'},
                    status=status.HTTP_201_CREATED
                )
            
            # Processar evento de nova mensagem
            elif event_type == 'NEW_MESSAGE':
                with transaction.atomic():
                    message_id = data.get('id')
                    conversation_id = data.get('conversation_id')
                    direction = data.get('direction')
                    content = data.get('content')
                    
                    # Verificar se todos os campos necessários estão presentes
                    if not all([message_id, conversation_id, direction, content]):
                        return Response(
                            {'error': 'Dados incompletos para criação de mensagem'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Verificar se a mensagem já existe
                    if Message.objects.filter(id=message_id).exists():
                        return Response(
                            {'error': 'Mensagem já existe'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Verificar se a conversa existe
                    try:
                        conversation = Conversation.objects.get(id=conversation_id)
                    except Conversation.DoesNotExist:
                        return Response(
                            {'error': 'Conversa não encontrada'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    
                    # Verificar se a conversa está fechada
                    if conversation.status == 'CLOSED':
                        return Response(
                            {'error': 'Não é possível adicionar mensagens a uma conversa fechada'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Criar nova mensagem
                    Message.objects.create(
                        id=message_id,
                        conversation=conversation,
                        direction=direction,
                        content=content,
                        timestamp=timestamp or timezone.now()
                    )
                    
                    conversation.save()  # Atualiza o timestamp updated_at
                    
                    return Response(
                        {'message': 'Mensagem criada com sucesso'},
                        status=status.HTTP_201_CREATED
                    )
            
            # Processar evento de fechamento de conversa
            elif event_type == 'CLOSE_CONVERSATION':
                conversation_id = data.get('id')
                
                # Verificar se a conversa existe
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    return Response(
                        {'error': 'Conversa não encontrada'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Atualizar status da conversa
                conversation.status = 'CLOSED'
                conversation.save()
                
                return Response(
                    {'message': 'Conversa fechada com sucesso'},
                    status=status.HTTP_200_OK
                )
            
            # Tipo de evento desconhecido
            else:
                return Response(
                    {'error': f'Tipo de evento desconhecido: {event_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {'error': f'Erro ao processar webhook: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ConversationDetailView(APIView):
    def get(self, request, conversation_id):
        try:
            conversation = get_object_or_404(Conversation, id=conversation_id)
            serializer = ConversationSerializer(conversation)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erro ao obter conversa: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# View para renderização do template HTML
def conversation_detail_template(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    return render(request, 'conversations/conversation_detail.html', {
        'conversation': conversation
    })


# View para listar todas as conversas (para o frontend)
def conversation_list(request):
    conversations = Conversation.objects.all()
    return render(request, 'conversations/conversation_list.html', {
        'conversations': conversations
    })
