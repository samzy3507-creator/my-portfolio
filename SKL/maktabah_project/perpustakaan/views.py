from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from urllib3 import request
from .models import Peminjaman, Siswa, Buku  # Sesuaikan dengan nama model kamu
from .models import Siswa, Peminjaman  # Mengimpor model yang dibutuhkan
from .models import Siswa, Buku, Peminjaman  # Pastikan Buku juga sudah diimpor



# Fungsi pembantu untuk mengubah hasil kueri SQL menjadi dictionary
def dictfetchall(cursor):
    """Mengembalikan semua baris dari kursor sebagai dictionary"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def dictfetchone(cursor):
    """Mengembalikan satu baris dari kursor sebagai dictionary"""
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(zip(columns, row))


# 1. DAFTAR BUKU
def buku_list(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok 
            FROM buku 
            ORDER BY id
        """)
        # Mengubah hasil fetchall menjadi daftar dictionary agar sesuai dengan template list.html
        buku = dictfetchall(cursor)

    return render(
        request,
        'buku/list.html',
        {'buku_list': buku} # Menggunakan 'buku_list' sesuai perulangan di list.html
    )


# 2. TAMBAH BUKU
def buku_tambah(request):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO buku (
                    judul, pengarang, kategori, penerbit, 
                    tahun_terbit, rak, stok, deskripsi
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                request.POST['judul'],
                request.POST['pengarang'],
                request.POST['kategori'],
                request.POST['penerbit'],
                request.POST['tahun_terbit'],
                request.POST['rak'],
                request.POST['stok'],
                request.POST['deskripsi']
            ])
        return redirect('buku_list')

    return render(request, 'buku/tambah.html')


# 3. DETAIL BUKU
def buku_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, deskripsi 
            FROM buku 
            WHERE id = %s
        """, [id])
        buku = dictfetchone(cursor)
    
    # Jika buku tidak ditemukan di database
    if not buku:
        return render(request, '404.html', status=404)

    return render(
        request,
        'buku/detail.html',
        {'buku': buku}
    )


# 4. EDIT BUKU
def buku_edit(request, id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE buku 
                SET judul = %s, 
                    pengarang = %s, 
                    kategori = %s, 
                    penerbit = %s, 
                    tahun_terbit = %s, 
                    rak = %s, 
                    stok = %s, 
                    deskripsi = %s
                WHERE id = %s
            """, [
                request.POST['judul'],
                request.POST['pengarang'],
                request.POST['kategori'],
                request.POST['penerbit'],
                request.POST['tahun_terbit'],
                request.POST['rak'],
                request.POST['stok'],
                request.POST['deskripsi'],
                id
            ])
        return redirect('buku_list')

    # Ambil data lama untuk ditampilkan di form edit.html
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku WHERE id = %s", [id])
        buku = dictfetchone(cursor)

    if not buku:
        return render(request, '404.html', status=404)

    return render(
        request,
        'buku/edit.html',
        {'buku': buku}
    )


# 5. HAPUS BUKU
def buku_delete(request, id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM buku WHERE id = %s", [id])
        return redirect('buku_list')

    # Ambil data buku untuk konfirmasi nama buku sebelum dihapus di delete.html
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, judul FROM buku WHERE id = %s", [id])
        buku = dictfetchone(cursor)

    if not buku:
        return render(request, '404.html', status=404)

    return render(
        request,
        'buku/delete.html',
        {'buku': buku}
    )





# 1. Menampilkan Daftar Peminjaman (list-peminjaman.html)
def peminjaman_list(request):
    peminjaman_list = Peminjaman.objects.all().order_by('-id')
    # SESUDAH (BENAR)
    return render(request, 'peminjaman/list_peminjaman.html', { 'peminjaman_list': peminjaman_list })
# 2. Menambah Transaksi Peminjaman (tambah-peminjaman.html)
def peminjaman_tambah(request):
    if request.method == 'POST':
        siswa_id = request.POST.get('siswa_id')
        buku_id = request.POST.get('buku_id')
        tanggal_pinjam = request.POST.get('tanggal_pinjam')
        jatuh_tempo = request.POST.get('jatuh_tempo')
        keperluan = request.POST.get('keperluan')
        catatan = request.POST.get('catatan')

        # Mengambil objek siswa dan buku
        siswa = get_object_or_404(Siswa, id=siswa_id)
        buku = get_object_or_404(Buku, id=buku_id)

        # Validasi jika stok buku mencukupi
        if buku.stok > 0:
            # Simpan data peminjaman baru
            Peminjaman.objects.create(
                siswa=siswa,
                buku=buku,
                tanggal_pinjam=tanggal_pinjam,
                jatuh_tempo=jatuh_tempo,
                keperluan=keperluan,
                catatan=catatan,
                status='Dipinjam'  # Status awal otomatis 'Dipinjam'
            )
            
            # Kurangi stok buku secara otomatis
            buku.stok -= 1
            buku.save()

            return redirect('peminjaman_list')
        else:
            # Jika stok habis (opsional: bisa tambah pesan error/alert di sini)
            pass

    # Mengambil data untuk pilihan dropdown di form
    siswa_list = Siswa.objects.all()
    buku_list = Buku.objects.filter(stok__gt=0)  # Hanya menampilkan buku yang stoknya > 0
    
   # UBAH MENJADI (BENAR)
    return render(request, 'peminjaman/tambah_peminjaman.html', { 'siswa_list': siswa_list, 'buku_list': buku_list })

# 3. Mengubah Status Menjadi Dikembalikan (ubah-status.html)
def peminjaman_ubah_status(request, id):
    peminjaman = get_object_or_404(Peminjaman, id=id)

    if request.method == 'POST':
        # Pastikan status sebelumnya belum dikembalikan agar tidak terjadi duplikasi manipulasi stok
        if peminjaman.status != 'Dikembalikan':
            peminjaman.status = 'Dikembalikan'
            peminjaman.save()

            # Tambah kembali stok buku otomatis
            buku = peminjaman.buku
            buku.stok += 1
            buku.save()

        return redirect('peminjaman_list')

    return render(request, 'peminjaman/ubah_status.html', {
        'peminjaman': peminjaman
    })   







from django.shortcuts import render, redirect, get_object_or_404
from .models import Siswa, Peminjaman

# 1. READ ALL - Menampilkan semua daftar siswa
def siswa_list(request):
    semua_siswa = Siswa.objects.all()
    return render(request, 'siswa/list-siswa.html', {'siswa_list': semua_siswa})


# 2. CREATE - Menambah data siswa baru
def siswa_tambah(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        kelas = request.POST.get('kelas')
        nis = request.POST.get('nis')
        
        # is_active sengaja dibuang dari create karena field tidak ada di model kamu
        Siswa.objects.create(
            nama=nama,
            kelas=kelas,
            nis=nis
        )
        return redirect('siswa_list')
        
    return render(request, 'siswa/tambah-siswa.html')


# 3. READ DETAIL - Menampilkan detail satu siswa & info peminjamannya
def siswa_detail(request, id):
    siswa = get_object_or_404(Siswa, pk=id)
    total_peminjaman = Peminjaman.objects.filter(siswa=siswa).count()
    peminjaman_aktif_count = Peminjaman.objects.filter(siswa=siswa, tanggal_kembali__isnull=True).count()
    
    context = {
        'siswa': siswa,
        'total_peminjaman': total_peminjaman,
        'peminjaman_aktif_count': peminjaman_aktif_count,
    }
    return render(request, 'siswa/detail-siswa.html', context)


# 4. UPDATE - Mengedit data siswa
def siswa_edit(request, id):
    siswa = get_object_or_404(Siswa, pk=id)
    
    if request.method == 'POST':
        siswa.nama = request.POST.get('nama')
        siswa.kelas = request.POST.get('kelas')
        siswa.nis = request.POST.get('nis')
        
        # siswa.is_active dibuang agar tidak TypeError
        siswa.save()
        return redirect('siswa_list')
        
    return render(request, 'siswa/edit-siswa.html', {'siswa': siswa})


# 5. DELETE - Menghapus data siswa
def siswa_hapus(request, id):
    siswa = get_object_or_404(Siswa, pk=id)
    
    if request.method == 'POST':
        siswa.delete()
        return redirect('siswa_list')
        
    return render(request, 'siswa/hapus-siswa.html', {'siswa': siswa})

  


# ... (fungsi-fungsi siswa_list, siswa_tambah, dll yang kemarin biarkan tetap ada)

# 6. DASHBOARD ANALITIK
def dashboard(request):
    # Menghitung total data dari masing-masing model
    total_buku = Buku.objects.count()
    total_siswa = Siswa.objects.count()
    total_peminjaman = Peminjaman.objects.count()
    
    # Menghitung peminjaman yang aktif (buku belum dikembalikan / tanggal_kembali masih kosong)
    peminjaman_aktif = Peminjaman.objects.filter(tanggal_kembali__isnull=True).count()
    
    # Bungkus data ke dalam context untuk dikirim ke HTML
    context = {
        'total_buku': total_buku,
        'total_siswa': total_siswa,
        'total_peminjaman': total_peminjaman,
        'peminjaman_aktif': peminjaman_aktif,
    }
    
    # Render ke template dashboard.html
    return render(request, 'perpustakaan/dashboard.html', context)