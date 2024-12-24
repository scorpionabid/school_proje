from .auth_views import (
    SchoolLoginView, SchoolLogoutView,
    SchoolPasswordChangeView, SchoolPasswordChangeDoneView
)
from .dashboard_views import school_dashboard
from .settings_views import school_settings, school_profile
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
    StaffDeleteView, SettingsStaffListView,
    SettingsStaffCreateView, SettingsStaffUpdateView,
    SettingsStaffDeleteView
)

__all__ = [
    'SchoolLoginView',
    'SchoolLogoutView',
    'SchoolPasswordChangeView',
    'SchoolPasswordChangeDoneView',
    'school_dashboard',
    'school_settings',
    'school_profile',
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
    'SettingsStaffListView',
    'SettingsStaffCreateView',
    'SettingsStaffUpdateView',
    'SettingsStaffDeleteView'
]
