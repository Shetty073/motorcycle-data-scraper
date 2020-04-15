import requests, json
from bs4 import BeautifulSoup as bs


BASE_URL = "https://www.bikedekho.com"
ALL_BRAND_BIKE_PAGES = {}


def get_soup(url):
    res = requests.get(url)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
    soup = bs(res.content, "html.parser")
    return soup


def parse_bike_url(url):
    soup = get_soup(url)
    bike_brand = url[26:]
    bike_list_ul = soup.find("ul", class_="bikelist")
    bike_list_li = bike_list_ul.find_all("h3")
    bike_urls = []
    for element in bike_list_li:
        link = element.find("a")
        bike_urls.append(BASE_URL + link["href"] + "/specifications")
    ALL_BRAND_BIKE_PAGES[bike_brand] = bike_urls


def brand_links_parser(urls):
    total_brands = len(urls)
    n = 1
    for url in urls:
        print(f"Parsing brand {n} of {total_brands}")
        parse_bike_url(url)
        n += 1
    print("All brands parsed successfully")
    print("Converting python dict to json format for storage")
    all_brand_bike_pages_json = json.dumps(ALL_BRAND_BIKE_PAGES)
    print("Dumping final json data into 'brand_links.json'")
    with open("brand_links.json", "w") as json_file:
        json_file.write(all_brand_bike_pages_json)


def save_brand_links(url):
    soup = get_soup(url)
    brands_div = soup.find("div", id="all_brands")
    brands_ul = brands_div.contents[1]
    brand_links = brands_ul.find_all("a")
    urls = []
    for link in brand_links:
        urls.append(BASE_URL + link["href"])
    brand_links_parser(urls)
    # Get brand logos
    url = "https://bd.gaadicdn.com/pwa/img/"
    dct = {}
    img_dct = {}
    with open("brand_links.json", "r") as json_file:
        dct = json.loads(json_file.read())
    for k in dct.keys():
        img_dct[k] = f"{url}{k[:-6]}.png"


    with open("brand_logos.json", "w") as json_file:
        json_file.write(json.dumps(img_dct))
    


def start_main_scraper():
    url = "https://www.bikedekho.com/new-bikes"
    save_brand_links(url)

