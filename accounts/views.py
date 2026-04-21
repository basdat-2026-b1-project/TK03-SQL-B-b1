from django.shortcuts import render, redirect
from django.contrib import messages

# ============================================================
# DUMMY DATA - Simulasi database untuk TK03
# Pada TK04 ini akan diganti dengan query ke PostgreSQL
# ============================================================

DUMMY_USERS = {
    'john@example.com': {
        'password': 'password123',
        'role': 'member',
        'salutation': 'Mr.',
        'nama': 'John William Doe',
        'first_mid_name': 'John William',
        'last_name': 'Doe',
        'country_code': '+62',
        'mobile_number': '81234567890',
        'tanggal_lahir': '1990-05-15',
        'kewarganegaraan': 'Indonesia',
        # Data khusus member
        'nomor_member': 'M0001',
        'tanggal_bergabung': '2024-01-15',
        'tier': 'Gold',
        'total_miles': 45000,
        'award_miles': 32000,
    },
    'admin@aeromiles.com': {
        'password': 'admin123',
        'role': 'staf',
        'salutation': 'Mr.',
        'nama': 'Admin Aero',
        'first_mid_name': 'Admin',
        'last_name': 'Aero',
        'country_code': '+62',
        'mobile_number': '81111111111',
        'tanggal_lahir': '1988-01-01',
        'kewarganegaraan': 'Indonesia',
        # Data khusus staf
        'id_staf': 'S0001',
        'maskapai': 'Garuda Indonesia',
        'kode_maskapai': 'GA',
    },
}

DUMMY_TRANSAKSI_TERBARU = [
    {'tipe': 'Transfer', 'timestamp': '2025-01-15 10:30', 'jumlah': -5000},
    {'tipe': 'Redeem', 'timestamp': '2025-01-20 16:00', 'jumlah': -3000},
    {'tipe': 'Package', 'timestamp': '2025-03-01 08:00', 'jumlah': 10000},
    {'tipe': 'Klaim', 'timestamp': '2024-10-05 18:45', 'jumlah': 2500},
    {'tipe': 'Transfer', 'timestamp': '2024-12-10 14:00', 'jumlah': 2000},
]

# ============================================================


def login_view(request):
    if request.session.get('role'):
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = DUMMY_USERS.get(email)
        if user and user['password'] == password:
            # Simpan session
            request.session['email'] = email
            request.session['role'] = user['role']
            request.session['salutation'] = user['salutation']
            request.session['nama'] = user['nama']
            # Simpan semua data user ke session untuk kemudahan
            for k, v in user.items():
                if k != 'password':
                    request.session[k] = v
            messages.success(request, f"Selamat datang, {user['salutation']} {user['nama']}!")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Email atau password salah. Silakan coba lagi.')

    return render(request, 'accounts/login.html')


def register_view(request):
    if request.session.get('role'):
        return redirect('accounts:dashboard')

    MASKAPAI_CHOICES = [
        ('GA', 'GA - Garuda Indonesia'),
        ('QG', 'QG - Citilink'),
        ('JT', 'JT - Lion Air'),
        ('ID', 'ID - Batik Air'),
        ('SQ', 'SQ - Singapore Airlines'),
    ]

    if request.method == 'POST':
        role = request.POST.get('role', 'member')
        email = request.POST.get('email', '').strip()
        # Validasi sederhana untuk demo
        if not email:
            messages.error(request, 'Email tidak boleh kosong.')
        elif email in DUMMY_USERS:
            messages.error(request, 'Email sudah terdaftar.')
        else:
            messages.success(request, 'Akun berhasil dibuat! Silakan login.')
            return redirect('accounts:login')

    return render(request, 'accounts/register.html', {
        'maskapai_choices': [
            ('GA', 'GA - Garuda Indonesia'),
            ('QG', 'QG - Citilink'),
            ('JT', 'JT - Lion Air'),
            ('ID', 'ID - Batik Air'),
            ('SQ', 'SQ - Singapore Airlines'),
        ]
    })


def logout_view(request):
    request.session.flush()
    messages.info(request, 'Anda telah logout.')
    return redirect('accounts:login')


def dashboard_view(request):
    if not request.session.get('role'):
        return redirect('accounts:login')

    role = request.session.get('role')

    if role == 'member':
        context = {
            'transaksi_terbaru': DUMMY_TRANSAKSI_TERBARU,
        }
    else:  # staf
        context = {
            'klaim_menunggu': 7,
            'klaim_disetujui': 12,
            'klaim_ditolak': 3,
        }

    return render(request, 'accounts/dashboard.html', context)


def profil_view(request):
    if not request.session.get('role'):
        return redirect('accounts:login')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profil':
            # Update session dengan data baru (demo)
            request.session['salutation'] = request.POST.get('salutation', request.session.get('salutation'))
            request.session['first_mid_name'] = request.POST.get('first_mid_name', request.session.get('first_mid_name'))
            request.session['last_name'] = request.POST.get('last_name', request.session.get('last_name'))
            request.session['country_code'] = request.POST.get('country_code', request.session.get('country_code'))
            request.session['mobile_number'] = request.POST.get('mobile_number', request.session.get('mobile_number'))
            request.session['kewarganegaraan'] = request.POST.get('kewarganegaraan', request.session.get('kewarganegaraan'))
            request.session['tanggal_lahir'] = request.POST.get('tanggal_lahir', request.session.get('tanggal_lahir'))
            # Update nama display
            request.session['nama'] = f"{request.session['first_mid_name']} {request.session['last_name']}"
            messages.success(request, 'Profil berhasil diperbarui.')

        elif action == 'update_password':
            password_lama = request.POST.get('password_lama', '')
            password_baru = request.POST.get('password_baru', '')
            konfirmasi = request.POST.get('konfirmasi_password_baru', '')

            email = request.session.get('email')
            user = DUMMY_USERS.get(email, {})

            if user.get('password') != password_lama:
                messages.error(request, 'Password lama tidak sesuai.')
            elif password_baru != konfirmasi:
                messages.error(request, 'Konfirmasi password baru tidak cocok.')
            elif len(password_baru) < 8:
                messages.error(request, 'Password baru minimal 8 karakter.')
            else:
                messages.success(request, 'Password berhasil diubah.')

        return redirect('accounts:profil')

    MASKAPAI_CHOICES = [
        ('GA', 'GA - Garuda Indonesia'),
        ('QG', 'QG - Citilink'),
        ('JT', 'JT - Lion Air'),
        ('ID', 'ID - Batik Air'),
        ('SQ', 'SQ - Singapore Airlines'),
    ]

    COUNTRY_CODES = [
        ('+62', '+62 Indonesia'),
        ('+1', '+1 USA/Canada'),
        ('+65', '+65 Singapore'),
        ('+60', '+60 Malaysia'),
        ('+61', '+61 Australia'),
        ('+44', '+44 UK'),
        ('+81', '+81 Japan'),
    ]

    return render(request, 'accounts/profil.html', {
        'maskapai_choices': MASKAPAI_CHOICES,
        'country_codes': COUNTRY_CODES,
    })