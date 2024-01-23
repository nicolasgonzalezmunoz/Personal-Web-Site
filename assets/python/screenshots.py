import os
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By

urls = [
    # Current projects
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/underfitting-overfitting-and-regularization",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/ml-the-statistician-way-basics/notebook",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/cross-validation-dataset-split-strategies",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/all-you-want-to-know-about-linear-regression",
    "https://www.kaggle.com/datasets/nicolasgonzalezmunoz/earthquakes-on-chile",
    "https://www.kaggle.com/datasets/nicolasgonzalezmunoz/world-bank-world-development-indicators"
]
screenshot_names = [
    # Current projects
    "overfitting-project.png",
    "statistics-project.png",
    "split-project.png",
    "linear-project.png",
    "overfitting-project.png",
    "world-bank-dataset.png"
]
n_projects = len(urls)

path = os.path.join('..', 'imgs')

# Set browser options
opts = FirefoxOptions()
opts.add_argument("--headless")

for i in range(n_projects):
    filepath = os.path.join(path, screenshot_names[i])
    # Open browser
    driver = webdriver.Firefox(options=opts)

    # Navigate to site
    driver.get(urls[i])

    # Click on accept cookies
    driver.find_element(
        By.XPATH,
        "//div[contains(text(), 'Ok, Got it.')]"
    ).click()

    # Get content and take screenshot
    element = driver.find_element(
        By.ID,
        'site-content'
    )
    element.screenshot(filepath)

    # Exit browser
    driver.quit()
