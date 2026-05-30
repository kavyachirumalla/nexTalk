from django.contrib import messages
from urllib import request
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Room, Message
from django.contrib.auth.models import User
# Create your views here.
@login_required
def roomlist_view(request):
    rooms = Room.objects.filter(users=request.user)
    return render(request, 'chat/room_list.html', {'rooms': rooms})
@login_required
def room_view(request, room_name):
    room=get_object_or_404(Room, name=room_name)

    if request.user not in room.users.all():
        raise Http404("You are not a member of this room.")
    if request.method == 'POST':
        content = request.POST.get('message')
        if content and content.strip():
         Message.objects.create(room=room,sender=request.user, content=content)
        return redirect('room', room_name=room_name)
    messages = Message.objects.filter(room=room).order_by('created_at')
    return render(request, 'chat/room.html', {'room_name': room_name, 'messages': messages})
@login_required
def create_room(request):
   users=User.objects.exclude(id=request.user.id)
   if request.method == 'POST':
      room_name=request.POST.get("room_name","").strip()
      if not room_name:
         messages.error(request,"Room name cannot be empty.")
         return redirect('create_room')
      if Room.objects.filter(name=room_name).exists():
         messages.error(request,"Room name already exists. Please choose a different name.")
         return redirect('create_room')
      selected_users=request.POST.getlist("users")
      if len(selected_users)==0:
         messages.error(request,"Please select at least one user to create a room.")
         return redirect('create_room')
      selected_users=request.POST.getlist("users")

      room=Room.objects.create(name=room_name)
      room.users.add(request.user)
      for user_id in selected_users:
         user=User.objects.get(id=user_id)
         room.users.add(user)
      return redirect("room_list")
   return render(request,"chat/create_room.html",{"users":users})
@login_required
def delete_message(request,message_id):
   message=get_object_or_404(Message,id=message_id)
   if message.sender!=request.user:
      raise Http404("You are not authorized to delete this message.")
   room_name=message.room.name
   message.delete()
   return redirect("room",room_name=room_name)  
@login_required
def upload_file(request, room_name):
    if request.method == 'POST': 
        room = get_object_or_404(Room, name=room_name)
        if request.user not in room.users.all():
            raise Http404("You are not a member of this room.")
        uploaded_file = request.FILES.get('file')
        msg= Message(room=room, sender=request.user, content=request.POST.get("message", ""))
        if uploaded_file:
            if uploaded_file.content_type.startswith('image/'):
                msg.image = uploaded_file
            else:
                msg.file = uploaded_file
        msg.save()
    return redirect('room', room_name=room_name)

      
