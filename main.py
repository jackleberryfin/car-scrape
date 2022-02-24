# coding=utf-8
import codecs
import os

import pandas as pd

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from car import Car
from time import sleep
import csv


key_details_kms = 0
key_details_body_style = 1
key_details_transmission = 2
key_details_engine = 3

car_db = []
browser = None

# def get_page_info(url, desc, year, make, model, badge, series, price, kms, body, engine, trans):
#     # These need to be arrays
#     page_info = pd.DataFrame({
#         'Make': make,
#         'Model': model,
#         'Badge': badge,
#         'Series': series,
#         'Price': price,
#         'Odometer': kms,
#         'Year': year,
#         'Body': body,
#         'Engine': engine,
#         'Trans': trans,
#         'Desc': desc,
#         'link': url})
#     print(page_info)

def wait_for_page_cmd(fun, argument, timeout, attempts):
    result = None
    for attempt in range(attempts):
        result = fun(argument)
        if (result):
            if len(result) > 0:
                return result
        print "Sleeping {0} for {1}s on {2}({3})".format(attempt, timeout, str(fun), argument)
        sleep(timeout)
        result = fun(argument)

def scrape_target_url(page):
    global browser
    listings = wait_for_page_cmd(browser.find_elements_by_class_name, 'listing-item', 1, 3)

    print "Scraping Page:{0}".format(page+1)
    for listing in listings:
        make = ''
        model = ''
        badge = ''
        series = ''
        price = ''
        kms = ''
        year = ''
        body = ''
        engine = ''
        trans = ''
        category = ''
        url = ''

        #print listing.text
        listing_attrs = browser.execute_script(
            'var items = {};\
             for (index = 0; index < arguments[0].attributes.length; ++index)\
              { \
                items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value \
              }; \
              return items;',
            listing)
        el_price = listing.find_element_by_class_name('price')
        el_list_key_details = listing.find_elements_by_class_name('key-details__value')
        # Price
        price = el_price.text.replace('$', '').replace(',', '').replace('*','')
        # Url
        url = el_price.find_element_by_css_selector('a').get_attribute('href')
        # Desc
        desc = listing.find_elements_by_class_name('card-body')[0].find_elements_by_class_name('col')[0].text
        split_desc = desc.split(' ')
        # Vehicle Category
        category = listing_attrs['data-webm-vehcategory']

        if len(split_desc) < 5:
            print "length of desc is odd: {0}".format(desc)
            print url
        else:
            # Year
            year = split_desc[0]
            # Make
            make = split_desc[1]
            # Model
            model = split_desc[2]
            # Badge
            badge = split_desc[3]
            # Series
            series = split_desc[4]

        if not len(el_list_key_details) == 4:
            engine_list = ['Petrol', 'Diesel', 'cyl']
            km_list = ['km']
            body_list = ['Sedan', 'Hatch','Bus','Cab','Convertible','Coupe','Truck','Mover','SUV','Ute','Van','Wagon']
            trans_list = ['Automatic','Manual']
            for key_detail in el_list_key_details:
                if any(word in str(key_detail.text) for word in engine_list):
                    engine = key_detail.text
                elif any(word in str(key_detail.text) for word in body_list):
                    body = key_detail.text
                elif any(word in str(key_detail.text) for word in trans_list):
                    trans = key_detail.text
                elif any(word in str(key_detail.text) for word in km_list):
                    kms = key_detail.text
        else:
            # Kms
            kms = el_list_key_details[key_details_kms].text.replace('km', '').replace(',', '').replace(' ', '')
            # Body
            body = el_list_key_details[key_details_body_style].text
            # Engine
            engine = el_list_key_details[key_details_engine].text
            # Trans
            trans = el_list_key_details[key_details_transmission].text


        if category == 'dealer' and kms == '':
            kms = '0'
        car_db.append(Car(make, model, badge, series, price, kms, year, body, engine, trans, desc, category, url))

    # else:
    #     print "Some other web elements were found check page source!"
    #     for listing in listings:
    #         print str(listing)

    pagination = wait_for_page_cmd(browser.find_elements_by_class_name, 'pagination', 1, 3)
    # pagination_pages = wait_for_page_cmd(pagination[0].find_elements_by_class_name, 'page-item', 1, 3)

    # If single page of listings then pagination will not exist
    try:
        next = pagination[0].find_element_by_css_selector('a.page-link.next')
        attrs = browser.execute_script(
            'var items = {};\
             for (index = 0; index < arguments[0].attributes.length; ++index)\
              { \
                items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value \
              }; \
              return items;',
            next)
    except Exception:
        return

    if not attrs['class'] == 'page-link next disabled':
        #print "Clicking Next"
        next.click()
        #sleep(3)
        scrape_target_url(page+1)
    else:
        return


#for car in car_db:
    #attrs = vars(car)
    # now dump this in some way or another
    #print(', '.join("%s: %s" % item for item in attrs.items()))


if __name__ == '__main__':

    PROG_STATE = 'scrape' # scrape / calculate

    CONDITION='used' # used / new
    CATEGORY='' # private / dealer
    MAKE='holden' # mazda / nissan / toyota
    MODEL='commodore' # 3 / silvia / supra
    BADGE=''
    SERIES=''
    STATE='' # queensland-state / victoria-state
    REGION='' # brisbane-region / melbourne-region
    TRANSMISSION='' # manual-transmission / automatic-transmission

    if PROG_STATE == 'scrape':
        START_URL='https://www.carsales.com.au/cars/{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}/'.format(CONDITION, CATEGORY, MAKE, MODEL, BADGE, SERIES, STATE, REGION, TRANSMISSION)

        print "Scraping Target URL: {0}".format(START_URL)
        opts = Options()
        opts.headless = True
        assert opts.headless  # Operating in headless mode
        browser = Firefox(options=opts)
        print "Starting Firefox..."
        browser.get(START_URL)
        title = browser.find_element_by_css_selector('h1.title')
        print title.text

        scrape_target_url(0)
        browser.quit()

        print "Writing CSV"
        with open('db_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}.csv'.format(CONDITION, CATEGORY, MAKE, MODEL, BADGE, SERIES, STATE, REGION, TRANSMISSION), 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Make', 'Model', 'Badge', 'Series', 'Kms', 'Price', 'Year', 'Body', 'Engine', 'Trans', 'Category', 'Url'])
            for car in car_db:
                writer.writerow([car.Make, car.Model, car.Badge, car.Series, car.Kms, car.Price, car.Year, car.Body, car.Engine, car.Trans, car.Category, car.Url])


    if PROG_STATE == 'scrape' or PROG_STATE == 'calculate':
        print "--- Calculating Top 10 Deals! ---"
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.colheader_justify', 'center')
        pd.set_option('display.precision', 3)
        pd.set_option('display.max_colwidth', 350)

        #pd.set_option('display.width', 320)


        #pd.set_option('display.max_columns', 10)
        df = pd.read_csv('db_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}.csv'.format(CONDITION, CATEGORY, MAKE, MODEL, BADGE, SERIES, STATE, REGION, TRANSMISSION))
                   # Price , Kms, Year
        jacks_move = [3.2, 1.8, 1]
        best_value = [7, 3, 1]
        newer_car = [2.5, 1, 2]

        price_only = [100, 1, 1]
        kms_only = [1, 100, 1]
        year_only = [1, 1, 100]

        scalars = jacks_move

        #df = df[df.Trans == 'Automatic']


        #df = df[df.Kms < 200000]
        #df = df[df.Year > 2015]

        df['Price_pct'] = df.Price.rank(pct = True).multiply(scalars[0])
        df['Kms_pct'] = df.Kms.rank(pct = True).multiply(scalars[1])
        df['Year_pct'] = (1-df.Year.rank(pct = True)).multiply(scalars[2])
        df['Overall_pct'] = df[['Price_pct', 'Kms_pct', 'Year_pct']].mean(axis=1)
        df.sort_values(by=['Overall_pct'], inplace=True, ascending=True)

        top_15 = df.head(15)
        print(top_15[['Make', 'Model', 'Badge', 'Series', 'Kms', 'Price', 'Year', 'Body', 'Engine', 'Trans', 'Category', 'Url']])

        with open('Top_15_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}.text'.format(CONDITION, CATEGORY, MAKE, MODEL, BADGE, SERIES, STATE, REGION, TRANSMISSION), 'w') as f:
            dfAsString = top_15.to_string(header=False, index=False)
            f.write(dfAsString)

        top_15.to_csv('Top_15_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}.csv'.format(CONDITION, CATEGORY, MAKE, MODEL, BADGE, SERIES, STATE, REGION, TRANSMISSION), header=None, index=None, sep=' ', mode='w')


