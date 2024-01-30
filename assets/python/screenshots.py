import os
import asyncio
from PIL import Image
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By


async def take_kaggle_screenshot(
    url: str, filepath: os.PathLike, opts: FirefoxOptions, *,
    size: tuple[int, int] = (600, 400)
    ) -> None:

    # Initialize navigator
    driver = webdriver.Firefox(options=opts)

    # Navigate to URL
    driver.get(url)

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

    # Open image with PIL and save as thumbnail
    with Image.open(filepath) as im:
        im.thumbnail(size)
        im.save(filepath, "PNG")


async def take_kaggle_screenshots(
    urls: list[str], filenames: list[str]
        ) -> None:
    n_projects: int = len(urls)
    basepath: os.PathLike = os.path.join('..', 'imgs')

    # Create set to save concurrent tasks
    bg_tasks = set()

    # Set browser options
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    for i in range(n_projects):
        filepath = os.path.join(basepath, filenames[i])
        task = asyncio.create_task(
            take_kaggle_screenshot(urls[i], filepath, opts)
        )
        bg_tasks.add(task)
        task.add_done_callback(bg_tasks.discard)
    

urls = [
    # Current projects
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/interactive-visualizations-plotly-datashader",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/underfitting-overfitting-and-regularization",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/ml-the-statistician-way-basics/notebook",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/cross-validation-dataset-split-strategies",
    "https://www.kaggle.com/code/nicolasgonzalezmunoz/all-you-want-to-know-about-linear-regression",
    "https://www.kaggle.com/datasets/nicolasgonzalezmunoz/earthquakes-on-chile",
    "https://www.kaggle.com/datasets/nicolasgonzalezmunoz/world-bank-world-development-indicators"
]

filenames = [
    # Current projects
    "interactive-viz-project.png",
    "overfitting-project.png",
    "statistics-project.png",
    "split-project.png",
    "linear-project.png",
    "overfitting-project.png",
    "world-bank-dataset.png"
]

asyncio.run(take_kaggle_screenshots(urls, filenames))
