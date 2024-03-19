import requests
from bs4 import BeautifulSoup
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def scrape_website(url):
    base_url = "https://jwc.njmu.edu.cn"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.select('.news_list li')
    news_list = []
    for item in items:
        news = {}
        news_anchor = item.select_one('.news_title a')
        news['title'] = news_anchor.get('title').strip()
        news['link'] = base_url + news_anchor.get('href')
        news['date'] = item.select_one('.news_meta').text.strip()
        news_list.append(news)
    return news_list

def scrape_news_details(news_link):
    page = requests.get(news_link)
    soup = BeautifulSoup(page.content, 'html.parser')
    content_element = soup.select_one('.wp_articlecontent')
    if content_element:
        content_text = content_element.get_text(separator=" ", strip=True)
        length = len(content_text)
        if length > 200:
            summary = content_text[:200] + " ......"
        else:
            summary = content_text
        return summary
    else:
        return "No content found."

def send_email(subject, content, to_email):
    sender_email = "***"
    password = "***"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email
    msg.attach(MIMEText(content, 'html'))
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)
    server.login(sender_email, password)
    server.send_message(msg)
    server.quit()

if __name__ == "__main__":
    email_list = ["***"]
    url = 'https://jwc.njmu.edu.cn/842/list.htm'
    news_list = scrape_website(url)
    
    content_mail = """
    <html>
    <head>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }
        .container { margin-top: 20px; }
        .news-item { background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .news-title { font-size: 18px; color: #333; font-weight: bold; margin-bottom: 10px; }
        .news-date { font-size: 14px; color: #666; margin-bottom: 10px; }
        .news-link { background-color: #007bff; color: #ffffff; padding: 8px 12px; text-decoration: none; border-radius: 5px; font-size: 12px; display: inline-block; margin-top: 10px; }
        .news-summary { font-size: 14px; color: #444; line-height: 1.6; margin-top: 10px; }
    </style>
    </head>
    <body>
    <h1 style="color: #333;">教务处通知公告</h1>
    <div class="container">
    """

    for news in news_list:
        summary = scrape_news_details(news['link'])
        summary_display = summary.replace(" ","")

        content_mail += f"""
        <div class="news-item">
            <div class="news-title">{news['title']}</div>
            <div class="news-date">{news['date']}</div>
            <p class="news-summary">{summary_display}</p>
            <a href="{news['link']}" class="news-link">阅读原文</a>
        </div>
        """
    
    content_mail += """
    </div>
    </body>
    </html>
    """
    
    for email in email_list:
        if str(datetime.date.today()) in content_mail:
            send_email("今日有更新|教务处通知公告", content_mail, email)
            print("今日有更新！")
        elif str(datetime.date.today()-datetime.timedelta(days=1)) in content_mail:
            send_email("昨日有更新|教务处通知公告", content_mail, email)
            print("昨日有更新！")
        else:
            print("无最新通知！")

    user_input = input("退出请按任意键。")
