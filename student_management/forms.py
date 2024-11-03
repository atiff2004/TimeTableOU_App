from django import forms
from .models import FYP, Student

class FYPForm(forms.ModelForm):
    # Filter students to exclude any who are already in an FYP group
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(fyp__isnull=True),  # Ensure only students without an FYP are shown
        widget=forms.CheckboxSelectMultiple,
        label="Select Students (Max 3)"
    )

    class Meta:
        model = FYP
        fields = ['group_name', 'students', 'title', 'supervisor', 'deadline']

    def __init__(self, *args, **kwargs):
        super(FYPForm, self).__init__(*args, **kwargs)
        # Set placeholders and types for form fields for user guidance
        self.fields['group_name'].widget.attrs.update({'placeholder': 'Enter group name'})
        self.fields['title'].widget.attrs.update({'placeholder': 'Enter project title'})
        self.fields['deadline'].widget = forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'})

    def clean_students(self):
        students = self.cleaned_data.get('students')
        if students.count() > 3:
            raise forms.ValidationError("You can only select a maximum of 3 students for a group.")
        return students
class FYPFormedit(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.filter(fyp__isnull=True),
        widget=forms.CheckboxSelectMultiple,
        label="Edit Group Members (Max 3)"
    )
    deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    submission_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = FYP
        fields = ['group_name', 'students', 'title', 'supervisor', 'deadline', 'submission_date', 'status']

    def clean_students(self):
        students = self.cleaned_data.get('students')
        if students.count() > 3:
            raise forms.ValidationError("You can only select a maximum of 3 students for a group.")
        return students
