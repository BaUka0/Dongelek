import uuid
import json
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.contrib import messages

from .models import ChatbotIntent, ChatSession, ChatMessage
from .nltk_utils import match_intent

# Default chatbot settings
INTELLIGENCE_API_URL = getattr(settings, 'INTELLIGENCE_API_URL', "https://api.intelligence.io.solutions/api/v1/chat/completions")
INTELLIGENCE_MODEL_NAME = getattr(settings, 'INTELLIGENCE_MODEL_NAME', "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8")
IOINTELLIGENCE_API_KEY = getattr(settings, 'IOINTELLIGENCE_API_KEY', "")
CHATBOT_SYSTEM_PROMPT = getattr(settings, 'CHATBOT_SYSTEM_PROMPT', "You are Dongelek Assistant, an AI helper for a car marketplace in Kazakhstan. Provide helpful, concise answers about car buying, selling, and features on the Dongelek platform. Be friendly and informative.")
CHATBOT_HISTORY_LENGTH = getattr(settings, 'CHATBOT_HISTORY_LENGTH', 10)
CHATBOT_MAX_TOKENS = getattr(settings, 'CHATBOT_MAX_TOKENS', 1024)
USE_ADVANCED_AI = getattr(settings, 'USE_ADVANCED_AI', False)

def get_default_responses():
    """Get default responses for common scenarios"""
    return {
        'greeting': "Здравствуйте! Я — Dongelek AI Assistant. Чем могу помочь вам в поиске идеального автомобиля сегодня?",
        'fallback': "Извините, я не понял ваш запрос. Пожалуйста, переформулируйте вопрос или спросите о списках автомобилей, их характеристиках или о продаже авто.",
        'thanks': "Пожалуйста! Могу ли я ещё чем-то помочь?",
        'goodbye': "Спасибо за общение! Возвращайтесь, если появятся вопросы по автомобилям.",
    }

def get_chat_history(session, max_history=CHATBOT_HISTORY_LENGTH):
    """Get formatted chat history for AI integration"""
    messages = session.messages.all().order_by('-created_at')[:max_history]
    messages = reversed(list(messages))  # Reverse to get chronological order
    
    history = []
    for msg in messages:
        history.append({"role": "user", "content": msg.user_message})
        history.append({"role": "assistant", "content": msg.bot_response})
    
    return history

def get_advanced_ai_response(user_message, session):
    """Get response from io.net AI API"""
    if not IOINTELLIGENCE_API_KEY:
        return None, "Advanced AI is not configured. Please set up your API key."
    
    # Get chat history for context
    history = get_chat_history(session)
    
    # Prepare messages for the API call
    messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}]
    
    # Add history if available
    if history:
        messages.extend(history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = requests.post(
            INTELLIGENCE_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {IOINTELLIGENCE_API_KEY}"
            },
            json={
                "model": INTELLIGENCE_MODEL_NAME,
                "messages": messages,
                "max_tokens": CHATBOT_MAX_TOKENS
            },
            timeout=15  # 15 seconds timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            return ai_response, None
        else:
            error_msg = f"Error: API returned status {response.status_code}"
            return None, error_msg
    
    except Exception as e:
        error_msg = f"Error connecting to AI service: {str(e)}"
        return None, error_msg

@require_POST
@csrf_exempt
def chatbot_api(request):
    """API endpoint for chatbot interactions"""
    user_message = request.POST.get('message', '').strip()
    session_id = request.POST.get('session_id', None)
    use_advanced_ai = request.POST.get('use_advanced_ai') == 'true'
    
    # Create or get session
    if not session_id:
        session_id = str(uuid.uuid4())
        if request.user.is_authenticated:
            session = ChatSession.objects.create(session_id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(session_id=session_id)
    else:
        try:
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            session = ChatSession.objects.create(session_id=session_id)
            if request.user.is_authenticated:
                session.user = request.user
                session.save()
    
    # Process user message
    if not user_message:
        return JsonResponse({
            'response': "Hello! How can I help you find your perfect car today?",
            'session_id': session_id
        })
    
    # Check if we should use advanced AI
    if use_advanced_ai:
        ai_response, error = get_advanced_ai_response(user_message, session)
        
        if ai_response:
            # Save the message and AI response
            ChatMessage.objects.create(
                session=session,
                user_message=user_message,
                bot_response=ai_response
            )
            
            return JsonResponse({
                'response': ai_response,
                'session_id': session_id
            })
        else:
            # Fallback to basic bot if there's an error with AI
            response = f"Sorry, I couldn't connect to my advanced brain. Let me answer with my basic knowledge: {error}"
    
    # If not using advanced AI or if there was an error, use basic NLTK
    # Get all intents from database
    intents = ChatbotIntent.objects.all()
    
    # Match intent
    matched_intent = match_intent(user_message, intents)
    
    # Prepare response
    default_responses = get_default_responses()
    
    if matched_intent:
        response = matched_intent.response
    elif any(word in user_message.lower() for word in ['hello', 'hi', 'hey']):
        response = default_responses['greeting']
    elif any(word in user_message.lower() for word in ['thank', 'thanks']):
        response = default_responses['thanks']
    elif any(word in user_message.lower() for word in ['bye', 'goodbye']):
        response = default_responses['goodbye']
    else:
        response = default_responses['fallback']
    
    # Save the message
    ChatMessage.objects.create(
        session=session,
        user_message=user_message,
        bot_response=response,
        intent=matched_intent
    )
    
    return JsonResponse({
        'response': response,
        'session_id': session_id
    })

def chatbot_widget(request):
    """View for rendering the chatbot widget"""
    use_advanced_ai = getattr(settings, 'USE_ADVANCED_AI', False)
    return render(request, 'chatbot/widget.html', {
        'use_advanced_ai': use_advanced_ai
    })

@login_required
def chatbot_history(request):
    """View for displaying chat history"""
    user_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    
    return render(request, 'chatbot/history.html', {
        'user_sessions': user_sessions
    })

@login_required
def delete_chat_session(request, session_id):
    """View to delete a chat session"""
    session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)
    session.delete()
    messages.success(request, "Chat session deleted successfully.")
    return redirect(reverse('chatbot_history'))

@login_required
def clear_chat_history(request):
    """View to delete all chat sessions for a user"""
    ChatSession.objects.filter(user=request.user).delete()
    messages.success(request, "All chat history deleted successfully.")
    return redirect(reverse('chatbot_history'))

def toggle_ai_mode(request):
    """AJAX endpoint to toggle Advanced AI mode"""
    if request.method == 'POST' and request.is_ajax():
        new_state = request.POST.get('use_advanced_ai') == 'true'
        # In a real application, you would save this to the user's preferences
        # Here we just return the new state
        return JsonResponse({'success': True, 'using_advanced_ai': new_state})
    return JsonResponse({'success': False}, status=400)
