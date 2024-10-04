from django import forms
from .models import Course,Shift,Class, CourseOffering, Teacher, Room, Timeslot, Day, Schedule, CourseAssignment, Department, Semester
from django_select2.forms import ModelSelect2Widget
from .models import Shift

class AddShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ['name']  # Ensure 'name' is the field representing the shift
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. M'}),
        }
class addday(forms.ModelForm):
    class Meta:
        model = Day
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: Monday'})
        }

class addroom(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: ABIII-G01'})
        }



class addslot(forms.ModelForm):
    class Meta:
        model = Timeslot
        fields = ['slot', 'shift']

    def __init__(self, *args, **kwargs):
        super(addslot, self).__init__(*args, **kwargs)

        # Fetch shifts and modify their display values
        self.fields['shift'].queryset = Shift.objects.all()
        self.fields['shift'].label_from_instance = lambda obj: 'Morning' if obj.name == 'M' else 'Evening' if obj.name == 'E' else obj.name

        # Set default value to "Morning" by default (Shift 'M')
        try:
            self.fields['shift'].initial = Shift.objects.get(name='M').id  # Assuming 'M' is in the database
        except Shift.DoesNotExist:
            pass

        # Remove the '-------' option by making the field required and removing the empty label
        self.fields['shift'].empty_label = None  # This removes the '-------' line

        # Slot field customization
        self.fields['slot'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: 08:30-10:00'})


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class ClassForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        label="Select Department",
        empty_label="Select Department",  # Set the default text here
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(),
        label="Select Semester",
        empty_label="Select Semester",  # Set the default text here
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.CharField(
        max_length=10,
        help_text="Enter section, e.g: 'M', 'E'",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: M'})
    )

    class Meta:
        model = Class
        fields = ['department', 'semester', 'name', 'section']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g: BSSE'})
        }

        

class CourseOfferingForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=ModelSelect2Widget(
            model=Course,
            search_fields=['full_name__icontains'],
            attrs={'data-placeholder': 'Select a course', 'data-allow-clear': 'true'}
        )
    )
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    semesters = forms.ModelMultipleChoiceField(
        queryset=Semester.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        departments = cleaned_data.get('departments')
        semesters = cleaned_data.get('semesters')

        if not course:
            self.add_error('course', "Please select a course.")

        if not departments:
            self.add_error('departments', "Please select at least one department.")

        if not semesters:
            self.add_error('semesters', "Please select at least one semester.")

        for department in departments:
            for semester in semesters:
                if CourseOffering.objects.filter(course=course, department=department, semester=semester).exists():
                    self.add_error(None, f"The course '{course}' is already offered in {department} for {semester}.")
                    break

        return cleaned_data

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'short_name', 'full_name', 'credit_hours', 'lab_crh', 'pre_req', 'category']
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CS101'}),
            'short_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ML'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Machine Learning'}),
            'credit_hours': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '3'}),
            'lab_crh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1'}),  # New field for lab credit hours
            'pre_req': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PF for OOP'}),  # New field for prerequisites
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Core/Elective'})
        }

class CourseAssignmentForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    class_assigned = forms.ModelChoiceField(queryset=Class.objects.none(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    courses = forms.ModelMultipleChoiceField(queryset=Course.objects.none(), widget=forms.CheckboxSelectMultiple, required=True)

    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        semester_id = kwargs.pop('semester_id', None)
        super().__init__(*args, **kwargs)

        if department_id and semester_id:
            self.fields['class_assigned'].queryset = Class.objects.filter(
                department_id=department_id,
                semester_id=semester_id
            ).order_by('name')

            self.fields['courses'].queryset = Course.objects.filter(
                courseoffering__department_id=department_id,
                courseoffering__semester_id=semester_id
            ).distinct().order_by('full_name')

class TeacherAssignmentForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    course_assignment = forms.ModelChoiceField(queryset=CourseAssignment.objects.none(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    teacher = forms.ModelChoiceField(queryset=Teacher.objects.all(), required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'department' in self.data and 'semester' in self.data:
            try:
                department_id = int(self.data.get('department'))
                semester_id = int(self.data.get('semester'))
                selected_department = Department.objects.get(id=department_id)
                selected_semester = Semester.objects.get(id=semester_id)

                self.fields['course_assignment'].queryset = CourseAssignment.objects.filter(
                    class_assigned__department=selected_department,
                    class_assigned__semester=selected_semester
                ).order_by('course__short_name')
            except (ValueError, TypeError, Department.DoesNotExist, Semester.DoesNotExist):
                self.fields['course_assignment'].queryset = CourseAssignment.objects.none()
        else:
            self.fields['course_assignment'].queryset = CourseAssignment.objects.none()

class ScheduleForm(forms.Form):
    day = forms.ModelChoiceField(queryset=Day.objects.all(), label='Day', required=True)
    room = forms.ModelChoiceField(queryset=Room.objects.all(), label='Room', required=True)
    timeslot = forms.ModelChoiceField(queryset=Timeslot.objects.all(), label='Timeslot', required=True)

    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Department', required=True)
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), label='Semester', required=True)

    class_select = forms.ModelChoiceField(queryset=Class.objects.none(), label='Class', required=True)
    course_assignment = forms.ModelChoiceField(queryset=CourseAssignment.objects.none(), label='Course Assignment', required=True)

    def __init__(self, *args, **kwargs):
        department_id = kwargs.pop('department_id', None)
        semester_id = kwargs.pop('semester_id', None)
        class_id = kwargs.pop('class_id', None)
        super().__init__(*args, **kwargs)

        # Set class attributes and initial placeholder text for each field
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.empty_label = f'Select {field.label}'

        if department_id and semester_id:
            self.fields['class_select'].queryset = Class.objects.filter(department_id=department_id, semester_id=semester_id)

        if class_id:
            self.fields['course_assignment'].queryset = CourseAssignment.objects.filter(class_assigned_id=class_id)

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'phone_number', 'gmail']  # Include the 'gmail' field
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0301-2348578'}),
            'gmail': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Gmail (optional)'})  # Widget for gmail field
        }

class SelectSlotForm(forms.Form):
    day = forms.ModelChoiceField(queryset=Day.objects.all(), label='Day', widget=forms.Select(attrs={'class': 'form-control'}))
    room = forms.ModelChoiceField(queryset=Room.objects.all(), label='Room', widget=forms.Select(attrs={'class': 'form-control'}))
    timeslot = forms.ModelChoiceField(queryset=Timeslot.objects.all(), label='Timeslot', widget=forms.Select(attrs={'class': 'form-control'}))
class ScheduleSwapForm(forms.Form):
    # Select first schedule (Schedule A)
    day_a = forms.ModelChoiceField(queryset=Day.objects.all(), label='Day for Schedule A', required=True)
    room_a = forms.ModelChoiceField(queryset=Room.objects.all(), label='Room for Schedule A', required=True)
    timeslot_a = forms.ModelChoiceField(queryset=Timeslot.objects.all(), label='Timeslot for Schedule A', required=True)

    # Select second schedule (Schedule B)
    day_b = forms.ModelChoiceField(queryset=Day.objects.all(), label='Day for Schedule B', required=True)
    room_b = forms.ModelChoiceField(queryset=Room.objects.all(), label='Room for Schedule B', required=True)
    timeslot_b = forms.ModelChoiceField(queryset=Timeslot.objects.all(), label='Timeslot for Schedule B', required=True)

    def clean(self):
        cleaned_data = super().clean()
        day_a = cleaned_data.get('day_a')
        room_a = cleaned_data.get('room_a')
        timeslot_a = cleaned_data.get('timeslot_a')

        day_b = cleaned_data.get('day_b')
        room_b = cleaned_data.get('room_b')
        timeslot_b = cleaned_data.get('timeslot_b')

        # Validate if schedule A and B exist
        schedule_a = Schedule.objects.filter(day=day_a, room=room_a, timeslot=timeslot_a).first()
        schedule_b = Schedule.objects.filter(day=day_b, room=room_b, timeslot=timeslot_b).first()

        if not schedule_a or not schedule_b:
            raise forms.ValidationError("One or both schedules do not exist.")

        return cleaned_data