import pandas as pd
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from .models import Student, FYP
from timetable.models import Class, Department, Semester
from django.shortcuts import render, redirect
from .forms import FYPForm, FYPFormedit
from timetable.models import Department, Semester, Class
from django.http import JsonResponse

def edit_fyp_group(request):
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    selected_class = None
    selected_group = None
    fyps = []
    form = None
    group_members = None  # Initialize group_members to None

    if request.GET.get('class_id'):
        class_id = request.GET.get('class_id')
        selected_class = get_object_or_404(Class, id=class_id)
        fyps = FYP.objects.filter(students__class_assigned=selected_class).distinct()

    if request.GET.get('fyp_id'):
        fyp_id = request.GET.get('fyp_id')
        selected_group = get_object_or_404(FYP, id=fyp_id)
        group_members = selected_group.students.all()  # Retrieve current group members for read-only display

        if request.GET.get('action') == 'submit':
            if request.method == 'POST':
                selected_group.submission_date = request.POST.get('submission_date')
                selected_group.status = request.POST.get('status')
                selected_group.save(update_fields=['submission_date', 'status'])
                messages.success(request, "Submission details updated successfully.")
                return redirect('edit_fyp_group')
        elif request.GET.get('action') == 'edit':
            # Edit form setup
            form = FYPFormedit(request.POST or None, instance=selected_group)
            if request.method == 'POST' and form.is_valid():
                form.save()
                messages.success(request, "FYP group details updated successfully.")
                return redirect('edit_fyp_group')

    return render(request, 'student/edit_fyp_group.html', {
        'departments': departments,
        'semesters': semesters,
        'fyps': fyps,
        'selected_class': selected_class,
        'selected_group': selected_group,
        'form': form,
        'group_members': group_members,
    })


def swap_group_members(request):
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    selected_class = None
    group_x = None
    group_y = None
    students_x = []
    students_y = []

    # Handle selected class and groups
    if request.GET.get('class_id'):
        class_id = request.GET.get('class_id')
        selected_class = Class.objects.get(id=class_id)
        fyps = FYP.objects.filter(students__class_assigned=selected_class).distinct()

    if request.GET.get('group_x_id') and request.GET.get('group_y_id'):
        group_x_id = request.GET.get('group_x_id')
        group_y_id = request.GET.get('group_y_id')
        group_x = get_object_or_404(FYP, id=group_x_id)
        group_y = get_object_or_404(FYP, id=group_y_id)
        students_x = group_x.students.all()
        students_y = group_y.students.all()

    if request.method == "POST":
        # Process swapping members
        selected_students_x = request.POST.getlist('students_x')
        selected_students_y = request.POST.getlist('students_y')
        
        # Update members for group X
        group_x.students.set(selected_students_y)
        # Update members for group Y
        group_y.students.set(selected_students_x)

        return redirect('edit_fyp_group')

    return render(request, 'student/swap_group_members.html', {
        'departments': departments,
        'semesters': semesters,
        'selected_class': selected_class,
        'group_x': group_x,
        'group_y': group_y,
        'students_x': students_x,
        'students_y': students_y,
        'fyps': fyps,
    })

def load_class(request):
    department_id = request.GET.get('department_id')
    semester_id = request.GET.get('semester_id')

    try:
        # Retrieve the Department and Semester based on IDs
        department = Department.objects.get(id=department_id)
        semester = Semester.objects.get(id=semester_id)
        
        # Filter classes based on the selected department and semester
        classes = Class.objects.filter(department=department, semester=semester).values('id', 'name', 'section')
        
        # Return the list of classes as JSON data
        return JsonResponse({'classes': list(classes)})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)
    except Semester.DoesNotExist:
        return JsonResponse({'error': 'Semester not found'}, status=404)

def load_students(request):
    class_id = request.GET.get('class_id')
    students = Student.objects.filter(class_assigned_id=class_id, fyp__isnull=True).values('id', 'name')
    return JsonResponse({'students': list(students)})


def create_fyp(request):
    if request.method == 'POST':
        form = FYPForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "FYP created successfully.")
            return redirect('fyp_list')  # Adjust this to your actual redirect path
        else:
            messages.error(request, "Error creating FYP. Please correct the issues below.")
    else:
        form = FYPForm()

    departments = Department.objects.all()
    semesters = Semester.objects.all()
    
    return render(request, 'student/create_fyp.html', {
        'form': form,
        'departments': departments,
        'semesters': semesters,
    })



def upload_students(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        try:
            # Read the uploaded file using pandas
            df = pd.read_excel(file)

            # Iterate through each row in the DataFrame and save student data
            for _, row in df.iterrows():
                try:
                    # Retrieve department, semester, and class based on the Excel data
                    department = Department.objects.get(name=row['Department'])
                    semester = Semester.objects.get(name=row['Semester'])

                    # Find the exact Class match using all necessary fields
                    class_assigned = Class.objects.get(
                        name=row['Class Name'],
                        section=row['Section'],
                        department=department,
                        semester=semester,
                    )

                    # Create or update the Student record
                    Student.objects.update_or_create(
                        roll_no=row['Roll No'],
                        defaults={
                            'name': row['Name'],
                            'cnic': row['CNIC'],
                            'email': row['Email'],
                            'contact_number': row['Contact Number'],
                            'class_assigned': class_assigned,
                            'session': row['Session'],
                        }
                    )
                except Class.DoesNotExist:
                    messages.error(request, f"Class '{row['Class Name']}' with Section '{row['Section']}', "
                                            f"Department '{row['Department']}', and Semester '{row['Semester']}' "
                                            f"does not exist in the database.")
                    continue
                except Department.DoesNotExist:
                    messages.error(request, f"Department '{row['Department']}' does not exist in the database.")
                    continue
                except Semester.DoesNotExist:
                    messages.error(request, f"Semester '{row['Semester']}' does not exist in the database.")
                    continue

            messages.success(request, "Student data uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Error processing file: {e}")
        return redirect('upload_students')

    return render(request, 'student/upload_students.html')


def fyp_list(request):
    departments = Department.objects.all()
    semesters = Semester.objects.all()
    selected_class = None
    fyps = []

    if request.GET.get('class_id'):
        class_id = request.GET.get('class_id')
        selected_class = Class.objects.get(id=class_id)
        fyps = FYP.objects.filter(students__class_assigned=selected_class).distinct()

    return render(request, 'student/fyp_list.html', {
        'departments': departments,
        'semesters': semesters,
        'fyps': fyps,
        'selected_class': selected_class,
    })