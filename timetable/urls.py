from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('upload_courses_excel/', views.upload_courses_excel, name='upload_courses_excel'),
    path('upload_classes_excel/', views.upload_classes_excel, name='upload_classes_excel'),
    path('upload_teachers_excel/', views.upload_teachers_excel, name='upload_teachers_excel'),
    path('upload_course_offering/', views.upload_course_offerings, name='upload_course_offering'),
    path('upload_schedule/', views.upload_schedule, name='upload_schedule'),
    path('upload_course_assignments/', views.upload_course_assignments_excel, name='upload_course_assignments'),
    path('upload-days-rooms-timeslots/', views.upload_days_rooms_timeslots, name='upload_days_rooms_timeslots'),

    # URL for deleting Days, Rooms, and Timeslots
    path('delete_data/', views.delete_data, name='delete_data'),
    path('manage_data/', views.manage_days_rooms_timeslots, name='manage_data'),
    path('add_data/', views.add_data, name='add_data'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('Room/timetable/', views.room_timetable_selection_view, name='room_timetable_selection_view'),
    path('Room/timetable/<int:room_id>/', views.room_timetable_view, name='room_timetable_view'),
    path('class/timetable/', views.class_timetable_selection_view, name='class_timetable_selection'),
    path('class/timetable/<int:class_id>/', views.class_timetable_view, name='class_timetable'),
    path('teacher/timetable/', views.teacher_timetable_selection_view, name='teacher_timetable_selection'),
    path('teacher/timetable/<int:teacher_id>/', views.teacher_timetable_view, name='teacher_timetable'),
    path('add_course/', views.add_course, name='add_course'),
    path('add_class/', views.add_class, name='add_class'),
    path('add_Room/', views.add_Room, name='add_Room'),
    path('teacher_contacts', views.teacher_contacts, name='teacher_contacts'),
    path('Courses_details', views.Courses_details, name='Courses_details'),
    path('add_day/', views.add_day, name='add_day'),
    path('add_Timeslot/', views.add_Timeslot, name='add_Timeslot'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('assign-schedule/', views.assign_schedule, name='assign_schedule'),
    # path('load-classes/', views.load_classes_by_department_and_semester, name='load_classes_by_department_and_semester'),
    path('load-classes/', views.load_classes, name='load_classes'),
    path('load-course-assignments/', views.load_course_assignments, name='load_course_assignments'),
    path('get-class-list/', views.get_class_list, name='get_class_list'),
    path('filter_classes/', views.filter_classes, name='filter_classes'),
    path('filter_course_assignments/', views.filter_course_assignments, name='filter_course_assignments'),
    path('get-course-assignments/', views.get_course_assignments, name='get_course_assignments'),
    path('schedule/delete/', views.delete_schedule, name='delete_schedule'),
    path('swap_schedules/', views.swap_schedules, name='swap_schedules'),
    path('assign-course-to-class/', views.assign_course_to_class, name='assign_course_to_class'),
    path('get-classes/<int:department_id>/', views.get_classes, name='get_classes'),
    path('get-courses/<int:department_id>/', views.get_courses, name='get_courses'),
    path('get-course-assignments/<int:department_id>/', views.get_course_assignments, name='get_course_assignments'),
    # path('search_courses/', views.course_search, name='search_courses'),
    path('search_courses/', views.course_search, name='search_courses'),
    path('course_details/', views.course_details, name='course_details'),
        # Course offering related views
    path('add_course_offering/', views.add_course_offering, name='add_course_offering'),

    # Assignments
    path('assign_teacher_to_course/', views.assign_teacher_to_course, name='assign_teacher_to_course'),
    path('load_classes_and_courses/', views.load_classes_and_courses, name='load_classes_and_courses'),
    path('load_course_class_pairs/', views.load_course_class_pairs, name='load_course_class_pairs'),


]




