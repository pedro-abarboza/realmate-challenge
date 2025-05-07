from django.urls import path
from .views import WebhookView, ConversationDetailView, conversation_detail_template, conversation_list

urlpatterns = [
    # API endpoints
    path('webhook/', WebhookView.as_view(), name='webhook'),
    path('conversations/<uuid:conversation_id>/', ConversationDetailView.as_view(), name='conversation_detail'),
    
    # Frontend templates
    path('', conversation_list, name='conversation_list'),
    path('conversations/<uuid:conversation_id>/view/', conversation_detail_template, name='conversation_detail_template'),
] 