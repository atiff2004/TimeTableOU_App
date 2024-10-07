from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class Semester(models.Model):
    name = models.CharField(max_length=50) 
    def __str__(self):
        return self.name
class Shift(models.Model):
    name = models.CharField(max_length=8)  # Example: 'M', 'E', etc.

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=10)  # Section field, e.g., 'M', 'E', etc.
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)  # New shift field

    def __str__(self):
        return f"{self.name} ({self.section}) - {self.department} - {self.semester} - {self.shift}"

    
class Course(models.Model):
    course_code = models.CharField(max_length=20)
    short_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200)
    credit_hours = models.CharField(max_length=200)
    lab_crh = models.IntegerField(default=0)  # New field for lab credit hours
    pre_req = models.CharField(max_length=200, blank=True, null=True)  # New field for prerequisites
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.short_name
    
class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()  # Adding a field to track the year

    class Meta:
        unique_together = ('course', 'department', 'semester', 'year')

    def __str__(self):
        return f'{self.department.name} - {self.semester.name} - {self.course.short_name} ({self.year})'

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12, null=True, blank=True)  # Phone number can be null
    gmail = models.EmailField(null=True, blank=True)  # Gmail field is optional

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class Timeslot(models.Model):
    slot = models.CharField(max_length=20)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)  # New shift field

    def __str__(self):
        return f"{self.slot} - {self.shift}"

class Day(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class CourseAssignment(models.Model):
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)  # Make teacher nullable

    class Meta:
        unique_together = ('course', 'class_assigned')

    def __str__(self):
        return f'{self.class_assigned.name} - {self.course.short_name} - {self.teacher.name if self.teacher else "No Teacher"}'

class Schedule(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    course_assignment = models.ForeignKey(CourseAssignment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('day', 'room', 'timeslot')

    def __str__(self):
        return f'{self.day.name} - {self.room.name} - {self.timeslot.slot} - {self.course_assignment}'
class NewTimeslot(models.Model):
    slot = models.CharField(max_length=20)
    start_time = models.TimeField()  # New field for start time
    end_time = models.TimeField()  # New field for end time
    shift = models.ForeignKey('Shift', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.slot} - {self.shift} ({self.start_time} to {self.end_time})"