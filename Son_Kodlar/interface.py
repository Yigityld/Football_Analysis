from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QSpacerItem, QSizePolicy, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import sys
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import Gpt_area

def search_team_url(team_name):
    query = team_name.replace(" ", "+")
    search_url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.select("a[href*='/startseite/verein/']")
    for a in results:
        img = a.find("img")
        if img and img.get("alt"):
            alt_text = img["alt"].strip().lower()
            if team_name.lower() in alt_text:
                return "https://www.transfermarkt.com.tr" + a["href"]
        else:
            if a.text.strip().lower() == team_name.lower():
                return "https://www.transfermarkt.com.tr" + a['href']
    if results:
        return "https://www.transfermarkt.com.tr" + results[0]['href']
    return None


def get_team_id_from_url(team_url):
    match = re.search(r"/verein/(\d+)", team_url)
    if match:
        return match.group(1)
    return None


def find_team_id(team_name):
    url = search_team_url(team_name)
    if url is None:
        return None
    return get_team_id_from_url(url)


def temizle_takim_adi(adi):
    return re.sub(r"\(.*?\)", "", adi).strip().lower()


def get_match_result_emoji(team_score, opponent_score):
    if team_score > opponent_score:
        return "✅"  # galibiyet
    elif team_score == opponent_score:
        return "🤝"  # beraberlik
    else:
        return "❌"  # mağlubiyet

def team_name_Temizle(team_name):
    name = team_name.lower().strip()

    import re
    name = re.sub(r'\bfc\b', '', name)
    name = name.strip()
    return name

# 2. Takımın son 5 maçını (diziliş + skor) getir
def get_team_last_5_matches_with_tactics(team_name):

    def fetch_matches_from_url(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Fikstür sayfası açılamadı.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find("div", class_="responsive-table").find("tbody")
        if not tbody:
            print("Maç tablosu bulunamadı.")
            return []

        matches = []
        rows = tbody.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if not cols or len(cols) < 10:
                continue
            try:
                tarih = cols[1].get_text(strip=True)
                skor = cols[-1].get_text(strip=True)
                parts = skor.split(":")
                rakip = cols[6].get_text(strip=True)
                emoji = ""  # Her döngüde sıfırla
                # team_deneme = team_name.lower.split(" ")
                if temizle_takim_adi(rakip) == team_name_Temizle(team_name):
                    rakip = cols[4].get_text(strip=True)
                    if len(parts) == 2:
                        rakip_gol, takim_gol = int(parts[0]), int(parts[1])
                        emoji = get_match_result_emoji(takim_gol, rakip_gol)
                else:
                    if len(parts) == 2:
                        takim_gol, rakip_gol = int(parts[0]), int(parts[1])
                        emoji = get_match_result_emoji(takim_gol, rakip_gol)

                dizilis = cols[-4].get_text(strip=True)
                if re.match(r"\d+:\d+", skor):
                    matches.append({
                        "tarih": tarih,
                        "rakip": rakip,
                        "sonuc": skor,
                        "dizilis": dizilis if dizilis else "Yok",
                        "emoji": emoji
                    })
            except Exception:
                continue

            if len(matches) == 500:
                break

        return matches

    team_url = search_team_url(team_name)
    if not team_url:
        print("Takım bulunamadı:", team_name)
        return []
    team_id = get_team_id_from_url(team_url)
    if not team_id:
        print("Takım ID bulunamadı:", team_name)
        return []

    team_url_slug = team_name.lower().replace(" ", "-")
    base_url = f"https://www.transfermarkt.com.tr/{team_url_slug}/spielplandatum/verein/{team_id}/plus/1"

    matches = fetch_matches_from_url(base_url)

    if len(matches) < 500:
        alt_url = f"https://www.transfermarkt.com.tr/{team_url_slug}/spielplandatum/verein/{team_id}/saison_id/2024/plus/1"
        matches = fetch_matches_from_url(alt_url)

    last_5 = matches[-5:][::-1]

    return last_5


def get_last_matches(team_a, team_b):

    team_a_id = find_team_id(team_a)
    team_b_id = find_team_id(team_b)
    if not team_a_id or not team_b_id:
        return []

    url = f"https://www.transfermarkt.com.tr/vergleich/bilanzdetail/verein/{team_a_id}/gegner_id/{team_b_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="items")
    if not table:
        return []

    tbody = table.find("tbody")
    rows = tbody.find_all("tr")
    matches = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        date_text = cols[6].get_text(strip=True)
        try:
            match_date = datetime.strptime(date_text, "%d.%m.%Y")
        except ValueError:
            continue
        home_team = cols[10].find('a')['title'] if cols[10].find('a') else cols[10].get_text(strip=True)
        guest_team = cols[8].find('a')['title'] if cols[8].find('a') else cols[8].get_text(strip=True)
        result = cols[9].get_text(strip=True)
        parts = result.split(":")
        if parts[0] == "-":
            continue

        matches.append({
            "date": match_date.strftime("%d.%m.%Y"),
            "home_team": home_team,
            "guest_team": guest_team,
            "result": result
        })

    return matches[:5]


# ==== Maç Geçmişi Çekici QThread ====
class MatchHistoryFetcher(QThread):
    finished = pyqtSignal(list)

    def __init__(self, team_a, team_b):
        super().__init__()
        self.team_a = team_a
        self.team_b = team_b

    def run(self):
        matches = get_last_matches(self.team_a, self.team_b)
        self.finished.emit(matches)

# === Hakem Bilgisi Çekici ===
class RefereeInfoFetcher(QThread):
    finished = pyqtSignal(str, QPixmap, str)

    def __init__(self, name, referee_type="main", season="2024"):
        super().__init__()
        self.name = name
        self.referee_type = referee_type
        self.season = season

    def run(self):
        html, pixmap = self.get_ref_info(self.name, self.season)
        self.finished.emit(html, pixmap, self.referee_type)

    def search_referee(self, name):
        query = name.replace(" ", "+")
        url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        link = soup.find("a", href=re.compile(r"/profil/schiedsrichter/"))
        return ("https://www.transfermarkt.com.tr" + link["href"]) if link else None

    def get_ref_info(self, name, season="2024"):
        url = self.search_referee(name)
        if not url:
            return "<b>❌ Hakem bulunamadı.</b>", QPixmap()

        if not url.endswith("/"):
            url += "/"
        url += f"saison/{season}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        img_pixmap = QPixmap()
        img = soup.find("img", class_="data-header__profile-image")
        if img:
            try:
                img_data = requests.get(img["src"], headers=headers).content
                img_pixmap.loadFromData(img_data)
            except:
                pass

        dob_bold = soup.select("div.info-table--equal-space > span.info-table__content--bold")
        dob = dob_bold[0].text.strip() if dob_bold else "?"
        birthplace = "?"
        for span in dob_bold:
            if "(" not in span.text and "Türkiye" in span.text:
                birthplace = span.text.strip()
                break

        try:
            form = soup.find("form", action=lambda x: x and "/profil/schiedsrichter" in x)
            action_url = form["action"]
            full_url = "https://www.transfermarkt.com.tr" + action_url
            saison_select = form.select_one("select[name='saison_id']")
            saison_options = saison_select.find_all("option")

            season_id = None
            for option in saison_options:
                if season in option.text:
                    season_id = option["value"]
                    break

            if season_id:
                data = {
                    "funktion": "1",  # Hakem
                    "saison_id": season_id
                }
                stats_resp = requests.post(full_url, headers=headers, data=data)
                stats_soup = BeautifulSoup(stats_resp.text, "html.parser")

                stats_table = stats_soup.find("table", class_="items")
            else:
                stats_table = None
        except Exception as e:
            stats_table = None

            # 4. İstatistikleri çek
        stats = {"Maç": 0, "Sarı Kart": 0, "2. Sarıdan Kırmızı": 0, "Direkt Kırmızı": 0, "Penaltı": 0}
        if stats_table:
            tbody = stats_table.find("tbody")
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 7:
                    try:
                        stats["Maç"] += int(cols[2].text.strip())
                    except:
                        pass
                    try:
                        stats["Sarı Kart"] += int(cols[3].text.strip())
                    except:
                        pass
                    try:
                        stats["2. Sarıdan Kırmızı"] += int(cols[4].text.strip())
                    except:
                        pass
                    try:
                        stats["Direkt Kırmızı"] += int(cols[5].text.strip())
                    except:
                        pass
                    try:
                        stats["Penaltı"] += int(cols[6].text.strip())
                    except:
                        pass

        html = f"""
           <b>📋 Hakem:</b> {name.title()}<br>
           <b>🎂 Doğum Tarihi/Yaş:</b> {dob}<br>
           <b>📍 Doğum Yeri:</b> {birthplace}<br>
           <b>📊 {season} Sezonu İstatistikleri:</b><br>
           {''.join([f"{k}: {v}<br>" for k, v in stats.items()])}
           """
        return html, img_pixmap


# === Takım Bilgisi Çekici ===
class TeamInfoFetcher(QThread):
    finished = pyqtSignal(dict, QPixmap, str)

    def __init__(self, team_name, team_type="A"):
        super().__init__()
        self.team_name = team_name
        self.team_type = team_type

    def run(self):
        info = self.get_team_info(self.team_name)
        pixmap = QPixmap()
        if info and info["Logo URL"]:
            try:
                img_data = requests.get(info["Logo URL"], headers={"User-Agent": "Mozilla/5.0"}).content
                pixmap.loadFromData(img_data)
            except:
                pass
        self.finished.emit(info, pixmap, self.team_type)

    def search_team_url(self, team_name):
        query = team_name.replace(" ", "+")
        url = f"https://www.transfermarkt.com.tr/schnellsuche/ergebnis/schnellsuche?query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.select("a[href*='/startseite/verein/']")
        for a in results:
            img = a.find("img")
            if img and img.get("alt"):
                alt_text = img["alt"].strip().lower()
                if team_name.lower() in alt_text:
                    return "https://www.transfermarkt.com.tr" + a["href"]
            else:
                if a.text.strip().lower() == team_name.lower():
                    return "https://www.transfermarkt.com.tr" + a['href']
        if results:
            return "https://www.transfermarkt.com.tr" + results[0]['href']
        return None

    def get_team_info(self, name):
        url = self.search_team_url(name)
        if not url:
            return {}

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        team_name_tag = soup.find("h1", class_="data-header__headline-wrapper")
        team_name = team_name_tag.text.strip() if team_name_tag else "?"

        league_name_tag = soup.find("span", class_="data-header__club")
        league_name = league_name_tag.text.strip() if league_name_tag else "?"

        league_rank = "?"
        labels = soup.find_all("span", class_="data-header__label")
        for label in labels:
            if "Lig Sıralaması" in label.text:
                content_span = label.find("span", class_="data-header__content")
                if content_span and content_span.find("a"):
                    league_rank = content_span.find("a").text.strip()
                break

        logo_tag = soup.find("div", class_="data-header__profile-container")
        logo_img = logo_tag.find("img") if logo_tag else None
        logo_url = logo_img['src'] if logo_img else None

        cups = []
        for cup in soup.find_all("a", class_="data-header__success-data"):
            title = cup.get("title", "Kupa")
            count = cup.find("span", class_="data-header__success-number")
            cups.append(f"{title}: {count.text.strip() if count else '?'}")

        squad_val = soup.find("a", class_="data-header__market-value-wrapper")
        squad_value = squad_val.text.strip() if squad_val else "?"

        def find_data(label_text):
            for li in soup.select("ul.data-header__items li.data-header__label"):
                if label_text in li.text:
                    content = li.find("span", class_="data-header__content")
                    return content.text.strip() if content else "?"
            return "?"

        return {
            "Takım": team_name,
            "Lig": league_name,
            "Lig Sıralaması": league_rank,
            "Logo URL": logo_url,
            "Kupalar": cups,
            "Kadro Değeri": squad_value,
            "Yaş Ortalaması": find_data("Yaş ortalaması"),
            "Stadyum": find_data("Stadyum")
        }

class TeamLastMatchesFetcher(QThread):
    finished = pyqtSignal(list, str)

    def __init__(self, team_name, team_type):
        super().__init__()
        self.team_name = team_name
        self.team_type = team_type

    def run(self):
        matches = get_team_last_5_matches_with_tactics(self.team_name)
        self.finished.emit(matches, self.team_type)


# === Arayüz Uygulaması ===
class Interface(QWidget):
    def __init__(self, pipe):
        super().__init__()
        self.pipe = pipe
        self.setWindowTitle("Futbol Arayüzü")
        self.setGeometry(100, 100, 1550, 800)
        self.setStyleSheet("""
            QWidget { background-color: #2E2E2E; color: #EAEAEA; font-family: 'Segoe UI'; font-size: 13px; }
            QGroupBox { font-weight: bold; border: 1px solid #555; border-radius: 8px; margin-top: 10px; padding: 15px; background-color: #3C3C3C; }
            QLineEdit { background-color: #1E1E1E; color: white; border: 1px solid #555; border-radius: 4px; padding: 5px; }
            QPushButton { background-color: #4CAF50; border: none; border-radius: 6px; color: white; padding: 8px 14px; margin-top: 10px; }
            QPushButton:hover { background-color: #45A049; }
          QPushButton#blueButton {
    background-color: #2196F3;
    border: none;
    border-radius: 15px;       
    color: white;
    padding: 1px 1px;          
    font-weight: bold;
    font-size: 12px;            
    min-width: 30px;            
    min-height: 30px;     
     max-width: 300px;      
    max-height: 75px;
}

QPushButton#blueButton:hover {
    background-color: #1976D2;
}
            QLabel { font-weight: normal; }
            QTextEdit { background-color:#1E1E1E; color:#EAEAEA; border:1px solid #555; }
        """)

        self.team_a_input, self.team_b_input = QLineEdit(), QLineEdit()
        self.main_ref_input, self.side_ref_input = QLineEdit(), QLineEdit()
        self.team_a_button, self.team_b_button = QPushButton("Takım A Forması Seç"), QPushButton("Takım B Forması Seç")
        self.team_a_button.clicked.connect(self.select_team_a_jersey)
        self.team_b_button.clicked.connect(self.select_team_b_jersey)
        self.team_a_jersey = self.team_b_jersey = ""

        self.ref_info_main_image, self.ref_info_main_text = QLabel(), QLabel()
        self.ref_info_side_image, self.ref_info_side_text = QLabel(), QLabel()
        for label in [self.ref_info_main_image, self.ref_info_side_image]:
            label.setFixedSize(100, 100)
            label.setStyleSheet("border: 1px solid #777;")

        self.team_a_logo, self.team_a_info = QLabel(), QLabel()
        self.team_b_logo, self.team_b_info = QLabel(), QLabel()
        for label in [self.team_a_logo, self.team_b_logo]:
            label.setFixedSize(100, 100)
            label.setStyleSheet("border: 1px solid #777;")

        self.team_a_info.setWordWrap(True)
        self.team_b_info.setWordWrap(True)

        # Maç geçmişi için QTextEdit
        self.match_history_label = QLabel("<b>Aralarındaki Son 5 Maç:</b>")
        self.match_history_text = QTextEdit()
        self.match_history_text.setReadOnly(True)
        self.match_history_text.setFixedWidth(400)
        self.match_history_text.setFixedHeight(180)

        # Takım A ve B Son 5 maç metin kutuları
        self.team_a_last_label = QLabel("")
        self.team_a_last_text = QTextEdit()
        self.team_a_last_text.setReadOnly(True)
        self.team_a_last_text.setFixedWidth(400)
        self.team_a_last_text.setFixedHeight(180)

        self.team_b_last_label = QLabel("")
        self.team_b_last_text = QTextEdit()
        self.team_b_last_text.setReadOnly(True)
        self.team_b_last_text.setFixedWidth(400)
        self.team_b_last_text.setFixedHeight(180)

        form_layout = QFormLayout()
        form_layout.addRow("Takım A Adı:", self.team_a_input)
        form_layout.addRow(self.team_a_button)
        form_layout.addRow("Takım B Adı:", self.team_b_input)
        form_layout.addRow(self.team_b_button)
        form_layout.addRow("Ana Hakem:", self.main_ref_input)
        form_layout.addRow("Yan Hakem:", self.side_ref_input)

        update_button = QPushButton("Güncelle")
        update_button.clicked.connect(self.send_data)
        form_layout.addRow(update_button)

        self.start_button = QPushButton("Özeti Başlat")
        self.start_button.clicked.connect(self.start_summary)
        form_layout.addRow(self.start_button)

        match_history_vbox = QVBoxLayout()
        match_history_vbox.addWidget(self.match_history_label)
        match_history_vbox.addWidget(self.match_history_text)
        match_history_vbox.addStretch()

        hakem_hbox = QHBoxLayout()
        main_vbox, side_vbox = QVBoxLayout(), QVBoxLayout()
        main_vbox.addWidget(self.ref_info_main_image, alignment=Qt.AlignCenter)
        main_vbox.addWidget(self.ref_info_main_text)
        side_vbox.addWidget(self.ref_info_side_image, alignment=Qt.AlignCenter)
        side_vbox.addWidget(self.ref_info_side_text)

        hakem_hbox.addLayout(main_vbox)
        hakem_hbox.addLayout(side_vbox)
        form_layout.addRow("👨‍⚖️ Hakem Bilgileri:", QLabel())
        form_layout.addRow(hakem_hbox)

        group_box = QGroupBox("Maç Bilgileri")
        group_box.setLayout(form_layout)
        main_layout = QVBoxLayout()
        main_layout.addWidget(group_box)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        team_info_vbox = QVBoxLayout()
        for logo, info in [(self.team_a_logo, self.team_a_info), (self.team_b_logo, self.team_b_info)]:
            team_info_vbox.addWidget(logo, alignment=Qt.AlignCenter)
            team_info_vbox.addWidget(info)
            team_info_vbox.addSpacing(15)

        match_and_last_vbox = QVBoxLayout()
        match_and_last_vbox.addWidget(self.match_history_label)
        match_and_last_vbox.addWidget(self.match_history_text)
        match_and_last_vbox.addSpacing(10)
        match_and_last_vbox.addWidget(self.team_a_last_label)
        match_and_last_vbox.addWidget(self.team_a_last_text)
        match_and_last_vbox.addSpacing(10)
        match_and_last_vbox.addWidget(self.team_b_last_label)
        match_and_last_vbox.addWidget(self.team_b_last_text)
        match_and_last_vbox.addStretch()

        top_hbox = QHBoxLayout()
        top_hbox.addLayout(team_info_vbox)
        top_hbox.addLayout(match_and_last_vbox)
        top_hbox.addStretch()

        self.predict_button = QPushButton("PredictFutureMatchWithFootballGPT")
        self.predict_button.setObjectName("blueButton")
        self.predict_button.clicked.connect(self.predict_match)

        self.prediction_result = QTextEdit()
        self.prediction_result.setReadOnly(True)
        self.prediction_result.setFixedWidth(300)
        self.prediction_result.setFixedHeight(60)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.predict_button)
        input_layout.addWidget(QLabel("GPT Tahmin Sonucu:"))
        input_layout.addWidget(self.prediction_result)
        """
        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        """
        match_and_last_vbox.addSpacing(15)  
        match_and_last_vbox.addLayout(input_layout)

        hbox = QHBoxLayout()
        hbox.addLayout(main_layout)
        hbox.addLayout(top_hbox)
        # hbox.addWidget(input_widget, alignment=Qt.AlignTop)
        self.setLayout(hbox)

    def select_team_a_jersey(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Takım A Forması", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.team_a_jersey = file_name
            self.team_a_button.setText(f"Seçildi: {file_name.split('/')[-1]}")

    def start_summary(self):
        self.pipe.send({'start_summary': True})

    def predict_match(self):
        team_a = self.team_a_input.text().strip()
        team_b = self.team_b_input.text().strip()
        if not team_a or not team_b:
            self.prediction_result.setText("Lütfen iki takım adını da giriniz.")
            return

        self.prediction_result.setText("Tahmin yapılıyor, lütfen bekleyin...")

        # Burada gpt.py'deki predict_match fonksiyonunu çağırıyoruz
        sonuc = Gpt_area.predict_match(team_a, team_b)

        self.prediction_result.setText(sonuc)

    def select_team_b_jersey(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Takım B Forması", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.team_b_jersey = file_name
            self.team_b_button.setText(f"Seçildi: {file_name.split('/')[-1]}")

    def send_data(self):
        self.pipe.send({
            'team_a': self.team_a_input.text(),
            'team_a_jersey': self.team_a_jersey,
            'team_b': self.team_b_input.text(),
            'team_b_jersey': self.team_b_jersey,
            'main_ref': self.main_ref_input.text(),
            'side_ref': self.side_ref_input.text(),
        })
        if self.team_a_input.text():
            self.team_a_thread = TeamInfoFetcher(self.team_a_input.text(), "A")
            self.team_a_thread.finished.connect(self.display_team_info)
            self.team_a_thread.start()

        if self.team_b_input.text():
            self.team_b_thread = TeamInfoFetcher(self.team_b_input.text(), "B")
            self.team_b_thread.finished.connect(self.display_team_info)
            self.team_b_thread.start()

        self.match_history_thread = MatchHistoryFetcher(self.team_a_input.text().strip(), self.team_b_input.text().strip())
        self.match_history_thread.finished.connect(self.display_match_history)
        self.match_history_thread.start()

        # Takım A son 5 maç
        self.team_a_last_thread = TeamLastMatchesFetcher(self.team_a_input.text().strip(), "A")
        self.team_a_last_thread.finished.connect(self.display_team_last_matches)
        self.team_a_last_thread.start()

        # Takım B son 5 maç
        self.team_b_last_thread = TeamLastMatchesFetcher(self.team_b_input.text().strip(), "B")
        self.team_b_last_thread.finished.connect(self.display_team_last_matches)
        self.team_b_last_thread.start()

        if self.main_ref_input.text():
            self.main_ref_thread = RefereeInfoFetcher(self.main_ref_input.text(), "main")
            self.main_ref_thread.finished.connect(self.display_ref_info)
            self.main_ref_thread.start()

        if self.side_ref_input.text():
            self.side_ref_thread = RefereeInfoFetcher(self.side_ref_input.text(), "side")
            self.side_ref_thread.finished.connect(self.display_ref_info)
            self.side_ref_thread.start()

    def display_match_history(self, matches):
        if not matches:
            self.match_history_text.setText("Maç bulunamadı.")
            return
        text = ""
        for m in matches:
            text += f"{m['date']}: {m['guest_team']} vs {m['home_team']} - {m['result']}\n"
        self.match_history_text.setText(text)

    def display_team_last_matches(self, matches, team_type):
        if not matches:
            text = "Veri bulunamadı."
        else:
            text = ""
            wins = draws = losses = 0
            for m in matches:
                if m["emoji"] == "✅":
                    wins += 1
                elif m["emoji"] == "🤝":
                    draws += 1
                elif m["emoji"] == "❌":
                    losses += 1

                text += f"{m['tarih']} vs {m['rakip']} | Sonuç: {m['sonuc']} {m['emoji']} | Diziliş: {m['dizilis']}\n"
        text += f"\nSon 5 maçta: {wins} galibiyet ✅, {draws} beraberlik 🤝, {losses} mağlubiyet ❌"
        if team_type == "A":
            # Label'ı takım ismiyle doldur
            self.team_a_last_label.setText(f"<b>{self.team_a_input.text().strip()} Son 5 Maçı:</b>")
            self.team_a_last_text.setText(text)
        else:
            self.team_b_last_label.setText(f"<b>{self.team_b_input.text().strip()} Son 5 Maçı:</b>")
            self.team_b_last_text.setText(text)

    def display_ref_info(self, html, pixmap, ref_type):
        label, image = (self.ref_info_main_text, self.ref_info_main_image) if ref_type == "main" else (self.ref_info_side_text, self.ref_info_side_image)
        label.setText(html)
        image.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def display_team_info(self, info, pixmap, team_type):
        html = f"""
        <b>🏟️ {info['Takım']}</b><br>
        Lig: {info['Lig']}<br>
        Sıralama: {info['Lig Sıralaması']}<br>
        Kadro Değeri: {info['Kadro Değeri']}<br>
        Yaş Ort.: {info['Yaş Ortalaması']}<br>
        Stadyum: {info['Stadyum']}<br>
        {'<br>'.join(info['Kupalar'])}
        """
        if team_type == "A":
            self.team_a_logo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.team_a_info.setText(html)
        else:
            self.team_b_logo.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.team_b_info.setText(html)


def AppManager(pipe):
    app = QApplication(sys.argv)
    window = Interface(pipe)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    from multiprocessing import Pipe, Process
    pipe_parent, pipe_child = Pipe()
    p = Process(target=AppManager, args=(pipe_child,))
    p.start()
    p.join()
