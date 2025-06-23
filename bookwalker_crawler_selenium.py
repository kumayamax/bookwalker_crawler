from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from fastapi import FastAPI, Query

# MySQL設定
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'chen19990713'  # ご自身のMySQLパスワードに変更してください
MYSQL_DB = 'bookwalker'
MYSQL_TABLE = 'light_novel_rank'

# データベース・テーブル自動作成SQL
CREATE_DB_SQL = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} DEFAULT CHARACTER SET utf8mb4;"
CREATE_TABLE_SQL = f'''
CREATE TABLE IF NOT EXISTS {MYSQL_TABLE} (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `rank` INT,
    title VARCHAR(255),
    author VARCHAR(255),
    price VARCHAR(64),
    rating VARCHAR(16),
    url VARCHAR(512)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
'''

INSERT_SQL = f'''
INSERT INTO {MYSQL_TABLE} (`rank`, title, author, price, rating, url)
VALUES (%s, %s, %s, %s, %s, %s)
'''

def save_to_mysql(books, period_tag):
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, charset='utf8mb4')
    cursor = conn.cursor()
    # データベース作成
    cursor.execute(CREATE_DB_SQL)
    conn.select_db(MYSQL_DB)
    # テーブル作成（period_tag列を追加）
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {MYSQL_TABLE} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        `rank` INT,
        title VARCHAR(255),
        author VARCHAR(255),
        price VARCHAR(64),
        rating VARCHAR(16),
        url VARCHAR(512),
        period_tag VARCHAR(16)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ''')
    # データ挿入
    data = [(int(b['rank']), b['title'], b['author'], b['price'], b['rating'], b['url'], period_tag) for b in books]
    # 只清空本期数据
    cursor.execute(f"DELETE FROM {MYSQL_TABLE} WHERE period_tag=%s", (period_tag,))
    cursor.executemany(f'''
        INSERT INTO {MYSQL_TABLE} (`rank`, title, author, price, rating, url, period_tag)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', data)
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{len(books)}件のデータをMySQLデータベース {MYSQL_DB}.{MYSQL_TABLE}（{period_tag}） に保存しました。")

def crawl_bookwalker_with_selenium():
    # 取得期别标签（如 2024-06-1 或 2024-06-2）
    now = datetime.now()
    if now.day < 16:
        period_tag = f"{now.year}-{now.month:02d}-1"
    else:
        period_tag = f"{now.year}-{now.month:02d}-2"

    options = Options()
    options.add_argument('--headless')  # ヘッドレスモード（画面非表示）
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.get("https://bookwalker.jp/rank/ct3/")

    # ページを自動で下までスクロールし、全ランキングを読み込む
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # 新しい内容の読み込み待ち
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # ページ解析
    soup = BeautifulSoup(driver.page_source, "lxml")
    books = []
    for card in soup.find_all("div", class_="rankingCard"):
        rank_tag = card.find("p", class_="rankingNum")
        rank = rank_tag.text.strip().replace("位", "") if rank_tag else ""
        title_tag = card.find("h3")
        title = title_tag.text.strip() if title_tag else ""
        link_tag = title_tag.find("a") if title_tag else None
        book_url = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
        author = ""
        writer_dl = card.find("dl", class_="writerDl")
        if writer_dl:
            dd_tags = writer_dl.find_all("dd")
            if dd_tags:
                author = dd_tags[0].text.strip()
        price_tag = card.find("p", class_="rankingPrice")
        price = price_tag.text.strip() if price_tag else ""
        rating_tag = card.find("span", class_="a-rating-starts_text")
        rating = rating_tag.text.strip() if rating_tag else ""
        if title:
            books.append({
                "rank": rank,
                "title": title,
                "author": author,
                "price": price,
                "rating": rating,
                "url": book_url
            })
    driver.quit()
    if books:
        df = pd.DataFrame(books)
        df.set_index("rank", inplace=True)
        excel_name = f"bookwalker_light_novel_{period_tag}.xlsx"
        df.to_excel(excel_name)
        print(f"{excel_name} にエクスポートしました。")
        save_to_mysql(books, period_tag)
    else:
        print("ライトノベルデータが取得できませんでした。")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    # 毎月1日と16日午前2時に自動でクローリングを実行
    scheduler.add_job(crawl_bookwalker_with_selenium, 'cron', day=1, hour=2, minute=0)
    scheduler.add_job(crawl_bookwalker_with_selenium, 'cron', day=16, hour=2, minute=0)
    print("スケジューラーが起動しました。毎月1日と16日午前2時に自動でランキングを取得します。Ctrl+Cで終了できます。")
    scheduler.start()

app = FastAPI()

def get_mysql_connection():
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
        password=MYSQL_PASSWORD, db=MYSQL_DB, charset='utf8mb4'
    )

@app.get("/rank/")
def get_rank(period_tag: str = Query(..., description="例: 2024-06-1")):
    conn = get_mysql_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(f"SELECT * FROM {MYSQL_TABLE} WHERE period_tag=%s ORDER BY `rank` ASC", (period_tag,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"period_tag": period_tag, "data": data}

# 你可以根据需要添加更多API接口 