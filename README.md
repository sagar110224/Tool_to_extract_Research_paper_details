# Tool_to_extract_Research_paper_details
This langchain tool uses Selenium to search papers on Google Scholar for the given keywords. It then extracts given details (URL, Title, Authors, Year of publication, and DOI) for the given number of papers.

This tool requires two inputs: search_str and number_of_papers
search_str- short phrase that need to searched on google scholar
number_of_papers- number of paper details required

It returns a list of dictionary of length number_of_papers. Each dictionary has following details:
1. url: Website URL on which research paper is available 
2. title: Title of research paper
3. year: Year of publication of research paper
4. author: Authors of research paper
5. doi: DOI of research paper
P.S.: 
- those research papers are included in the dictionary for which all four details are present
- Change the path of ChromeWebdriver at line number 17
- ChromeWebdriver can be downloaded from website: https://googlechromelabs.github.io/chrome-for-testing/#stable


If you want to use proxies then use the file 'Langchain_RP_details_with_proxy.py'. 
You can get free proxies from the website: www.webshare.io
Copy the proxy list in a .txt file. 
Copy this .txt file path at line 15 in proxy_extraction.py file
