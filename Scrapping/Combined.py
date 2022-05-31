# importing
import re
import requests
from bs4 import BeautifulSoup
from itertools import accumulate
from selenium import webdriver
import time
from selenium.webdriver.support.ui import Select
import pandas as pd
import pymongo
import numpy as np
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import warnings
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()
warnings.filterwarnings('ignore')

States = ['Andhra Pradesh',
          'Bihar',
          'Chattisgarh',
          'Delhi',
          'Goa',
          'Haryana',
          'Himachal Pradesh',
          'Jammu and Kashmir',
          'Jharkand',
          'Madhya Pradesh',
          'Maharastra',
          'Pondicherry',
          'Rajasthan',
          'Tamilnadu',
          'Telangana',
          'Tripura',
          'Uttar Pradesh',
          'Uttarkhand',
          'West Bengal'
          ]


def store_Db(df):
    if not df.empty:
        client = pymongo.MongoClient("mongodb+srv://Covidadmin:coadmin@cluster0.vqxrk.mongodb.net/myFirstDatabase?" +
                                     "retryWrites=true&w=majority")
        information = client['db']['dbinformation']
        state = str(df['State'][0])
        district = list(set(df['District']))
        if len(district) == 1:
            information.delete_many({'state.name': state, 'state.district.name': district[0]})
        else:
            information.delete_many({'state.name': state})
        record = {
            'type': 'data',
            'state': [
                {
                    'name': state,
                    'district': [
                        {
                            'name': list(df['District']),
                            'hospital': [
                                {
                                    'name': list(df['Hospital Name']),
                                    'contact_details': list(df['Contact Details']),
                                    'Requirement': [
                                        {
                                            'name': list(df['Requirement']),
                                            'update': list(df['Last Updated On']),
                                            'availability': [
                                                {
                                                    'Total': list(df['Total']),
                                                    'Vacant': list(df['Vacant'])
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        information.insert_one(record)


def Scrape_AndhraPradesh(district):
    url = 'http://dashboard.covid19.ap.gov.in/ims/hospbed_reports//'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    Requirements = ['ICU Beds', 'General Beds With O2', 'General Beds Without O2', 'Pediatric General Beds',
                    'Pediatric O2 Beds', 'Pediatric ICU Beds', 'Pediatric Ventilators', 'Neonatal Beds',
                    'Neonatal ICU Beds', 'SNCU Beds', 'Neonatal Ventilators', 'Ventilator']
    hospital_Details = []
    x = True
    while (x):
        try:
            driver.find_element(By.LINK_TEXT, value=district).click()
            x = False
        except:
            x = True
    while district in hospital_Details or len(hospital_Details) == 0:
        try:
            hospital_Details = [i.text for i in driver.find_elements(By.XPATH,
                                                                     value='/html/body/main/div/section[2]/div[3]/div/table/tbody/tr/td[2]')]
            if driver.find_element(By.XPATH, value='//*[@id="dataTable"]/tfoot/tr/td[2]').text == '0':
                break
        except:
            continue
    contact_details1 = [i.text for i in
                        driver.find_elements(By.XPATH,
                                             value='/html/body/main/div/section[2]/div[3]/div/table/tbody/tr/td[3]')]
    contact_details2 = [i.text for i in
                        driver.find_elements(By.XPATH,
                                             value='/html/body/main/div/section[2]/div[3]/div/table/tbody/tr/td[4]')]
    dicto = {}
    k = 6
    for i in Requirements:
        dicto[i] = {}
    for i in range(0, len(Requirements) - 1):
        dicto[Requirements[i]]['Total'] = [i.text for i in
                                           driver.find_elements(By.XPATH,
                                                                value=f'//*[@id="dataTable"]/tbody/tr/td[{k}]')]
        dicto[Requirements[i]]['Vacant'] = [i.text for i in
                                            driver.find_elements(By.XPATH,
                                                                 value=f'//*[@id="dataTable"]/tbody/tr/td[{k + 2}]')]
        k += 3
    lt1 = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="dataTable"]/tbody/tr/td[39]')]
    dicto['Ventilator']['Total'] = lt1
    dicto['Ventilator']['Vacant'] = lt1
    lt = []
    for j in range(0, len(hospital_Details)):
        for k in Requirements:
            lt.append([hospital_Details[j], 'Andhra Pradesh', district, k, dicto[k]['Total'][j], dicto[k]['Vacant'][j],
                       [contact_details1[j], contact_details2[j]], 'NA'])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_Bihar():
    url = 'http://covid19health.bihar.gov.in/dailydashboard/bedsoccupied'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    search = [i for i in driver.find_elements(By.XPATH, value='//*[@id="example_filter"]/label/input')]
    search[0].clear()
    search[0].send_keys('a')
    search[0].click()
    x = True
    lt = []
    while x:
        districts = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[1]/span')]
        hospital_name = [i.text for i in
                         driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[2]/span[2]')]
        update = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[5]')]
        contact = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[10]/a')]
        total_beds = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[6]')]
        vacant_beds = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[7]')]
        total_icu_beds = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[8]')]
        vacant_icu_beds = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="example"]/tbody/tr/td[9]')]
        for i in range(0, len(districts)):
            lt.append(
                [hospital_name[i], 'Bihar', districts[i], contact[i], 'Beds', total_beds[i], vacant_beds[i], update[i]])
            lt.append(
                [hospital_name[i], 'Bihar', districts[i], contact[i], 'ICU Beds', total_icu_beds[i], vacant_icu_beds[i],
                 update[i]])
        try:
            driver.find_element(By.XPATH, value='//*[@id="example_next"]/a').click()
            x = True
        except Exception as e:
            x = False
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Contact Details', 'Requirement', 'Total',
                                   'Vacant', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_Chattisgarh(district):
    url = 'https://cg.nic.in/health/covid19/RTPBedAvailable.aspx'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    select = Select(driver.find_element(By.ID, value='ctl00_ContentPlaceHolder1_ddldistricts'))
    select.select_by_visible_text(district)
    hospital_names = [i.text for i in driver.find_elements(By.XPATH,
                                                           value='//*[@id="ctl00_ContentPlaceHolder1_gvAdmindashboard"]/tbody/tr/td[3]')]
    contact_details = [i.text for i in driver.find_elements(By.XPATH,
                                                            value='//*[@id="ctl00_ContentPlaceHolder1_gvAdmindashboard"]/tbody/tr/td[4]/span[2]')]
    updates_date = [i.text for i in driver.find_elements(By.XPATH,
                                                         value='//*[@id="ctl00_ContentPlaceHolder1_gvAdmindashboard"]/tbody/tr/td[21]')]
    updates_time = [i.text for i in driver.find_elements(By.XPATH,
                                                         value='//*[@id="ctl00_ContentPlaceHolder1_gvAdmindashboard"]/tbody/tr/td[22]')]
    update = [((updates_time[i] + " " + updates_date[i]).strip()) for i in range(0, len(updates_date))]
    Reqirements = ['Beds with O2 support', 'Beds without O2 support', 'Isolation bed outside hospital', 'HDU Beds',
                   'ICU Beds', 'Ventilator']
    dicto = {}
    for i in Reqirements:
        dicto[i] = {}
    k = 7
    for i in Reqirements:
        dicto[i]['Total'] = [j.text for j in driver.find_elements(By.XPATH,
                                                                  value=f'//*[@id="ctl00_ContentPlaceHolder1_gvAdmindashboard"]/tbody/tr/td[{k}]')]
        dicto[i]['Vacant'] = [j.text for j in driver.find_elements(By.XPATH,
                                                                   value=f'//*[@id="ctl00_ContentPlaceHolder1_gvAdmindashboard"]/tbody/tr/td[{k + 1}]')]
        k += 2
    lt = []
    for i in range(0, len(hospital_names) - 1):
        for j in Reqirements:
            lt.append([hospital_names[i], 'Chhattisgarh', district, j, dicto[j]['Total'][i], dicto[j]['Vacant'][i],
                       contact_details[i], update[i]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_delhi(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    # getting requirement from the page
    requirement = driver.find_element(By.XPATH, value='//*[@id="page_title"]').text
    # Scraping the list for count of mobile numbers for each hospital
    h = []
    availability_data = [j for j in driver.find_elements(By.XPATH, value='//*[@id="hospitals_list"]/tr/td/a[1]')]
    for x in range(len(availability_data) // 3):
        t = [j.text for j in driver.find_elements(By.XPATH, value=f'//*[@id="collapse{x + 1}"]/td/div/ul/li[2]/a')]
        h.append(t)
    # Scraping mobile numbers
    elems = driver.find_elements(By.CSS_SELECTOR, value=".list-group-item [href]")
    mobile = [elem.get_attribute('href') for elem in elems]
    # spliting mobile numbers to each hospital based on the count we scraped before
    split_length = [len(i) for i in h]
    Contact_details = [mobile[x - y: x] for x, y in zip(
        accumulate(split_length), split_length)]
    # Modifying mobile numbers
    for i in range(len(Contact_details)):
        for j in range(len(Contact_details[i])):
            Contact_details[i][j] = Contact_details[i][j].replace('tel:', '')
    # Getting hospital names
    hospital_name = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="hospitals_list"]/tr/th/a[2]')]
    # Getting last updated data
    update = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="hospitals_list"]/tr/td[1]/small/a')]
    # Getting availability of resourses in each hospital
    Total = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="hospitals_list"]/tr/td[2]/a[1]')]
    Vacant = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="hospitals_list"]/tr/td[4]/a[1]')]
    oxygen = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="hospitals_list"]/tr/td[5]/small/a')]
    # Adding the data to a list to format it based on headers list
    lt = []
    for i in range(len(hospital_name)):
        lt.append([hospital_name[i], 'Delhi', 'NA', requirement, Total[i], Vacant[i], Contact_details[i], update[i]])
        lt.append([hospital_name[i], 'Delhi', 'NA', 'Oxygen', oxygen[i], oxygen[i], Contact_details[i], update[i]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_Goa():
    url = 'https://goaonline.gov.in/beds'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    date = '[0-9]{2}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}[am|pm]'
    data = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="cphBody_gvBedsAvailable"]/tbody/tr')]
    for i in data:
        if not re.search(date, i):
            data.remove(i)
    regex = '[0-9]+ [a-z]*'
    update = []
    hospital_name = []
    details = []
    for i in range(0, len(data)):
        t = [(m.start(), m.end()) for m in re.finditer(regex, data[i])]
        if len(t) == 0:
            del data[i]
        else:
            t1 = [(m.start(), m.end()) for m in re.finditer(date, data[i])]
            t2 = [(m.start(), m.end()) for m in re.finditer('[0-9 ]+', data[i])]
            if len(t1) != 0:
                update.append(data[i][t1[0][0]:])
                data[i] = data[i][t[0][1]:t1[0][0]].strip()
                t2 = [(m.start(), m.end()) for m in re.finditer('[0-9]+', data[i])]
                details.append(data[i][t2[0][0]:])
                hospital_name.append(data[i][:t2[0][0]])
    Requirements = ['Covid Beds', 'ICU Beds']
    for i in range(0, len(details)):
        details[i] = details[i].split()
    details = sum(details, [])
    Requirements = ['Covid Beds', 'ICU Beds']
    dicto = {}
    j = 0
    for i in Requirements:
        dicto[i] = {}
    for i in Requirements:
        dicto[i]['Total'] = [details[k] for k in range(j, len(details), 4)]
        dicto[i]['Vacant'] = [details[k + 1] for k in range(j, len(details), 4)]
        j += 2
    lt = []
    for i in range(0, len(hospital_name)):
        for j in Requirements:
            lt.append([hospital_name[i], 'Goa', 'NA', j, dicto[j]['Total'][i], dicto[j]['Vacant'][i], 'NA', update[i]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_Haryana():
    url = 'https://coronaharyana.in/'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    districts = [i.get_attribute("value") for i in driver.find_elements(By.TAG_NAME, value="option")]
    forming = []
    for dist in range(1, len(districts) + 1):
        url = f'https://coronaharyana.in/?city={dist}'
        driver.get(url)
        Requirements = ['Oxygen Beds', 'Non-Oxygen Beds', 'ICU Beds', 'Ventilators']
        total = []
        dicto = {}
        k = 1
        hospital_name = [i.text[15:] for i in
                         driver.find_elements(By.XPATH, value='//*[@id="containner0-tab"]/div/div[1]/div/div[1]/h6')]
        update = [i.text[12:] for i in
                  driver.find_elements(By.XPATH,
                                       value='/html/body/div[1]/section[3]/div/div/div[1]/div/div/div[2]/ul/li[1]')]
        t = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="containner0-tab"]/div/div[1]/div/div[2]')]
        for j in t:
            t1 = [(m.start(0), m.end(0)) for m in re.finditer('[0-9]+', j)]
            for i in t1:
                total.append(j[i[0]:i[1]])
        change = np.array(total).reshape(-1, 4)
        for i in Requirements:
            dicto[i] = {}
        for i in Requirements:
            dicto[i]['Vacant'] = [i.text for i in
                                  driver.find_elements(By.XPATH,
                                                       value=f'//*[@id="containner0-tab"]/div/div[1]/div/p/a[{k}]')]
            dicto[i]['Total'] = [i[k - 1] for i in change]
            k += 1
        contact = [i.text for i in
                   driver.find_elements(By.XPATH, value='//*[@id="containner0-tab"]/div/div[1]/div/div[3]/span/a')]
        for i in range(0, len(hospital_name)):
            for j in Requirements:
                forming.append(
                    [hospital_name[i], 'Haryana', districts[dist - 1], j, dicto[j]['Total'][i], dicto[j]['Vacant'][i],
                     contact[i], update[i]])
    df = pd.DataFrame(forming, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                        'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_HimachalPradesh(Requirement, itera):
    url = 'https://covidcapacity.hp.gov.in/index.php#'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    driver.find_element(By.LINK_TEXT, value=Requirement).click()
    district = [i.text for i in
                driver.find_elements(By.XPATH, value=f'/html/body/div[{itera}]/div/div/div[2]/table/tbody/tr/td[1]')]
    hospital_name = [i.text for i in
                     driver.find_elements(By.XPATH,
                                          value=f'/html/body/div[{itera}]/div/div/div[2]/table/tbody/tr/td[2]')]
    total = [i.text for i in
             driver.find_elements(By.XPATH, value=f'/html/body/div[{itera}]/div/div/div[2]/table/tbody/tr/td[3]')]
    vacant = [i.text for i in
              driver.find_elements(By.XPATH, value=f'/html/body/div[{itera}]/div/div/div[2]/table/tbody/tr/td[5]')]
    update = [i.text for i in
              driver.find_elements(By.XPATH, value=f'/html/body/div[{itera}]/div/div/div[2]/table/tbody/tr/td[6]')]
    contact = [i.text for i in
               driver.find_elements(By.XPATH, value=f'/html/body/div[{itera}]/div/div/div[2]/table/tbody/tr/td[7]')]
    del district[len(contact)]
    del hospital_name[len(contact)]
    del total[len(contact)]
    del vacant[len(contact)]
    del update[len(contact)]
    lt = []
    for j in range(0, len(hospital_name)):
        lt.append([hospital_name[j], 'Himachal Pradesh', district[j], Requirement, total[j], vacant[j], contact[j],
                   update[j]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_JK(district, i, dicto):
    url = 'https://covidrelief.jk.gov.in/Beds'
    options = Options()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    lt = []
    c = 0
    driver.get(url)
    while 1:
        try:
            driver.find_element(By.XPATH,
                                value=f'/html/body/div/div/div/div[2]/div/div/div/div/div[{i + 1}]/div[1]').click()
            hospital_name = []
            while len(hospital_name) == 0:
                hospital_name = [j.text for j in driver.find_elements(By.XPATH,
                                                                      value='/html/body/div/div/div/div[2]/div/div/div/div/div/div[1]/h4')]
            update = [j.text for j in
                      driver.find_elements(By.XPATH,
                                           value='/html/body/div/div/div/div[2]/div/div/div/div/div/div[3]/h5/span')]
            for k in range(1, len(hospital_name) + 1):
                while 1:
                    try:
                        time.sleep(1)
                        driver.find_element(By.XPATH,
                                            value=f'/html/body/div/div/div/div[2]/div/div/div/div/div[{k}]/div[1]/h4').click()
                        lrt = []
                        while len(lrt) != 4:
                            vacant = [j.text for j in
                                      driver.find_elements(By.XPATH,
                                                           value='/html/body/div/div/div/div/div/div/div[1]/span')]
                            total = [j.text for j in
                                     driver.find_elements(By.XPATH, value='/html/body/div/div/div[2]/div/div/div/div')]
                            lrt = [re.sub("[^0-9]", "", j) for j in total]
                        lt.append([hospital_name[k - 1], 'Jammu and Kashmir', district, 'Isolation Bed', lrt[1], lrt[0],
                                   dicto[district], update[k - 1]])
                        lt.append([hospital_name[k - 1], 'Jammu and Kashmir', district, 'ICU Bed', lrt[3], lrt[2],
                                   dicto[district], update[k - 1]])
                        driver.back()
                        break
                    except Exception as e:
                        links = driver.find_elements(By.XPATH,
                                                     value="/html/body/div/div/div/div[2]/div/div/div/div/div/div[1]/h4")
                        for link in links:
                            driver.execute_script("arguments[0].scrollIntoView();", link)
            break
        except Exception as e:
            c += 1
            links = driver.find_elements(By.XPATH, value="/html/body/div/div/div/div[2]/div/div/div/div/div/div[1]/p")
            for link in range(0, min((i + 1), len(links))):
                driver.execute_script("arguments[0].scrollIntoView();", links[link])
            if c > 3:
                break
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_Jharkand(district):
    url = 'http://amritvahini.in/DashBoardHospitalDetails.aspx?Districtcode=0&HType=0'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    select = Select(driver.find_element(By.ID, value='ContentPlaceHolder1_ddlDistrict'))
    select.select_by_visible_text(district)
    driver.find_element(By.XPATH, value='//*[@id="ContentPlaceHolder1_btnsearch"]').click()
    hospital_names = [i.text for i in driver.find_elements(By.XPATH,
                                                           value='/html/body/form/div[5]/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div/table/tbody/tr/td[2]/a')]
    update = []
    contact = []
    Requirements = ['Beds Without Oxygen', 'Beds With Oxygen', 'ICU Beds Without Ventilator',
                    'ICU Beds With Ventilator']
    dicto = {}
    k = 3
    for i in Requirements:
        dicto[i] = {}
        dicto[i]['Total'] = [i.text for i in driver.find_elements(By.XPATH,
                                                                  value=f'/html/body/form/div[5]/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div/table/tbody/tr/td[{k}]/span[3]')]
        dicto[i]['Vacant'] = [i.text for i in driver.find_elements(By.XPATH,
                                                                   value=f'/html/body/form/div[5]/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div/table/tbody/tr/td[{k}]/span[1]')]
        k += 1
    for i in range(1, len(hospital_names)):
        while 1:
            try:
                driver.find_element(By.XPATH,
                                    value=f'/html/body/form/div[5]/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div/table/tbody/tr[{i + 1}]/td[2]/a').click()
                update.append(driver.find_element(By.XPATH,
                                                  value='/html/body/form/div[5]/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/ul/li[1]/span').text)
                contact.append(driver.find_element(By.XPATH,
                                                   value='/html/body/form/div[5]/div[2]/div/div/div/div[2]/div/div/div[2]/div[1]/ul/li[3]/a').text)
                driver.find_element(By.XPATH,
                                    value='/html/body/form/div[5]/div[2]/div/div/div/div[2]/div/div/div[2]/div[2]/a/input').click()
                break
            except Exception as e:
                body = driver.find_element(By.CSS_SELECTOR, value='body')
                body.send_keys(Keys.PAGE_DOWN)
    lt = []
    for i in range(0, len(hospital_names) - 1):
        for j in Requirements:
            lt.append(
                [hospital_names[i], 'Jharkand', district, j, dicto[j]['Total'][i], dicto[j]['Vacant'][i], contact[i],
                 update[i]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_MadhyaPradesh(dt, district):
    try:
        url = 'http://sarthak.nhmmp.gov.in/covid/facility-bed-occupancy-details/'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        lt = []
        select = Select(driver.find_element(By.ID, value='district_id'))
        select.select_by_visible_text(dt)
        driver.find_element(By.XPATH, value='//*[@id="main"]/div/section[2]/form/div/div[4]/button').click()
        while 1:
            try:
                update = [i.text for i in driver.find_elements(By.XPATH,
                                                               value='//*[@id="main"]/div/section[3]/table/tbody/tr/td[2]/div[2]/span')]
                let = [driver.find_element(By.XPATH,
                                           value=f'//*[@id="main"]/div/section[3]/table/tbody/tr[{k}]/td[1]/div[1]').text
                       for k in
                       range(1, len(update) * 2, 2)]
                hospital = [i[:i.index('/')] for i in let]
                contact = [driver.find_element(By.XPATH,
                                               value=f'/html/body/div[1]/div[3]/div/div/section[3]/table/tbody/tr[{k}]/td/div/div/span/a').text
                           for k in
                           range(2, len(update) * 2 + 1, 2)]
                dicto = {}
                Requirement = ['Isolation Beds', 'Oxygen Supported Beds', 'ICU/HDU Beds']
                k = 1
                for req in Requirement:
                    dicto[req] = [i.text for i in driver.find_elements(By.XPATH,
                                                                       value=f'//*[@id="main"]/div/section[3]/table/tbody/tr/td[2]/div[1]/ul/li[{k}]/label')]
                    k += 1
                for j in range(0, len(hospital)):
                    for k in Requirement:
                        lt.append([hospital[j], 'Madhya Pradesh', district, k, dicto[k][j], dicto[k][j], contact[j],
                                   update[j]])
                driver.find_element(By.LINK_TEXT, value='Next').click()
            except:
                break
        df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                       'Contact Details', 'Last Updated On'], dtype=object)
        driver.quit()
        store_Db(df)
    except Exception as e:
        print(str(e))


def Scrape_Mumbai():
    url = 'https://nmmchealthfacilities.com/HospitalInfo/showhospitalist'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    while 1:
        try:
            hospital_name = [i.text for i in driver.find_elements(By.XPATH,
                                                                  value='/html/body/div/div[2]/div/div[3]/div/div[3]/div/div/div/div/div[1]/div/h4/b')]
            break
        except:
            continue
    dicto = {}
    Requirement = ['ICU bed', 'Bed with oxygen', 'Bed without oxygen', 'Ventilator']
    for i in Requirement:
        dicto[i] = {}
    k = 2
    for i in Requirement:
        dicto[i]['Total'] = [i.text for i in driver.find_elements(By.XPATH,
                                                                  value=f'/html/body/div/div[2]/div/div[3]/div/div[3]/div/div/div/div/div[2]/div[2]/div/table/tbody/tr[{k}]/td[2]')]
        dicto[i]['Vacant'] = [i.text for i in driver.find_elements(By.XPATH,
                                                                   value=f'/html/body/div/div[2]/div/div[3]/div/div[3]/div/div/div/div/div[2]/div[2]/div/table/tbody/tr[{k}]/td[4]')]
        k += 1
    lt = []
    for i in range(0, len(hospital_name)):
        for j in Requirement:
            lt.append([hospital_name[i], 'Maharastra', 'Navi Mumbai', j, dicto[j]['Total'][i], dicto[j]['Vacant'][i],
                       '022-27567460', 'NA'])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_Nashik():
    url = 'http://covidcbrs.nmc.gov.in/home/searchHosptial'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    Requirements = ['General Beds', 'Oxygen Beds', 'ICU Beds', 'Ventilator Beds']
    dicto = {}
    k = 4
    for j in Requirements:
        dicto[j] = {}
        dicto[j]['Total'] = [(re.findall('[0-9]+', i.text)[0]) for i in driver.find_elements(By.XPATH,
                                                                                             value=f'/html/body/section/div/div/div/div/div/form/table/tbody/tr/td[{k}]')]
        dicto[j]['Vacant'] = [(re.findall('[0-9]+', i.text)[0]) for i in driver.find_elements(By.XPATH,
                                                                                              value=f'/html/body/section/div/div/div/div/div/form/table/tbody/tr/td[{k + 1}]')]
        k += 2
    details = [i for i in
               driver.find_elements(By.XPATH,
                                    value='/html/body/section/div/div/div/div/div/form/table/tbody/tr/td[2]/a')]
    hospital = []
    contact = []
    for i in range(0, len(details)):
        name = ''
        cont = ''
        while 1:
            try:
                name2 = driver.find_element(By.XPATH,
                                            value=f'/html/body/section/div/div/div/div/div/form/table/tbody/tr[{i + 1}]/td[2]/a')
                ActionChains(driver).move_to_element(name2).click(name2).perform()
                time.sleep(0.5)
                name = driver.find_element(By.XPATH,
                                           value=f'/html/body/section/div/div/div/div/div/form/div[{i + 1}]/div/div/div[2]/ul/li[1]/label[2]').text
                cont = driver.find_element(By.XPATH,
                                           value=f'/html/body/section/div/div/div/div/div/form/div[{i + 1}]/div/div/div[2]/ul/li[6]/label[2]').text
                button = driver.find_element(By.XPATH,
                                             value=f'/html/body/section/div/div/div/div/div/form/div[{i + 1}]/div/div/div[3]/button')
                button.click()
                break
            except Exception as e:
                print(str(e))
                body = driver.find_element(By.CSS_SELECTOR, value='body')
                body.send_keys(Keys.PAGE_DOWN)
                continue
        hospital.append(name)
        contact.append(cont)
    lt = []
    for i in range(0, len(hospital)):
        for j in Requirements:
            lt.append(
                [hospital[i], 'Maharastra', 'Nashik', j, dicto[j]['Total'][i], dicto[j]['Vacant'][i], contact[i], 'NA'])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_Thane():
    url = 'https://coviguard.in/Tmc_HM/HospitalInfo/showhospitalist'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    while 1:
        try:
            hospital_name = [i.text for i in driver.find_elements(By.XPATH,
                                                                  value='/html/body/div/div[2]/div/div[3]/div/div[3]/div/div/div/div/div[1]/div/h4/b')]
            break
        except:
            print('Web page loading')
    dicto = {}
    Requirement = ['ICU bed', 'Bed with oxygen', 'Bed without oxygen', 'Ventilator']
    for i in Requirement:
        dicto[i] = {}
    k = 2
    for i in Requirement:
        dicto[i]['Total'] = [i.text for i in driver.find_elements(By.XPATH,
                                                                  value=f'/html/body/div/div[2]/div/div[3]/div/div[3]/div/div/div/div/div[2]/div[2]/div/table/tbody/tr[{k}]/td[2]')]
        dicto[i]['Vacant'] = [i.text for i in driver.find_elements(By.XPATH,
                                                                   value=f'/html/body/div/div[2]/div/div[3]/div/div[3]/div/div/div/div/div[2]/div[2]/div/table/tbody/tr[{k}]/td[4]')]
        k += 1
    lt = []
    for i in range(0, len(hospital_name)):
        for j in Requirement:
            lt.append([hospital_name[i], 'Maharastra', 'Thane', j, dicto[j]['Total'][i], dicto[j]['Vacant'][i],
                       '022-27567460', 'NA'])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_Pondicherry():
    url = 'https://covid19dashboard.py.gov.in/BedAvailabilityDetails'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    dicto2 = {'Pondicherry': 'PDY', 'Karaikal': 'KKL', 'Mahe': 'MAH', 'Yanam': 'YAN'}
    date = '[0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2}'
    forming = []
    Requirements = ['Isolation Beds', 'Oxygen Beds', 'Ventilator Beds']
    for district in dicto2.keys():
        hospital_name = []
        hospital_type = []
        update = []
        data = []
        a = ''
        driver.find_element(By.LINK_TEXT, value=district).click()
        time.sleep(2)
        result = [i.text for i in
                  driver.find_elements(By.XPATH, value=f'//*[@id="Vaccination_{dicto2[district]}"]/div/table/tbody/tr')]
        for j in range(0, len(result)):
            i = result[j]
            if not re.search(date, i):
                a = i
            else:
                t1 = [(m.start(0), m.end(0)) for m in re.finditer(date, i)]
                hospital_type.append(a)
                update.append(i[t1[0][0]:t1[0][1]])
                result[j] = i[:t1[0][0]] + "" + i[t1[0][1]:]
                t2 = [(m.start(0), m.end(0)) for m in re.finditer('[0-9]+', i)]
                data.append((result[j][t2[0][0]:t2[len(t2) - 1][1]]).strip())
                result[j] = result[j][:t2[0][0]] + "" + result[j][t2[len(t2) - 1][1]:]
                hospital_name.append(result[j].strip())
        for i in range(0, len(data)):
            data[i] = data[i].split(" ")
        data = sum(data, [])
        dicto = {}
        k = 0
        for i in Requirements:
            dicto[i] = [(data[i], data[i + 1]) for i in range(k, len(data), 6)]
            k += 2
        for i in range(0, len(hospital_name)):
            for j in Requirements:
                forming.append(
                    [hospital_name[i], 'Pondicherry', district, j, dicto[j][i][0], dicto[j][i][1], 'NA', update[i]])
    df = pd.DataFrame(forming, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                        'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scrape_Tamilnadu(i):
    url = 'https://tncovidbeds.tnega.org/'
    options = Options()
    options.headless = True
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    Requirements = ['Normal Beds', 'Oxygen Supported Beds', 'ICU Beds', 'Total Beds']
    lt = []
    count = 0
    while 1:
        try:
            select = Select(driver.find_element(By.XPATH,
                                                value='//*[@id="root"]/div/div/div[1]/div/div/div[2]/div/div/div[1]/div/div/p[2]/select'))
            select.select_by_index(i)
            break
        except Exception as e:
            if count > 5:
                break
            count += 1
            continue
    driver.find_element(By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/center/button').click()
    count = 0
    while 1:
        try:
            driver.find_element(By.XPATH,
                                value='/html/body/div/div/div/div[1]/div/div/div[3]/div/div/div/div/div[1]/div[4]/div/div/div/div/div/div/button').click()
            driver.find_element(By.XPATH,
                                value='/html/body/div/div/div/div[1]/div/div/div[3]/div/div/div/div/div[1]/div[4]/div/div/div/div/div/div/div/button[5]').click()
            break
        except Exception as e:
            if count > 5:
                break
            count += 1
            continue
    details = []
    while len(details) == 0:
        details = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="tableBody"]/tr')]
    Str = driver.find_element(By.XPATH,
                              value='//*[@id="root"]/div/div/div[1]/div/div/div[3]/div/div/div/div/div[1]/div[4]/div/div/div/div/div/span[2]').text
    total = int(Str[Str.index('of') + 2:].strip())
    for i in range(0, len(details), 3):
        details[i] = details[i].split('\n')
        if 'Total' in details[i]:
            k = details[i].index('Total') + 1
            if len(details[i]) > 12:
                for a in Requirements:
                    lt.append(
                        [details[i][0], 'Tamilnadu', details[i][2], details[i][3], a, details[i][k], details[i][k + 1],
                         details[i][5].replace('Last Updated on: ', '')])
                    k += 2
    total -= 100
    while total > 0:
        while 1:
            try:
                driver.find_element(By.XPATH,
                                    value='//*[@id="root"]/div/div/div[1]/div/div/div[3]/div/div/div/div/div[2]/ul/li[6]/a').click()
                break
            except Exception as e:
                print(str(e))
                body = driver.find_element(By.CSS_SELECTOR, value='body')
                body.send_keys(Keys.PAGE_DOWN)
        details = []
        while len(details) == 0:
            details = [j.text for j in driver.find_elements(By.XPATH, value='//*[@id="tableBody"]/tr')]
        for i in range(0, len(details), 3):
            details[i] = details[i].split('\n')
            if 'Total' in details[i]:
                k = details[i].index('Total') + 1
                if len(details[i]) > 12:
                    for a in Requirements:
                        lt.append([details[i][0], 'Tamilnadu', details[i][2], details[i][3], a, details[i][k],
                                   details[i][k + 1], details[i][5].replace('Last Updated on: ', '')])
                        k += 2
        total -= 100
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Contact Details', 'Requirement', 'Total',
                                   'Vacant', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_Telangana(lt, Type):
    trail = []
    headers = ['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Occupied', 'Vacant', 'Contact Details',
               'Last Updated On']
    dicto = {}
    # to split the requirements availability list
    split = [3, 3, 3, 3]
    # to get district name
    reg = '[0-9]+ [A-Z]'
    # to remove index value
    reg3 = '[0-9]+.'
    # to get contact numbers
    mobile = '[0-9]{5,10}|--'
    # to get last updated date and time
    date = '[0-9]{2}/[0-9]{2}/[0-9]{4}'
    Requirements = ['REGULAR BEDS', 'OXYGEN BEDS', 'ICU BEDS (Ventilator/ CPAP)', 'TOTAL BEDS']
    for j in lt:
        # retriving district from 1st data and then processing
        if re.match(reg, j):
            reg2 = ' [0-9]+. [A-Z]'
            t = [(m.start(0), m.end(0)) for m in re.finditer(reg2, j)]
            district = j[:t[0][0]].split()[1]
            i = j[t[0][0]:].strip()
        else:
            i = j
        # removing of index value from the data    
        t2 = [(m.start(0), m.end(0)) for m in re.finditer(reg3, i)]
        tt = i[t2[0][1]:].strip()
        # getting hospital name and contacts
        t3 = [(m.start(0), m.end(0)) for m in re.finditer(mobile, tt)]
        hospital_name = tt[:t3[0][0]]
        contacts = []
        # appending all the contacts in a single list
        for j in t3:
            contacts.append(tt[j[0]:j[1]])
        # getting latest updated date and time
        t4 = [(m.start(0), m.end(0)) for m in re.finditer(date, tt)]
        update = tt[t4[0][0]:]
        # getting the availability status data for all the requirements
        data = tt[t3[len(t3) - 1][1]:t4[0][0]].strip().split()
        # spliting the data into 3 subcategories for each requirement
        Output = [data[x - y: x] for x, y in zip(
            accumulate(split), split)]
        # adding the splitted date w.r.t requirement in a dictonary
        for i in range(len(Requirements)):
            dicto[Requirements[i]] = Output[i]
        # Appending all the data to create a list[list] for forming the data frame
        for require in dicto.keys():
            apaend = [hospital_name, 'Telangana', district, require, dicto[require][0], dicto[require][1],
                      dicto[require][2], contacts, update]
            trail.append(apaend)
        df = pd.DataFrame(trail, columns=headers, dtype=object)
        store_Db(df)


def Scrape_Tripura():
    url = 'https://covid19.tripura.gov.in/bed_availability_status.html'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    table1_head = soup.find('thead')
    table_body = soup.find('tbody')
    headers = []
    for i in table1_head.find_all('td'):
        title = i.text.strip()
        headers.append(title)
    for i in range(0, len(headers)):
        headers[i] = headers[i].replace('  ', '')
        headers[i] = headers[i].replace('\n', '')
        headers[i] = headers[i].replace('\r', '')
    data = []
    for j in table_body.find_all('tr'):
        row_data = j.find_all('td')
        row = [i.text.strip() for i in row_data]
        for i in range(0, len(row)):
            row[i] = row[i].replace('  ', '')
            row[i] = row[i].replace('\n', '')
            row[i] = row[i].replace('\r', '')
        del row[0]
        data.append(row)
    districts = ['Dhalai', 'Gomati', 'Khowai', 'North Tripura', 'Sepahijala', 'South Tripura', 'Unakoti',
                 'West Tripura']
    types = ['DCH', 'DCHC', 'DCCC', 'Isolation Centre']
    district = 'NA'
    typed = ''
    lt = []
    contact = {'Dhalai': ['1077', ' 0382626726'], 'Gomati': ['9863673349', '8414974777', '7629900889'],
               'Khowai': ['03825295254'],
               'North Tripura': ['03822234349', '8415046060', '6033192564', '8414833072'],
               'Sepahijala': ['03812951750', '9362711916'],
               'South Tripura': ['03823222145'], 'Unakoti': ['0382461200', '9362822706', '9362822707', '9362822708'],
               'West Tripura': [
                   '03817967125'], 'NA': ['NA']}
    last_updated = re.findall('[0-9]{2}.[0-9]{2}.[0-9]{4}', headers[4])[0]
    for i in data:
        for j in i:
            if (j in districts):
                district = j
            elif (j in types):
                typed = j
        if (district in i):
            i.remove(district)
        if (typed in i):
            i.remove(typed)
        lt.append(
            [i[0], 'Tripura', district, 'General Bed', (int(i[1]) + int(i[2])), i[2], contact[district], last_updated])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)


def Scrape_UttarPradesh(district):
    url = 'https://beds.dgmhup-covid19.in/EN/covid19bedtrack'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    reg = 'Private|Public'
    phone = '[0-9]{10}'
    lt = []
    Requirements = ['Isolation Bed', 'Isolation Bed with Oxygen', 'HDU/ICU Bed', 'Post Covid Bed']
    sub = ['Total', 'Vacant']
    xt = ['No Data', 'No Data', 'No Data', 'No Data', 'No Data', 'No Data', 'No Data', 'No Data']
    t = []
    while True:
        try:
            select = Select(driver.find_element(By.ID, value='MainContent_EN_ddDistrict'))
            select.select_by_visible_text(district)
            driver.find_element(By.XPATH, value='//*[@id="MainContent_EN_Button2"]').click()
            break
        except:
            body = driver.find_element(By.CSS_SELECTOR, value='body')
            body.send_keys(Keys.PAGE_UP)
    Hospital_Details = [j.text for j in driver.find_elements(By.XPATH,
                                                             value='/html/body/form/div[4]/table/tbody/tr[3]/td[2]/div[1]/table/tbody/tr/td/table/tbody/tr/td[2]')]
    t.append(Hospital_Details)
    update = [i.text for i in driver.find_elements(By.XPATH,
                                                   value='/html/body/form/div[4]/table/tbody/tr[3]/td[2]/div[1]/table/tbody/tr/td/table/tbody/tr/td[6]/span')]
    st = []
    for i in range(2, len(update) * 3, 3):
        driver.find_element(By.XPATH,
                            value=f'/html/body/form/div[4]/table/tbody/tr[3]/td[2]/div[1]/table/tbody/tr/td/table/tbody/tr[{i}]/td[3]/a').click()
        time.sleep(2)
        ot = []
        try:
            ot = ([i.text for i in driver.find_elements(By.XPATH,
                                                        value='/html/body/form/div[6]/table/tbody/tr/td/div/table/tbody/tr/td/span')])
            driver.find_element(By.XPATH, value='/html/body/form/div[6]/input').click()
        except:
            ot = (xt)
        if (len(ot) == 0):
            st.append(xt)
        else:
            st.append(ot)
    a = 0
    dicto = {}
    for i in Requirements:
        dicto[i] = {}
        for j in sub:
            dicto[i][j] = []
    while a < len(st):
        k = 0
        for j in sub:
            for i in Requirements:
                dicto[i][j].append(st[a][k])
                k += 1
        a += 1
    for j in range(0, len(t)):
        for i in range(0, len(t[j])):
            t[j][i] = t[j][i].split('\n')
    k = []
    for j in range(0, len(t)):
        for i in range(1, len(t[j]), 3):
            st = ""
            for a in t[j][i]:
                st = st + " " + a.strip()
            for a in t[j][i + 1]:
                st = st + " " + a.strip()
            k.append(st.strip())
    for i2 in range(0, len(k)):
        t4 = [(m.start(0), m.end(0)) for m in re.finditer(reg, k[i2])]
        hospital_name = k[i2][:t4[0][0]]
        t = k[i2][t4[0][1]:].strip()
        t1 = [(m.start(0), m.end(0)) for m in re.finditer(phone, t)]
        if len(t1) != 0:
            phone_number = t[t1[0][0]:t1[0][1]].strip()
        else:
            phone_number = ''
        for j in Requirements:
            lt.append([hospital_name, 'Uttar Pradesh', district, j, dicto[j]['Total'][i2], dicto[j]['Vacant'][i2],
                       phone_number, update[i2]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    store_Db(df)
    driver.quit()


def Scrape_Uttarakhand():
    url = 'https://covid19.uk.gov.in/bedssummary.aspx'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    Districts = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="lblDistrictName"]')]
    Hospital_names = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="lblhospitalName"]')]
    Contact_details = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="lblnodalofficerContactNumber"]')]
    Requirements = ['Beds Without Oxygen', 'Beds With Oxygen', 'ICU Beds', 'Ventilators']
    sub2 = ['//*[@id="Lbloccupiedgenralbeds"]', '//*[@id="lbltotGenralbeds"]', '//*[@id="lbloccupiedoxygenbeds"]',
            '//*[@id="lbltotoxygenbeds"]', '//*[@id="lbloccupiedicubeds"]', '//*[@id="lbltoticubeds"]',
            '//*[@id="lbloccupiedventilators"]', '//*[@id="lbltotventilaors"]']
    dicto = {}
    counter = 0
    for i in Requirements:
        dicto[i] = {}
    for i in Requirements:
        dicto[i]['Vacant'] = [k.text for k in driver.find_elements(By.XPATH, value=sub2[counter])]
        dicto[i]['Total'] = [k.text for k in driver.find_elements(By.XPATH, value=sub2[counter + 1])]
        counter += 2
    update = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="lbllastupdated"]')]
    lt = []
    for i in range(0, len(Hospital_names)):
        for j in Requirements:
            lt.append([Hospital_names[i], 'Uttarakhand', Districts[i], j, dicto[j]['Total'][i], dicto[j]['Vacant'][i],
                       Contact_details[i], update[i]])
    df = pd.DataFrame(lt, columns=['Hospital Name', 'State', 'District', 'Requirement', 'Total', 'Vacant',
                                   'Contact Details', 'Last Updated On'], dtype=object)
    driver.quit()
    store_Db(df)


def Scraping(state):
    if state == 'Andhra Pradesh':
        url = 'http://dashboard.covid19.ap.gov.in/ims/hospbed_reports//'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        districts = []
        while len(districts) == 0:
            districts = [i.text.strip() for i in
                         driver.find_elements(By.XPATH, value='//*[@id="dataTable"]/tbody/tr/td[2]')]
        driver.quit()
        with ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(Scrape_AndhraPradesh, districts)
        driver.quit()
    elif state == 'Bihar':
        Scrape_Bihar()
    elif state == 'Chattisgarh':
        url = 'https://cg.nic.in/health/covid19/RTPBedAvailable.aspx'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)

        districts = [i.text for i in driver.find_elements(By.XPATH,
                                                          value='/html/body/form/div[3]/nav/nav/div[1]/div/center/table/tbody[2]/tr[1]/td/select[2]/option')]
        del districts[0]
        driver.quit()
        with ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(Scrape_Chattisgarh, districts)
    elif state == 'Delhi':
        url = 'https://coronabeds.jantasamvad.org/'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        # Getting links for various available requirements
        elems = driver.find_elements(By.CSS_SELECTOR, value=".col [href]")
        links = [elem.get_attribute('href') for elem in elems]
        links = list(set(links))
        driver.quit()
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(Scrape_delhi, links)
    elif state == 'Goa':
        Scrape_Goa()
    elif state == 'Haryana':
        Scrape_Haryana()
    elif state == 'Himachal Pradesh':
        url = 'https://covidcapacity.hp.gov.in/index.php#'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        Requirements = [i.text for i in
                        driver.find_elements(By.XPATH,
                                             value='/html/body/section[1]/div/div/div[2]/table/tbody/tr/th/a/span')]
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(Scrape_HimachalPradesh, Requirements, [2, 1, 3])
        driver.quit()
    elif state == 'Jammu and Kashmir':
        helpline = 'https://covidrelief.jk.gov.in/Helplines'
        options = Options()
        options.headless = True
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(helpline)
        dicto = {}
        district = [i.text for i in
                    driver.find_elements(By.XPATH, value='/html/body/div/div/div[2]/div/table[1]/tbody/tr/td[2]')]
        contact = [i.text for i in
                   driver.find_elements(By.XPATH, value='/html/body/div/div/div[2]/div/table[1]/tbody/tr/td[3]')]
        for i in district:
            dicto[i] = []
        for i in range(0, len(district)):
            dicto[district[i]].append(contact[i])
        district = [i.text for i in
                    driver.find_elements(By.XPATH, value='/html/body/div/div/div[2]/div/table[2]/tbody/tr/td[2]')]
        contact = [i.text for i in
                   driver.find_elements(By.XPATH, value='/html/body/div/div/div[2]/div/table[2]/tbody/tr/td[3]')]
        for i in district:
            if i not in dicto.keys():
                dicto[i] = []
        for i in range(0, len(district)):
            dicto[district[i]].append(contact[i])
        driver.quit()
        url = 'https://covidrelief.jk.gov.in/Beds'
        options = Options()
        options.headless = True
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        districts = [i.text for i in
                     driver.find_elements(By.XPATH, value='/html/body/div/div/div/div[2]/div/div/div/div/div/div[1]/p')]
        driver.quit()
        for i in districts:
            if (i not in dicto.keys()):
                dicto[i] = ['NA']
        with ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(Scrape_JK, districts, [j for j in range(0, len(districts) - 1)],
                         [dicto for _ in range(0, len(districts) - 1)])
    elif state == 'Jharkand':
        url = 'http://amritvahini.in/DashBoardHospitalDetails.aspx?Districtcode=0&HType=0'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        districts = [i.text for i in driver.find_elements(By.XPATH,
                                                          value='/html/body/form/div[5]/div[2]/div/div/div/div[1]/div[2]/div[1]/div/div[1]/div/select/option')]
        if len(districts) != 0:
            del districts[0]
            driver.quit()
            with ThreadPoolExecutor(max_workers=6) as executor:
                executor.map(Scrape_Jharkand, districts)
    elif state == 'Madhya Pradesh':
        url = 'http://sarthak.nhmmp.gov.in/covid/facility-bed-occupancy-details/'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        details = [i.text for i in driver.find_elements(By.XPATH, value='//*[@id="district_id"]/option')]
        reg = '^[a-zA-Z]+[ a-zA-Z]*'
        districts = []
        for i in details:
            t = re.findall(reg, i)
            if len(t) != 0:
                districts.append(t[0])
        driver.quit()
        with ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(Scrape_MadhyaPradesh, [details[j] for j in range(1, len(details) - 1)], districts)
    elif state == 'Maharastra':
        Scrape_Nashik()
        Scrape_Mumbai()
        Scrape_Thane()
    elif state == 'Pondicherry':
        Scrape_Pondicherry()
    elif state == 'Tamilnadu':
        url = 'https://tncovidbeds.tnega.org/'
        options = Options()
        options.headless = True
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        districts = [j.text for j in driver.find_elements(By.XPATH,
                                                          value='//*[@id="root"]/div/div/div[2]/div/div/div[1]/div[5]/div/div[2]/select/option')]
        with ThreadPoolExecutor(max_workers=6) as executor:
            executor.map(Scrape_Tamilnadu, [j for j in range(1, len(districts))])
        driver.quit()
    elif state == 'Telangana':
        # opening telangana website
        url = 'http://164.100.112.24/SpringMVC/Hospital_Beds_Statistic_Bulletin_citizen.htm'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        # getting hospital types
        lt = [i.text.strip() for i in
              driver.find_elements(By.XPATH, value='//table[@id="datatable-default1"]/tbody/tr/td[2]')]
        for i in lt:
            # opening the link for each hospital type
            driver.get(url)
            element = driver.find_element(By.LINK_TEXT, value=i)
            element.click()
            # getting all the data to be scraped
            data_to_be_scraped = driver.find_elements(By.XPATH, value='//*[@id="datatable-default1"]/tbody/tr')
            lt = [i.text.strip() for i in data_to_be_scraped]
            # function call
            Scrape_Telangana(lt, i)
        driver.quit()
    elif state == 'Tripura':
        Scrape_Tripura()
    elif state == 'Uttar Pradesh':
        url = 'https://beds.dgmhup-covid19.in/EN/covid19bedtrack'
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(url)
        Districts = [i.text for i in
                     driver.find_elements(By.XPATH, value='//*[@id="MainContent_EN_ddDistrict"]/option')]
        if 'Please Select' in Districts:
            Districts.remove('Please Select')
        with ThreadPoolExecutor(max_workers=7) as executor:
            executor.map(Scrape_UttarPradesh, Districts)
        driver.quit()
    elif state == 'Uttarkhand':
        Scrape_Uttarakhand()


for state in States:
    Scraping(state)
