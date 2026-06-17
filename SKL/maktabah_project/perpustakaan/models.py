from django.db import models

# Create your models here.


from django.db import models

# 1. Model untuk data Siswa
class Siswa(models.Model):
    nis = models.CharField(max_length=20, unique=True)
    nama = models.CharField(max_length=100)
    kelas = models.CharField(max_length=50)

    def __str__(self):
        return self.nama

# 2. Model untuk data Buku
class Buku(models.Model):
    judul = models.CharField(max_length=200)
    penulis = models.CharField(max_length=100)
    stok = models.IntegerField(default=1)

    def __str__(self):
        return self.judul
    



    

# 3. Model untuk data Peminjaman
class Peminjaman(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE)
    buku = models.ForeignKey(Buku, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(auto_now_add=True)
    tanggal_kembali = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.siswa.nama} meminjam {self.buku.judul}"
    



