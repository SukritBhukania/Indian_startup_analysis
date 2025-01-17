import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet


# Define the database connection string
db_url = 'mysql+pymysql://root:new_password@localhost:3306/indian_startups'

# Function to authenticate with Google Sheets and load data
def load_data_from_gsheets(sheet_url, creds_json_file):
    try:
        # Authenticate with Google Sheets API using the credentials
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json_file, scope)
        client = gspread.authorize(creds)

        # Open the Google Sheet by URL
        sheet = client.open_by_url(sheet_url)

        # Select the first worksheet (if more than one sheet exists)
        worksheet = sheet.get_worksheet(0)

        # Get all values from the sheet and convert to a pandas DataFrame
        data = pd.DataFrame(worksheet.get_all_records())

        return data
    except Exception as e:
        print(f"Error reading the Google Sheet: {e}")
        return None

# Function to clean and transform the data
def load_and_transform_data(data):
    try:
        # Step 1: Clean the 'Company' column by removing special characters '^' and '*'
        data['Company'] = data['Company'].replace({r'\^': '', r'\*': ''}, regex=True)

        # Step 2: Clean 'Sector' column (remove extra spaces)
        data['Sector'] = data['Sector'].str.strip()

        # Step 3: Clean 'Entry Valuation' and 'Valuation' by removing currency symbols and commas
        data['Entry Valuation'] = data['Entry Valuation'].replace({',': '', '₹': '', '$': '', 'B': ''}, regex=True).apply(pd.to_numeric, errors='coerce')
        data['Valuation'] = data['Valuation'].replace({',': '', '₹': '', '$': '', 'B': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

        # Step 4: Clean the 'Entry' column (convert to datetime)
        data['Entry'] = pd.to_datetime(data['Entry'], errors='coerce')

        # Step 5: Clean other columns like 'Location' and 'Select Investors'
        data['Location'] = data['Location'].str.strip()
        data['Select Investors'] = data['Select Investors'].str.strip()

        # Step 6: Handle missing or NaN values
        data['Entry Valuation'] = data['Entry Valuation'].fillna(0)
        data['Valuation'] = data['Valuation'].fillna(0)

        # Step 7: Remove rows with missing 'Company' or 'Sector'
        data = data.dropna(subset=['Company', 'Sector'])

        return data
    except Exception as e:
        print(f"An error occurred during transformation: {e}")
        return None

# Function to upload the data to the database
def upload_to_database(data, db_url):
    try:
        engine = create_engine(db_url)
        data.to_sql('startups', con=engine, if_exists='replace', index=False)
        print("Data uploaded successfully to the database!")
    except Exception as e:
        print(f"Error uploading data to the database: {e}")

# Function to run SQL queries and perform analysis
def analyze_data_from_db(db_url):
    try:
        engine = create_engine(db_url)

        # SQL Query: Total valuation per sector
        query = '''
            SELECT Sector, SUM(Valuation) AS Total_Valuation
            FROM startups
            GROUP BY Sector
            ORDER BY Total_Valuation DESC;
        '''
        sector_analysis = pd.read_sql(query, con=engine)

        # SQL Query: Get all companies and their entry and valuation data
        query_growth = '''
    SELECT Company, Sector, Entry, Valuation, `Entry Valuation`
    FROM startups;
'''
        growth_data = pd.read_sql(query_growth, con=engine)

        return sector_analysis, growth_data
    except Exception as e:
        print(f"Error analyzing data from the database: {e}")
        return None, None

# Function to calculate days in business and growth
def calculate_growth(data):
    try:
        # Step 1: Calculate "Days in Business"
        data['Days in Business'] = (datetime.now() - data['Entry']).dt.days

        # Step 2: Calculate valuation growth (current valuation - entry valuation)
        data['Valuation Growth'] = data['Valuation'] - data['Entry Valuation']

        # Step 3: Filter companies that have been in business for 5 years or less
        data_within_5_years = data[data['Days in Business'] <= 5 * 365]  # 5 years in days

        # Step 4: Group by sector and calculate the average growth
        sector_growth_analysis = data_within_5_years.groupby('Sector')['Valuation Growth'].mean().reset_index()

        return sector_growth_analysis
    except Exception as e:
        print(f"Error calculating growth: {e}")
        return None

# Function to visualize the results using matplotlib and seaborn
def beautify_plot(sector_analysis):
    # Beautify the barplot
    plt.figure(figsize=(12, 8))
    sns.barplot(data=sector_analysis, x='Sector', y='Total_Valuation', palette='viridis')

    # Adding titles and labels
    plt.title('Total Valuation by Sector', fontsize=16, fontweight='bold')
    plt.xlabel('Sector', fontsize=14)
    plt.ylabel('Total Valuation (in Billion ₹)', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the plot
    plot_file = 'sector_valuation_plot.png'
    plt.savefig(plot_file)
    plt.close()
    
    return plot_file

# Function to generate a detailed PDF report with introduction and conclusions
def generate_pdf_report_with_intro_and_conclusion(inferences, sector_analysis, sector_growth_analysis, plot_files):
    try:
        # Create PDF
        pdf_path = 'startup_analysis_report_with_intro_and_conclusion.pdf'
        document = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Add Title
        elements.append(Paragraph("Startup Valuation and Growth Analysis Report", style=styles["Title"]))
        elements.append(Spacer(1, 12))

        # Add Introduction
        elements.append(Paragraph("<b>Introduction:</b>", style=styles["Heading2"]))
        intro_text = """
        This report provides an analysis of the valuation and growth of startups across various sectors. 
        The aim is to identify trends in startup performance, highlight sectors with the highest valuation 
        and growth potential, and identify challenges faced by specific industries based on data collected from 
        various sources. The findings are supported by data-driven insights and visualizations.
        """
        elements.append(Paragraph(intro_text, style=styles["BodyText"]))
        elements.append(Spacer(1, 12))

        # Add Inferences
        elements.append(Paragraph("<b>Inferences:</b>", style=styles["Heading2"]))
        for inference in inferences:
            elements.append(Paragraph(inference, style=styles["BodyText"]))
        elements.append(Spacer(1, 12))

        # Add Industries in Problem Section
        elements.append(Paragraph("<b>Industries Facing Challenges:</b>", style=styles["Heading2"]))
        problematic_sectors = sector_growth_analysis[sector_growth_analysis['Valuation Growth'] < 0]
        if not problematic_sectors.empty:
            problem_sectors_text = "The following industries have shown negative valuation growth, indicating potential problems:\n"
            for _, row in problematic_sectors.iterrows():
                problem_sectors_text += f"Sector: {row['Sector']} - Negative Growth: {row['Valuation Growth']}\n"
        else:
            problem_sectors_text = "No industries with negative growth identified in the dataset."

        elements.append(Paragraph(problem_sectors_text, style=styles["BodyText"]))
        elements.append(Spacer(1, 12))

        # Add Total Valuation per Sector Data Table
        elements.append(Paragraph("<b>Total Valuation per Sector:</b>", style=styles["Heading2"]))
        data = [["Sector", "Total Valuation"]] + sector_analysis.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                                   ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                   ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                   ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                                   ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                                   ("GRID", (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Add Valuation Growth by Sector Data Table
        elements.append(Paragraph("<b>Valuation Growth per Sector (Companies in Business for 5 Years or Less):</b>", style=styles["Heading2"]))
        growth_data = [["Sector", "Average Valuation Growth"]] + sector_growth_analysis.values.tolist()
        growth_table = Table(growth_data)
        growth_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                                         ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                                         ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                         ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                                         ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                                         ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                                         ("GRID", (0, 0), (-1, -1), 1, colors.black)]))
        elements.append(growth_table)
        elements.append(Spacer(1, 12))

        # Add Plots to the PDF
        elements.append(Paragraph("<b>Visualizations:</b>", style=styles["Heading2"]))
        for plot_file in plot_files:
            elements.append(Image(plot_file, width=400, height=300))
            elements.append(Spacer(1, 12))

        # Add Conclusion
        elements.append(Paragraph("<b>Conclusion:</b>", style=styles["Heading2"]))
        conclusion_text = """
        Based on the analysis, several sectors are leading in terms of valuation, while others are facing 
        challenges due to negative growth. Further research and strategic investments in high-growth sectors 
        can potentially yield greater returns in the coming years. This report serves as a valuable resource for 
        identifying trends and making informed decisions in the startup ecosystem.
        """
        elements.append(Paragraph(conclusion_text, style=styles["BodyText"]))

        # Build PDF
        document.build(elements)
        print(f"PDF report successfully generated: {pdf_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


# Main execution
def main():
    # Load data from Google Sheets
    sheet_url = 'https://docs.google.com/spreadsheets/d/1lPR1JO7i74THJY7Ea7Gvz0yhEJ0ShO3T-ipBB2h7NBQ/edit?usp=sharing'
    creds_json_file = '/Users/sukrit/Downloads/pivotal-biplane-448109-k1-354445b84c8e.json'
    data = load_data_from_gsheets(sheet_url, creds_json_file)

    # Transform the data
    if data is not None:
        data = load_and_transform_data(data)

        # Upload to MySQL Database
        upload_to_database(data, db_url)

        # Analyze data from the database
        sector_analysis, growth_data = analyze_data_from_db(db_url)

        # Calculate growth data
        sector_growth_analysis = calculate_growth(growth_data)

        # Beautify the plots
        plot_file = beautify_plot(sector_analysis)

        # Generate PDF report with introduction, inferences, and conclusions
        inferences = ["- Valuation has been increasing in sectors like AI and SaaS.",
                      "- Industries such as fintech and healthtech are facing challenges."]
        generate_pdf_report_with_intro_and_conclusion(inferences, sector_analysis, sector_growth_analysis, [plot_file])


if __name__ == '__main__':
    main()