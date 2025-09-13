# Naukri Job Scraper

A comprehensive job scraping tool for Naukri.com with a clean Tkinter GUI interface.

## Features

- 🔐 **Secure Login** - Login to Naukri.com with your credentials
- 🔍 **Advanced Search** - Search jobs by title, location, and experience
- 📄 **Pagination Support** - Automatically navigate through multiple pages
- 📊 **Data Extraction** - Extract comprehensive job details including:
  - Job Title
  - Company Name
  - Experience Required
  - Location
  - Company Rating
  - Posted Date
  - Skills Required
  - Job Description
  - Direct Job Links
  - Job IDs
- 💾 **CSV Export** - Export all scraped data to CSV format
- 🖥️ **Clean GUI** - User-friendly Tkinter interface
- ⚡ **Real-time Progress** - Live progress updates and status tracking

## Installation

1. **Clone or download the project files**

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Chrome browser** (if not already installed)

## Usage

### GUI Application (Recommended)

1. **Run the GUI application:**
   ```bash
   python3 naukri_gui.py
   ```

2. **Fill in the form:**
   - Enter your Naukri.com email and password
   - Specify job title (e.g., "Python Developer")
   - Enter location (e.g., "Bangalore", "Mumbai", "Delhi")
   - Select experience level (0-10 years)
   - Set maximum number of jobs to scrape (default: 100)

3. **Start scraping:**
   - Click "Start Scraping" button
   - Monitor progress in real-time
   - View results in the table below

4. **Export results:**
   - Click "Export to CSV" to save all data
   - Choose file location and name
   - Data will be saved with timestamp

### Command Line Usage

```bash
python3 naukri.py
```

## File Structure

```
job_scraper_selenium/
├── naukri.py              # Main scraping logic
├── naukri_gui.py          # GUI application
├── main.py                # Alternative entry point
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── output_files/         # Generated CSV files
```

## Output Files

The application generates two types of output files:

1. **CSV Files** (`naukri_jobs_YYYYMMDD_HHMMSS.csv`)
   - Complete structured data
   - All job details in spreadsheet format
   - Ready for analysis in Excel/Google Sheets

2. **Summary Files** (`naukri_jobs_summary_YYYYMMDD_HHMMSS.txt`)
   - Human-readable format
   - Quick overview of all jobs
   - Easy to read and share

## CSV Columns

- Job Title
- Company
- Experience
- Location
- Rating
- Posted Date
- Skills
- Description
- Job Link
- Job ID

## Features in Detail

### Search Parameters
- **Job Title**: Any job role (e.g., "Python Developer", "Data Scientist", "Software Engineer")
- **Location**: City names (e.g., "Bangalore", "Mumbai", "Delhi", "Hyderabad")
- **Experience**: Years of experience (0-10 years)
- **Max Jobs**: Maximum number of jobs to scrape (recommended: 50-200)

### Pagination
- Automatically navigates through multiple pages
- Collects jobs from up to 10 pages
- Stops when target number is reached or no more pages available

### Data Quality
- Robust error handling
- Multiple fallback selectors
- Data validation and cleaning
- Handles missing or incomplete data gracefully

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify email and password are correct
   - Check if account is locked or requires verification
   - Ensure stable internet connection

2. **No Jobs Found**
   - Try different job titles or locations
   - Check if the search criteria is too specific
   - Verify Naukri.com is accessible

3. **Browser Issues**
   - Ensure Chrome browser is installed
   - Update Chrome to latest version
   - Check if antivirus is blocking browser automation

4. **Export Issues**
   - Ensure you have write permissions in the target directory
   - Check available disk space
   - Try different file location

### Performance Tips

- Use specific job titles for better results
- Limit max jobs to 100-200 for faster execution
- Run during off-peak hours for better performance
- Close other browser instances to free up memory

## Legal Notice

This tool is for educational and personal use only. Please respect Naukri.com's terms of service and robots.txt. Use responsibly and don't overload their servers.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all requirements are installed
3. Check internet connectivity
4. Ensure Chrome browser is up to date

## Version History

- **v1.0** - Initial release with basic scraping
- **v1.1** - Added GUI interface
- **v1.2** - Added pagination support
- **v1.3** - Enhanced data extraction and CSV export