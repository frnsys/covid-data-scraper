import time
import lxml.html
import pandas as pd
from selenium import webdriver
from pyvirtualdisplay.smartdisplay import SmartDisplay

url = 'https://coronavirus.1point3acres.com/en'
next_page_target = '.active .case-table .ant-pagination-next[aria-disabled=false]'
cols = ['case', 'date', 'state', 'county', 'notes', 'news_reference']

if __name__ == '__main__':
    display = SmartDisplay(visible=0, size=(1920, 1080))
    display.start()

    # Necessary for headless on server
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)

    page = 1
    rows = []
    while True:
        html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
        html = lxml.html.fromstring(html)
        table = html.cssselect('.active .case-table')[0]
        for row_el in table.cssselect('.ant-table-row'):
            row = {}
            for name, el in zip(cols, row_el.cssselect('td')):
                val = el.text_content()
                if name == 'news_reference':
                    links = [a.attrib.get('href') for a in el.cssselect('a')]
                    links = [l for l in links if l is not None]
                    val = ', '.join(links)
                row[name] = val
            rows.append(row)

        print(page, len(rows))
        if html.cssselect(next_page_target):
            next_page = driver.find_element_by_css_selector(next_page_target)
            driver.execute_script('arguments[0].click();', next_page)
            time.sleep(0.1)
            page += 1
        else:
            break

    df = pd.DataFrame(rows)
    df.to_csv('data.csv', index=False)