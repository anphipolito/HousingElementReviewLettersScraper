# Housing Element Review Letters Scraper
## Overview
This project focuses on evaluating housing compliance for various jurisdictions in California, particularly their adherence to statutory housing requirements and their performance in developing housing units as outlined in the Regional Housing Needs Allocation (RHNA) Progress Report. By analyzing data extracted from housing plan PDFs, the project identifies trends and correlations between compliance levels and housing development metrics such as Very Low-Income (VLI) units, Moderate-Income units, and overall population impact. The repository contains scripts for data extraction and analysis, offering insights into jurisdictional housing performance.
## Project Structure
```
- pdfDownloader.py       # Script for downloading pdfs
- extractpdf.py          # Script for extracting data from housing plan PDFs
- DataAnalysis.ipynb     # Jupyter notebook for housing data analysis
- requirements.txt       # Dependency list if not using poetry
- README.md              # Instructions for setting up and running the project
```
## Required Dependencies
These are included in the pyproject.toml and will be installed via Poetry:
* pandas
* matplotlib 
* numpy 
* census
* selenium 
* pymupdf

## Setup Instructions
### Prerequisites
1. **Python**: Ensure Python 3.7 or higher is installed.
2. **Poetry**: Install Poetry to manage dependencies. Run:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -


### A. Install Poetry and Setup Virtual Environment
1. Clone the git repository
```
git clone https://github.com/anphipolito/HousingElementReviewLettersScraper.git
cd HousingElementReviewLettersScraper
```
2. Install dependencies using Poetry:
```
poetry install
```
3. Activate the virtual environment.
```
poetry shell
```

### B. Census API Token Setup

To request an API Token, kindly request [here](https://api.census.gov/data/key_signup.html)

1. Set environment variables:
   ```bash
   export CENSUS_API_TOKEN=your_token_here
   ```
   On Windows (Command Prompt):
   ``` bash
      set CENSUS_API_KEY=your_census_api_key
   ```

### C. Data Download and Extraction
1. To download  the necessary PDF files, execute:
   ```
   python pdfDownloader.py
   ```
2. Run the following command to extract housing data from the PDFs:
   ```
   python extractpdf.py
   ```
### D.  Run Jupyter Notebook for Data Analysis
1. To perform the data analysis, open the Jupyter notebook:
   ```
   jupyter notebook DataAnalysis.ipynb
   ```
   Follow the instructions in the notebook to visualize the correlations and insights related to housing compliance.


## Contribution
   Feel free to submit pull requests or report issues.