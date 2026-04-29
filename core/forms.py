from django import forms


class EWUSignupForm(forms.Form):
    """
    Custom signup form for allauth's ACCOUNT_SIGNUP_FORM_CLASS hook.
    This form is merged INTO allauth's own SignupForm — it's not a
    subclass of it (newer allauth versions require this pattern).
    """
    first_name = forms.CharField(
        max_length=50,
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': 'First name', 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        max_length=50,
        label='Last Name',
        widget=forms.TextInput(attrs={'placeholder': 'Last name', 'autocomplete': 'family-name'})
    )
    role = forms.ChoiceField(
        choices=[
            ('student', 'Student'),
            ('faculty', 'Faculty'),
        ],
        label='I am a',
        widget=forms.Select()
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        label='Department',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Computer Science & Engineering'})
    )
    student_id = forms.CharField(
        max_length=30,
        required=False,
        label='Student / Faculty ID',
        widget=forms.TextInput(attrs={'placeholder': 'Optional'})
    )
    profile_picture = forms.ImageField(
        required=True,
        label='Image of User',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )
    id_card_image = forms.ImageField(
        required=True,
        label='Image of ID Card',
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'})
    )
    whatsapp_number = forms.CharField(
        max_length=20,
        required=True,
        label='WhatsApp Number',
        widget=forms.TextInput(attrs={'placeholder': '+8801XXXXXXXXX'})
    )

    def signup(self, request, user):
        """Called by allauth after the user object is created."""
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.role = self.cleaned_data.get('role', 'student')
        user.department = self.cleaned_data.get('department', '')
        user.student_id = self.cleaned_data.get('student_id', '')
        
        # File Handling
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        if 'id_card_image' in request.FILES:
            user.id_card_image = request.FILES['id_card_image']
            
        user.whatsapp_number = self.cleaned_data.get('whatsapp_number', '')
        user.is_approved = False
        user.save()
