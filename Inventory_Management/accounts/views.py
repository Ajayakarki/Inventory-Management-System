from django.shortcuts import redirect, render
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            print("Account created successfull for ", username)
            messages.success(request, f"Account created successfull for username {username}")
            return redirect('login')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }

    return render(request, 'accounts/register.html', context)

def profile(request):
    return render(request, 'accounts/profile.html')

## Profile update
def profileUpdate(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        user_profile = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and user_profile.is_valid():
            user_form.save()
            user_profile.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        user_profile = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'user_profile': user_profile,
    }


    return render(request, 'accounts/profile_update.html', context)
