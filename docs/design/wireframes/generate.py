"""Generate reviewable SVG wireframes. Run from any directory with Python 3."""
from pathlib import Path
from html import escape
import json
import textwrap

OUT = Path(__file__).resolve().parent
SCREENS = {
    'login': ('Giriş yap', 'UC-01 · FR-03–FR-06', [
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
    'quiz': ('Kısa sınav', 'UC-07 · FR-22–FR-25', [
        ('Ders ve hazır kaynaklar', 'Kaynağa dayalı 5–10 çoktan seçmeli soru.'),
        ('Soru ve seçenekler', 'Radyo düğmeleri; görünür soru ve grup etiketi.'),
        ('Yanıtları gönder', 'Göndermeden doğru yanıtı gösterme.'),
        ('Sonuç ve atıflar', 'Puan, doğru yanıtlar, konular ve kaynak pasajları.'),
    ], 'Üretim hatası: mesaj ve tekrar deneme (FR-25). Boş yanıt politikası ekipçe doğrulanmalı.'),
    'planner': ('Haftalık çalışma planım', 'UC-08 · FR-27–FR-31', [
        ('Hafta ve veri tarihi', 'Plan haftası ve kullanılan notların tarihi.'),
        ('Odaklanılacak konu', 'Başarı oranı ve neden gelişime açık olduğu.'),
        ('Çalışma süresi', 'Konu başına saat ve önerilen çalışma adımları.'),
        ('Diğer konular', 'Gelişime açık konuların sıralı listesi.'),
    ], 'Zayıf konu yok: kaynaklarından kısa sınav öner (UC-08 A1). Not yok: plan notlar gelince hazırlanır. AI adımları yok: varsayılan adımlar.'),
}
NAV = [('courses', 'Derslerim'), ('sources', 'Kaynaklarım'), ('questions', 'Soru sor'), ('summaries', 'Özetlerim'), ('quiz', 'Kısa sınavlar'), ('planner', 'Çalışma planım')]

def rect(x, y, w, h, fill='#fff', radius=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="#b7bfcc"/>'

def text(x, y, value, size=16, color='#263248', weight=400):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'

def lines(x, y, value, width, size=14):
    return ''.join(text(x, y + n * (size + 7), line, size, '#46536a') for n, line in enumerate(textwrap.wrap(value, width)))

def control(x, y, w, label, fill='#e8ebf0'):
    return rect(x, y, w, 44, fill, 6) + text(x+12, y+28, label, 14, weight=600)

def field(x, y, w, label, value, height=44):
    return (text(x, y+14, label, 14, weight=600) +
            rect(x, y+24, w, height, '#fff', 6) +
            lines(x+12, y+50, value, max(20, int((w-24)/8)), 14))

def detailed_screen(key, x, y, w, phone):
    """Draw illustrative controls. These SVG controls do not perform app actions."""
    parts = []
    if key == 'sources':
        parts += [field(x, y, w if phone else 380, 'Ders', 'Kimya 10  ▾')]
        y += 84
        parts += [control(x, y, 150, '+ PDF yükle'),
                  text(x, y+68, 'En fazla 20 MB / dosya · 20 kaynak / ders', 13)]
        y += 92
        parts += [text(x, y, 'Kaynaklar · örnek durumlar', 16, weight=700)]
        y += 18
        rows = [('Kimya notları.pdf', 'Hazır', True),
                ('Konu özeti.pdf', 'İşleniyor', False),
                ('Tarama.pdf', 'Başarısız: metin yok', False)]
        for name, status, ready in rows:
            height = 100 if phone else 72
            parts += [rect(x, y, w, height), rect(x+12, y+16, 20, 20, '#fff' if ready else '#edf0f4', 3)]
            parts += [text(x+15, y+32, '✓' if ready else '–', 16)]
            parts += [text(x+44, y+31, name, 14, weight=600),
                      text(x+44, y+55, status, 13)]
            parts += [control(x+w-72, y+(48 if phone else 14), 60, 'Sil', '#fff')]
            y += height+12
        parts += [control(x, y, w if phone else 280, 'Seçili kaynakla soru sor →')]
        return parts, y+60
    if key == 'questions':
        parts += [field(x, y, w if phone else 480, 'Ders ve hazır kaynak', 'Kimya 10 · Kimya notları.pdf  ▾')]
        y += 84
        parts += [field(x, y, w, 'Sorun', 'Kimyasal bağ nedir?', 64)]
        y += 104
        parts += [control(x, y, 120, 'Gönder')]
        y += 64
        answer_h = 142 if phone else 126
        parts += [rect(x, y, w, answer_h), text(x+16, y+28, 'Yanıt · örnek yerleşim', 16, weight=700),
                  lines(x+16, y+55, 'Kimyasal bağ, atomları bir arada tutan etkileşimdir. [1]', 33 if phone else 90)]
        parts += ['<a href="#citation-passage">'+control(x+16, y+(86 if phone else 76), min(w-32, 300), '[1] Kimya notları.pdf · s. 3', '#fff')+'</a>']
        y += answer_h+16
        passage_h = 142 if phone else 94
        parts += ['<g id="citation-passage">', rect(x, y, w, passage_h, '#edf0f4'),
                  text(x+16, y+28, 'Kaynak pasajı · sayfa 3', 16, weight=700),
                  lines(x+16, y+56, '“Atomları bir arada tutan etkileşimler kimyasal bağ olarak adlandırılır.”', 33 if phone else 90),
                  text(x+16, y+passage_h-20, 'Örnek pasaj; gerçek dosya veya AI yanıtı değil.', 12), '</g>']
        return parts, y+passage_h+16
    parts += [text(x, y+14, 'Hafta: 9–15 Kasım 2026', 14, weight=600),
              text(x, y+39, 'Notların tarihi: 9 Kasım · örnek plan', 13)]
    y += 62
    entries = [('Kimyasal bağlar', '%45 · %60 altında', '2 saat'),
               ('Atomlar', '%70 · sınıf ortalaması %90', '1 saat')]
    if not phone:
        parts += [rect(x, y, w, 44, '#e8ebf0'), text(x+16, y+28, 'Konu / seçilme nedeni', 14, weight=700),
                  text(x+370, y+28, 'Haftalık süre', 14, weight=700), text(x+520, y+28, 'Çalışma adımları', 14, weight=700)]
        y += 44
    for topic, reason, hours in entries:
        height = 196 if phone else 100
        parts += [rect(x, y, w, height), text(x+16, y+28, topic, 16, weight=700),
                  text(x+16, y+53, reason, 13)]
        if phone:
            parts += [text(x+16, y+78, f'Haftalık süre: {hours}', 14, weight=600),
                      text(x+16, y+103, '1. Konuyu tekrar et', 14), text(x+16, y+126, '2. Alıştırma sorularını çöz', 14),
                      control(x+16, y+140, w-32, 'Kaynakları ve sınavı aç →', '#fff')]
        else:
            parts += [text(x+370, y+28, hours, 14), text(x+520, y+28, '1. Konuyu tekrar et · 2. Soruları çöz', 14),
                      control(x+520, y+42, 300, 'Kaynakları ve sınavı aç →', '#fff')]
        y += height+12
    return parts, y


for key, (title, refs, blocks, note) in SCREENS.items():
    for mode, w, h in [('desktop', 1440, 900), ('phone', 360, 1080)]:
        phone = mode == 'phone'
        x = 20 if phone else 290
        content_w = w - x - (20 if phone else 60)
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">', f'<title id="title">{escape(title)} — {mode} wireframe</title>', '<desc id="desc">Proposed interface, not an implemented feature. Illustrative controls and notes describe the proposed states. No live student data.</desc>', rect(0, 0, w, h, '#f5f6f8', 0)]
        parts += [rect(0, 0, w, 80, '#fff', 0), text(24, 48, 'Chiron', 26, weight=700), text(w - (110 if phone else 240), 46, 'TASLAK' if phone else 'WIREFRAME · TASLAK', 12)]
        if not phone:
            parts += [rect(0, 80, 230, h-80, '#fff', 0), text(26, 130, 'ÇALIŞMA ALANI', 12)]
            for n, (dest, label) in enumerate(NAV):
                parts.append(f'<a href="index.html#{dest}" target="_top">' + rect(16, 160+n*62, 198, 48, '#e8ebf0' if dest == key else '#fff') + text(30, 190+n*62, label, 15) + '</a>')
        else:
            parts += [rect(20, 96, 320, 46, '#fff'), text(34, 124, 'Menü / geçerli ders / rol', 14)]
        y = 180 if phone else 140
        title_lines = textwrap.wrap(title, 24) if phone else [title]
        for line in title_lines:
            parts.append(text(x, y, line, 25 if phone else 34, weight=700))
            y += 30 if phone else 40
        parts += [text(x, y+2, refs, 12), text(x, y+27, 'Önerilen ekran düzeni · gerçek veri içermez', 12)]
        y += 56
        if key in {'sources', 'questions', 'planner'}:
            controls, y = detailed_screen(key, x, y, content_w, phone)
            parts.extend(controls)
        for index, (name, detail) in enumerate([] if key in {'sources', 'questions', 'planner'} else blocks):
            height = 116 if phone else 112
            parts += [rect(x, y, content_w, height), text(x+16, y+30, f'{index+1}. {name}', 16, weight=700), lines(x+16, y+57, detail, 34 if phone else 100)]
            y += height + 16
        parts += [rect(x, y+8, content_w, 152 if phone else 98, '#edf0f4'), text(x+16, y+37, 'Alternatif / hata durumları', 14, weight=700), lines(x+16, y+62, note, 34 if phone else 110, 13)]
        parts += [text(x, h-26, 'WBS-11.3 · Faruk Özbek · 13.11.2026 · Taslak', 11), '</svg>']
        (OUT / f'{key}-{mode}.svg').write_text(''.join(parts), encoding='utf-8')

manifest = {key: {'title': value[0], 'refs': value[1]} for key, value in SCREENS.items()}
(OUT / 'screens.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(f'Generated {len(SCREENS)*2} SVG wireframes and screens.json')
