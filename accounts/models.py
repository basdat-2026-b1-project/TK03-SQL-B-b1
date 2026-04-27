from django.db import models

class Pengguna(models.Model):
    email = models.EmailField(max_length=100, primary_key=True)
    password = models.CharField(max_length=255)
    salutation = models.CharField(max_length=10)
    first_mid_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5)
    mobile_number = models.CharField(max_length=20)
    tanggal_lahir = models.DateField()
    kewarganegaraan = models.CharField(max_length=50)

    class Meta:
        db_table = 'PENGGUNA'

class Member(models.Model):
    email = models.OneToOneField(Pengguna, on_delete=models.CASCADE, primary_key=True)
    # nomor_member = models.CharField(max_length=20, unique=True)
    # tanggal_bergabung = models.DateField()
    # id_tier = models.ForeignKey(Tier, on_delete=models.PROTECT)
    # award_miles = models.IntegerField(null=True, blank=True)
    # total_miles = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'MEMBER'

class Staf(models.Model):
    email = models.OneToOneField(Pengguna, on_delete=models.CASCADE, primary_key=True)
    # id_staf = models.CharField(max_length=20, unique=True)
    # kode_maskapai = models.ForeignKey(Maskapai, on_delete=models.CASCADE)

    class Meta:
        db_table = 'STAF'
