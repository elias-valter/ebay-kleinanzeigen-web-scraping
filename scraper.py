import requests, csv, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


# header to avoid beeing blocked by ebay kleinanzeigen
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
}
query = input("please enter the product you want to search << ")
URL = "https://www.kleinanzeigen.de/s-" + query + "/k0"
page = requests.get(url=URL, headers=header)
list_for_csv = []
csv_header = ["title", "price", "is negotiable", "number of images", "zip code", "location", "date listed"]


# takes list with values from listed products and writes to a new csv
def write_to_csv(data_list):
    csv_file_path = "new_output.csv"
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        writer.writerows(data_list[0:])
    print(f"CSV file '{csv_file_path}' has been created.") 


# split adress to zip code and location
def get_zip_code_location(address) -> list:
    zip_code = address[:5]
    location = address[6:].strip()
    return [zip_code, location]
    

# returns the date the product was listed (dd.mm.yyyy format)
def get_date(date: str) -> str:
    pattern = r'^\d{2}.\d{2}.\d{4}$'
    current_date = datetime.now()
    yesterday_date = current_date - timedelta(days=1)

    if re.match(pattern, date):
        return date    
    elif "Heute" in date:
        return current_date.strftime("%d.%m.%Y")
    else:
        return yesterday_date.strftime("%d.%m.%Y")


# perfom the scraping and write to csv
def perform_scraping(query): 
    soup = BeautifulSoup(page.content, "html.parser")

    # List with listed products shown as the search result
    results = soup.find_all(class_="aditem")

    # extract data from each product listed and wirte to csv file
    for rslt in results:
        itemsoup = BeautifulSoup(str(rslt), "html.parser")
        
        title_text = itemsoup.find('a', class_='ellipsis').text.strip()
        
        price_original = itemsoup.find("p", class_="aditem-main--middle--price-shipping--price").text.strip() 
        isVB = "VB" in price_original
        price = price_original.replace(".", "").split()[0]

        place = get_zip_code_location(itemsoup.find(class_="aditem-main--top--left").text.strip())
        
        zip_code = place[0]
        
        location = place[1]
        
        date = get_date(itemsoup.find(class_="aditem-main--top--right").text.strip())
        
        try:
            numberOfImages = int(itemsoup.find(class_="galleryimage--counter").text.strip())
        except:
            numberOfImages = 0
        
        ls = [title_text, price, isVB, numberOfImages, zip_code, location, date]
        list_for_csv.append(ls)

    write_to_csv(list_for_csv)
    #return {"result": "Scraping completed successfully!"}

if __name__ == "__main__":
    perform_scraping(query)