from datetime import datetime
import json
import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.empleonuevo.com"
SEEN_FILE = "seen_jobs.json"
KEYWORDS = [
    ".net",
    "c#",
    "desarrollador",
    "software",
    "programador",
    "remote",
    "remoto",
]


def load_seen_jobs():
  if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return []
  return []


def save_seen_jobs(seen_jobs):
  with open(SEEN_FILE, "w", encoding="utf-8") as f:
    json.dump(seen_jobs, f, ensure_ascii=False, indent=4)


def scrape_jobs():
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  try:
    response = requests.get(URL, headers=headers, timeout=15)
    if response.status_code != 200:
      print(f"Error al acceder a la web: {response.status_code}")
      return []

    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    job_elements = soup.find_all(
        ["h2", "h3", "a"], class_=lambda x: x and "job" in x.lower()
    )

    if not job_elements:
      job_elements = soup.find_all("a", href=True)

    for el in job_elements:
      title = el.get_text(strip=True)
      link = el.get("href", "")
      if len(title) > 5:
        if link and link.startswith("/"):
          link = "https://www.empleonuevo.com" + link
        jobs.append({"title": title, "link": link})
    return jobs
  except Exception as e:
    print(f"Excepción al conectar con la página: {e}")
    return []


def check_vacancies():
  print(
      f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Analizando"
      f" vacantes..."
  )
  current_jobs = scrape_jobs()
  if not current_jobs:
    print("No se pudieron extraer elementos.")
    return

  seen_jobs = load_seen_jobs()
  seen_links = {job["link"] for job in seen_jobs}
  new_matches = []

  for job in current_jobs:
    title_lower = job["title"].lower()
    link = job["link"]
    if link not in seen_links:
      matched_keyword = next(
          (kw for kw in KEYWORDS if kw in title_lower), None
      )
      if matched_keyword:
        new_matches.append(job)
        seen_jobs.append(job)

  if new_matches:
    print(
        f"\n¡Se encontraron {len(new_matches)} nuevas vacantes con tus"
        " criterios!\n"
    )
    for match in new_matches:
      print(f"- Puesto: {match['title']}")
      print(f"  Enlace: {match['link']}\n")
  else:
    print("Sin nuevas vacantes relevantes detectadas.")

  save_seen_jobs(seen_jobs)


if __name__ == "__main__":
  check_vacancies()