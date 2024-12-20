from .auth_views import (
    SchoolLoginView, SchoolLogoutView,
    SchoolPasswordChangeView, SchoolPasswordChangeDoneView
)
from .dashboard_views import DashboardView
from .school_views import (
    SchoolListView, SchoolCreateView, SchoolDetailView,
    SchoolUpdateView, SchoolDeleteView
)
from .class_views import (
    ClassRoomListView, ClassRoomCreateView,
    ClassRoomDetailView, ClassRoomUpdateView,
    ClassRoomDeleteView, ClassStudentsView,
    ClassAttendanceView, ClassGradesView
)
from .student_views import (
    StudentListView, StudentCreateView,
    StudentDetailView, StudentUpdateView,
    StudentDeleteView, export_students_excel,
    import_students_excel
)
from .staff_views import (
    SchoolStaffListView, StaffCreateView,
    StaffDetailView, StaffUpdateView,
    StaffDeleteView
)
from .attendance_views import (
    AttendanceCreateView, AttendanceDetailView,
    AttendanceUpdateView, AttendanceDeleteView,
    AttendanceBulkCreateView, AttendanceClassDetailView,
    GeneralAttendanceView
)
from .grade_views import (
    KSQGradeView, BSQGradeView,
    MonitoringGradeView, FinalGradeView
)
from .settings_views import (
    settings_view, school_profile
)

__all__ = [
    'SchoolLoginView',
    'SchoolLogoutView',
    'SchoolPasswordChangeView',
    'SchoolPasswordChangeDoneView',
    'DashboardView',
    'SchoolListView',
    'SchoolCreateView',
    'SchoolDetailView',
    'SchoolUpdateView',
    'SchoolDeleteView',
    'ClassRoomListView',
    'ClassRoomCreateView',
    'ClassRoomDetailView',
    'ClassRoomUpdateView',
    'ClassRoomDeleteView',
    'ClassStudentsView',
    'ClassAttendanceView',
    'ClassGradesView',
    'StudentListView',
    'StudentCreateView',
    'StudentDetailView',
    'StudentUpdateView',
    'StudentDeleteView',
    'export_students_excel',
    'import_students_excel',
    'SchoolStaffListView',
    'StaffCreateView',
    'StaffDetailView',
    'StaffUpdateView',
    'StaffDeleteView',
    'AttendanceCreateView',
    'AttendanceDetailView',
    'AttendanceUpdateView',
    'AttendanceDeleteView',
    'AttendanceBulkCreateView',
    'AttendanceClassDetailView',
    'GeneralAttendanceView',
    'KSQGradeView',
    'BSQGradeView',
    'MonitoringGradeView',
    'FinalGradeView',
    'settings_view',
    'school_profile',
]
