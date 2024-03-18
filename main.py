import requests
from bs4 import BeautifulSoup
import time
import telegram
import asyncio

URL = "http://tickets.ft.org.ua/web/afisha"
SEARCH_TERM = "Моя професія – синьйор з вищого світу"
TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHAT_IDS = []
CHECK_INTERVAL = 120

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)


def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events_table = soup.find('table')
    if not events_table:
        return None

    events = []
    for row in events_table.find_all('tr'):
        event_name = row.find('h3')
        if event_name and SEARCH_TERM in event_name.text:
            event_details = event_name.text.strip()
            event_date = row.find('h4').text.strip() if row.find('h4') else "Date not found"
            event_link = row.find('a', class_='link-button')['href'] if row.find('a',
                                                                                 class_='link-button') else ("Link not "
                                                                                                             "found")
            events.append({
                "title": event_details,
                "date": event_date,
                "link": event_link
            })

    return events


async def send_telegram_notification(event_info):
    message = f"{event_info['title']} on {event_info['date']}. Tickets available at: {event_info['link']}"
    for chat_id in TELEGRAM_CHAT_IDS:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Failed to send message to chat ID {chat_id}: {e}")


def main():
    notified_events = set()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            try:
                current_events = scrape_website(URL)
                for event in current_events:
                    event_key = (event['title'], event['date'])
                    if event_key not in notified_events:
                        loop.run_until_complete(send_telegram_notification(event))
                        notified_events.add(event_key)
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                print(f"An error occurred: {e}")
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


if __name__ == "__main__":
    main()
