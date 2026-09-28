# BlueBug-Task

#### What broke or took longer than expected?
-The price came through as "Â£51.77" instead of "£51.77" because of an encoding issue, So I changed the encoding to "UTF-8" to handle special characters.
-Re-running the script inserted every book again in the database, so I added a check that skips any book whose URL is already in the table.

#### What if the site blocked me after 50 requests?
-I'd add a short random delay between requests (time.sleep) and send a normal browser User-Agent header, so the traffic isn't seen as a bot.
-If a request still gets blocked, I'd wait longer and retry.
-As a last resort spread the requests across different proxies.
