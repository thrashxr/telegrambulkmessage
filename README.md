# Telegram Toplu Mesaj Gönderici Bot

Toplu mesaj gönderme botumu sonunda paylaşıyorum. Sunucunuza veya bilgisayarınıza kurup hemen kullanmaya başlayabilirsiniz :)

Bu bot sayesinde kendi telegram hesaplarınız üzerinden gruplara otomatik mesajlar gönderebilirsiniz. Hem de spam/flood limitlerine takılmamak için gerekli önlemler alınmış durumda!

## Özellikler

Botta mevcut özellikler sırası ile;

-  **Çoklu Hesap Yönetimi:** Birden fazla hesap ekleyebilir, bu hesaplar arasında geçiş yapabilir ve oturumları (session) kaydedebilirsiniz. Yani botu kapatıp açsanız bile tekrar tekrar giriş yapmanıza gerek kalmaz.
-  **Grup Yönetimi:** Hesabınızdaki grupları otomatik olarak çeker, listeler ve dilerseniz yeni gruplara link ile katılmanızı sağlar.
-  **Toplu Mesaj Gönderimi:**
   -  **Tek Seferlik:** Seçtiğiniz gruplara mesajınızı bir kez gönderir.
   -  **Döngü Modu (Loop):** Mesajınızı belirlediğiniz aralıklarla sürekli gönderir.
   -  **Resimli Mesaj:** İsterseniz mesajlarınıza resim de ekleyebilirsiniz.
-  **Ayarlanabilir Gecikmeler:** Spam'e düşmemek için grup arası ve döngü arası bekleme sürelerini (delay) kendiniz ayarlayabilirsiniz.

## Kurulum

Kurulum oldukça basit, aşağıdaki adımları takip etmeniz yeterli:

1. Öncelikle bilgisayarınızda **Python 3.8 veya üzeri** yüklü olmalıdır.
2. Proje dosyalarını indirin ve terminali açın.
3. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install telethon python-dotenv
   ```
4. `.env.example` dosyasının adını `.env` olarak değiştirin ve içine girin.
5. `API_ID` ve `API_HASH` bilgilerinizi ekleyin. (Bu bilgileri [my.telegram.org](https://my.telegram.org) adresinden alabilirsiniz).

## Kullanım

Botu başlatmak için terminale şu komutu yazmanız yeterli:

```bash
python main.py
```

Menü sizi yönlendirecektir:

1. Önce **Hesap Yönetimi**'nden giriş yapın.
2. Sonra **Grup Yönetimi**'nden mesaj göndermek istediğiniz grupları seçin (`all` yazarak hepsini seçebilirsiniz).
3. **Mesaj Gönder** menüsünden modunuzu seçip arkanıza yaslanın!

## Notlar

-  Mesajlarınız dosyaya kaydedilmiyor, her başlattığınızda yeni mesaj girebilirsiniz.
-  Premium emojileri destekler.
