from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import json
import re
import random
from bs4 import BeautifulSoup
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

#This class returns a list of papers with following details: URL, Title, Year of Publication, Authors name, and DOI. 
class get_doi:
    def __init__(self):
        driver_path='/Users/drago/Documents/chromedriver-mac-arm64_V137/chromedriver'
        # self.service = Service(ChromeDriverManager().install())
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 10)
        self.all_paper_details=[]
    
    #function to accept cookies from cookies popup window
    def accept_cookies(self,popup):
        accept_button = popup.find_element(By.XPATH, ".//button[contains(text(), 'Accept')]")
        accept_button.click()

    #function to check of cookies window is opened or not
    def check_cookie_popup(self):
        try:
            popup=self.wait.until(By.XPATH,"//div[contains(text(), 'cookies')]")
            self.accept_cookies(popup)
        except:
            pass
    
    #function to open papers on new window
    def open_url(self,url):
        self.driver.execute_script(f"window.open('{url}', '_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.check_cookie_popup()
        try:
            self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        except:
            print("Timeout waiting for page to load")
        html = self.driver.page_source
        return html
    
    #function to extract whole text of the website
    def get_whole_text_of_page(self,html):
        soup = BeautifulSoup(html, "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        page_text = soup.get_text(separator="\n", strip=True)
        return page_text
    
    
    def get_citation(self,paper_number):
        cite_button_xpath=f'/html/body/div[1]/div[10]/div[2]/div[3]/div[2]/div[{paper_number}]/div[2]/div[3]/a[2]'
        cite_button=self.wait.until(EC.element_to_be_clickable((By.XPATH,cite_button_xpath)))
        cite_button.click()
        time.sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'gs_citr')))
        popup_xpath = '/html/body/div[1]/div[4]/div/div[2]/div/div[1]/table/tbody/tr[2]/td/div'
        popup = self.wait.until(EC.presence_of_element_located((By.XPATH, popup_xpath)))
        citation_text = popup.text
        close_btn_xpath='/html/body/div[1]/div[4]/div/div[1]/a'
        close_btn=self.wait.until(EC.element_to_be_clickable((By.XPATH,close_btn_xpath)))
        close_btn.click()
        return citation_text
    
    #function to extract authors name and year of publication
    def extract_details_from_citation(self,citation_text):
        pattern = r"^(.*?)\s\((\d{4})\)"
        match = re.match(pattern, citation_text)
        if match:
            authors = match.group(1)
            year = match.group(2)
            return authors, year
        return 'Authors name not present','Year not present'
       
    def get_text_after_marker(self,page_text,marker):
        page_text=page_text.lower()
        marker=marker.lower()
        index=page_text.find(marker)
        if index!=-1:
            after_text=page_text[(index+len(marker)):]
            return after_text
        return -1
    
    #function to extract DOI
    def get_doi_from_text(self,text):
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        doi=re.findall(doi_pattern, text, re.I)
        return doi

    #function to search string on google scholar
    def search(self,keyword):
        self.driver.get(f'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={keyword}&oq=')
        try:
            self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        except:
            print("Timeout waiting for page to load")
    
    def move_to_next_page(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # next_btn_xpath='/html/body/div/div[10]/div[2]/div[3]/div[3]/div[3]/button[2]'
        time.sleep(2)
        next_button = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Next'))
        )
        next_button.click()

    #function to extract URL and title of paper
    def select_paper(self,paper_number):
        paper=self.driver.find_element(By.XPATH,f'/html/body/div/div[10]/div[2]/div[3]/div[2]/div[{paper_number}]/div[2]/h3/a')
        url=paper.get_attribute('href')
        title=paper.text
        return url,title
    
    #function to extract all required details from k number of papers
    def extract_details_from_page(self,k):
        for i in range(10):
            self.driver.switch_to.window(self.driver.window_handles[0])
            paper_details={}
            try:
                url,title=self.select_paper(i+1)
                # time.sleep(random.randint(2,5))
            except:
                continue
            if 'books.google' in url:
                continue
            paper_details['url']=url
            paper_details['title']=title
            citation_text=self.get_citation(i+1)
            print(citation_text)
            authors,year=self.extract_details_from_citation(citation_text)
            # time.sleep(random.randint(2,5))
            paper_details['authors']=authors
            paper_details['year']=year
            html=self.open_url(url)
            # time.sleep(random.randint(2,5))
            try:
                page_text=self.get_whole_text_of_page(html)
                after_text=self.get_text_after_marker(page_text,'Cite this article')
                if after_text==-1:
                    after_text=self.get_text_after_marker(page_text,title)
                if after_text==-1:
                    continue
                else:
                    doi=self.get_doi_from_text(after_text)
                    if len(doi)==0:
                        continue
                    else:
                        paper_details['doi']=doi[0]
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                print('Cannot extract html for ',i)
                self.driver.switch_to.window(self.driver.window_handles[0])
                continue
            self.all_paper_details.append(paper_details)
            if len(self.all_paper_details)==k:
                break
    
    #main function. call this function to get all the details
    def main(self,search_str,k):
        try:
            self.search(search_str)
            time.sleep(random.randint(2,5))
            while len(self.all_paper_details)<=k:
                self.extract_details_from_page(k)
                try:
                    self.move_to_next_page()
                except:
                    break
            return json.dumps(self.all_paper_details)
        except:
            return json.dumps([{"server error":"Not able to extract the reaseach paper details"}])
            

class details_tool_input(BaseModel):
    search_str:str=Field(required=True,description="Enter a concise and focused sentence containing all the key terms you want to search for on Google Scholar to find relevant research papers")
    number_of_papers:int=Field(required=True,default=1,description="Enter the number of papers for which DOI need to extracted")

def details_extraction_tool(search_str:str,number_of_papers:int)->json:
    get_doi_=get_doi()
    paper_details=get_doi_.main(search_str,number_of_papers)
    return paper_details

#Extraction of paper details tool. Bind this tool directly with langchain
extract_paper_details_tool=StructuredTool.from_function(
    func=details_extraction_tool,
    description="""
    This tool extracts a list of research paper details relevant to the input sentence.

    This tool requires two input:
    search_str: A short phrase or query to search for relevant research papers on Google Scholar
    number_of_papers: The number of research paper details to extract from Google Scholar

    For each research paper, the tool returns the following fields:
    title: Title of the research paper
    url: Direct link to the research paper
    year: Year of publication of research paper
    author: Name(s) of the author(s) of research paper
    doi: Digital Object Identifier (DOI) of research paper

    Only papers with a valid DOI are included in the final output.

    If the server is unavailable or the extraction fails, the tool returns the message: "Not able to extract the research paper details"
    
    The output is returned as a JSON-formatted list of dictionaries
    """,
    args_schema=details_tool_input
)



"""
P.S.: Change the path of ChromeWebdriver at line number 17
ChromeWebdriver can be downloaded from website:
https://googlechromelabs.github.io/chrome-for-testing/#stable
"""