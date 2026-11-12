"""Generate reviewable SVG wireframes. Run from any directory with Python 3."""
from pathlib import Path
from html import escape
import json
import textwrap

OUT = Path(__file__).resolve().parent
SCREENS = {
    'login': ('Giriş yap', 'UC-01 · FR-02–FR-06', [
        ('Portal kimliği', 'Okul portalındaki hesabının kimliği.'),
        ('Şifre', 'Şifre yöneticisi ve yapıştırma desteklenir.'),
        ('Giriş yap', 'Geçerli hesap → rolün başlangıç sayfası.'),
        ('İlk kez mi geliyorsun?', 'Hesabını etkinleştir → etkinleştirme ekranı.'),
    ], 'Hatalı kimlik veya şifre: aynı hata mesajı. Alan değerlerini koru.'),
    'activation': ('Hesabını etkinleştir', 'UC-01 · FR-02', [
        ('Portal kimliği', 'Yalnızca portalda bulunan hesaplar.'),
        ('Yeni şifre', 'Şifre kuralları erişim tasarımında belirlenecek.'),
        ('Hesabını etkinleştir', 'Başarılı işlem → rolün başlangıç sayfası.'),
        ('Zaten bir hesabın var mı?', 'Girişe dön.'),
    ], 'Portal hesabı bulunamadı veya hesap zaten etkin. Açık kayıt sunulmaz.'),
    'courses': ('Derslerim', 'UC-03 · FR-10', [
        ('Ders seçimi', 'Ders adı / üniteler / konular. Veriler portaldan gelir.'),
        ('Ders çalışma alanı', 'Seçili ders: kaynaklar, soru-cevap, özet, sınav.'),
        ('Haftalık çalışma planı', 'Gelişime açık konular ve çalışma adımları.'),
    ], 'Ders yoksa boş durum. Portal hatasında son veri ve tarihi göster.'),
    'sources': ('Kaynaklarım', 'UC-04 · FR-13–FR-17', [
        ('Ders seç', 'Kaynaklar bir derse bağlıdır.'),
        ('PDF yükle', 'En fazla 20 MB / dosya ve 20 kaynak / ders.'),
        ('Kaynak listesi', 'Dosya adı · işleniyor / hazır / başarısız · sil.'),
        ('Çalışmada kullan', 'Yalnızca hazır kaynaklar seçilebilir.'),
    ], 'Tür, boyut, okunabilir metin ve sayı sınırı için ayrı mesajlar. Silme onayı.'),
    'questions': ('Soru sor', 'UC-05 · FR-18–FR-20, FR-37', [
        ('Ders ve hazır kaynaklar', 'Soru için kullanılacak kaynakları seç.'),
        ('Sorun', 'Etiketli çok satırlı alan ve Gönder düğmesi.'),
        ('Yanıt ve atıflar', 'Türkçe yanıt. Atıf → ilgili kaynak pasajı.'),
        ('Kaynak pasajı', 'PDF sayfası; telefon ekranında ayrı görünüm.'),
    ], 'Kaynakta yanıt yok / limit ve sıfırlama tarihi / servis hatası. Geçmiş: Should.'),
    'summaries': ('Özet oluştur', 'UC-06 · FR-21, FR-25', [
        ('Ders ve hazır kaynaklar', 'Özete dahil edilecek kaynakları seç.'),
        ('Özet oluştur', 'İş başlatılır; bekliyor / çalışıyor gösterilir.'),
        ('Özet hazır', 'PDF indir / aç. Telefonda dosya açılışı.'),
    ], 'Başarısız veya 2 dakikayı geçen iş: hata ve tekrar deneme.'),
    'quiz': ('Kısa sınav', 'UC-07 · FR-22–FR-24', [
        ('Ders ve hazır kaynaklar', 'Kaynağa dayalı 5–10 çoktan seçmeli soru.'),
        ('Soru ve seçenekler', 'Radyo düğmeleri; görünür soru ve grup etiketi.'),
        ('Yanıtları gönder', 'Göndermeden doğru yanıtı gösterme.'),
        ('Sonuç ve atıflar', 'Puan, doğru yanıtlar, konular ve kaynak pasajları.'),
    ], 'Üretim hatası ve iş durumu gösterilir. Boş yanıt politikası ekipçe doğrulanmalı.'),
    'planner': ('Haftalık çalışma planım', 'UC-08 · FR-27–FR-31', [
        ('Hafta ve veri tarihi', 'Plan haftası ve kullanılan notların tarihi.'),
        ('Odaklanılacak konu', 'Başarı oranı ve neden gelişime açık olduğu.'),
        ('Çalışma süresi', 'Konu başına saat ve önerilen çalışma adımları.'),
        ('Diğer konular', 'Gelişime açık konuların sıralı listesi.'),
    ], 'Zayıf konu yoksa bunu açıkla. AI adımları yoksa varsayılan adımlar.'),
}
NAV = [('courses', 'Derslerim'), ('sources', 'Kaynaklarım'), ('questions', 'Soru sor'), ('summaries', 'Özetlerim'), ('quiz', 'Kısa sınavlar'), ('planner', 'Çalışma planım')]

def rect(x, y, w, h, fill='#fff', radius=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="#b7bfcc"/>'

def text(x, y, value, size=16, color='#263248', weight=400):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'

def lines(x, y, value, width, size=14):
    return ''.join(text(x, y + n * (size + 7), line, size, '#46536a') for n, line in enumerate(textwrap.wrap(value, width)))

for key, (title, refs, blocks, note) in SCREENS.items():
    for mode, w, h in [('desktop', 1440, 900), ('phone', 360, 1080)]:
        phone = mode == 'phone'
        x = 20 if phone else 290
        content_w = w - x - (20 if phone else 60)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">', f'<title id="title">{escape(title)} — {mode} wireframe</title>', '<desc id="desc">Proposed interface, not an implemented feature. Boxes describe controls and states.</desc>', rect(0, 0, w, h, '#f5f6f8', 0)]
        parts += [rect(0, 0, w, 80, '#fff', 0), text(24, 48, 'Chiron', 26, weight=700), text(w - (110 if phone else 240), 46, 'TASLAK' if phone else 'WIREFRAME · TASLAK', 12)]
        if not phone:
            parts += [rect(0, 80, 230, h-80, '#fff', 0), text(26, 130, 'ÇALIŞMA ALANI', 12)]
            for n, (dest, label) in enumerate(NAV):
                parts.append(f'<a href="index.html#{dest}" target="_top">' + rect(16, 160+n*62, 198, 48, '#e8ebf0' if dest == key else '#fff') + text(30, 190+n*62, label, 15) + '</a>')
        else:
            parts += [rect(20, 96, 320, 46, '#fff'), text(34, 124, 'Menü / geçerli ders / rol', 14)]
        y = 180 if phone else 140
        parts += [text(x, y, title, 25 if phone else 34, weight=700), text(x, y+32, refs, 12), text(x, y+61, 'Önerilen ekran düzeni · gerçek veri içermez', 12)]
        y += 90
        for index, (name, detail) in enumerate(blocks):
            height = 116 if phone else 112
            parts += [rect(x, y, content_w, height), text(x+16, y+30, f'{index+1}. {name}', 16, weight=700), lines(x+16, y+57, detail, 34 if phone else 100)]
            y += height + 16
        parts += [rect(x, y+8, content_w, 132 if phone else 98, '#edf0f4'), text(x+16, y+37, 'Alternatif / hata durumları', 14, weight=700), lines(x+16, y+62, note, 34 if phone else 110, 13)]
        parts += [text(x, h-26, 'WBS-11.3 · Faruk Özbek · 12.11.2026 · Taslak', 11), '</svg>']
        (OUT / f'{key}-{mode}.svg').write_text(''.join(parts), encoding='utf-8')

manifest = {key: {'title': value[0], 'refs': value[1]} for key, value in SCREENS.items()}
(OUT / 'screens.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(f'Generated {len(SCREENS)*2} SVG wireframes and screens.json')
