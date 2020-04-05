from main_scraper import start_main_scraper, get_soup
import requests, json
from bs4 import BeautifulSoup as bs
import os


ALL_DATA_DICT = {}


def save_final_data_to_json():
    # Clean the data before saving
    print("Cleaning data before saving")
    keys_for_deletion = []
    for brand, data in ALL_DATA_DICT.items():
        if not data:
            keys_for_deletion.append(brand)
    print("Removing entries with empty dictionary values")
    for key in keys_for_deletion:
        del ALL_DATA_DICT[key]
    
    # Saving data
    print("Preparing for final save..")
    print("Converting dictionary to JSON..")
    all_data_json = json.dumps(ALL_DATA_DICT)
    print("Saving final data into 'all_bikes_data.json'")
    with open("all_bikes_data.json", "w") as json_file:
        json_file.write(all_data_json)
    print("**** COMPLETE ****")


def parse_spec_page(brand_name, spec_page_url):
    soup = get_soup(spec_page_url)
    # Get bike picture
    image_div = soup.find("div", class_="imgleft")
    image = image_div.find("a", href=f"{spec_page_url[25:][:-15]}")
    image_tag = image.find("img")
    bike_picture = image_tag["src"] # bike_picture

    # Get bike name
    bike_model_name = image_tag["alt"]
    bike_model_name = bike_model_name.replace("(", "aka ")
    bike_model_name = bike_model_name.replace(")", "") # bike_model_name

    # Get the price range
    price_div = soup.find("div", class_="price")
    price_inside_div = price_div.find("span")
    price_span = price_inside_div.find("span")
    bike_price = price_span.get_text() # bike_price

    # Get technical specs
    ALL_DATA_DICT[brand_name][bike_model_name] = {}
    tech_spec_div = soup.find("div", id="technicalSpecsTop")
    spec_tables = tech_spec_div.find_all("table")
    for table in spec_tables:
        table_rows = table.find_all("tr")
        for data in table_rows:
            # Clean data
            key = data.find("td").get_text().lower()
            key = key.replace(" ", "_")
            key = key.replace("(", "")
            key = key.replace(")", "")
            key = key.replace(".", "")
            if key == "mileage_":
                key = "mileage"
            if key == "range":
                key = "range_km"
            value = data.find("td", class_="right").get_text()
            value = value.replace("(", "")
            value = value.replace(")", "")
            # Add data to dict
            ALL_DATA_DICT[brand_name][bike_model_name][key] = value
    # Store all remaining info into ALL_DATA_DICT
    ALL_DATA_DICT[brand_name][bike_model_name]["bike_picture"] = bike_picture
    ALL_DATA_DICT[brand_name][bike_model_name]["bike_price"] = bike_price


def parse_spec_links(brand_name, brand_links_list):
    print(f"\tGetting data for {brand_name}")
    ALL_DATA_DICT[brand_name] = {}
    total_models = len(brand_links_list)
    n = 1
    for spec_page_url in brand_links_list:
        print(f"\t\tParsing model {n} of {total_models}")
        parse_spec_page(brand_name, spec_page_url)
        n += 1


def start():
    # First check if file is empty
    with open("brand_links.json", "r") as json_file:
        one_char = json_file.read(1)
        if not one_char:
            print("'brand_links.json' is empty..")
            print("Starting main scraper..")
            start_main_scraper()
    # Continue with spec_parser code
    with open("brand_links.json", "r") as json_file:
        print("Loading data from 'brand_links.json' to a dictionary")
        all_brand_bike_pages_json = json_file.read()
    all_brand_bike_pages_dict = json.loads(all_brand_bike_pages_json)
    total_brands = len(all_brand_bike_pages_dict)
    n = 1
    for brand_name, brand_links_list in all_brand_bike_pages_dict.items():
        print(f"Parsnig spec links for brand {n} of {total_brands}")
        parse_spec_links(brand_name.replace("-", "_"), brand_links_list)
        n += 1
    print("Finished parsing spec links for all brands")
    save_final_data_to_json()


start()
