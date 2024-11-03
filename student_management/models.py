from django.db import models
from timetable.models import Class, Teacher # Import only Class as it already links to Department, Semester, and Shift



class Student(models.Model):
    roll_no = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    cnic = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    session = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.roll_no} - {self.name}"

class FYP(models.Model):
    GROUP_STATUS_CHOICES = [
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
    ]

    group_name = models.CharField(max_length=10)
    students = models.ManyToManyField(Student)  # Limit to 3 students per group
    title = models.CharField(max_length=255)
    supervisor = models.ForeignKey(Teacher, on_delete=models.CASCADE)  # Supervisor is selected from Teacher model
    deadline = models.DateField()
    submission_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=GROUP_STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.group_name} - {self.title}"

