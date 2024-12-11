from datetime import datetime, timedelta, timezone
import json
import logging

from bs4 import BeautifulSoup
import dateparser
import requests
from requests.adapters import HTTPAdapter, Retry
# from selenium_driverless.sync import webdriver
# from selenium_driverless.types.by import By


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
SESSION = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
SESSION.mount('https://', HTTPAdapter(max_retries=retries))


def scrape_krebsonsecurity_articles():
    """
    Scrape articles from Krebs on Security
    """
    logging.info('Getting Krebs on Security articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://krebsonsecurity.com', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.post'):
            try:
                title_elem = article.select_one('h2.entry-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.entry-date')
                if date_elem:
                    pub_date = datetime.strptime(date_elem.text.strip(), '%B %d, %Y')
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.entry-content p')
                articles.append({
                    'source': 'Krebs on Security',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Krebs on Security: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Krebs on Security articles: {str(e)}')
        return []


def scrape_krebsonsecurity_articles():
    """
    Scrape articles from Krebs on Security
    """
    logging.info('Getting Krebs on Security articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://krebsonsecurity.com', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.post'):
            try:
                title_elem = article.select_one('h2.entry-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.entry-date')
                if date_elem:
                    pub_date = datetime.strptime(date_elem.text.strip(), '%B %d, %Y')
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.entry-content p')
                articles.append({
                    'source': 'Krebs on Security',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Krebs on Security: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Krebs on Security articles: {str(e)}')
        return []

def scrape_totaltelecom_articles():
    """
    Scrape articles from Total Telecom
    """
    logging.info('Getting Total Telecom articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://totaltele.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.post'):
            try:
                title_elem = article.select_one('h2.entry-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.published')
                if date_elem:
                    pub_date = datetime.fromisoformat(date_elem.get('datetime', '')[:-6])
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.entry-content p')
                articles.append({
                    'source': 'Total Telecom',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Total Telecom: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Total Telecom articles: {str(e)}')
        return []

def scrape_telecomreview_articles():
    """
    Scrape articles from Telecom Review
    """
    logging.info('Getting Telecom Review articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://www.telecomreview.com/index.php/articles/news', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('div.itemContainer'):
            try:
                title_elem = article.select_one('div.catItemHeader h3.catItemTitle a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('span.catItemDateCreated')
                if date_elem:
                    pub_date = datetime.strptime(date_elem.text.strip(), '%d %B %Y')
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.catItemIntroText')
                articles.append({
                    'source': 'Telecom Review',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Telecom Review: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Telecom Review articles: {str(e)}')
        return []

def scrape_thehackernews_articles():
    """
    Scrape articles from The Hacker News
    """
    logging.info('Getting The Hacker News articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://thehackernews.com/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('div.body-post'):
            try:
                title_elem = article.select_one('h2.home-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('div.item-label span.h-datetime')
                if date_elem:
                    pub_date = datetime.strptime(date_elem.text.strip(), '%B %d, %Y')
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.home-desc')
                articles.append({
                    'source': 'The Hacker News',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from The Hacker News: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get The Hacker News articles: {str(e)}')
        return []

def scrape_cybersecuritydive_articles():
    """
    Scrape articles from Cybersecurity Dive
    """
    logging.info('Getting Cybersecurity Dive articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://www.cybersecuritydive.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('div.feed-item'):
            try:
                title_elem = article.select_one('h3.feed__title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time')
                if date_elem:
                    pub_date = datetime.fromisoformat(date_elem.get('datetime', ''))
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('p.feed__description')
                articles.append({
                    'source': 'Cybersecurity Dive',
                    'title': title_elem.text.strip(),
                    'url': 'https://www.cybersecuritydive.com' + title_elem.get('href', ''),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Cybersecurity Dive: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Cybersecurity Dive articles: {str(e)}')
        return []

def scrape_threatpost_articles():
    """
    Scrape articles from Threatpost
    """
    logging.info('Getting Threatpost articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://threatpost.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.c-card'):
            try:
                title_elem = article.select_one('h2.c-card__title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.c-card__date')
                if date_elem:
                    pub_date = datetime.fromisoformat(date_elem.get('datetime', ''))
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.c-card__excerpt')
                articles.append({
                    'source': 'Threatpost',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Threatpost: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Threatpost articles: {str(e)}')
        return []

def scrape_bleepingcomputer_articles():
    """
    Scrape articles from Bleeping Computer
    """
    logging.info('Getting Bleeping Computer articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://www.bleepingcomputer.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('div.article_front'):
            try:
                title_elem = article.select_one('h2 a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('div.article_time')
                if date_elem:
                    # Bleeping Computer uses relative time, might need to adjust this
                    pub_date_text = date_elem.text.strip()
                    if 'day' in pub_date_text.lower() or 'days' in pub_date_text.lower():
                        continue
                
                excerpt = article.select_one('div.article_content')
                articles.append({
                    'source': 'Bleeping Computer',
                    'title': title_elem.text.strip(),
                    'url': 'https://www.bleepingcomputer.com' + title_elem.get('href', ''),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Bleeping Computer: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Bleeping Computer articles: {str(e)}')
        return []

def scrape_scmedia_articles():
    """
    Scrape articles from SC Media
    """
    logging.info('Getting SC Media articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://www.scmagazine.com/news', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.article-card'):
            try:
                title_elem = article.select_one('h3.article-card__title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time')
                if date_elem:
                    pub_date = datetime.fromisoformat(date_elem.get('datetime', ''))
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('p.article-card__description')
                articles.append({
                    'source': 'SC Media',
                    'title': title_elem.text.strip(),
                    'url': 'https://www.scmagazine.com' + title_elem.get('href', ''),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from SC Media: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get SC Media articles: {str(e)}')
        return []

def scrape_securityweek_articles():
    """
    Scrape articles from SecurityWeek
    """
    logging.info('Getting SecurityWeek articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://www.securityweek.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.article-card'):
            try:
                title_elem = article.select_one('h2.entry-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.entry-date')
                if date_elem:
                    pub_date = datetime.fromisoformat(date_elem.get('datetime', ''))
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.entry-summary')
                articles.append({
                    'source': 'SecurityWeek',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from SecurityWeek: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get SecurityWeek articles: {str(e)}')
        return []

def scrape_cyberscoop_articles():
    """
    Scrape articles from CyberScoop
    """
    logging.info('Getting CyberScoop articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://www.cyberscoop.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.article'):
            try:
                title_elem = article.select_one('h2.entry-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.entry-date')
                if date_elem:
                    pub_date = datetime.fromisoformat(date_elem.get('datetime', ''))
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.entry-summary')
                articles.append({
                    'source': 'CyberScoop',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from CyberScoop: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get CyberScoop articles: {str(e)}')
        return []

def scrape_krebsonsecurity_articles():
    """
    Scrape articles from Krebs on Security
    """
    logging.info('Getting Krebs on Security articles')
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = SESSION.get('https://krebsonsecurity.com', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        
        for article in soup.select('article.post'):
            try:
                title_elem = article.select_one('h2.entry-title a')
                if not title_elem:
                    continue
                    
                date_elem = article.select_one('time.entry-date')
                if date_elem:
                    pub_date = datetime.strptime(date_elem.text.strip(), '%B %d, %Y')
                    if (now - pub_date).days > 1:
                        continue
                
                excerpt = article.select_one('div.entry-content p')
                articles.append({
                    'source': 'Krebs on Security',
                    'title': title_elem.text.strip(),
                    'url': title_elem.get('href'),
                    'excerpt': excerpt.text.strip() if excerpt else None
                })
            except Exception as e:
                logging.exception(f'Error retrieving an article from Krebs on Security: {str(e)}')
                continue
                
        return articles
    except Exception as e:
        logging.exception(f'Error: Failed to get Krebs on Security articles: {str(e)}')
        return []

def scrape_scmp_articles():
    logging.info('Getting SCMP articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.scmp.com/economy/china-economy', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('div[data-qa="Component-ActionBar"]'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    break
                link = art.parent.select_one('div ~ a')
                title = link.select_one('div[data-qa="Component-Headline"]').text.strip()
                excerpt = link.select_one('div[data-qa="Component-Summary"]')
                if excerpt is None:
                    r = SESSION.get('https://www.scmp.com/' + link.get('href'), headers=headers)
                    s = BeautifulSoup(r.content, 'html.parser')
                    excerpt = s.select_one('div[data-qa="GenericArticle-SubHeadline"]')
                articles.append({'source': 'SCMP', 'title': title, 'excerpt': excerpt.text.strip()})
            except:
                logging.exception('Error retrieving an article from SCMP.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get SCMP articles.')
        return []
    

def scrape_telecoms_articles():
    logging.info('Getting SCMP articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.scmp.com/economy/china-economy', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('div[data-qa="Component-ActionBar"]'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    break
                link = art.parent.select_one('div ~ a')
                title = link.select_one('div[data-qa="Component-Headline"]').text.strip()
                excerpt = link.select_one('div[data-qa="Component-Summary"]')
                if excerpt is None:
                    r = SESSION.get('https://www.scmp.com/' + link.get('href'), headers=headers)
                    s = BeautifulSoup(r.content, 'html.parser')
                    excerpt = s.select_one('div[data-qa="GenericArticle-SubHeadline"]')
                articles.append({'source': 'SCMP', 'title': title, 'excerpt': excerpt.text.strip()})
            except:
                logging.exception('Error retrieving an article from SCMP.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get SCMP articles.')
        return []

def scrape_ft_articles():
    logging.info('Getting Financial Times articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.ft.com/chinese-economy', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('.o-teaser--article'):
            try:
                time = art.parent.parent.parent.select_one('time').get('datetime')[:-1]
                time = datetime.fromisoformat(time)
                if (now - time).days:
                    break
                title = art.select_one('.o-teaser__heading').text.strip()
                excerpt = art.select_one('.o-teaser__standfirst').text.strip()
                articles.append({'source': 'Financial Times', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from Financial Times.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Financial Times articles.')
        return []


# TODO reuters


def scrape_cnn_articles():
    logging.info('Getting CNN Business articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://edition.cnn.com/business/china', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('div.stack:nth-child(1) .card,div.stack:nth-child(2) .card'):
            try:
                link = art.select_one('a').get('href')
                r = SESSION.get('https://edition.cnn.com/' + link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = s.select_one('div.timestamp').text.strip().replace('Updated', '').replace('Published', '')
                time = dateparser.parse(time)
                if (now - time).days:
                    break
                title = s.select_one('h1').text.strip()
                excerpt = s.select_one('p.paragraph').text.strip()
                articles.append({'source': 'CNN Business', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from CNN Business.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get CNN Business articles.')
        return []


def scrape_cna_articles():
    logging.info('Getting CNA articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.channelnewsasia.com/topic/china-economy', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('div.list-object'):
            try:
                time = art.select_one('.timestamp')
                time = datetime.fromtimestamp(int(time.get('data-lastupdated')))
                if (now - time).days:
                    break
                link = art.select_one('h6 a').get('href')
                r = SESSION.get('https://www.channelnewsasia.com/' + link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                title = s.select_one('h1').text.strip()
                excerpt = s.select_one('.content-detail__description')
                if excerpt is None:
                    excerpt = s.select_one('.text p')
                excerpt = excerpt.text.strip().replace('…\n\n    see\xa0more', '')
                articles.append({'source': 'CNA', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from CNA.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get CNA articles.')
        return []


def scrape_pvtech_articles():
    logging.info('Getting PV Tech articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.pv-tech.org/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('[data-id="32f39be"] h2 a'):
            try:
                link = art.get('href')
                r = SESSION.get(link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days:
                    if art.parent.parent.parent.get('data-id') == '42a5d20':
                        break
                    else:
                        continue
                title = s.select_one('h1').text.strip()
                excerpt = s.select_one('#post-content p').text.strip()
                articles.append({'source': 'PV Tech', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from PV Tech.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get PV Tech articles.')
        return []


def scrape_rew_articles():
    logging.info('Getting Renewable Energy World articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.renewableenergyworld.com/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('div.header a'):
            try:
                link = art.get('href')
                r = SESSION.get(link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = s.select_one('h1').text.strip()
                excerpt = art.parent.parent.select_one('div.excerpt').text.strip()
                articles.append({'source': 'Renewable Energy World', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from Renewable Energy World.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Renewable Energy World articles.')
        return []


def scrape_esn_articles():
    logging.info('Getting Energy Storage News articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.energy-storage.news/category/news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('[data-id="4de41f9"] h2 a'):
            try:
                link = art.get('href')
                r = SESSION.get(link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days > 1:
                    break
                title = s.select_one('h1').text.strip()
                excerpt = s.select_one('.wpwp-non-paywall p').text.strip()
                articles.append({'source': 'Energy Storage News', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from Energy Storage News.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Energy Storage News articles.')
        return []


def scrape_logisticsmanagement_articles():
    logging.info('Getting Logistics Management articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.logisticsmgmt.com/topic/category/news', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('#content'):
            try:
                time = datetime.fromisoformat(art.select_one('span[itemprop="datePublished"]').get('content'))
                if (now - time).days:
                    break
                title = art.select_one('div.head').text.strip()
                excerpt = art.select_one('div.text').text.strip()
                articles.append({'source': 'Logistics Management', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from Logistics Management.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Logistics Management articles.')
        return []


def scrape_supplychaindive_articles():
    logging.info('Getting Supply Chain Dive articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.supplychaindive.com/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('.hero-article h1 a, .top-stories h3 a, ul > li.row.feed__item h3 a'):
            try:
                link = art.get('href')
                r = SESSION.get('https://www.supplychaindive.com' + link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = s.select_one('span.published-info')
                if time is None:
                    time = s.select_one('div.full-width-byline')
                time = time.text.strip().replace('Published', '')
                if 'Updated' in time:
                    time = time[time.index('Updated') + 7:]
                if 'By' in time:
                    time = time[:time.index('By')]
                time = dateparser.parse(time)
                if (now - time).days > 1:
                    break
                title = s.select_one('article h1').text.strip()
                excerpt = s.select_one('p.full-width__subtitle')
                if excerpt is None:
                    excerpt = s.select_one('article h1 ~ p')
                articles.append({'source': 'Supply Chain Dive', 'title': title, 'excerpt': excerpt.text.strip()})
            except:
                logging.exception('Error retrieving an article from Supply Chain Dive.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Supply Chain Dive articles.')
        return []


def scrape_maersk_articles():
    logging.info('Getting Maersk articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.maersk.com/news', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('.p-section__news__teaser'):
            try:
                link = art.select_one('a').get('href')
                time = art.select_one('.p-section__news__teaser__timestamp').text.strip()
                time = dateparser.parse(time)
                if (now - time).days > 5:
                    break
                r = SESSION.get('https://www.maersk.com/' + link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                title = s.select_one('h1').text.strip()
                excerpt = s.select_one('.p-page__section__child p').text.strip()
                articles.append({'source': 'Maersk', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from Maersk.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Maersk articles.')
        return []


def scrape_freightwaves_articles():
    logging.info('Getting FreightWaves articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.freightwaves.com/news', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('article'):
            try:
                link = art.select_one('a').get('href')
                r = SESSION.get(link, headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = s.select_one('h1').text.strip()
                excerpt = art.select_one('.mb-12').text.strip()
                articles.append({'source': 'FreightWaves', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from FreightWaves.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get FreightWaves articles.')
        return []
