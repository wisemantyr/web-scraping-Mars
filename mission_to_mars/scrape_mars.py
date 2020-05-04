from bs4 import BeautifulSoup as bs
from splinter import Browser
import re
import pandas as pd

results = {"news_results": [], "featured_image_url" : "", "mars_weather": "", "mars_facts_html": "", "hemisphere_image_urls": []}

def scrape():
    ### Mars News ###

    #navigate to site
    newsURL = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    executable_path = {"executable_path": "chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit(newsURL)
    #get HTML and create soup object
    html = browser.html
    soup = bs(html, "html.parser")
    #get titles
    #isolate content
    newsItems = soup.find_all("div", class_="content_title")
    newsLinks = []
    for item in newsItems:
        newsLinks.append(item.find("a"))
    newsLinks = newsLinks[1:]
    #get paragraphs below titles
    #isolate soup object content
    articleTeasers = soup.find_all("div", class_="article_teaser_body")
    #get text from links
    newsTitles = []
    for link in newsLinks:
        title = link.text.strip()
        newsTitles.append(title)
    #get text only
    newsText = []
    for teaser in articleTeasers:
        paragraph = teaser.text.strip()
        newsText.append(paragraph)
    #zip items to create dict
    zippedNews = zip(newsTitles, newsText)
    for (a, b) in zippedNews:
        results["news_results"].append({"news_title": a, "news_p": b})

    ### Featured Image ###

    #navigate to site
    SpaceImagesURL = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    executable_path = {"executable_path": "chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit(SpaceImagesURL)
    #get next URL to visit
    elements = browser.find_by_id("full_image")
    ImageInfoLink = elements["data-link"]
    #get root URL for site
    ImageRootURL = SpaceImagesURL.split("/space")
    ImageRootURL = ImageRootURL[0]
    #concatenate strings to get correct link
    ImageInfoLink = ImageRootURL + ImageInfoLink
    #visit relevant page
    browser.visit(ImageInfoLink)
    #isolate element containing JPEG link
    if browser.is_element_present_by_css(".download_tiff") == True:
        JPEGLink = browser.links.find_by_partial_href("jpeg")
    #save URL
    FeaturedImageURL = JPEGLink["href"]
    #update result dict
    results["featured_image_url"] = FeaturedImageURL

    ### Mars Weather ###

    #visit site
    twitterURL = "https://twitter.com/marswxreport?lang=en"
    executable_path = {"executable_path": "chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit(twitterURL)
    #get HTML and create soup object
    twitterHTML = browser.html
    twitterSoup = bs(twitterHTML, "html.parser")
    #create regular expression string
    pattern = "([css]{3,3}.[a-zA-Z0-9_]{6,7}.){2,2}(r.[a-zA-Z0-9_]{6,7}.){3,4}"
    #use regex to isolate elements
    tweets = twitterSoup.find_all("span", class_= re.compile(pattern))
    #get text only
    tweetsText = []
    for tweet in tweets:
        tweetsText.append(tweet.text.strip())
    #create regular expression string
    pattern = "^(InSight)"
    #user regex to isolate content
    weatherTweets = []
    for text in tweetsText:
        matches = re.findall(pattern, text)
        for _ in matches:
            weatherTweets.append(text.strip())
    #get latest tweet
    marsWeather = weatherTweets[0]
    marsWeather = marsWeather.replace("\n", " ")
    #update result dict
    results["mars_weather"] = marsWeather

    ### Mars Facts ###

    #visit site
    factsURL = "https://space-facts.com/mars/"
    executable_path = {"executable_path": "chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit(factsURL)
    #get tables
    tables = pd.read_html(factsURL)
    #save desire table
    marsFactsDF = tables[0]
    #convert df to HTML string
    marsFactsHTML = marsFactsDF.to_html()
    marsFactsHTML = marsFactsHTML.replace("\n", "")
    #update result dict
    results["mars_facts_html"] = marsFactsHTML

    ### Hemispheres ###

    #visit site
    hemiURL = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    executable_path = {"executable_path": "chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=False)
    browser.visit(hemiURL)
    #save relevent elements
    elements = browser.links.find_by_partial_text("Hemisphere")
    #extract titles and urls
    hemiLinks = []
    titles = []
    for element in elements:
        hemiLinks.append(element["href"])
        title= element.text.split(" Enhanced")
        titles.append(title[0])
    #use previous urls to get image urls
    finalHemiLinks = []
    for link in hemiLinks:
        browser.visit(link)
        imageLink = browser.links.find_by_partial_text("Sample")
        finalHemiLinks.append(imageLink["href"])
    #zip results to put in dict
    zippedHemis = zip(titles, finalHemiLinks)
    #update results dict
    for (x, y) in zippedHemis:
        results["hemisphere_image_urls"].append({"title": x, "image_url": y})

    return results
