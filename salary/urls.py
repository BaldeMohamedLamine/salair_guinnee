from django.urls import path
from .views import net_to_gross_view, export_excel_view, delete_all_employees_view, delete_selected_employees_view

urlpatterns = [
    path('', net_to_gross_view, name='index'),
    path('export-excel/', export_excel_view, name='export_excel'),
    path('delete-all/', delete_all_employees_view, name='delete_all'),
    path('delete-selected/', delete_selected_employees_view, name='delete_selected'),
]
