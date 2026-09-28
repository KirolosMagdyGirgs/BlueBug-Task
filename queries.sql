--1. Average price for each rating
select rating, round(AVG(price),2) avg_price
from books
group by rating 
order by rating 

--2. The 5 most expensive books rated 4 or 5
SELECT TOP 5 *
FROM books
WHERE rating IN (4, 5)
ORDER BY price DESC


--3. How many books are out of stock, per rating
SELECT rating, SUM(CASE WHEN in_stock = 0 THEN 1 ELSE 0 END) AS out_of_stock_count 
--No scraped book is out of stock
FROM books 
GROUP BY rating 
ORDER BY rating   