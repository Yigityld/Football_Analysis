# gpt.py
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# --- Takım URL ve ID çekme fonksiyonları ---
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
    return match.group(1) if match else None

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
    name = re.sub(r'\bfc\b', '', name)  # fc'yi tam kelime olarak çıkar
    name = name.strip()  # Son boşlukları temizle
    return name

# --- Takımın son 5 maçını (diziliş + skor) getir ---
def get_team_last_5_matches_with_tactics(team_name):
    def fetch_matches_from_url(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Fikstür sayfası açılamadı.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        div_responsive = soup.find("div", class_="responsive-table")
        if not div_responsive:
            print("Fikstür tablosu bulunamadı.")
            return []

        tbody = div_responsive.find("tbody")
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
                emoji = ""

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
        return [], 0, 0, 0
    team_id = get_team_id_from_url(team_url)
    if not team_id:
        print("Takım ID bulunamadı:", team_name)
        return [], 0, 0, 0

    team_url_slug = team_name.lower().replace(" ", "-")
    base_url = f"https://www.transfermarkt.com.tr/{team_url_slug}/spielplandatum/verein/{team_id}/plus/1"

    matches = fetch_matches_from_url(base_url)

    if len(matches) < 500:
        alt_url = f"https://www.transfermarkt.com.tr/{team_url_slug}/spielplandatum/verein/{team_id}/saison_id/2024/plus/1"
        matches = fetch_matches_from_url(alt_url)

    last_5 = matches[-5:][::-1]

    wins = sum(1 for m in last_5 if m["emoji"] == "✅")
    draws = sum(1 for m in last_5 if m["emoji"] == "🤝")
    losses = sum(1 for m in last_5 if m["emoji"] == "❌")

    return last_5, wins, draws, losses

# --- İki takım arası son 5 maç ---
def get_last_matches(team_a, team_b):
    team_a_id = find_team_id(team_a)
    team_b_id = find_team_id(team_b)
    if not team_a_id or not team_b_id:
        print("Takımlardan biri bulunamadı.")
        return []

    url = f"https://www.transfermarkt.com.tr/vergleich/bilanzdetail/verein/{team_a_id}/gegner_id/{team_b_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Maçlar sayfası açılamadı.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="items")
    if not table:
        print("Maç tablosu bulunamadı.")
        return []

    rows = table.find("tbody").find_all("tr")
    matches = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        try:
            match_date = datetime.strptime(cols[6].get_text(strip=True), "%d.%m.%Y")
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

# --- Prompt hazırlama ---
def hazirla_prompt_string(matches, team_a, maclar_a, wins_a, draws_a, losses_a,
                         team_b, maclar_b, wins_b, draws_b, losses_b):
    if not matches:
        return "Veri bulunamadı."

    prompt = f"Sen bir futbol yorumcusun.\n\n"
    prompt += f"{team_a} takımının son 5 maçı:\n"
    for m in maclar_a:
        prompt += f"{m['tarih']} vs {m['rakip']} | Sonuç: {m['sonuc']} | Diziliş: {m['dizilis']}\n"
    prompt += f"Son 5 maçta: {wins_a} galibiyet ✅, {draws_a} beraberlik 🤝, {losses_a} mağlubiyet ❌\n\n"

    prompt += f"{team_b} takımının son 5 maçı:\n"
    for m in maclar_b:
        prompt += f"{m['tarih']} vs {m['rakip']} | Sonuç: {m['sonuc']} | Diziliş: {m['dizilis']}\n"
    prompt += f"Son 5 maçta: {wins_b} galibiyet ✅, {draws_b} beraberlik 🤝, {losses_b} mağlubiyet ❌\n\n"

    prompt += f"{team_a} ve {team_b} arasındaki son 5 maç:\n"
    for m in matches:
        prompt += f"{m['date']} - {m['guest_team']} {m['result']} {m['home_team']}\n"

    prompt += f"""
Lütfen sadece bir sonraki maçın tahmini skorunu şu formatta yaz:

Tahmin: {team_a} X - Y {team_b} (Burada X ve Y yerine kendi rakam tercihlerini yaz (0,1,2,3,4,5 gibi)

Başka hiçbir şey yazma.
"""
    return prompt

# --- LLM'ye sorgu gönderme ---
def sor_local_llm(prompt, model="mistral"):
    try:
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Hata: {response.status_code} - {response.text}"
    except Exception as e:
        return f"LLM bağlantısı başarısız: {e}"

# --- Dışa açılan fonksiyon ---
def predict_match(team_a, team_b):
    maclar_a, wins_a, draws_a, losses_a = get_team_last_5_matches_with_tactics(team_a)
    maclar_b, wins_b, draws_b, losses_b = get_team_last_5_matches_with_tactics(team_b)
    ikili = get_last_matches(team_a, team_b)

    prompt = hazirla_prompt_string(ikili, team_a, maclar_a, wins_a, draws_a, losses_a,
                                  team_b, maclar_b, wins_b, draws_b, losses_b)

    sonuc = sor_local_llm(prompt)
    return sonuc

# Eğer dosya doğrudan çalıştırılırsa test amaçlı:
if __name__ == "__main__":
    team_a = input("Takım A: ").strip()
    team_b = input("Takım B: ").strip()
    print("Tahmin yapılıyor, lütfen bekleyin...")
    print(predict_match(team_a, team_b))
