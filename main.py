from bs4 import BeautifulSoup
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import logging
import os
from datetime import datetime
import sys

# Set up artifact directories
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
artifact_dir = "./artifacts"
log_dir = os.path.join(artifact_dir, "logs")
html_dir = os.path.join(artifact_dir, "html")
html_full_dir = os.path.join(html_dir, "full_html")
html_filtered_dir = os.path.join(html_dir, "filtered_html")
csv_dir = os.path.join(artifact_dir, "csv")

# Create directories if they do not exist
os.makedirs(log_dir, exist_ok=True)
os.makedirs(html_full_dir, exist_ok=True)
os.makedirs(html_filtered_dir, exist_ok=True)
os.makedirs(csv_dir, exist_ok=True)

# Set up logging
log_file = os.path.join(log_dir, f"{timestamp}.log")
logging.basicConfig(
    filename=log_file,
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_command():
    # Log the full command used to run the script
    command = ' '.join(sys.argv)
    logging.info(f"Command used to run the script: {command}")

def expand_all_elements(driver):
    while True:
        elements_to_expand = driver.find_elements(By.XPATH, '//li[@aria-expanded="false"]//span[@class="tree-expander"]')
        if not elements_to_expand:
            break
        for element in elements_to_expand:
            try:
                driver.execute_script("arguments[0].click();", element)
                time.sleep(1)
            except Exception as e:
                logging.error(f"Error clicking element: {e}")
                continue

def save_filtered_html(soup, filter_by_id=None, filter_by_class=None, filter_element=None, custom_attribute=None, custom_attribute_value=None):
    filtered_html_content = None
    if filter_by_id:
        parent_element = soup.find(id=filter_by_id)
        if parent_element:
            html_file = os.path.join(html_filtered_dir, f"{timestamp}_filtered_content_{filter_by_id}.html")
            with open(html_file, "w", encoding="utf-8") as file:
                file.write(str(parent_element))
            filtered_html_content = parent_element
            logging.info(f"Filtered HTML content saved to '{html_file}'.")
        else:
            logging.warning(f"No element found with ID '{filter_by_id}'.")
    elif filter_by_class and filter_element:
        parent_elements = soup.find_all(filter_element, class_=filter_by_class)
        if parent_elements:
            for i, parent_element in enumerate(parent_elements):
                html_file = os.path.join(html_filtered_dir, f"{timestamp}_filtered_content_{filter_by_class}_{i+1}.html")
                with open(html_file, "w", encoding="utf-8") as file:
                    file.write(str(parent_element))
                if i == 0:  # Save the first match for further processing
                    filtered_html_content = parent_element
                logging.info(f"Filtered HTML content saved to '{html_file}'.")
        else:
            logging.warning(f"No elements found with class name '{filter_by_class}' and element '{filter_element}'.")
    elif custom_attribute and custom_attribute_value and filter_element:
        parent_elements = soup.find_all(filter_element, {custom_attribute: custom_attribute_value})
        if parent_elements:
            for i, parent_element in enumerate(parent_elements):
                html_file = os.path.join(html_filtered_dir, f"{timestamp}_filtered_content_{custom_attribute}_{custom_attribute_value}_{i+1}.html")
                with open(html_file, "w", encoding="utf-8") as file:
                    file.write(str(parent_element))
                if i == 0:  # Save the first match for further processing
                    filtered_html_content = parent_element
                logging.info(f"Filtered HTML content saved to '{html_file}'.")
        else:
            logging.warning(f"No elements found with custom attribute '{custom_attribute}' and value '{custom_attribute_value}'.")
    else:
        logging.error("Please provide either an ID, a class name and element type, or a custom attribute and value for filtering.")
    
    return filtered_html_content

def parse_html_and_generate_csv(soup, output_csv_file):
    with open(output_csv_file, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Title", "Href", "Breadcrumb"])

        # Find all anchor tags with href attribute
        for a_tag in soup.find_all('a', href=True):

            # Get the text of the anchor tag to be used as a title
            title = a_tag.text.strip()
            # Get the href of the achor tag
            href = a_tag['href']
            # Get the breadcrumb of the anchor tag
            breadcrumb_parts = []
            # Start from the current <a> tag
            current_element = a_tag
            
            # Logging: Starting processing of <a> tag
            logging.debug(f"Processing <a> tag with href: {href}")

            # Find the parent <li> or <ul> element and its text
            while current_element:
                parent = current_element.find_parent(['li', 'ul'])
                if parent and parent.name == 'li':
                    span_text = parent.find('span', recursive=False)
                    if span_text and span_text.text.strip():
                        breadcrumb_parts.insert(0, span_text.text.strip())
                        logging.debug(f"Added '{span_text.text.strip()}' to breadcrumb")
                current_element = parent
            
            breadcrumb = ' > '.join(breadcrumb_parts)
            writer.writerow([title, href, breadcrumb])
            logging.debug(f"Final breadcrumb for achor tag titled '{title}' with href '{href}': {breadcrumb}")

    logging.info(f"CSV file '{output_csv_file}' has been generated.")

def main(url, filter_by_id=None, filter_by_class=None, filter_element=None, custom_attribute=None, custom_attribute_value=None):
    driver = webdriver.Chrome()
    driver.get(url)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    except Exception as e:
        logging.error(f"Error waiting for page to load: {e}")
        driver.quit()
        exit()

    expand_all_elements(driver)
    time.sleep(5)  # Ensure all content is loaded
    full_html = driver.page_source

    # Save full HTML content
    full_html_file = os.path.join(html_full_dir, f"{timestamp}_fully_expanded_content.html")
    with open(full_html_file, "w", encoding="utf-8") as file:
        file.write(full_html)
    logging.info(f"Full page HTML content saved to '{full_html_file}'.")

    soup = BeautifulSoup(full_html, "html.parser")
    
    # Save filtered HTML based on user input
    filtered_html = save_filtered_html(soup, filter_by_id, filter_by_class, filter_element, custom_attribute, custom_attribute_value)

    # Check if filtered HTML is found and parse
    if filtered_html:
        logging.info("Parsing filtered HTML to CSV...")
        output_csv_file = os.path.join(csv_dir, f"{timestamp}_parsed_links_and_breadcrumbs.csv")
        parse_html_and_generate_csv(filtered_html, output_csv_file)
    else:
        logging.warning("Filtered HTML not found; skipping CSV generation.")

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Expand and filter HTML content from a webpage.")
    parser.add_argument("--url", type=str, required=True, help="The URL of the webpage to scrape.")
    parser.add_argument("--id", type=str, help="The ID of the parent element to filter.")
    parser.add_argument("--class-name", type=str, help="The class name of the parent element to filter.")
    parser.add_argument("--element", type=str, help="The HTML element type to filter (e.g., 'ul', 'div').")
    parser.add_argument("--custom-attribute", type=str, help="The custom attribute to filter by.")
    parser.add_argument("--custom-attribute-value", type=str, help="The value of the custom attribute to filter by.")

    args = parser.parse_args()

    # Improved validation logic
    if not args.id and not (args.class_name and args.element) and not (args.custom_attribute and args.custom_attribute_value):
        logging.error("Error: You must provide either an ID, a class name and element type, or a custom attribute and its value for filtering.")
        exit()

    # Log the command used to run the script
    log_command()

    main(args.url, filter_by_id=args.id, filter_by_class=args.class_name, filter_element=args.element, custom_attribute=args.custom_attribute, custom_attribute_value=args.custom_attribute_value)
