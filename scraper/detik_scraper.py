from bs4 import BeautifulSoup
import sys
import requests
import csv

def detik(keyword=None, n_berita=None):
    if keyword != None and n_berita != None:
        alamatURL = 'https://www.detik.com/search/searchall?query=%s' %keyword
        req = requests.get(alamatURL)
        data_detik= []
        url_last_page = []
        pakem = True
        while pakem:
            page_source = req.content
            soup = BeautifulSoup(page_source, 'lxml')
            try:
                classToIgnore = ["foto_tag", "video_tag"]
                article = soup.find_all('article', class_=lambda x: x not in classToIgnore)
                for i in article:
                    judul = [span.get_text() for span in i.find_all('h2', {'class' : 'title'})]
                    url = [a['href'] for a in i.find_all('a', href=True)]
                    date = [span.get_text() for span in soup.find_all('span', {'class' : 'date'})]                    
                    
                    # page detail berita
                    req = requests.get(url[-1])
                    soup_detail_berita = BeautifulSoup(req.content, 'lxml')
                    berita = [span.get_text() for span in soup_detail_berita.find_all('div', {'class' : 'detail__body-text itp_bodycontent'})]
                    
                    if berita != []:
                        if len(data_detik) == int(n_berita):
                            pakem = False
                            break
                        else:
                            data = {
                                'judul':judul[0],
                                'berita':''.join(berita[0].splitlines()),
                                'url':url[0],
                                'tanggal':date[0].split(',')[1]
                            }
                            data_detik.append(data)
                            print('Judul berita : %s' % judul[0])
                            print('Total berita yang didapat: %s' % len(data_detik))
                            print('================================================')
                
                url = [a['href'] for a in soup.find_all('a', {'onclick' : '_pt(this, "pagination", "button pagination", "pagination Next")'})]
                url_last_page.append(url[0])
                url_last_page = url_last_page[-1:]      
                req = requests.get(url_last_page[-1])  
                page_source = req.content
            except IndexError as e:
                print(e)
                pakem = False
                
        # export to csv
        keys = data_detik[0].keys()
        with open('detik_%s_%s.csv' %(' '.join(keyword),n_berita), 'w', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data_detik)
            print('data save to detik_%s_%s.csv' %(' '.join(keyword),n_berita))

    else:
         print('''
        Masukan keyword dan jumlah berita yang ingin anda ambil
        contoh:
        python detik_scraper.py KPK 10
        ''')

try:
    KEYWORD = sys.argv[1:-1]
    N_BERITA = sys.argv[-1]
    detik(keyword = KEYWORD, n_berita = N_BERITA)
except IndexError:
    print('''
    Masukan keyword dan jumlah berita yang ingin anda ambil
    contoh:
    python detik_scraper.py KPK 10
    ''')
