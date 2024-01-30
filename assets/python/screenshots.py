"""
Automates the process of taking screenshots from projects.

Each screenshot task is run asynchronously to reduce I/O overhead.
"""
import os
import time
import asyncio
from typing import Optional
from PIL import Image
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_kaggle_code_urls(opts: FirefoxOptions) -> list[str]:
    """
    Get the URLs from code projects from Kaggle.

    Parameters
    ----------
    opts: selenium.webdriver.FirefoxOptions
        Options to be passed to a Firefox web driver.

    Return
    ------
    urls: list[str]
        A list with all the urls found.
    """
    base_url = 'https://www.kaggle.com/nicolasgonzalezmunoz/code'
    classes = '.sc-dsAqUS.cxEwNC.sc-hECAZF.cVHAgC'
    works_window_classes = '.km-list.km-list--avatar-list.km-list--three-line'
    url_check = 'https://www.kaggle.com/code/nicolasgonzalezmunoz'

    driver = webdriver.Firefox(options=opts)
    driver.get(base_url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, f'ul{works_window_classes}')
        )
    )
    # Click on accept cookies
    driver.find_element(
        By.XPATH,
        "//div[contains(text(), 'Ok, Got it.')]"
    ).click()

    works_window = driver.find_element(
        By.CSS_SELECTOR, f'ul{works_window_classes}'
    )
    driver.execute_script("arguments[0].scrollIntoView();", works_window)
    time.sleep(5)
    elements = driver.find_elements(By.CSS_SELECTOR, f"a{classes}")
    urls = []
    # Setup wait for later
    wait = WebDriverWait(driver, 10)

    # Store the ID of the original window
    original_window = driver.current_window_handle
    project_counter = 0
    exit_condition = False

    # Kaggle loads projects 20 by 20, so we have to wait content to load for
    # each 20 projects we scrap
    while not exit_condition:
        n_projects = len(elements)

        # On each loop, omit the projects previously found
        for i in range(project_counter, n_projects):
            element = elements[i]
            if not element.is_displayed():
                driver.execute_script(
                    "arguments[0].scrollIntoView(false);", element
                )

            # Access the project by clicking on element
            element.click()

            # Wait for the new tab to open
            wait.until(EC.number_of_windows_to_be(2))

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)
                    break

            # Wait for the new tab to load
            wait.until(EC.title_is(driver.title))

            href = driver.current_url
            urls.append(href)
            if href is not None:
                if href.startswith(url_check):
                    urls.append(href)

            # Close project tab and come back to Kaggle projects
            driver.close()
            driver.switch_to.window(original_window)

        if n_projects % 20 != 0:
            exit_condition = True
        else:
            project_counter += 20

            # Wait and see if there's more elements to scrap
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(5)
            elements = driver.find_elements(By.CSS_SELECTOR, f"a{classes}")

    driver.quit()
    return urls


def get_kaggle_dataset_urls(opts: FirefoxOptions) -> list[str]:
    """
    Get the URLs from dataset projects from Kaggle.

    Parameters
    ----------
    opts: selenium.webdriver.FirefoxOptions
        Options to be passed to a Firefox web driver.

    Return
    ------
    urls: list[str]
        A list with all the urls found.
    """
    base_url = 'https://www.kaggle.com/nicolasgonzalezmunoz/datasets'
    classes = '.sc-dsAqUS.cxEwNC'
    url_check = 'https://www.kaggle.com/datasets/nicolasgonzalezmunoz/'
    urls = []

    driver = webdriver.Firefox(options=opts)
    driver.get(base_url)

    # Wait content to load
    jobs = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, f"a{classes}")
        )
    )

    for job in jobs:
        href = job.get_attribute('href')

        # Check if url is valid
        if href is not None:
            if href.startswith(url_check):
                urls.append(href)
    driver.quit()
    return urls


def get_kaggle_urls(opts: FirefoxOptions) -> list[str]:
    """
    Get the URLs from both, code and dataset projects from Kaggle.

    Parameters
    ----------
    opts: selenium.webdriver.FirefoxOptions
        Options to be passed to a Firefox web driver.

    Return
    ------
    urls: list[str]
        A list with all the urls found.
    """
    urls = get_kaggle_code_urls(opts) + get_kaggle_dataset_urls(opts)
    return urls


def get_freecodecamp_urls(opts: FirefoxOptions) -> list[str]:
    """
    Get the URLs corresponding to FreeCodeCamp certifications.

    Parameters
    ----------
    opts: selenium.webdriver.FirefoxOptions
        Options to be passed to a Firefox web driver.

    Return
    ------
    urls: list[str]
        A list with all the urls found.
    """
    base_url = 'https://www.freecodecamp.org/nicolas-gonzalezmu'
    urls = []

    driver = webdriver.Firefox(options=opts)
    driver.get(base_url)
    jobs = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a[data-cy=claimed-certification]")
        )
    )
    for job in jobs:
        urls.append(job.get_attribute('href'))
    return urls


def get_github_urls(opts: FirefoxOptions) -> list[str]:
    """
    Get the URLs corresponding to GitHub repositories.

    Parameters
    ----------
    opts: selenium.webdriver.FirefoxOptions
        Options to be passed to a Firefox web driver.

    Return
    ------
    urls: list[str]
        A list with all the urls found.
    """
    base_url = 'https://github.com/nicolasgonzalezmunoz?tab=repositories'
    urls = []
    driver = webdriver.Firefox(options=opts)
    driver.get(base_url)
    elements = driver.find_elements(
        By.CSS_SELECTOR, "a[itemprop='name codeRepository']"
    )
    for element in elements:
        urls.append(element.get_attribute('href'))
    return urls


def get_filename_from_url(url: str, ext: str = 'png'):
    """
    Infer a file name from a URL.

    Parameters
    ----------
    url: str
        The URL where the files comes from.
    ext: str, default='png'
        Extension of the file.

    Return
    ------
    filename: str
        The file name with format project_code-source-type.ext.
    """
    split_url = url.split('/')
    url_source = split_url[2].split('.')[-2]
    url_type = split_url[3]
    code = split_url[-1]
    if url_type.startswith('certificat'):
        url_type = 'cert'
    elif url_type.startswith('dataset'):
        url_type = 'dataset'
    elif url_type == 'code' or 'repositories' in url_type:
        url_type = 'code'
    filename = f'{code}-{url_source}-{url_type}.{ext}'
    return filename


def optimize_image(
    filepath: os.PathLike, size: tuple[int, int] = (600, 400)
) -> None:
    """Optimize image on filepath using size as max thumbnail size."""
    with Image.open(filepath) as im:
        im.thumbnail(size)
        im.save(filepath, "PNG")


async def take_kaggle_screenshot(
    url: str, *, base_path: os.PathLike = os.path.join('..', 'imgs'),
    opts: Optional[FirefoxOptions] = None,
    driver: Optional[webdriver.Firefox] = None,
    size: tuple[int, int] = (600, 400), ext: str = 'png'
) -> None:
    """
    Take screenshot from a Kaggle project on the given url.

    The screenshot is optimized to have a smaller size and is converted into a
    thumbnail.

    Parameters
    ----------
    url: str
        The URL on which the project is stored.
    base_path: os.PathLike, default=os.path.join('..', 'imgs')
        The direction of the folder to save the thumbnail.
    opts: selenium.webdriver.FirefoxOptions, default=None
        The options to be passed to a selenium Firefox webdriver.
    driver: selenium.webdriver.Firefox, default=None
        A webdriver to use for navigation. If passed, opts is ignored.
    size: tuple[int, int], default=(600, 400)
        Tuple with the max dimensions of the thumbnail.
    ext: str
        File extension of the thumbnail when saved.

    Return
    ------
    None
    """
    # Get filepath of the file based on URL
    filepath = os.path.join(base_path, get_filename_from_url(url))

    # Set up webdriver for navigation
    if driver is None:
        if opts is None:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)

    # Navigate to URL
    driver.get(url)

    # Click on accept cookies
    driver.find_element(
        By.XPATH,
        "//div[contains(text(), 'Ok, Got it.')]"
    ).click()

    # Get content and take screenshot
    element = driver.find_element(By.ID, 'site-content')
    element.screenshot(filepath)

    # Exit browser
    driver.quit()

    # Open image with PIL and save as thumbnail
    optimize_image(filepath, size)


async def take_freecodecamp_screenshot(
    url: str, *, base_path: os.PathLike = os.path.join('..', 'imgs'),
    opts: Optional[FirefoxOptions] = None,
    driver: Optional[webdriver.Firefox] = None,
    size: tuple[int, int] = (600, 400), ext: str = 'png'
) -> None:
    """
    Take a screenshot from a FreeCodeCamp certification on the given URL.

    The screenshot is optimized to have a smaller size and is converted into a
    thumbnail.

    Parameters
    ----------
    url: str
        The URL on which the project is stored.
    base_path: os.PathLike, default=os.path.join('..', 'imgs')
        The direction of the folder to save the thumbnail.
    opts: selenium.webdriver.FirefoxOptions, default=None
        The options to be passed to a selenium Firefox webdriver.
    driver: selenium.webdriver.Firefox, default=None
        A webdriver to use for navigation. If passed, opts is ignored.
    size: tuple[int, int], default=(600, 400)
        Tuple with the max dimensions of the thumbnail.
    ext: str
        File extension of the thumbnail when saved.

    Return
    ------
    None
    """
    # Get filepath of the file based on URL
    filepath = os.path.join(base_path, get_filename_from_url(url))

    # Set up webdriver for navigation
    if driver is None:
        if opts is None:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)

    driver.get(url)
    element = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div[class=certificate-wrapper]")
        )
    )[0]
    element.screenshot(filepath)
    driver.quit()

    # Open image with PIL and save as thumbnail
    optimize_image(filepath, size)


async def take_desafio_latam_screenshot(
    code: str, *, base_path: os.PathLike = os.path.join('..', 'imgs'),
    opts: Optional[FirefoxOptions] = None,
    driver: Optional[webdriver.Firefox] = None,
    size: tuple[int, int] = (600, 400), ext: str = 'png'
) -> None:
    """
    Take a screenshot from a Desafío Latam certification for the given code.

    The screenshot is optimized to have a smaller size and is converted into a
    thumbnail.

    Parameters
    ----------
    code: str
        Identification code of the certificate.
    base_path: os.PathLike, default=os.path.join('..', 'imgs')
        The direction of the folder to save the thumbnail.
    opts: selenium.webdriver.FirefoxOptions, default=None
        The options to be passed to a selenium Firefox webdriver.
    driver: selenium.webdriver.Firefox, default=None
        A webdriver to use for navigation. If passed, opts is ignored.
    size: tuple[int, int], default=(600, 400)
        Tuple with the max dimensions of the thumbnail.
    ext: str
        File extension of the thumbnail when saved.

    Return
    ------
    None
    """
    # Set up URL and file name
    base_url = 'https://cursos.desafiolatam.com/certificates/'
    url = base_url + code
    filepath = os.path.join(base_path, get_filename_from_url(url))

    # Set up webdriver for navigation
    if driver is None:
        if opts is None:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)

    driver.get(url)
    element = driver.find_element(By.XPATH, "(//main/section/div/div/img)")
    element.screenshot(filepath)
    driver.quit()

    # Open image with PIL and save as thumbnail
    optimize_image(filepath, size)


async def take_github_screenshot(
    url: str, *, base_path: os.PathLike = os.path.join('..', 'imgs'),
    opts: Optional[FirefoxOptions] = None,
    driver: Optional[webdriver.Firefox] = None,
    size: tuple[int, int] = (600, 400), ext: str = 'png'
) -> None:
    """
    Take a screenshot of a GitHub repository on the given URL.

    The screenshot is optimized to have a smaller size and is converted into a
    thumbnail.

    Parameters
    ----------
    url: str
        The URL on which the project is stored.
    base_path: os.PathLike, default=os.path.join('..', 'imgs')
        The direction of the folder to save the thumbnail.
    opts: selenium.webdriver.FirefoxOptions, default=None
        The options to be passed to a selenium Firefox webdriver.
    driver: selenium.webdriver.Firefox, default=None
        A webdriver to use for navigation. If passed, opts is ignored.
    size: tuple[int, int], default=(600, 400)
        Tuple with the max dimensions of the thumbnail.
    ext: str
        File extension of the thumbnail when saved.

    Return
    ------
    None
    """
    # Get filepath of the file based on URL
    filepath = os.path.join(base_path, get_filename_from_url(url))

    # Set up webdriver for navigation
    if driver is None:
        if opts is None:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)

    driver.get(url)
    element = driver.find_element(
        By.CSS_SELECTOR,
        "div[class='clearfix container-xl px-md-4 px-lg-5 px-3']"
    )
    # Wait page to fully load
    time.sleep(2)

    element.screenshot(filepath)
    driver.quit()

    # Open image with PIL and save as thumbnail
    optimize_image(filepath, size)


async def take_screenshot(
    url: str, *, base_path: os.PathLike = os.path.join('..', 'imgs'),
    opts: Optional[FirefoxOptions] = None,
    driver: Optional[webdriver.Firefox] = None,
    size: tuple[int, int] = (600, 400), ext: str = 'png'
) -> None:
    """
    Take a screenshot of project/certification on the given URL.

    The function selects the function to use based on the passed URL.

    Parameters
    ----------
    url: str
        The URL on which the project is stored, or certification code.
    base_path: os.PathLike, default=os.path.join('..', 'imgs')
        The direction of the folder to save the thumbnail.
    opts: selenium.webdriver.FirefoxOptions, default=None
        The options to be passed to a selenium Firefox webdriver.
    driver: selenium.webdriver.Firefox, default=None
        A webdriver to use for navigation. If passed, opts is ignored.
    size: tuple[int, int], default=(600, 400)
        Tuple with the max dimensions of the thumbnail.
    ext: str
        File extension of the thumbnail when saved.

    Return
    ------
    None
    """
    if len(url.split('/')) < 2:
        take_desafio_latam_screenshot(
            url, base_path=base_path, opts=opts, driver=driver, size=size,
            ext=ext
        )
        return
    source = url.split('/')[2].split('.')[-2]
    if source == 'kaggle':
        take_kaggle_screenshot(
            url, base_path=base_path, opts=opts, driver=driver, size=size,
            ext=ext
        )
    elif source == 'freecodecamp':
        take_freecodecamp_screenshot(
            url, base_path=base_path, opts=opts, driver=driver, size=size,
            ext=ext
        )
    elif source == 'github':
        take_github_screenshot(
            url, base_path=base_path, opts=opts, driver=driver, size=size,
            ext=ext
        )
    else:
        raise ValueError(
            f"Functionality for source '{source}' not implemented."
        )


async def take_screenshots(
    *, base_path: os.PathLike = os.path.join('..', 'imgs'),
    opts: Optional[FirefoxOptions] = None,
    driver: Optional[webdriver.Firefox] = None,
    size: tuple[int, int] = (600, 400), ext: str = 'png'
) -> None:
    """
    Take a screenshot of projects and certificates from several sources.

    This function calls the take_[source]_screenshot functions to take the
    screenshot on the given source. Also automates getting the URLs and file
    names.

    Parameters
    ----------
    base_path: os.PathLike, default=os.path.join('..', 'imgs')
        Direction of the folder where the thumbnails will be saved.

    Return
    ------
    None
    """
    # Set up URLs
    kaggle_urls = get_kaggle_urls(opts)
    freecodecamp_urls = get_freecodecamp_urls(opts)
    github_urls = get_github_urls(opts)
    desafio_codes = ['mmthueoauo', 'n09qxomzta']

    urls = kaggle_urls + freecodecamp_urls + github_urls + desafio_codes

    # Create set to save concurrent tasks
    bg_tasks = set()

    for url in urls:
        task = asyncio.create_task(
            take_screenshot(
                url, base_path=base_path, opts=opts, driver=driver,
                size=size, ext=ext
            )
        )
        bg_tasks.add(task)
        task.add_done_callback(bg_tasks.discard)


try:
    loop = asyncio.get_running_loop()
except RuntimeError:  # 'RuntimeError: There is no current event loop...'
    loop = None

if loop and loop.is_running():
    tsk = loop.create_task(take_screenshots())
else:
    asyncio.run(take_screenshots())
