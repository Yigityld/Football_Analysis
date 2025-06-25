# **[EN] ⚽ Football Match Analyzer (Demo)**
This project is developed using AI-powered visual analysis techniques to analyze football match footage. The system performs the following on a football match video:

Detects all players, goalkeepers, referees, and technical staff on the field

Automatically separates teams based on jersey colors

Retrieves referee and team statistics from the web

💡 The user only needs to enter the team names, jersey samples, and referee name to start the analysis.

## **🧠 Defined Classes**
Using the YOLOv8 object detection model, the system identifies 6 different classes:
🧤 Goalkeeper
👟 Player
🟨 Main Referee
🟥 Assistant Referee
⚽ Ball
🧠 Technical Staff

## **📊 Automatic Data Retrieval**

**🟦 Team Information**

Based on the entered team names:

Team Logo

League Info

League Ranking

Average Age

Team Value

Stadium Name & Capacity

Trophies Won

Last 5 Head-to-Head Matches (if available)

Information is retrieved from Transfermarkt and shown on the interface.

**🟨 Referee Information**

Based on the entered referee name:

Referee Photo

Place of Birth

Date of Birth

Card Statistics for Last Season (Yellow / Red / Second Yellow-Red)

Penalty Stats for Last Season

Number of Matches

This data is also pulled from Transfermarkt.

## **🎮 Usage Steps**

**1️⃣ Update the Video Path**

In main.py, edit the video_path variable:

video_path = "videos/match-footage.mp4"

**2️⃣ Launch the Interface**

Enter Team A and Team B names

Select jersey samples for both teams

Enter referee name

The system classifies teams based on jersey color analysis and fetches referee info from Transfermarkt.

**3️⃣ Start and Update the Summary**

Click the Start Summary button to begin the analysis

Use the Update button to refresh the tactical map

**🛠 If team assignments are incorrect, just change the team names.**

## **📽️ Demo: Analysis Output**

**🔍 Tactical Map and Player Tracking**
🎯 Below you can see how the system successfully distinguishes Arsenal and Manchester United teams, their goalkeepers, referees, and staff member. The interface also displays referee details, team stats, and the last 5 head-to-head matches between Arsenal and Manchester United.
![OutputEn](https://github.com/user-attachments/assets/4bc8bb6d-fe91-46f2-b0d9-d606078a9bf9)









# **[TR]** ⚽ **Football Match Analyzer (Demo)**
Bu proje, futbol karşılaşmalarının analizini gerçekleştirmek için yapay zekâ destekli görsel analiz teknikleri ile geliştirilmiştir. Sistem, bir futbol maç videosu üzerinden:
Sahadaki tüm oyuncu, kaleci, hakem ve teknik ekip üyelerini tespit eder
Takımları forma rengine göre otomatik olarak ayırır
Hakem bilgilerini ve takım istatistiklerini web'den çeker

💡 Kullanıcı, sadece takım isimlerini, forma örneklerini ve hakem isimlerini girerek analizi başlatabilir.

## 🧠 **Tanımlanan Sınıflar (Classes)**

Sistem, YOLOv8 nesne tespiti modeli ile 6 farklı sınıfı tanımlar:

🧤 Kaleci

👟 Oyuncu

🟨 Orta Hakem

🟥 Yan Hakem

⚽ Top

🧠 Teknik Ekip

## 📊 **Otomatik Bilgi Çekimi**

🟦 **Takım Bilgileri**

Girilen takım isimlerine göre:

-Takım Logosu

-Lig bilgisi

-Lig sıralaması

-Ortalama yaş

-Takım değeri

-Stadyum adı ve kapasitesi

-Kazanılan kupalar

- İki takımın aralarında (varsa)son 5 Maç Sonucu 

Transfermarkt'tan çekilerek arayüzde gösterilir.

🟨 **Hakem Bilgileri**

Girilen hakem adına göre:

-Hakem fotoğrafı

-Doğum yeri

-Doğum Tarihi

-Son sezon kart istatistikleri (Sarı / Kırmızı / İkinci sarıdan kırmızı)

-Son sezon penaltı istatistiği

-Maç sayısı

bilgileri yine Transfermarkt üzerinden alınır.

## 🎮 **Kullanım Adımları**

1️⃣**Video Yolunu Güncelleyin**

main.py dosyasındaki video_path değişkenini düzenleyin:

video_path = "videos/match-footage.mp4"

2️⃣**Arayüzü Başlatın**

Takım A ve Takım B isimlerini girin
Her takım için forma örneği seçin
Hakem adını yazın
Sistem, forma renklerini analiz ederek takımları sınıflandırır. Hakem bilgilerini Transfermarkt’tan çeker.

3️⃣ **Özeti Başlatın ve Güncelleyin**

Özeti Başlat butonuyla analiz başlar
Güncelle butonuyla sahadaki taktiksel harita güncellenir
**🛠 Eğer takım eşleşmeleri yanlışsa sadece takım isimlerini değiştirmeniz yeterlidir.**

## 📽️ **Demo: Analiz Çıktısı**

🔍 **Taktiksel Harita ve Oyuncu Takibi**

🎯 Aşağıda sistemin Kayserispor ve Samsunspor takımlarını, kalecileri, hakem ve teknik ekibi başarıyla ayırt ettiğini aryıca arayüzde hakem bilgilerini, takım bilgilerini, Kayserispor ve Samsunspor arasındaki son 5 maçı da görebilirsiniz.
![OutputTR (1)](https://github.com/user-attachments/assets/3df6d701-4186-48b5-8d07-b9a86b6367b1)



