import requests

print(
    requests.get(
        "https://news.google.com/read/CBMilgFBVV95cUxQeEZ4MkZSbno2RE41S214RmpzRzA2RmdBT0M5U0kybktXZTZyZzZKM1pGRTdxaFZTZE1EUXMteEJUZnQ2ZzFmbDl4bHUwaWxfYmhPbUltVC1lcXBreEpCTHJzTkVuMGhjSFlLbmc2SmlCYmJuaDJpM0M3cFdGUXVXdTROU0lJMkdZQUFZQXV5VFpQcmlNQ3c?hl=en-IN&amp;gl=IN&amp;ceid=IN%3Aen"
    ).text
)
