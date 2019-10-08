from bs4 import BeautifulSoup  
import unicodedata
import requests
import pymysql


def main():
    url = 'https://kazan.hh.ru/search/vacancy?area=88&clusters=true&enable_snippets=true&search_field=name&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&page='
    i = 0
    #Чем больше i, тем больше страниц на HH проанализирует парсер.
    while (i < 1):
        parse(get_url(url + str(i)))
        i+=1
    print('End')
    
    
def get_url(url):
    #Я добавил к http запросу User-Agent, Language и Encoding, чтобы сделать запрос более похожим на настоящий запрос из браузера.
    headers = {
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Language':'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Encoding':'gzip, deflate, br'}
    return requests.get(url, headers=headers).text

def parse(html):
    none = 'Не указана заработная плата'
    soup = BeautifulSoup(html, features='html.parser')
    jobs = {}
    #Очевидно, что у вас свои пароли данные MySQL, поэтому заполните их самостоятельно.
    connection = pymysql.connect(
        host='localhost',
        #Пользователь
        user='',
        #Пароль
        password='',
        #Вам необходимо заранее создать новую базу данных и записать ее название тут. В базе данных необходимо установить кодировку UTF8.
        db='',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
        )
    
    for element in soup.find_all('div', {'class':'vacancy-serp-item__row vacancy-serp-item__row_header'}):
        try:
            job = element.find('a', {'class':'bloko-link HH-LinkModifier'}).string
            salary = unicodedata.normalize('NFKC', element.find('div', {'class':'vacancy-serp-item__compensation'}).string)
            jobs[job] = salary 
        except AttributeError:    
            jobs[job] = none
    with connection.cursor() as c:
        for I in jobs:
            sql = "INSERT INTO jobs (job, salary) VALUES(SUBSTRING('" + str(I) + "', 1, 40) ,'" + jobs[I] + "');"
            c.execute(sql)
            #Если закомментировать данное поле, то данные не будут сохраняться в базе данных, а лишь выведутся на консоль.
            connection.commit()
            
        
    for e in jobs:
        print(e + ' : ' + jobs[e])
    
    
        
if __name__ == '__main__':
    main()
    
