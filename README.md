# **[EN] ⚽ Football Match Analyzer (Demo)**
This project is developed using AI-powered visual analysis techniques to analyze football match videos. The system:

- Detects all players, goalkeepers, referees, and technical staff on the field
-  
- Automatically separates teams based on jersey colors
- 
- Retrieves referee and team statistics from the web
- 
- Provides match score prediction based on teams’ past data via FootballGPT  

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

Last 5 Matches Details:  
  - Match Date  
  - Opponent  
  - Match Score  
  - Team Formation  
  - Summary of wins, draws, and losses in last 5 matches  

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

## ⚽ FootballGPT Match Prediction

To get a match score prediction, press the **PredictFootballMatchWithFootballGPT** button.

FootballGPT provides only the predicted score of the upcoming match based on teams’ past data, without detailed analysis.

---

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

🎯 The system successfully distinguishes Arsenal and Manchester United teams, their goalkeepers, referees, and technical staff. The interface also displays referee details, team statistics, the last 5 head-to-head matches between the two teams, and detailed last 5 matches info (scores, dates, opponents, formations).

⚡ Additionally, FootballGPT uses all this data to provide only the predicted score result for the upcoming match.
![Arsenal_Output1-ezgif com-video-to-gif-converter (1)](https://github.com/user-attachments/assets/343a71d1-bc19-495b-858e-2719a9e86ca5)










# **[TR]** ⚽ **Football Match Analyzer (Demo)**
Bu proje, yapay zekâ destekli görsel analiz teknikleri ile futbol maç videolarını analiz etmek için geliştirilmiştir. Sistem:

- Sahadaki tüm oyuncuları, kalecileri, hakemleri ve teknik ekip üyelerini tespit eder  
- Takımları forma renklerine göre otomatik olarak ayırır  
- Hakem ve takım istatistiklerini web’den çeker  
- FootballGPT ile takımların geçmiş verilerine göre maç sonucu tahmini yapar

💡 Kullanıcı sadece takım isimlerini, forma örneklerini ve hakem ismini girerek analizi başlatabilir.

---

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

- Aralarındaki Son 5 Maç (varsa)
- 
- Son 5 Maç Detayları:  
  - Maç Tarihi  
  - Rakip Takım  
  - Maç Skoru  
  - Takımın Dizilişi  
  - Son 5 maçta kazanma, beraberlik ve mağlubiyet sayılarının özeti 

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

## ⚽ FootballGPT Maç Tahmini

Maç skor tahmini yapılmak istenirse **PredictFootballMatchWithFootballGPT** butonuna basılmalıdır.

FootballGPT, takımların geçmiş verilerine göre sadece gelecek maçın tahmini skorunu verir, analiz yapmaz.

---

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

🎯 Sistem Kayserispor ve Samsunspor takımlarını, kalecilerini, hakem ve teknik ekiplerini başarıyla ayırt eder. Arayüzde ayrıca hakem bilgileri, takım istatistikleri, iki takım arasındaki son 5 maç ve detaylı son 5 maç bilgileri (skorlar, tarihler, rakipler, dizilişler) gösterilir.

⚡ Ayrıca FootballGPT, tüm bu verileri kullanarak gelecekteki maç için sadece tahmini skor sonucunu sunar.

![Output_Last1-ezgif com-video-to-gif-converter (1)](https://github.com/user-attachments/assets/e2a5221c-a528-4a98-8795-47164a5bd64a)



