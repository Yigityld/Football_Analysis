⚽ Football Match Analyzer (Demo)
Bu proje, futbol karşılaşmalarının analizini gerçekleştirmek için yapay zekâ destekli görsel analiz teknikleri ile geliştirilmiştir. Sistem, bir futbol maç videosu üzerinden:
Sahadaki tüm oyuncu, kaleci, hakem ve teknik ekip üyelerini tespit eder
Takımları forma rengine göre otomatik olarak ayırır
Hakem bilgilerini ve takım istatistiklerini web'den çeker

💡 Kullanıcı, sadece takım isimlerini, forma örneklerini ve hakem isimlerini girerek analizi başlatabilir.

🧠 Tanımlanan Sınıflar (Classes)

Sistem, YOLOv8 nesne tespiti modeli ile 6 farklı sınıfı tanımlar:
🧤 Kaleci
👟 Oyuncu
🟨 Orta Hakem
🟥 Yan Hakem
⚽ Top
🧠 Teknik Ekip

📊 Otomatik Bilgi Çekimi

🟦 Takım Bilgileri

Girilen takım isimlerine göre:
Takım Logosu
Lig bilgisi
Lig sıralaması
Ortalama yaş
Takım değeri
Stadyum adı ve kapasitesi
Kazanılan kupalar
Transfermarkt'tan çekilerek arayüzde gösterilir.

🟨 Hakem Bilgileri

Girilen hakem adına göre:
Hakem fotoğrafı
Doğum yeri
Doğum Tarihi
Son sezon kart istatistikleri (Sarı / Kırmızı / İkinci sarıdan kırmızı)
Son sezon penaltı istatistiği
Maç sayısı
bilgileri yine Transfermarkt üzerinden alınır.

🎮 Kullanım Adımları

1️⃣ Video Yolunu Güncelleyin
main.py dosyasındaki video_path değişkenini düzenleyin:

video_path = "videos/match-footage.mp4"

2️⃣ Arayüzü Başlatın

Takım A ve Takım B isimlerini girin
Her takım için forma örneği seçin
Hakem adını yazın
Sistem, forma renklerini analiz ederek takımları sınıflandırır. Hakem bilgilerini Transfermarkt’tan çeker.

3️⃣ Özeti Başlatın ve Güncelleyin

Özeti Başlat butonuyla analiz başlar
Güncelle butonuyla sahadaki taktiksel harita güncellenir
🛠 Eğer takım eşleşmeleri yanlışsa sadece takım isimlerini değiştirmeniz yeterlidir.

📽️ Demo: Analiz Çıktısı

🔍 Taktiksel Harita ve Oyuncu Takibi
🎯 Aşağıda sistemin Kayserispor ve Samsunspor takımlarını, kalecileri, hakem ve teknik ekibi başarıyla ayırt ettiğini görebilirsiniz.
![Gif_Çıktı (1)](https://github.com/user-attachments/assets/41fc0c5f-764d-439c-bb14-7577545c9614)


