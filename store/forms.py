from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail

# class UserRegistrationForm(UserCreationForm):
#     print("***********************UserRegistrationForm**************************")
#     email = forms.EmailField()
#
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         self.fields['first_name'].widget.attrs['class'] = 'form-control'
#         self.fields['last_name'].widget.attrs['class'] = 'form-control'
#         self.fields['email'].widget.attrs['class'] = 'form-control'
#
#     def save(self, commit=True):
#         user = super(UserRegistrationForm, self).save(commit=False)
#         user.username = self.cleaned_data['email']
#         user.email = self.cleaned_data['email']
#
#         # Generate a random one-time password (OTP)
#         otp = str(random.randint(111111, 999999))
#
#         # Save the user object without setting the password
#         if commit:
#             user.save()
#
#             # Send the OTP to the user's email
#             send_mail(
#                 subject='One-Time Password (OTP)',
#                 message=f'Your OTP for registration: {otp}',
#                 from_email='your@example.com',  # Replace with your email
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )
#
#         return user




class UserLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLogin, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label="Email*")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))



class AdminLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AdminLogin, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email'}),
        label="Email*")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control form-control-lg', 'placeholder': 'Password'}))



from .models import Order
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'pincode']








    """
    
    
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
</head>
<body>

<div class="container" style="width:40%;margin-top:10%;border:2px solid black;border-radius:5px; padding:40px">
  <h3>SignIn</h3>
  {%if username%}
  <form method="post" action="{% url 'signin' %}">
    {% csrf_token %}
  <div class="form-outline mb-4">
    <label class="form-label">*Email</label>
    <input name="username" id="username" type="email" class="form-control" value="{{username}}" required>
  </div>


  <div class="form-outline mb-4">
    <label class="form-label">Password</label>
    <input name="password" id="password" type="password" class="form-control" >
  </div>


  <div class="row mb-4" style="text-align:center">
    <div class="col d-flex justify-content-center">
      <button type="submit" class="btn btn-primary btn-block mb-4">Sign in</button>

    </div>

    <div class="col">
      <!-- Simple link -->
<!--      <a href="#!">Forgot password?</a>-->
    </div>
  </div>
  <div class="text-center">
    <p>Don't have an account? <a href="/register">Register</a></p>
  </div>
</form>
  {%else%}
    <form method="post" action="{% url 'login' %}">
    {% csrf_token %}
  <div class="form-outline mb-4">
    <label class="form-label">*Email</label>
    <input name="username" id="username_1" type="email" class="form-control"  required>
  </div>


<!--  <div class="form-outline mb-4">-->
<!--    <label class="form-label">Password</label>-->
<!--    <input name="password" id="password_1" type="password" class="form-control" >-->
<!--  </div>-->


  <div class="row mb-4" style="text-align:center">
    <div class="col d-flex justify-content-center">
      <button type="submit" class="btn btn-primary btn-block mb-4">Request OTP</button>

    </div>

    <div class="col">
      <!-- Simple link -->
<!--      <a href="#!">Forgot password?</a>-->
    </div>
  </div>
  <div class="text-center">
    <p>Don't have an account? <a href="/register">Register</a></p>
  </div>
<div class="countdown" id="countdown"></div>
<a href="your-link.html" id="link" class="hidden">Send OTP Again</a>
</form>

  {%endif%}
  {%for message in messages%}
  {{message}}
  {%endfor%}

</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" integrity="sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz" crossorigin="anonymous"></script>


</body>

<style>
  body {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
  font-family: Arial, sans-serif;
}

.countdown-container {
  text-align: center;
}

.countdown {
  font-size: 48px;
  font-weight: bold;
}

.hidden {
  display: none;
}

</style>
{% if username %}
<script>
  document.addEventListener("DOMContentLoaded", function() {
  // Set the countdown duration in minutes
  const countdownDuration = 1;

  // Calculate the target date and time for the countdown
  const targetDate = new Date().getTime() + countdownDuration * 60 * 1000;

  // Update the countdown every second
  const countdownInterval = setInterval(function() {
    const now = new Date().getTime();
    const timeLeft = targetDate - now;

    // Calculate the minutes and seconds left
    const minutes = Math.floor(timeLeft / (1000 * 60));
    const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

    // Display the countdown in the element with id="countdown"
    document.getElementById("countdown").innerHTML = formatTime(minutes, seconds);

    // If the countdown is finished, display the link and clear the interval
    if (timeLeft < 0) {
      document.getElementById("countdown").innerHTML = "EXPIRED";
      document.getElementById("link").classList.remove("hidden");
      clearInterval(countdownInterval);
    }
  }, 1000);

  // Function to format time as "mm:ss"
  function formatTime(minutes, seconds) {
    return `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }
});
</script>
{%endif%}
</html>
    
    """


from paypal.standard.forms import PayPalPaymentsForm

class CustomPayPalPaymentsForm(PayPalPaymentsForm):

    def get_html_submit_element(self):
        return """<button type="submit">Continue on PayPal website</button>"""