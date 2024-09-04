# HREF Extractor
This tool is designed to scrape and parse HTML content from a webpage, expand all elements dynamically loaded with JavaScript, filter specific HTML content based on user-provided criteria, and generate a CSV file containing hyperlinks (`href`) and their corresponding breadcrumb paths.

## Features

- **Expand Dynamic Content**: Automatically expands all dynamic elements loaded by JavaScript on the webpage.
- **Filter HTML Content**: Allows filtering HTML content by:
  - ID
  - Class name and element type
  - Custom attributes and values (in development)
- **Generate Breadcrumbs**: Parses the filtered HTML to extract all `<a>` tag `href` attributes and generates a breadcrumb path for each hyperlink.
- **Output Files**: Saves the expanded full HTML, filtered HTML, and CSV output in organized directories under the `./artifacts/` folder.

## Usage

### Prerequisites

- Python 3.x
- Selenium WebDriver
- BeautifulSoup (bs4)
- ChromeDriver

Ensure you have all required Python packages installed. You can install them using pip:

`pip install selenium beautifulsoup4`

### Running the Tool

To run the tool, use the following command:

`python main.py --url <URL> [options]`

### Command-Line Options

- `--url`: (Required) The URL of the webpage to scrape.
- `--id`: (Optional) The ID of the parent element to filter.
- `--class-name`: (Optional) The class name of the parent element to filter.
- `--element`: (Optional) The HTML element type to filter (e.g., 'ul', 'div').
- `--custom-attribute`: (Optional) The custom attribute to filter by.
- `--custom-attribute-value`: (Optional) The value of the custom attribute to filter by.

### Example Commands

1. **Filter by Class Name and Element**:

`python main.py --url "https://learn.microsoft.com/en-us/azure/container-registry/" --class-name 'tree table-of-contents is-vertically-scrollable flex-grow-1 flex-shrink-1' --element "ul"`

2. **Filter by ID**:

`python main.py --url "https://learn.microsoft.com/en-us/azure/container-registry/" --id "main-content"`

### Output Files

All output files are stored in organized directories under the `./artifacts/` folder:

- **Logs**: Stored in `./artifacts/logs/`. The log file captures the entire command used to run the script, any errors, warnings, or debugging information.
- **HTML Files**:
  - **Full HTML**: Stored in `./artifacts/html/full_html/`. Contains the fully expanded HTML content of the webpage.
  - **Filtered HTML**: Stored in `./artifacts/html/filtered_html/`. Contains the filtered HTML content based on the user-provided criteria.
- **CSV Files**: Stored in `./artifacts/csv/`. Contains the parsed hyperlinks and their breadcrumbs.

### Example Output

The CSV output file will have the following structure:

| Href                                                    | Breadcrumb                                            |
|---------------------------------------------------------|-------------------------------------------------------|
| https://learn.microsoft.com/en-us/azure/container-registry/ | Azure Container Registry documentation                |
| https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro | Azure Container Registry documentation > Overview About Container Registry |

## Current Development

The following functionality is currently under development and is **not yet fully supported**:

- **Custom Attribute Filtering**: The ability to filter HTML elements based on a custom attribute and its value is planned. The options `--custom-attribute` and `--custom-attribute-value` are placeholders and do not work at the moment.

## Troubleshooting

If you encounter any issues, please check the log file in the `./artifacts/logs/` directory for detailed error messages and debugging information. 

### Common Issues

1. **No Elements Found**:
   - Ensure the filter criteria (ID, class name, element type) match the structure of the webpage's HTML.
   - Double-check that dynamic elements are expanded before filtering.

2. **WebDriver Errors**:
   - Make sure ChromeDriver is installed and the path to ChromeDriver is correctly set in your system.

## Future Enhancements

- Full support for custom attribute filtering.
- Enhanced compatibility with various documentation sites (not just Azure or AWS).
- Additional scraping options, such as capturing more HTML attributes.

## Contribution

Contributions to this project are welcome! Please submit issues or pull requests via GitHub.
