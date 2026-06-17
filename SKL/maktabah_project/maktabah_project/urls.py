"""
URL configuration for maktabah_project project.
"""

from django.contrib import admin
from django.urls import path
from perpustakaan import views  # Mengambil fungsi view dari aplikasi perpustakaan

urlpatterns = [
    path('admin/', admin.site.urls),

    # Dashboard / Halaman Utama Aplikasi
    path('', views.dashboard, name='dashboard'),

    # Modul Siswa / User (Lengkap CRUD sesuai template HTML kamu)
    path('siswa/', views.siswa_list, name='siswa_list'), 
    path('siswa/tambah/', views.siswa_tambah, name='siswa_tambah'),
    path('siswa/<int:id>/', views.siswa_detail, name='siswa_detail'),
    path('siswa/<int:id>/edit/', views.siswa_edit, name='siswa_edit'),
    path('siswa/<int:id>/hapus/', views.siswa_hapus, name='siswa_hapus'),
     
    # Modul Buku (Gunakan <int:id> agar sinkron dengan standar views)
    path('buku/', views.buku_list, name='buku_list'),
    path('buku/tambah/', views.buku_tambah, name='buku_tambah'),
    path('buku/detail/<int:id>/', views.buku_detail, name='buku_detail'),
    path('buku/edit/<int:id>/', views.buku_edit, name='buku_edit'),
    path('buku/hapus/<int:id>/', views.buku_delete, name='buku_delete'),

    # Modul Peminjaman
    path('peminjaman/', views.peminjaman_list, name='peminjaman_list'),
    path('peminjaman/tambah/', views.peminjaman_tambah, name='peminjaman_tambah'),
    path('peminjaman/ubah-status/<int:id>/', views.peminjaman_ubah_status, name='peminjaman_ubah_status'),
]