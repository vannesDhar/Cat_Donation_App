from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import stripe
from django.conf import settings 
from django.views.decorators.csrf import csrf_exempt 
from django.contrib.auth import login,authenticate,logout
from .forms import *
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseBadRequest
import json

# Create your views here.

def homepage(request):
    if request.user.is_authenticated:
        try:
            user_profile = request.user.profile
        except Profile.DoesNotExist:
            user_profile = None 
    else:
        user_profile = None
    return render(request, 'homepage.html', {'user_profile': user_profile})

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = SignUpForm()
    return render(request, 'signUp.html', {'form': form})

def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('homepage')
    else:
        form = SignInForm()
    return render(request, 'signIn.html', {'form': form})

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_detail(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
    return render(request, 'profile.html', {
        'profile_form': profile_form
    })

def logout_account(request):
    logout(request)
    return redirect('homepage')

def adoption(request):
    if request.method == 'POST':
        form = CatForm(request.POST, request.FILES)
        if form.is_valid():
            catform = form.save(commit=False)
            catform.submitted_by = request.user
            catform.save()
            return redirect('adoption')
    else:
        form = CatForm()
    return render(request, 'adoption.html', {'form': form})

@login_required
def handle_adoption(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cat_id = data.get('cat_id')

            if not cat_id:
                return JsonResponse({'status': 'failed', 'message': 'No cat ID provided'}, status=400)

            cat = Cat.objects.get(id=cat_id)
            user_email = request.user.email
            cat_name = cat.name

            # Send email
            send_adoption_email(user_email, cat_name)
            AdoptionRequest.objects.create(user=request.user, cat=cat)
            cat.in_review = True
            cat.save()
            return JsonResponse({'status': 'success'})

        except Cat.DoesNotExist:
            return JsonResponse({'status': 'failed', 'message': 'Cat not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'failed', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)

def send_adoption_email(user_email, cat_name):
    subject = f"Adoption Request Submitted for {cat_name}"
    message = (
        f"Hello,\n\n"
        f"Thank you for your interest in adopting {cat_name}.\n"
        f"We will review your request and get back to you soon.\n\n"
        f"Best regards,\nUnCollared"
    )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)

@api_view(['GET', 'POST'])
def cat_list(request):
    if request.method == 'GET':
        cats = Cat.objects.all()
        serializer = CatSerializer(cats, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

def community_cat(request):
    if request.method == 'POST':
        form = CommunityCatForm(request.POST, request.FILES)
        if form.is_valid():
            catform = form.save(commit=False)
            catform.reported_by= request.user
            catform.save()
            return redirect('community_cats')
    else:
        form = CommunityCatForm()
    return render(request, 'communityCat.html', {'form': form})


@api_view(['GET'])
def community_cat_list(request):
    cats = CommunityCat.objects.all()
    serializers = CommunityCatSerializer(cats, many=True)
    return Response(serializers.data)

@api_view(['GET'])
def search_community_cat(request):
    query = request.GET.get('q','')
    cats = CommunityCat.objects.filter(name__icontains=query)
    serializers = CommunityCatSerializer(cats,many=True)
    return Response(serializers.data)

@login_required
@api_view(['POST'])
def submit_community_cat(request):
    form = CommunityCatForm(request.POST, request.FILES)
    if form.is_valid():
        community_cat = form.save(commit=False)
        community_cat.reported_by = request.user
        community_cat.save()
        return Response({'status': 'success'}, status=201)
    else:
        return Response(form.errors, status=400)

def render_thread(request):
    return render(request, 'thread.html')



def render_create_thread(request):
    form = ThreadForm()
    return render(request, 'createThread.html', {'form': form})

def render_thread_details(request, thread_id):
    thread = Thread.objects.get(id=thread_id)
    form = CommentForm(request.POST)
    return render(request, 'threadDetails.html', {'form': form, 'thread': thread})

@api_view(['GET'])
def thread_list(request):
    threads = Thread.objects.all().order_by('-created_at')
    serializer = ThreadSerializer(threads, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def thread_detail(request, pk):
    thread = Thread.objects.get(pk=pk)
    serializer = ThreadSerializer(thread)
    return Response(serializer.data)

@api_view(['POST'])
def create_thread(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()
            return Response({'status': 'success'}, status=201)
    else:
        form = ThreadForm()
    return redirect(render_create_thread)

@api_view(['GET'])
def get_comments(request, thread_id):
    thread = Thread.objects.get(id=thread_id)
    comments = Comment.objects.filter(thread=thread)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def create_comment(request, thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        return Response({'error': 'Thread not found'}, status=404)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.thread = thread
        comment.author = request.user
        comment.save()
        return Response({'status': 'success'}, status=201)
    return Response({'error': 'Invalid data'}, status=400)

def donation(request):
	return render(request, 'donation.html')
 
def successView(request):
    amount = request.GET.get('amount')
    context = {
        'total' : amount
    }
    return render(request, 'success.html',context)

@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)
    
    
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Validate and convert amount to cents
        try:
            amount = int(request.POST.get('amount', 0)) * 100  # Convert to cents
            if amount <= 0:
                return HttpResponseBadRequest("Invalid amount.")
        except (ValueError, TypeError):
            return HttpResponseBadRequest("Invalid amount format.")

        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}&amount=' + str(amount / 100),
                cancel_url=domain_url,
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price_data': {
                            'currency': 'sgd',
                            'product_data': {
                                'name': f'{amount / 100}$ Donation',
                            },
                            'unit_amount': amount,
                        },
                        'quantity': 1,
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']}, status=201)
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)

    return HttpResponseBadRequest("Invalid request method.")