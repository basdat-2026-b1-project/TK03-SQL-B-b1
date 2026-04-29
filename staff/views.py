from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password
from datetime import date
from django.core.paginator import Paginator

DUMMY_MEMBERS = [
    {'nomor': 'M0001', 'nama': 'Mr. John William Doe', 'email': 'john@example.com',
     'tier': 'Gold', 'total_miles': 45000, 'award_miles': 32000, 'bergabung': '2024-01-15'},
    {'nomor': 'M0002', 'nama': 'Mrs. Jane Smith', 'email': 'jane@example.com',
     'tier': 'Silver', 'total_miles': 20000, 'award_miles': 15000, 'bergabung': '2024-03-10'},
    {'nomor': 'M0003', 'nama': 'Mr. Budi Anto Santoso', 'email': 'budi@example.com',
     'tier': 'Blue', 'total_miles': 5000, 'award_miles': 3500, 'bergabung': '2024-08-20'},
    {'nomor': 'M0004', 'nama': 'Mr. John Lennon', 'email': 'johnlennon@gmail.com',
     'tier': 'Blue', 'total_miles': 0, 'award_miles': 0, 'bergabung': '2026-04-12'},
    {'nomor': 'M0005', 'nama': 'Ms. Sari Dewi', 'email': 'sari@example.com',
     'tier': 'Platinum', 'total_miles': 120000, 'award_miles': 95000, 'bergabung': '2022-05-01'},
]

DUMMY_KLAIM_STAF = [
    {'id': 'CLM-001', 'member': 'John W. Doe', 'email': 'john@example.com',
     'maskapai': 'GA', 'rute': 'CGK → DPS', 'tanggal': '2024-10-01',
     'flight': 'GA404', 'kelas': 'Business', 'pengajuan': '2024-10-05 18:45:00', 'status': 'Disetujui'},
    {'id': 'CLM-002', 'member': 'John W. Doe', 'email': 'john@example.com',
     'maskapai': 'SQ', 'rute': 'SIN → NRT', 'tanggal': '2024-11-15',
     'flight': 'SQ12', 'kelas': 'Economy', 'pengajuan': '2024-11-20 18:45:00', 'status': 'Menunggu'},
    {'id': 'CLM-003', 'member': 'Jane Smith', 'email': 'jane@example.com',
     'maskapai': 'GA', 'rute': 'CGK → SUB', 'tanggal': '2024-12-01',
     'flight': 'GA310', 'kelas': 'Economy', 'pengajuan': '2024-12-05 18:45:00', 'status': 'Ditolak'},
    {'id': 'CLM-004', 'member': 'Budi A. Santoso', 'email': 'budi@example.com',
     'maskapai': 'MH', 'rute': 'KUL → BKK', 'tanggal': '2025-01-10',
     'flight': 'MH780', 'kelas': 'Premium Economy', 'pengajuan': '2025-01-15 18:45:00', 'status': 'Menunggu'},
    {'id': 'CLM-005', 'member': 'Ms. Sari Dewi', 'email': 'sari@example.com',
     'maskapai': 'GA', 'rute': 'CGK → SIN', 'tanggal': '2025-02-20',
     'flight': 'GA830', 'kelas': 'First', 'pengajuan': '2025-02-22 10:00:00', 'status': 'Menunggu'},
]

DUMMY_HADIAH_STAF = [
    {'kode': 'RWD-001', 'nama': 'Tiket Domestik PP', 'deskripsi': 'Tiket pulang-pergi domestik',
     'penyedia': 'Garuda Indonesia', 'tipe_penyedia': 'airline',
     'miles': 15000, 'periode': '2024-01-01 — 2025-12-31', 'aktif': True},
    {'kode': 'RWD-002', 'nama': 'Upgrade Business Class', 'deskripsi': 'Upgrade economy ke business',
     'penyedia': 'Garuda Indonesia', 'tipe_penyedia': 'airline',
     'miles': 25000, 'periode': '2024-01-01 — 2025-12-31', 'aktif': True},
    {'kode': 'RWD-003', 'nama': 'Voucher Hotel Rp 500.000', 'deskripsi': 'Voucher hotel Indonesia',
     'penyedia': 'TravelokaPartner', 'tipe_penyedia': 'partner',
     'miles': 8000, 'periode': '2024-06-01 — 2025-06-30', 'aktif': True},
    {'kode': 'RWD-004', 'nama': 'Akses Lounge 1x', 'deskripsi': 'Akses lounge premium 1x',
     'penyedia': 'Plaza Premium', 'tipe_penyedia': 'partner',
     'miles': 3000, 'periode': '2024-01-01 — 2025-12-31', 'aktif': False},
]

DUMMY_MITRA = [
    {'email': 'partner@traveloka.com', 'id_penyedia': 3, 'nama': 'TravelokaPartner', 'tanggal': '2023-01-15'},
    {'email': 'partner@plazapremium.com', 'id_penyedia': 4, 'nama': 'Plaza Premium', 'tanggal': '2023-06-01'},
    {'email': 'partner@hotelindo.com', 'id_penyedia': 5, 'nama': 'HotelIndo', 'tanggal': '2024-01-10'},
    {'email': 'partner@rentalcar.com', 'id_penyedia': 6, 'nama': 'RentalCar Express', 'tanggal': '2024-03-20'},
]

PENYEDIA_CHOICES = [
    ('1', 'GA - Garuda Indonesia (airline)'),
    ('2', 'SQ - Singapore Airlines (airline)'),
    ('3', 'TravelokaPartner (mitra)'),
    ('4', 'Plaza Premium (mitra)'),
    ('5', 'HotelIndo (mitra)'),
]

DUMMY_TRANSAKSI_LAPORAN = [
    {'tipe': 'Transfer', 'member': 'John W. Doe', 'email': 'john@example.com',
     'jumlah': -5000, 'timestamp': '2025-01-15 10:30'},
    {'tipe': 'Redeem', 'member': 'John W. Doe', 'email': 'john@example.com',
     'jumlah': -3000, 'timestamp': '2025-01-20 16:00'},
    {'tipe': 'Package', 'member': 'Jane Smith', 'email': 'jane@example.com',
     'jumlah': 5000, 'timestamp': '2025-02-01 09:15'},
    {'tipe': 'Klaim', 'member': 'Budi A. Santoso', 'email': 'budi@example.com',
     'jumlah': 2500, 'timestamp': '2025-02-05 11:45'},
    {'tipe': 'Transfer', 'member': 'Budi A. Santoso', 'email': 'budi@example.com',
     'jumlah': -2000, 'timestamp': '2025-02-10 14:00'},
    {'tipe': 'Package', 'member': 'John W. Doe', 'email': 'john@example.com',
     'jumlah': 10000, 'timestamp': '2025-03-01 08:00'},
]

DUMMY_TOP_MEMBERS = [
    {'rank': 1, 'member': 'Ms. Sari Dewi', 'email': 'sari@example.com',
     'total_miles': 120000, 'jumlah_transaksi': 15},
    {'rank': 2, 'member': 'Mr. John William Doe', 'email': 'john@example.com',
     'total_miles': 45000, 'jumlah_transaksi': 8},
    {'rank': 3, 'member': 'Mrs. Jane Smith', 'email': 'jane@example.com',
     'total_miles': 20000, 'jumlah_transaksi': 4},
]

TIER_CHOICES = ['Blue', 'Silver', 'Gold', 'Platinum']

def login_required_staf(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('role'):
            return redirect('accounts:login')
        if request.session.get('role') != 'staf':
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required_staf
def kelola_member_view(request):
    search = request.GET.get('q', '')
    filter_tier = request.GET.get('tier', 'Semua')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'tambah':
            new_member = {
                'nomor': f"M{len(DUMMY_MEMBERS) + 1:04d}",
                'nama': f"{request.POST.get('salutation')} {request.POST.get('first_mid_name')} {request.POST.get('last_name')}",
                'email': request.POST.get('email'),
                'tier': request.POST.get('tier', 'Blue'),
                'total_miles': 0,
                'award_miles': 0,
                'bergabung': date.today().strftime('%Y-%m-%d'),
            }
            DUMMY_MEMBERS.append(new_member)
            messages.success(request, 'Member baru berhasil ditambahkan.')

        elif action == 'edit':
            email = request.POST.get('email')

            for m in DUMMY_MEMBERS:
                if m['email'] == email:
                    m['nama'] = request.POST.get('nama')
                    m['tier'] = request.POST.get('tier')
                    m['total_miles'] = int(request.POST.get('total_miles', 0))
                    m['award_miles'] = int(request.POST.get('award_miles', 0))
                    break

            messages.success(request, f'Data member {email} berhasil diperbarui.')

        elif action == 'hapus':
            email = request.POST.get('email')

            for m in DUMMY_MEMBERS:
                if m['email'] == email:
                    DUMMY_MEMBERS.remove(m)
                    break

            messages.success(request, f'Member {email} berhasil dihapus.')

        return redirect('staff:kelola_member')

    members = DUMMY_MEMBERS

    if search:
        members = [
            m for m in members
            if search.lower() in m['nama'].lower()
            or search.lower() in m['email'].lower()
            or search.lower() in m['nomor'].lower()
        ]

    if filter_tier != 'Semua':
        members = [m for m in members if m['tier'] == filter_tier]

    paginator = Paginator(members, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'staff/kelola_member.html', {
        'members': page_obj,
        'page_obj': page_obj,
        'search': search,
        'filter_tier': filter_tier,
        'tier_choices': TIER_CHOICES,
    })

def dashboard(request):
    context = {
        'nama': 'Nisrina Alya',
        'email': 'nisrina.alya@ui.ac.id',
        'telepon': '+62-8137-0998-516',
        'kewarganegaraan': 'Indonesia',
        'tanggal_lahir': '19-09-2006',
        'id_staff': 'MOO01',
        'maskapai': 'Etihad',
        'klaim_menunggu': 15,
        'klaim_disetujui': 10,
        'klaim_ditolak': 3,
    }
    return render(request, 'staff/dashboard.html', context)

def kelola_klaim_view(request):
    filter_status = request.GET.get('status', 'Semua')
    filter_maskapai = request.GET.get('maskapai', 'Semua')

    if request.method == 'POST':
        action = request.POST.get('action')
        klaim_id = request.POST.get('klaim_id')
        if action == 'setujui':
            messages.success(request, f'Klaim {klaim_id} berhasil disetujui. Miles ditambahkan ke akun member.')
        elif action == 'tolak':
            messages.warning(request, f'Klaim {klaim_id} telah ditolak.')
        return redirect('staff:kelola_klaim')

    klaim_list = DUMMY_KLAIM_STAF
    if filter_status != 'Semua':
        klaim_list = [k for k in klaim_list if k['status'] == filter_status]
    if filter_maskapai != 'Semua':
        klaim_list = [k for k in klaim_list if k['maskapai'] == filter_maskapai]

    return render(request, 'staff/kelola_klaim.html', {
        'klaim_list': klaim_list,
        'filter_status': filter_status,
        'filter_maskapai': filter_maskapai,
        'maskapai_list': ['GA', 'QG', 'JT', 'SQ', 'MH'],
    })


@login_required_staf
def kelola_hadiah_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'tambah':
            messages.success(request, 'Hadiah baru berhasil ditambahkan.')
        elif action == 'edit':
            messages.success(request, 'Hadiah berhasil diperbarui.')
        elif action == 'hapus':
            messages.success(request, 'Hadiah berhasil dihapus.')
        return redirect('staff:kelola_hadiah')

    return render(request, 'staff/kelola_hadiah.html', {
        'hadiah_list': DUMMY_HADIAH_STAF,
        'penyedia_choices': PENYEDIA_CHOICES,
    })


@login_required_staf
def kelola_mitra_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'tambah':
            messages.success(request, 'Mitra baru berhasil didaftarkan. Entri PENYEDIA otomatis dibuat.')
        elif action == 'edit':
            messages.success(request, 'Informasi mitra berhasil diperbarui.')
        elif action == 'hapus':
            messages.warning(request, 'Mitra berhasil dihapus beserta hadiah yang disediakan.')
        return redirect('staff:kelola_mitra')

    return render(request, 'staff/kelola_mitra.html', {
        'mitra_list': DUMMY_MITRA,
    })


def laporan_view(request):
    filter_tipe = request.GET.get('tipe', 'Semua')
    active_tab = request.GET.get('tab', 'riwayat')

    transaksi = DUMMY_TRANSAKSI_LAPORAN
    if filter_tipe != 'Semua':
        transaksi = [t for t in transaksi if t['tipe'] == filter_tipe]

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'hapus_riwayat':
            messages.warning(request, 'Riwayat transaksi berhasil dihapus secara permanen.')
        return redirect('staff:laporan')

    return render(request, 'staff/laporan.html', {
        'transaksi': transaksi,
        'top_members': DUMMY_TOP_MEMBERS,
        'filter_tipe': filter_tipe,
        'active_tab': active_tab,
        'total_miles_beredar': 190000,
        'total_redeem_bulan_ini': 3000,
        'total_klaim_disetujui': 2500,
    })