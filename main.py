from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from dotenv import load_dotenv
import pandas as pd
import time
import glob
import os
import shutil

load_dotenv()

wp_email = os.getenv('wp_email')
wp_password = os.getenv('wp_password')

rc_email = os.getenv('rc_email')
rc_password = os.getenv('rc_password')

# check if there are files in the project files, if True delete them
def delete_old_els_files():
    is_existing = os.path.exists("./Export Files/ELS")
    if is_existing:
        files = glob.glob('./Export Files/ELS/*')
        for file in files:
            os.remove(file)


def delete_old_rc_files():
    is_existing = os.path.exists('./Export Files/Royal')
    if is_existing:
        files = glob.glob('./Export Files/Royal/*')
        for file in files:
            os.remove(file)


delete_old_els_files()
delete_old_rc_files()

print('deleted old files')

options = Options()
#options.add_argument('--headless')
# firefox_driver_path = '/usr/local/bin/geckodriver'
# driver_service = webdriver.FirefoxService(executable_path=firefox_driver_path)
# els_driver = webdriver.Firefox(options=options, service=driver_service)
els_driver = webdriver.Firefox(options=options)


# DOWNLOAD ELS CSV FILE
def download_els_export_file(driver):
    driver.get("https://electronicshop.ro/wp-admin")
    email_element = driver.find_element(By.ID, "user_login")
    pass_element = driver.find_element(By.ID, "user_pass")
    auth_btn_element = driver.find_element(By.ID, "wp-submit")

    email_element.send_keys(wp_email)
    pass_element.send_keys(wp_password)
    auth_btn_element.click()
    driver.implicitly_wait(5)

    produsebtn_element = driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/div[2]/ul/li[12]/a/div[3]")
    produsebtn_element.click()

    driver.implicitly_wait(5)
    # produseexport_btn = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[3]/div[1]/div[6]/a[3]")
    produseexport_btn = driver.find_element(By.CSS_SELECTOR, "a.page-title-action:nth-child(4)")
    produseexport_btn.click()

    driver.implicitly_wait(5)
    export_submit_btn = driver.find_element(By.CSS_SELECTOR, ".woocommerce-exporter-button")
    export_submit_btn.click()
    time.sleep(30)
    driver.quit()

    print('downloaded els file')


download_els_export_file(driver=els_driver)


# MOVE ELS EXPORT FILE TO PROJECT FOLDER, AND RETURN ITS LOCATION FOR LATER USE WITH PANDAS
def move_els_export_file():
    list_of_files = glob.glob('/home/manushamanu/Downloads/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    shutil.move(latest_file, './Export Files/ELS')

    export_file = glob.glob('./Export Files/ELS/*')
    latest_els_export_file = max(export_file, key=os.path.getctime)
    return latest_els_export_file


els_file = move_els_export_file()

# DOWNLOAD ROYAL CSV FILE
rc_driver = webdriver.Firefox(options=options)


def download_rc_export_file(driver):
    # unblock downloads
    driver.get('about:config')
    driver.implicitly_wait(5)
    agree_btn_element = driver.find_element(By.ID, 'warningButton').click()
    search_box = driver.find_element(By.ID, 'about-config-search').send_keys('dom.block_download_insecure')
    driver.implicitly_wait(5)
    toggle_btn = driver.find_element(By.CSS_SELECTOR, '.button-toggle')
    toggle_btn.click()

    driver.get("https://r-c.ro")

    # login phase
    b2b_btn = driver.find_element(By.CSS_SELECTOR, ".level1 > li:nth-child(3) > a:nth-child(1)")
    b2b_btn.click()
    driver.implicitly_wait(10)
    email_element = driver.find_element(By.ID, "user_login")
    pass_element = driver.find_element(By.ID, "user_pass")
    email_element.send_keys(rc_email)
    pass_element.send_keys(rc_password)
    submit_btn = driver.find_element(By.ID, "wp-submit")
    submit_btn.click()
    driver.implicitly_wait(10)

    # download file phase
    my_acc_element = driver.find_element(By.CSS_SELECTOR, ".level1 > li:nth-child(3) > a:nth-child(1)")
    my_acc_element.click()
    driver.implicitly_wait(10)

    # close_promobtn = driver.find_element(By.CSS_SELECTOR, ".daily-promo > button:nth-child(2) > i:nth-child(1)")
    # close_promobtn.click()
    # driver.implicitly_wait(10)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.implicitly_wait(2)
    csv_element = driver.find_element(By.CSS_SELECTOR,
                                      'div.col-md-12:nth-child(5) > div:nth-child(1) > span:nth-child(2) > a:nth-child(3)')
    csv_element.click()

    time.sleep(30)
    driver.quit()

    print('downloaded rc file')


download_rc_export_file(rc_driver)


# MOVE ROYAL EXPORT FILE TO PROJECT FOLDER, AND RETURN ITS LOCATION FOR LATER USE WITH PANDAS
def move_royal_export_file():
    list_of_files = glob.glob('/home/manushamanu/Downloads/*')
    latest_file = max(list_of_files, key=os.path.getctime)
    shutil.move(latest_file, './Export Files/Royal')

    export_file = glob.glob('./Export Files/Royal/*')
    latest_rc_export_file = max(export_file, key=os.path.getctime)
    return latest_rc_export_file


rc_file = move_royal_export_file()

# SKU CHECKING SECTION!!!!!!!
pd.set_option('display.max_columns', None)
pd.set_option("display.max_rows", None)

els_df = pd.read_csv(f'{els_file}')

rc_df = pd.read_csv(f'{rc_file}')

f = open('./Logs/found.txt', 'w')
n = open('./Logs/not-found.txt', 'w')

# GOOD CODE, DO NOT DELETE THIS PORTION!!!!!!
for i in range(len(els_df["SKU"]) - 1):
    if els_df['Tip'][i] == 'variable':
        continue
    elif els_df['Tip'][i] == 'variation':
        continue
    elif els_df['Stoc'][i] > 0:
        continue
    else:
        for j in range(len(rc_df['Cod']) - 1):
            if els_df['SKU'][i] == rc_df["Cod"][j]:
                f.write(f'{els_df["SKU"][i]} Found ' + str(j) + '\n')
                if rc_df['Stoc'][j] == '>50' or int(rc_df["Stoc"][j]) > 0:
                    els_df.loc[i, 'În stoc?'] = 1
                    if 0 < rc_df['Pret'][j] <= 50:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.5, 2)
                    elif rc_df['Pret'][j] <= 100:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.2, 2)
                    elif rc_df['Pret'][j] <= 500:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.15, 2)
                    elif rc_df['Pret'][j] <= 1000:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.125, 2)
                    elif rc_df['Pret'][j] <= 1500:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.1, 2)
                    elif rc_df['Pret'][j] <= 2000:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.075, 2)
                    elif rc_df['Pret'][j] <= 2500:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.05, 2)
                    elif rc_df['Pret'][j] <= 3000:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.025, 2)
                    elif rc_df['Pret'][j] <= 5000:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.02, 2)
                    else:
                        els_df.loc[i, 'Preț obișnuit'] = round(rc_df['Pret'][j] * 1.015, 2)
                else:
                    els_df.loc[i, 'În stoc?'] = 0

# REPLACE . WITH , TO PREVENT IMPORT ERROR INTO WP
for i in range(len(els_df["Preț obișnuit"]) - 1):
    cod_produs = str(els_df["Preț obișnuit"][i])
    if '.' in cod_produs:
        els_df.loc[i, 'Preț obișnuit'] = cod_produs.replace('.', ',')
    else:
        pass

f.close()

for i in range(len(els_df["SKU"])):
    if els_df['SKU'][i] not in rc_df['Cod'].values:
        n.write(f'{els_df["SKU"][i]}' + '\n')

els_df.to_csv('./Import Files/els_out.csv', index=False)
n.close()
