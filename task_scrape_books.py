import sys
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pyodbc



base_url = "https://books.toscrape.com/catalogue/"
ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
books = []

no_pages = 5 
# scrape n pages
for page in range(1, no_pages + 1):
    try:
        response = requests.get(f"{base_url}page-{page}.html", timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to get page {page}: {e}")
        continue
 
    response.encoding = "utf-8"  #to handle encoding issues with special characters in currency 
    soup = BeautifulSoup(response.text, "html.parser")
 
    for book in soup.select("article.product_pod"):
        title = book.h3.a["title"]
        price = Decimal(book.select_one(".price_color").text.replace("£", ""))
        rating = ratings[book.select_one(".star-rating")["class"][1]]
        in_stock = "In stock" in book.select_one(".availability").text         #returns 1 or 0 
        url = base_url + book.h3.a["href"]
        books.append((title, price, rating, in_stock, url))
 
if not books:
    print("No books scraped, stopping.")
    sys.exit()
 
print(f"Scraped {len(books)} books")
 
# save to csv
df = pd.DataFrame(books, columns=["Title", "Price", "Rating", "In Stock", "URL"])
df.to_csv("books.csv", index=False, encoding="utf-8-sig")
print("Data saved to books.csv")
 

# Insert into SQL Server database to run the queries 
server = r"SQL SERVER\INSTANCE"
driver = "ODBC Driver 17 for SQL Server"

conn = pyodbc.connect(f"DRIVER={{{driver}}};SERVER={server};Trusted_Connection=yes;", autocommit=True)
conn.cursor().execute("IF DB_ID('BooksDB') IS NULL CREATE DATABASE BooksDB")
conn.close()

# create table and insert data
conn = pyodbc.connect(f"DRIVER={{{driver}}};SERVER={server};DATABASE=BooksDB;Trusted_Connection=yes;")
cursor = conn.cursor()

cursor.execute("""
IF OBJECT_ID('books') IS NULL
CREATE TABLE books (
    id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(500),
    price DECIMAL(10,2),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    in_stock BIT,
    url NVARCHAR(500)
)
""")

# skip books that already exist (same url)
for title, price, rating, in_stock, url in books:
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM books WHERE url = ?)
        INSERT INTO books (title, price, rating, in_stock, url) VALUES (?, ?, ?, ?, ?)
    """, url, title, price, rating, in_stock, url)

conn.commit()
conn.close()

print("Data saved to SQL Server")