# importing
from selenium import webdriver
import dash_html_components as html
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()
import warnings
warnings.filterwarnings('ignore')

url = 'https://www.google.com/'
options = Options()
options.headless = True
driver = webdriver.Chrome(chrome_options=options)
driver.get(url)

driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(
    'new government guidelines for covid 19 in india')
driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(
    Keys.ENTER)
driver.find_element(By.XPATH, '/html/body/div[7]/div/div[4]/div/div[1]/div/div[1]/div/div[2]/a').click()

links = [i.get_attribute("href") for i in
         driver.find_elements(By.XPATH, '/html/body/div[7]/div/div[10]/div/div[2]/div[2]/div/div/div/g-card/div/div/a')]
images = [i.get_attribute('src') for i in
          driver.find_elements(By.XPATH,
                               '/html/body/div[7]/div/div[10]/div/div[2]/div[2]/div/div/div/g-card/div/div/a/div/div[1]/div/div/img')]
header = [i.text for i in driver.find_elements(By.XPATH, '//*[@id="rso"]/div/g-card/div/div/a/div/div[2]/div[2]')]
desc = [i.text for i in driver.find_elements(By.XPATH, '//*[@id="rso"]/div/g-card/div/div/a/div/div[2]/div[3]')]
time_up = [i.text for i in driver.find_elements(By.XPATH, '//*[@id="rso"]/div/g-card/div/div/a/div/div[2]/div[4]/span')]
while 'LIVE' in time_up:
    time_up.remove('LIVE')
driver.quit()
lis = []
for i in range(min(len(header),len(links),len(images),len(desc))):
    lis.append(
        html.A(html.Div([
            html.Div([
                html.Div([
                    html.Table((
                        html.Tr([
                            html.Td(html.Img(src=images[i], width='70px', height='70px',style={'border-radius':'3px'})),
                            html.Td([
                                html.Div([
                                    html.H4(html.B(header[i]), style={'font-size': 'medium'}),
                                    html.P(desc[i], style={'font-size': 'small'}),
                                    html.P(time_up[i], style={'font-size': 'x-small'}),
                                ], style={'padding-left': '10px'})
                            ])
                        ]),
                    ))
                ], className='container22'),
            ], className='card22')
        ],style={'Align':'center'}), href=links[i],
            style={'color': 'black','text-decoration': 'none'})
    )

if len(lis) == 0:
    lis.append('No Data Available')

layout = html.Div(children=lis)