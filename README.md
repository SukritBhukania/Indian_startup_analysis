# Indian Startup Analysis
This project focuses on analyzing startup valuation data, extracting it from a Google Sheet, cleaning and transforming the data using Python, and uploading it into a MySQL database. It then runs SQL queries to perform analysis and generates inferences about the valuation growth of different sectors. Finally, the project generates a comprehensive report with plots and insights.

## Project Overview

This project aims to help understand the valuation trends in the startup ecosystem. By analyzing entry valuations and current valuations across different sectors, we can identify high-growth industries and draw conclusions that could inform future investment decisions.


## Steps Involved

### 1. **Extract Data from Google Sheets**

The first step is to extract the data from a Google Sheet using the Google Sheets API. This is done in the script `load_data.py`, which fetches all the records from the provided Google Sheets URL and converts them into a Pandas DataFrame.

### 2. **Transform and Clean Data**

Once the data is loaded, it is cleaned and transformed using the `transform_data.py` script. This step includes:
- Removing special characters from the `Company` column.
- Stripping whitespace from the `Sector`, `Location`, and `Select Investors` columns.
- Converting the `Entry Valuation` and `Valuation` columns into numerical values by removing symbols and commas.
- Handling missing or NaN values and converting date columns appropriately.

### 3. **Upload to MySQL Database**

The cleaned data is then uploaded to a MySQL database using the `upload_to_db.py` script. The data is stored in a table called `startups` within the specified database.

### 4. **Analyze Data**

SQL queries are used to perform analysis on the data, including:
- Total valuation per sector.
- The growth of startups based on their entry valuation and current valuation.
These queries are executed in `analyze_data.py`, and the results are saved as Pandas DataFrames.

### 5. **Generate Report**

The final step is to generate a comprehensive PDF report with analysis, inferences, and visualizations. This is done in `generate_report.py`, which includes:
- A summary of the analysis performed.
- Plots showing sector-wise valuations and growth trends.
- Concluding remarks based on the results.

## Setup Instructions

### Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.x
- MySQL (for the database)

### Install Dependencies

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/startup-valuation-analysis.git
   cd startup-valuation-analysis
   ```
2. Install the required Python libraries:

```bash
pip install -r requirements.txt
```
## Configure Google Sheets API
Set up Google Sheets API and create a service account as described in Google Sheets API documentation.
Download the service account credentials JSON file and save it in the project directory (e.g., pivotal-biplane-448109-k1-354445b84c8e.json).
Database Configuration
Make sure MySQL is running on your local machine or a server.

## Create a database called indian_startups:
```sql
CREATE DATABASE indian_startups;
```
3. Update the database connection string in the upload_to_db.py file with your MySQL credentials.

## Run the Scripts

Load and Transform Data:

```bash
python scripts/load_data.py
python scripts/transform_data.py
```
Upload Data to Database:
```bash
python scripts/upload_to_db.py
```
Analyze Data:
```bash
python scripts/analyze_data.py
```
Generate Report:
``` bash
python scripts/generate_report.py
```
This will generate a PDF report and a plot in the reports/ folder.

## Contributing
Feel free to fork the repository, make improvements, and submit pull requests. Please ensure that your code adheres to the project's coding standards and includes tests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
```vbnet

### Key Points:
- The `README.md` provides a clear explanation of how the project is structured and how to run each part of it.
- It includes setup instructions to install dependencies and configure both the Google Sheets API and MySQL.
- It offers a simple overview of the process from loading data to generating the final report.

You can customize it further based on your needs.
```

