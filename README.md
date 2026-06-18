# iPhone Fotoğraf / Video Aktarma Uygulaması Kullanım Notu

iDropFolder, iPhone’daki seçtiğiniz fotoğraf ve videoları Windows 11 bilgisayardaki bir klasöre kablosuz olarak yüklemek için hazırlanmıştır.

Uygulama sadece şu işleri yapar:

* iPhone’dan fotoğraf ve video yükleme
* Yüklenen dosyaları uygulamanın bulunduğu klasörde saklama
* Klasör içeriğini web sayfasında listeleme

Uygulamada silme, düzenleme veya başka klasörlere erişme özelliği yoktur.

---

## 1. Gerekli Program

Bilgisayarda Python kurulu olmalıdır.

Python kurulu mu kontrol etmek için:

1. Başlat menüsüne tıklayın.
2. `cmd` yazın.
3. Komut İstemi’ni açın.
4. Şu komutu yazın:

```bat
python --version
```

Eğer Python sürümü görünüyorsa kurulu demektir.

Örnek:

```bat
Python 3.12.4
```

Python kurulu değilse Python kurulmalıdır.

---

## 2. Uygulama Klasörünü Hazırlama

Bilgisayarda bir klasör oluşturun.

Örnek:

```bat
E:\iphone_photo_al
```

Uygulama dosyaları bu klasörün içinde olmalıdır:

```text
app.py
baslat.bat
requirements.txt
```

Fotoğraf ve videolar da bu klasöre yüklenecektir.

---

## 3. Sanal Ortam Oluşturma

İlk kurulumda bir kez yapılır.

Klasörde boş bir yere sağ tıklayın ve Terminal veya Komut İstemi açın.

Sonra şu komutları sırayla çalıştırın:

```bat
cd E:\iphone_photo_al
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Bu işlem uygulamanın ihtiyaç duyduğu paketleri kurar.

---

## 4. Parola Ayarlama

`baslat.bat` dosyasını Not Defteri ile açın.

Şu satırı bulun:

```bat
set UPLOAD_PASSWORD=123456
```

Buradaki `123456` yerine kendi parolanızı yazın.

Örnek:

```bat
set UPLOAD_PASSWORD=BenimGucluSifrem_2026
```

Bu parola, iPhone’dan web sayfasına girerken kullanılacaktır.

Kullanıcı adı sorulursa boş bırakılabilir.

---

## 5. Uygulamayı Başlatma

Uygulamayı başlatmak için `baslat.bat` dosyasına çift tıklayın.

Siyah bir terminal penceresi açılacaktır.

Ekranda şuna benzer bilgiler görürsünüz:

```text
GÜVENLİ IPHONE FOTOĞRAF / VİDEO UPLOAD SUNUCUSU

Bilgisayardan: http://127.0.0.1:5000
iPhone'dan:    http://192.168.1.45:5000
```

Burada önemli olan adres `iPhone'dan` yazan adrestir.

Örnek:

```text
http://192.168.1.45:5000
```

---

## 6. iPhone’dan Bağlanma

iPhone ve bilgisayar aynı Wi-Fi ağına bağlı olmalıdır.

iPhone’da Safari’yi açın.

Terminal ekranında görünen iPhone adresini Safari’ye yazın.

Örnek:

```text
http://192.168.1.45:5000
```

Parola ekranı gelirse:

* Kullanıcı adı: boş bırakılabilir
* Parola: `baslat.bat` içine yazdığınız parola

---

## 7. Fotoğraf ve Video Yükleme

Web sayfası açıldığında:

1. Dosya seçme alanına dokunun.
2. iPhone’da Fotoğraf Arşivi’ni seçin.
3. Yüklemek istediğiniz fotoğraf ve videoları seçin.
4. Seçim tamamlandıktan sonra web sayfasına dönün.
5. Büyük mavi `SEÇİLENLERİ YÜKLE` butonuna basın.

Yükleme başladıktan sonra bilgisayardaki terminal ekranında hareketleri görebilirsiniz.

Örnek:

```text
UPLOAD BAŞLADI
Gelen dosya sayısı: 12
KAYDEDİLDİ | IMG_1234.HEIC
KAYDEDİLDİ | IMG_1235.MOV
UPLOAD BİTTİ
```

Yüklenen dosyalar uygulamanın bulunduğu klasöre kaydedilir.

---

## 8. Klasör İçeriğini Görme

Web sayfasında “Klasör İçeriği” bölümü vardır.

Yüklenen fotoğraf ve videolar burada listelenir.

Dosya adına tıklayarak dosyayı tarayıcıda açabilirsiniz.

---

## 9. Uygulamayı Kapatma

İşiniz bitince bilgisayardaki terminal penceresine gelin.

Klavyeden şu tuşlara basın:

```text
CTRL + C
```

Sonra pencereyi kapatabilirsiniz.

Uygulama kapatılınca iPhone artık bu adrese bağlanamaz.

---

## 10. Dikkat Edilmesi Gerekenler

Bu uygulamayı sadece güvenilir ağlarda kullanın.

Önerilen kullanım yerleri:

* Ev Wi-Fi ağı
* Ofis Wi-Fi ağı
* Kendi telefon hotspot’unuz

Kullanılmaması önerilen yerler:

* Kafe Wi-Fi
* Otel Wi-Fi
* Havalimanı Wi-Fi
* Herkese açık ağlar

Windows Güvenlik Duvarı izin sorarsa, özel/güvenilir ağ için izin verebilirsiniz.

---

## 11. Video Yükleme Sorunları

Videolar büyük boyutlu olabilir.

Eğer yükleme sırasında “çok büyük” hatası alınırsa `baslat.bat` dosyasındaki şu satır yükseltilebilir:

```bat
set MAX_UPLOAD_MB=20000
```

Bu değer MB cinsindendir.

Örnek:

```text
20000 MB yaklaşık 20 GB demektir.
```

---

## 12. Sorun Giderme

### Sayfa iPhone’da açılmıyor

Kontrol edin:

* iPhone ve bilgisayar aynı Wi-Fi ağında mı?
* `baslat.bat` çalışıyor mu?
* Terminal ekranında iPhone adresi görünüyor mu?
* Windows Güvenlik Duvarı izin verdi mi?

---

### Parola kabul edilmiyor

Kontrol edin:

* Parola `baslat.bat` içinde doğru mu?
* Uygulamayı parola değişikliğinden sonra kapatıp yeniden açtınız mı?

---

### Dosya yüklenmiyor

Kontrol edin:

* Dosya türü destekleniyor mu?
* Video çok büyük mü?
* Terminal ekranında hata yazıyor mu?

Desteklenen dosya türleri:

```text
.jpg
.jpeg
.png
.gif
.webp
.heic
.heif
.mov
.mp4
.m4v
.avi
.mkv
```

---

### Terminal penceresi hemen kapanıyor

Uygulamayı çift tıklamak yerine Komut İstemi’nden çalıştırın.

```bat
cd /d E:\iphone_photo_al
baslat.bat
```

Böylece hata mesajını görebilirsiniz.

---

## 13. Kısa Kullanım Özeti

Her kullanımda yapılacaklar:

1. `baslat.bat` dosyasına çift tıkla.
2. Terminalde yazan iPhone adresini kopyala.
3. iPhone’da Safari’ye bu adresi yaz.
4. Parolayı gir.
5. Fotoğraf ve videoları seç.
6. `SEÇİLENLERİ YÜKLE` butonuna bas.
7. İş bitince bilgisayarda `CTRL + C` ile kapat.


## License

This project is licensed under the PolyForm Noncommercial License 1.0.0.

iDropFolder is source-available for non-commercial use only. Commercial use is not permitted without prior written permission from the author.

Copyright (c) 2026 Yusuf Özdaş.
