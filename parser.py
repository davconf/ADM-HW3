# parser.py
import os
import re
from bs4 import BeautifulSoup

def extract_restaurant_info(html_file):
    
    # Extracts infos from the HTML file of a restaurant

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

        # Initialize variables to store extracted information
        restaurant_name = ''
        address = ''
        city = ''
        postal_code = ''
        country = ''
        price_range = ''
        cuisine_type = ''
        description = ''
        phone_number = ''
        website = ''
        facilities_services = []
        credit_cards = []

        try:
            ###################################
            ##### Extract Restaurant Name #####
            ###################################

            restaurant_name = soup.find('h1', class_='data-sheet__title').text.strip()

            ##################################################################################
            ##### Extract Address, City, Postal Code, Country, Price Range, Cuisine Type #####
            ##################################################################################

            # get the first two occurences of this div class (first and second line of infos)
            infos = soup.find_all('div', class_='data-sheet__block--text', limit=2)

            # parse the first line of infos
            first_line_infos = infos[0].text.strip().split(",")
            # reverse the first_line_infos list
            first_line_infos.reverse()
            # assign the values
            country = first_line_infos[0].strip()
            postal_code = first_line_infos[1].strip()
            city = first_line_infos[2].strip()
            # address is composed by the last items of the list (and we have to reverse again to obtain the original ordering)
            address = ','.join(reversed(first_line_infos[3:]))

            # parse the second line of infos
            second_line_infos = infos[1].text.strip().split("\n")
            second_line_infos_cleanded = [item.strip() for item in second_line_infos if item.strip() and item.strip() != "·"]
            price_range = second_line_infos_cleanded[0].strip()
            cuisine_type = second_line_infos_cleanded[1].strip()

            ###############################
            ##### Extract Description #####
            ###############################

            description = soup.find('div', class_='data-sheet__description').text.strip()

            ################################
            ##### Extract Phone Number #####
            ################################

            # Find the <a> element with the href attribute that matches the pattern "tel:" followed by any characters
            phone_number_element = soup.find('a', href=re.compile(r"tel:.*"))
            if phone_number_element:
              #  Extract the phone number from the href attribute
              phone_number = phone_number_element['href'].replace("tel:", "").strip()

            ###############################
            ##### Extract Website URL #####
            ###############################

            # Find the <a> element that contains the restaurant's website link.
            # This element has the class "link js-dtm-link" and the attribute "data-event" set to "CTA_website".
            website_element = soup.find('a', class_='link js-dtm-link', attrs={'data-event': 'CTA_website'})

            if website_element:
              # ...extract the website URL from the "href" attribute of the element.
              website = website_element['href']

            ###########################################
            ##### Extract Facilities and Services #####
            ###########################################

            facilities_services_elements = soup.find('div', class_='restaurant-details__services').find_all('li')

            for element in facilities_services_elements:
              facilities_services.append(element.get_text(strip=True))

            #########################################
            ##### Extract Accepted Credit Cards #####
            #########################################

            credit_cards_elem = soup.find('div', class_='list--card').find_all('img')
            if credit_cards_elem:
              # Find all <img> tags within the <div class="list--card">.
              for img in soup.find('div', class_='list--card').find_all('img'):
                # Extract the card name from the data-src attribute, splitting by '/' and then by '-'.
                card_name = img['data-src'].split('/')[-1].split('-')[0]
                credit_cards.append(card_name)

        except Exception as e:
            print(f"Error parsing {html_file}: {e}")

        # Store the extracted information in a dictionary
        restaurant_info = {
            'restaurantName': restaurant_name,
            'address': address,
            'city': city,
            'postalCode': postal_code,
            'country': country,
            'priceRange': price_range,
            'cuisineType': cuisine_type,
            'description': description,
            'facilitiesServices': facilities_services,
            'creditCards': credit_cards,
            'phoneNumber': phone_number,
            'website': website
        }

        return restaurant_info