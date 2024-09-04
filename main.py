from bs4 import BeautifulSoup
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

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
                print(f"Error clicking element: {e}")
                continue

def save_filtered_html(soup, filter_by_id=None, filter_by_class=None, filter_element=None):
    filtered_html_content = None
    if filter_by_id:
        parent_element = soup.find(id=filter_by_id)
        if parent_element:
            with open(f"filtered_content_{filter_by_id}.html", "w", encoding="utf-8") as file:
                file.write(str(parent_element))
            filtered_html_content = parent_element
            print(f"Filtered HTML content saved to 'filtered_content_{filter_by_id}.html'.")
        else:
            print(f"No element found with ID '{filter_by_id}'.")
    elif filter_by_class and filter_element:
        parent_elements = soup.find_all(filter_element, class_=filter_by_class)
        if parent_elements:
            for i, parent_element in enumerate(parent_elements):
                file_name = f"filtered_content_{filter_by_class}_{i+1}.html"
                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(str(parent_element))
                if i == 0:  # Save the first match for further processing
                    filtered_html_content = parent_element
                print(f"Filtered HTML content saved to '{file_name}'.")
        else:
            print(f"No elements found with class name '{filter_by_class}' and element '{filter_element}'.")
    else:
        print("Please provide either an ID or both a class name and element type for filtering.")
    
    return filtered_html_content

def parse_html_and_generate_csv(soup, output_csv_file):
    with open(output_csv_file, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Href", "Breadcrumb"])

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            breadcrumb_parts = []
            current_element = a_tag
            
            # Debugging: Starting processing of <a> tag
            print(f"Processing <a> tag with href: {href}")
            input("Press Enter to continue...")

            while current_element:
                parent = current_element.find_parent(['li', 'ul'])
                if parent and parent.name == 'li':
                    span_text = parent.find('span', recursive=False)
                    if span_text and span_text.text.strip():
                        breadcrumb_parts.insert(0, span_text.text.strip())
                        print(f"Added '{span_text.text.strip()}' to breadcrumb")
                        input("Press Enter to continue...")
                current_element = parent
            
            breadcrumb = ' > '.join(breadcrumb_parts)
            writer.writerow([href, breadcrumb])
            print(f"Final breadcrumb for href '{href}': {breadcrumb}\n")
            input("Press Enter to continue...")
    
    print(f"CSV file '{output_csv_file}' has been generated.")

def main(url, filter_by_id=None, filter_by_class=None, filter_element=None):
    driver = webdriver.Chrome()
    driver.get(url)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    except Exception as e:
        print(f"Error waiting for page to load: {e}")
        driver.quit()
        exit()

    expand_all_elements(driver)
    time.sleep(5)  # Ensure all content is loaded
    full_html = driver.page_source

    with open("fully_expanded_content.html", "w", encoding="utf-8") as file:
        file.write(full_html)
    print("Full page HTML content saved to 'fully_expanded_content.html'.")

    soup = BeautifulSoup(full_html, "html.parser")
    
    # Save filtered HTML based on user input
    filtered_html = save_filtered_html(soup, filter_by_id, filter_by_class, filter_element)

    # Check if filtered HTML is found and parse
    if filtered_html:
        print("Parsing filtered HTML to CSV...")
        parse_html_and_generate_csv(filtered_html, "parsed_links_and_breadcrumbs.csv")
    else:
        print("Filtered HTML not found; skipping CSV generation.")

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Expand and filter HTML content from a webpage.")
    parser.add_argument("--url", type=str, required=True, help="The URL of the webpage to scrape.")
    parser.add_argument("--id", type=str, help="The ID of the parent element to filter.")
    parser.add_argument("--class-name", type=str, help="The class name of the parent element to filter.")
    parser.add_argument("--element", type=str, help="The HTML element type to filter (e.g., 'ul', 'div').")

    args = parser.parse_args()

    if not args.id and (not args.class_name or not args.element):
        print("Error: You must provide either an ID or both a class name and element type for filtering.")
        exit()

    main(args.url, filter_by_id=args.id, filter_by_class=args.class_name, filter_element=args.element)
