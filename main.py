import sqlite3
import requests
from bs4 import BeautifulSoup
import re


class DatabaseManager:
    def __init__(self, db_name="search_database.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        query = """
                CREATE TABLE IF NOT EXISTS sites \
                ( \
                    id \
                    INTEGER \
                    PRIMARY \
                    KEY \
                    AUTOINCREMENT, \
                    url \
                    TEXT \
                    UNIQUE
                ) \
                """
        self.cursor.execute(query)
        self.connection.commit()

    def add_site(self, url):
        try:
            self.cursor.execute("INSERT INTO sites (url) VALUES (?)", (url,))
            self.connection.commit()
            return True
        except Exception as e:
            return False

    def get_sites(self):
        self.cursor.execute("SELECT url FROM sites")
        rows = self.cursor.fetchall()

        sites_list = []
        for row in rows:
            sites_list.append(row[0])

        return sites_list

    def clear_database(self):
        self.cursor.execute("DELETE FROM sites")
        self.connection.commit()


class WebParser:
    def count_word_on_page(self, url, search_word):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text().lower()
                count = text.count(search_word.lower())
                return count
            else:
                return 0

        except Exception as e:
            return 0


class UserInterface:
    def __init__(self):
        self.db = DatabaseManager()
        self.parser = WebParser()

    def run(self):
        while True:
            print("\n1. Знайти слово на сайтах")
            print("2. Додати сайт до бази")
            print("3. Показати список сайтів")
            print("4. Очистити базу даних")
            print("5. Вихід")

            choice = input("Виберіть пункт меню: ")

            if choice == "1":
                self.search_action()
            elif choice == "2":
                self.add_site_action()
            elif choice == "3":
                self.show_sites_action()
            elif choice == "4":
                self.clear_db_action()
            elif choice == "5":
                break

    def search_action(self):
        word = input("Введіть слово для пошуку: ").strip()
        if word == "":
            return

        sites = self.db.get_sites()
        if len(sites) == 0:
            return

        results = []

        for site in sites:
            count = self.parser.count_word_on_page(site, word)
            if count > 0:
                results.append((site, count))

        results.sort(key=lambda item: item[1], reverse=True)

        if len(results) > 0:
            for site, count in results:
                print(f"Сайт: {site} | Збігів: {count}")

    def add_site_action(self):
        url = input("Введіть URL сайту: ").strip()
        if url == "":
            return

        match = re.search(r'https?://[^\s\]\)]+', url)
        if match:
            url = match.group(0)

        self.db.add_site(url)

    def show_sites_action(self):
        sites = self.db.get_sites()
        if len(sites) > 0:
            for i, site in enumerate(sites, 1):
                print(f"{i}. {site}")

    def clear_db_action(self):
        answer = input("Очистити БД? (так/ні): ").strip().lower()
        if answer == "так":
            self.db.clear_database()


if __name__ == "__main__":
    app = UserInterface()
    app.run()