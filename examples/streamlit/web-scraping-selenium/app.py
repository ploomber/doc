import streamlit as st
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_table():
    url = "https://en.wikipedia.org/wiki/Mercury_Prize"
    xpath = "//table[contains(@class, 'wikitable')]"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # we need this since we'll run the container as root
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # wait for the table to load
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    )

    element_html = element.get_attribute("outerHTML")

    # remove links
    soup = BeautifulSoup(element_html, "html.parser")

    for a in soup.find_all("a"):
        a.replace_with(a.text)

    # return the cleaned html
    return str(soup)


st.title("Mercury Prize Winners")


if st.button("Load from Wikipedia"):
    content = get_table()
    st.html(content)
