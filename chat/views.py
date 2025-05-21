from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Max, F
from .models import Conversation, Message
from cars.models import Car
from accounts.models import User


@login_required
def inbox(request):
    # Get all conversations for the current user (as either buyer or seller)
    conversations = Conversation.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).annotate(
        # Fix: Using ~Q to create "not equals" condition instead of 'ne' lookup
        unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)),
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    return render(request, 'chat/inbox.html', {'conversations': conversations})


@login_required
def conversation_detail(request, conversation_id):
    # Get conversation and verify the user is either buyer or seller
    conversation = get_object_or_404(
        Conversation,
        Q(buyer=request.user) | Q(seller=request.user),
        id=conversation_id
    )

    # Mark messages as read if they were sent by the other user
    if request.user == conversation.buyer:
        other_user = conversation.seller
        Message.objects.filter(
            conversation=conversation,
            sender=other_user,
            is_read=False
        ).update(is_read=True)
    else:
        other_user = conversation.buyer
        Message.objects.filter(
            conversation=conversation,
            sender=other_user,
            is_read=False
        ).update(is_read=True)

    # Get all messages in the conversation
    messages = conversation.messages.all()

    return render(request, 'chat/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user
    })


@login_required
def start_conversation(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Check if user is not trying to message themselves
    if request.user == car.seller:
        return redirect('car_detail', slug=car.slug)

    # Check if conversation already exists
    conversation = Conversation.objects.filter(
        car=car,
        buyer=request.user,
        seller=car.seller
    ).first()

    if not conversation:
        # Create new conversation
        conversation = Conversation.objects.create(
            car=car,
            buyer=request.user,
            seller=car.seller
        )

    # If this is a POST request, add the message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            # Update the conversation's updated_at field
            conversation.updated_at = timezone.now()
            conversation.save()

        # Check if this request is AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})

    return redirect('conversation_detail', conversation_id=conversation.id)


@login_required
def send_message(request, conversation_id):
    if request.method == 'POST':
        conversation = get_object_or_404(
            Conversation,
            Q(buyer=request.user) | Q(seller=request.user),
            id=conversation_id
        )

        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )

            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()

            # Return JSON response for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message_id': message.id,
                    'timestamp': message.created_at.strftime('%H:%M'),
                    'sender_name': request.user.username,
                    'conversation_id': conversation.id,
                    'car_name': f"{conversation.car.make} {conversation.car.model}"
                })
            
            # Redirect for non-AJAX requests
            return redirect('conversation_detail', conversation_id=conversation.id)

    # Return error for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
    # Redirect for non-AJAX requests
    return redirect('conversation_detail', conversation_id=conversation_id)


@login_required
def check_new_messages(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Fix: Using ~Q to create "not equals" condition instead of 'ne' lookup
        unread_count = Message.objects.filter(
            conversation__in=Conversation.objects.filter(
                Q(buyer=request.user) | Q(seller=request.user)
            ),
            is_read=False
        ).exclude(sender=request.user).count()

        return JsonResponse({
            'unread_count': unread_count
        })

    return JsonResponse({'status': 'error'}, status=400)