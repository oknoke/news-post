import sys
from datetime import datetime, timezone, timedelta
import json
from random import choice
import re
from math import ceil
import requests
from requests.adapters import HTTPAdapter, Retry
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import dateparser
from selenium_driverless.sync import webdriver
from selenium_driverless.types.by import By
from selenium_driverless.types.webelement import NoSuchElementException

from news import *
from chat import *


load_dotenv()

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

SESSION = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
SESSION.mount('https://', HTTPAdapter(max_retries=retries))


def scrape_techcrunch_articles(category, n=5):
    logging.info('Getting Techcrunch articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get(f'https://techcrunch.com/category/{category}/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('.loop-card--default'):
            try:
                title = art.select_one('h3 a')
                time = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                r = SESSION.get(title.get('href'))
                s = BeautifulSoup(r.content, 'html.parser')
                summary = s.select_one('p#speakable-summary').text.strip()
                articles.append({'source': 'Techcrunch', 'title': title.text.strip(), 'excerpt': summary})
            except Exception:
                logging.exception('Error retrieving an article from Techcrunch.')
                continue
        return articles[:n]
    except Exception:
        logging.exception('Error: Failed to get Techcrunch articles.')
        return []


def scrape_arstechnica_articles(category, n=5):
    logging.info('Getting Ars Technica articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get(f'https://arstechnica.com/{category}/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('article'):
            try:
                t = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if (now - t).days:
                    break
                title = art.select_one('h2').text.strip()
                summary = art.select_one('p.leading-tighter').text.strip()
                articles.append({'source': 'ArsTechnica', 'title': title, 'excerpt': summary})
            except Exception:
                logging.exception('Error retrieving an article from Ars Technica.')
                continue
        return articles[:n]
    except Exception:
        logging.exception('Error: Failed to get Ars Technica articles.')
        return []


def scrape_theverge_articles(category):
    logging.info('Getting The Verge articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get(f'https://www.theverge.com/{category}', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        section = soup.select_one('section')
        titles = section.select('.duet--content-cards--content-card h2')
        summaries = section.select('.duet--content-cards--content-card h2+p')
        articles = [
            {'source': 'The Verge', 'title': titles[0].text.strip(), 'excerpt': summaries[0].text.strip()},
            {'source': 'The Verge', 'title': titles[1].text.strip(), 'excerpt': summaries[1].text.strip()}]
        return articles
    except Exception:
        logging.exception('Error: Failed to get The Verge articles.')
        return []


def scrape_platformer_articles():
    logging.info('Getting Platformer articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.platformer.news/page/2/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if time.day + 1 != now.day:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('.gh-card-excerpt').text.strip()
                articles.append({'source': 'Platformer', 'title': title, 'excerpt': snippet})
            except Exception:
                logging.exception('Error retrieving an article from Platformer.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Platformer articles.')
        return []


def scrape_binsider_articles(category='tech', n=5):
    logging.info('Getting Business Insider articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get(f'https://www.businessinsider.com/{category}', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        for art in soup.select('section.tout-layout.as-river article')[:n]:
            try:
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('div.tout-copy.headline-regular').text.strip()
                articles.append({'source': 'Business Insider', 'title': title, 'excerpt': snippet})
            except Exception:
                logging.exception('Error retrieving an article from Business Insider.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Business Insider articles.')
        return []


def scrape_morningbrew_articles():
    logging.info('Getting Morning Brew articles')
    headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json'
    }
    try:
        url = 'https://singularity.morningbrew.com/graphql'
        payload = "{\"query\":\"query GetTagPage($slug: String!, $domainId: ID!, $limit: Int, $offset: Int, $brandRoot: ID!) {\\n  tagPageV2(slug: $slug, domainId: $domainId, limit: $limit, offset: $offset) {\\n    headerImage {\\n      asset {\\n        _id\\n        url\\n        metadata {\\n          lqip\\n          __typename\\n        }\\n        __typename\\n      }\\n      alt\\n      source\\n      __typename\\n    }\\n    slug {\\n      current\\n      __typename\\n    }\\n    name\\n    description\\n    og {\\n      ...SEO\\n      __typename\\n    }\\n    featuredStories {\\n      ...StoryEditorialPreview\\n      ...StoryBrandedContentPreview\\n      ...CerosEditorialPagePreview\\n      __typename\\n    }\\n    tagStories {\\n      ...StoryEditorialPreview\\n      ...StoryBrandedContentPreview\\n      ...EventPreview\\n      ...CerosPagePreview\\n      ...CerosEditorialPagePreview\\n      ...GatedContentLandingPagePreview\\n      __typename\\n    }\\n    meteorAdContent {\\n      ...MeteorAdContent\\n      __typename\\n    }\\n    __typename\\n  }\\n  BrandRoot(id: $brandRoot) {\\n    _id\\n    ...NewsletterCTA\\n    __typename\\n  }\\n}\\n\\nfragment SEO on OpenGraphProperties {\\n  title\\n  seoTitle\\n  description\\n  noIndex\\n  image {\\n    asset {\\n      _id\\n      url\\n      altText\\n      __typename\\n    }\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment StoryEditorialPreview on StoryEditorial {\\n  __typename\\n  _id\\n  title\\n  subtitle\\n  slug\\n  publishDate\\n  tags {\\n    _id\\n    name\\n    __typename\\n  }\\n  authors {\\n    _id\\n    name\\n    __typename\\n  }\\n  featured\\n  previewActionText\\n  previewDescription\\n  previewHeadline\\n  previewThumbnail {\\n    ...Image\\n    __typename\\n  }\\n  headerImage {\\n    ...ImageWithAlt\\n    __typename\\n  }\\n  brand {\\n    _id\\n    slug\\n    __typename\\n  }\\n  contentType {\\n    contentSubtype\\n    contentType\\n    __typename\\n  }\\n  meteorAdContent {\\n    logoText\\n    partnerLogoUrl\\n    partnerName\\n    __typename\\n  }\\n  inlineMeteorAdvertisement {\\n    company {\\n      name\\n      __typename\\n    }\\n    logoText\\n    __typename\\n  }\\n}\\n\\nfragment Image on Image {\\n  asset {\\n    _id\\n    url\\n    webpUrl\\n    metadata {\\n      lqip\\n      dimensions {\\n        aspectRatio\\n        height\\n        width\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  hotspot {\\n    width\\n    height\\n    x\\n    y\\n    __typename\\n  }\\n  crop {\\n    top\\n    left\\n    bottom\\n    right\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment ImageWithAlt on ImageWithAlt {\\n  alt\\n  asset {\\n    _id\\n    url\\n    webpUrl\\n    metadata {\\n      lqip\\n      dimensions {\\n        aspectRatio\\n        height\\n        width\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  hotspot {\\n    width\\n    height\\n    x\\n    y\\n    __typename\\n  }\\n  crop {\\n    top\\n    left\\n    bottom\\n    right\\n    __typename\\n  }\\n  href\\n  source\\n  __typename\\n}\\n\\nfragment StoryBrandedContentPreview on StoryBrandedContent {\\n  __typename\\n  _id\\n  title\\n  subtitle\\n  slug\\n  publishDate\\n  featured\\n  tags {\\n    _id\\n    name\\n    __typename\\n  }\\n  authors {\\n    _id\\n    name\\n    __typename\\n  }\\n  previewActionText\\n  previewDescription\\n  previewHeadline\\n  previewThumbnail {\\n    ...Image\\n    __typename\\n  }\\n  headerImage {\\n    ...ImageWithAlt\\n    __typename\\n  }\\n  brand {\\n    _id\\n    slug\\n    __typename\\n  }\\n  contentType {\\n    contentSubtype\\n    contentType\\n    __typename\\n  }\\n  meteorAdContent {\\n    logoText\\n    partnerLogoUrl\\n    partnerName\\n    __typename\\n  }\\n  inlineMeteorAdvertisement {\\n    company {\\n      name\\n      __typename\\n    }\\n    logoText\\n    __typename\\n  }\\n}\\n\\nfragment CerosEditorialPagePreview on CerosEditorialPage {\\n  __typename\\n  _id\\n  title\\n  featured\\n  slugObj: slug {\\n    current\\n    __typename\\n  }\\n  publishDate\\n  layout\\n  tags {\\n    _id\\n    name\\n    __typename\\n  }\\n  previewActionText\\n  previewDescription\\n  previewHeadline\\n  previewThumbnail {\\n    ...Image\\n    __typename\\n  }\\n  headerImage {\\n    ...ImageWithAlt\\n    __typename\\n  }\\n  brand {\\n    _id\\n    slug\\n    __typename\\n  }\\n  og {\\n    ...SEO\\n    __typename\\n  }\\n  contentType {\\n    contentSubtype\\n    contentType\\n    __typename\\n  }\\n}\\n\\nfragment EventPreview on Events {\\n  __typename\\n  _id\\n  _type\\n  title\\n  slugObj: slug {\\n    current\\n    __typename\\n  }\\n  eventDate\\n  eventEndDate\\n  eventLocation\\n  type\\n  tags {\\n    _id\\n    name\\n    __typename\\n  }\\n  featured\\n  sponsor\\n  previewSponsorLabel\\n  previewActionText\\n  previewDescription\\n  previewHeadline\\n  previewThumbnail {\\n    ...Image\\n    __typename\\n  }\\n  brand {\\n    _id\\n    slug\\n    __typename\\n  }\\n  og {\\n    ...SEO\\n    __typename\\n  }\\n  contentType {\\n    contentSubtype\\n    contentType\\n    __typename\\n  }\\n}\\n\\nfragment CerosPagePreview on CerosPage {\\n  __typename\\n  _id\\n  slugObj: slug {\\n    current\\n    __typename\\n  }\\n  publishDate\\n  layout\\n  tags {\\n    _id\\n    name\\n    __typename\\n  }\\n  featured\\n  previewActionText\\n  previewDescription\\n  previewHeadline\\n  previewThumbnail {\\n    ...Image\\n    __typename\\n  }\\n  og {\\n    ...SEO\\n    __typename\\n  }\\n  contentType {\\n    contentSubtype\\n    contentType\\n    __typename\\n  }\\n}\\n\\nfragment GatedContentLandingPagePreview on GatedContentLandingPage {\\n  __typename\\n  _id\\n  title\\n  slugObj: slug {\\n    current\\n    __typename\\n  }\\n  tags {\\n    _id\\n    name\\n    __typename\\n  }\\n  previewActionText\\n  previewDescription\\n  previewHeadline\\n  featured\\n  previewThumbnail {\\n    ...Image\\n    __typename\\n  }\\n  primaryImage {\\n    ...ImageWithAltNoSource\\n    __typename\\n  }\\n  newsletter {\\n    _id\\n    slug\\n    __typename\\n  }\\n  contentType {\\n    contentSubtype\\n    contentType\\n    __typename\\n  }\\n  partner {\\n    _id\\n    name\\n    __typename\\n  }\\n  sponsorLanguage\\n}\\n\\nfragment ImageWithAltNoSource on ImageWithAltNoSource {\\n  alt\\n  asset {\\n    _id\\n    url\\n    webpUrl\\n    metadata {\\n      lqip\\n      dimensions {\\n        aspectRatio\\n        height\\n        width\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n  hotspot {\\n    width\\n    height\\n    x\\n    y\\n    __typename\\n  }\\n  crop {\\n    top\\n    left\\n    bottom\\n    right\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment MeteorAdContent on MeteorAdContent {\\n  meteorAdvertisement\\n  logoText\\n  link\\n  content\\n  adImageUrl\\n  adImageLink\\n  disclaimer\\n  partnerLogoUrl\\n  partnerLogoSize\\n  partnerName\\n  disableContent\\n  _id\\n  __typename\\n}\\n\\nfragment NewsletterCTA on BrandRoot {\\n  ctaDescription\\n  ctaHeading\\n  slug\\n  name\\n  __typename\\n}\\n\",\"variables\":{\"domainId\":\"singleton-domain-root-morningbrew\",\"brandRoot\":\"singleton-brand-root-daily\",\"slug\":\"tech\",\"limit\":6}}"
        response = SESSION.post(url, headers=headers, data=payload)
        stories = response.json()['data']['tagPageV2']['tagStories']
        articles = []
        now = datetime.utcnow()
        for i in stories:
            try:
                t = datetime.fromisoformat(i['publishDate'][:-1])
                if not (now - t).days:
                    articles.append({'source': 'Morning Brew', 'title': i['title'], 'excerpt': i['subtitle']})
            except Exception:
                logging.exception('Error retrieving an article from Morning Brew.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Morning Brew articles.')
        return []


def scrape_breitbart_articles(category='tech', n=7):
    logging.info('Getting Breitbart articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get(f'https://breitbart.com/{category}/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article div.tC')[:n]:
            try:
                title = art.select_one('h2 a')
                snippet = art.select_one('div.excerpt')
                if snippet:
                    snippet = snippet.text.strip()
                    t = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                    if (now - t).days:
                        break
                else:
                    r = SESSION.get(title.get('href'))
                    s = BeautifulSoup(r.content, 'html.parser')
                    t = datetime.fromisoformat(s.select_one('.header_byline time').get('datetime')[:-1])
                    if (now - t).days:
                        break
                    snippet = s.select_one('p.subheading').text.strip()
                articles.append({'source': 'Breitbart', 'title': title.text.strip(), 'excerpt': snippet})
            except Exception:
                logging.exception('Error retrieving an article from Breitbart.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Breitbart articles.')
        return []


def scrape_deepnewz_articles():
    # TODO check
    logging.info('Getting DeepNewz articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://deepnewz.com/ai', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        for art in soup.select('main ul[role="list"] div.flex-1'):
            try:
                time = art.select_one('.dn-label-2')
                if 'hour' not in time.text:
                    continue
                title = art.select_one('a.dn-body-2').text.strip()
                articles.append({'source': 'DeepNewz', 'title': title, 'excerpt': ''})
            except:
                logging.exception('Error retrieving an article from DeepNewz.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get DeepNewz articles.')
        return []


def scrape_softzone_articles():
    logging.info('Getting SoftZone articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.softzone.es/noticias/metabits/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article.news-item'):
            try:
                time = art.select_one('li.published-time')
                time = dateparser.parse(time.text) - timedelta(hours=2)
                if (now - time).days:
                    break
                title = art.select_one('h2').text.strip()
                snippet = art.select_one('div.excerpt').text.strip()
                articles.append({'source': 'SoftZone', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from SoftZone.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get SoftZone articles.')
        return []


def scrape_genbeta_articles():
    logging.info('Getting GENBETA articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.genbeta.com/categoria/inteligencia-artificial', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    continue
                title = art.select_one('h2').text.strip()
                snippet = art.select_one('div.abstract-excerpt p').text.strip()
                articles.append({'source': 'GENBETA', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from GENBETA.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get GENBETA articles.')
        return []


def scrape_elpais_articles():
    logging.info('Getting EL PAIS articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://elpais.com/noticias/inteligencia-artificial/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('main article'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = art.select_one('h2').text.strip()
                snippet = art.select_one('p.c_d').text.strip()
                articles.append({'source': 'EL PAIS', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from EL PAIS.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get EL PAIS articles.')
        return []


def scrape_wired_articles():
    logging.info('Getting WIRED articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://es.wired.com/tag/inteligencia-artificial', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('div.summary-item__content'):
            try:
                r = SESSION.get('https://es.wired.com' +  art.select_one('a').get('href'), headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('.summary-item__dek')
                snippet = snippet.text.strip() if snippet is not None else ''
                articles.append({'source': 'WIRED', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from WIRED.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get WIRED articles.')
        return []


def scrape_ainews_articles():
    logging.info('Getting Ai News articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.artificialintelligence-news.com/artificial-intelligence-news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('article'):
            try:
                title = art.select_one('h3 a')
                r = SESSION.get(title.get('href'), headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = title.text.strip()
                excerpt = s.select_one('article div ~ p').text.strip()
                articles.append({'source': 'Ai News', 'title': title, 'excerpt': excerpt})
            except:
                logging.exception('Error retrieving an article from Ai News.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Ai News articles.')
        return []


def scrape_theinformation_articles():
    logging.info('Getting The Information articles')
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'profile.default_content_setting_values.images': 2})
        with webdriver.Chrome(options=options) as driver:
            driver.set_window_state('minimized')
            driver.get('https://www.theinformation.com/technology?view=recent')
            articles = []
            now = datetime.now(timezone.utc)
            art = driver.find_element(By.CSS_SELECTOR, 'article')
            time = art.find_element(By.CSS_SELECTOR, 'time')
            time = re.search('datetime="(.+)"', time.get_attribute('outerHTML')).group(1)
            time = datetime.fromisoformat(time)
            if not (now - time).days:
                title = art.find_element(By.CSS_SELECTOR, 'a h2').text.strip()
                snippet = art.find_element(By.CSS_SELECTOR, 'a h2 + p').text.strip()
                articles.append({'source': 'The Information', 'title': title, 'excerpt': snippet})
            for art in driver.find_elements(By.CSS_SELECTOR, 'main section > div')[:-1]:
                try:
                    time = art.find_element(By.CSS_SELECTOR, 'time')
                    time = re.search('datetime="(.+)"', time.get_attribute('outerHTML')).group(1)
                    time = datetime.fromisoformat(time)
                    if (now - time).days:
                        break
                    title = art.find_element(By.CSS_SELECTOR, 'a h3').text.strip()
                    snippet = art.find_element(By.CSS_SELECTOR, 'a div').text.strip()
                    articles.append({'source': 'The Information', 'title': title, 'excerpt': snippet})
                except:
                    logging.exception('Error retrieving an article from The Information.')
                    continue
            return articles
    except Exception:
        logging.exception('Error: Failed to get The Information articles.')
        return []
    finally:
        driver.quit()


def scrape_xataka_articles():
    logging.info('Getting Xataka articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.xataka.com/categoria/robotica-e-ia', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    break
                title = art.select_one('h2 a').text.strip()
                snippet = art.select_one('.abstract-excerpt p').text.strip()
                articles.append({'source': 'Xataka', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from Xataka.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Xataka articles.')
        return []


def scrape_thedecoder_articles():
    logging.info('Getting The Decoder articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://the-decoder.com/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('article'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = art.select_one('a.link-overlay')
                snippet = art.select_one('.card__content__short p')
                if snippet is None:
                    r = SESSION.get(title.get('href'), headers=headers)
                    s = BeautifulSoup(r.content, 'html.parser')
                    snippet = s.select_one('.entry-content > p')
                articles.append({'source': 'The Decoder', 'title': title.get('aria-label'), 'excerpt': snippet.text.strip()})
            except:
                logging.exception('Error retrieving an article from The Decoder.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get The Decoder articles.')
        return []


def scrape_autogptnews_articles():
    logging.info('Getting AUTOGPT News articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://autogpt.net/category/ai-news/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('#main article'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if (now - time).days:
                    break
                title = art.select_one('h2 a').text.strip()
                snippet = art.select_one('.excerpt').text.strip()
                articles.append({'source': 'AUTOGPT News', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from AUTOGPT News.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get AUTOGPT News articles.')
        return []


def scrape_tomsguide_articles():
    logging.info('Getting tom\'s guide articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.tomsguide.com/ai', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article.search-result'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('p.synopsis').text.strip()
                articles.append({'source': 'tom\'s guide', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from tom\'s guide.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get tom\'s guide articles.')
        return []


def scrape_wsj_articles():
    # TODO check
    logging.info('Getting WSJ articles')
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'profile.default_content_setting_values.images': 2})
        with webdriver.Chrome(options=options) as driver:
            driver.set_window_state('minimized')
            driver.get('https://www.wsj.com/tech/ai', wait_load=False)
            driver.sleep(10)
            articles = []
            now = datetime.utcnow()

            content = driver.find_element(By.CSS, 'iframe[src*="captcha-delivery"], div[data-testid="allesseh"]', timeout=10)

            get_excerpts = []

            for art in driver.find_elements(By.CSS, 'div[data-testid="allesseh"] div[class*="CardLayoutItem"]'):
                try:
                    art.scroll_to()
                    time = art.find_element(By.CSS, 'p[data-testid="timestamp-text"]', timeout=5).text.strip()
                    time = dateparser.parse(time)
                    if (now - time).days > 0:
                        break
                    title = art.find_element(By.CSS, '[data-testid="flexcard-headline"]', timeout=5).text.strip()
                    try:
                        excerpt = art.find_element(By.CSS, 'p[data-testid="flexcard-text"]', timeout=5).text.strip()
                    except NoSuchElementException:
                        url = art.find_element(By.CSS, 'h3 a').get_attribute('href')
                        get_excerpts.append(url)
                    else:
                        articles.append({'source': 'WSJ', 'title': title, 'excerpt': excerpt})
                except Exception:
                    logging.exception('Error retrieving an article from WSJ.')
            for url in get_excerpts:
                try:
                    driver.get(url, wait_load=False)
                    title = driver.find_element(By.CSS, 'h1', timeout=10).text.strip()
                    excerpt = driver.find_element(By.CSS, '.article-header h2', timeout=5).text.strip()
                    articles.append({'source': 'WSJ', 'title': title, 'excerpt': excerpt})
                except Exception:
                    logging.exception('Error retrieving an article from WSJ.')
            return articles
    except Exception:
        logging.exception('Error: Failed to get WSJ articles.')
        return []
    finally:
        driver.quit()


def scrape_reuters_articles(section):
    logging.info('Getting Reuters articles')
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('prefs', {'profile.default_content_setting_values.images': 2})
        with webdriver.Chrome(options=options) as driver:
            driver.set_window_state('minimized')
            driver.get(f'https://www.reuters.com/{section}', wait_load=False)
            driver.sleep(10)
            articles = []
            now = datetime.utcnow()

            content = driver.find_element(By.CSS, 'iframe[src*="captcha-delivery"], main#main-content', timeout=10)

            urls = []
            arts = driver.find_elements(By.CSS, 'li[class*="story-card"]')
            if not arts:
                arts = driver.find_elements(By.CSS, 'div[data-testid="MediaStoryCard"]')
            for art in arts:
                    time = art.find_element(By.CSS, 'time', timeout=5)
                    time = datetime.fromisoformat(time.get_dom_attribute('datetime')[:-1])
                    if (now - time).days:
                        continue
                    url = art.find_element(By.CSS, 'a[data-testid="TitleLink"], a[data-testid="Heading"], h3 a[data-testid="Link"]').get_attribute('href')
                    urls.append(url)
            for url in urls:
                try:
                    driver.get(url, wait_load=False)
                    title = driver.find_element(By.CSS, 'h1[data-testid="Heading"]', timeout=5).text.strip()
                    snippet = driver.find_element(By.CSS, 'div[data-testid="paragraph-0"]', timeout=5).text.strip()
                    snippet = snippet.split('(Reuters) - ')[-1].replace('New Tab, opens new tab', '')
                    articles.append({'source': 'Reuters', 'title': title, 'excerpt': snippet})
                except Exception:
                    logging.exception('Error retrieving an article from Reuters.')
                    continue
            articles_unique = []
            for art in articles:
                if art not in articles_unique:
                    articles_unique.append(art)
            return articles_unique
    except Exception:
        logging.exception('Error: Failed to get Reuters articles.')
        return []
    finally:
        driver.quit()


def scrape_livescience_articles():
    logging.info('Getting Live Science articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.livescience.com/technology/artificial-intelligence', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('div.listingResult[data-page]'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('p.synopsis').text.strip()
                articles.append({'source': 'Live Science', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from Live Science.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Live Science articles.')
        return []


def scrape_techradar_articles():
    logging.info('Getting TechRadar articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.techradar.com/computing/software/artificial-intelligence', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        for art in soup.select('article.search-result'):
            try:
                time = datetime.fromisoformat(art.select_one('time').get('datetime')[:-1])
                if (now - time).days:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('p.synopsis').text.strip().replace('Updated\n', '')
                articles.append({'source': 'TechRadar', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from TechRadar.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get TechRadar articles.')
        return []


def scrape_infobae_articles():
    logging.info('Getting infobae articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.infobae.com/tag/inteligencia-artificial/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.utcnow()
        s = soup.select_one('script#fusion-metadata').text
        j = json.loads(s[s.index('Fusion.globalContent=') + 21: s.index('Fusion.globalContentConfig=') - 1])
        if not 'content_elements' in j:
            j = json.loads(s[s.index('Fusion.contentCache=') + 20: s.index('Fusion.layout=') - 1])
            feed = j['content-feed']
            j = feed[list(feed.keys())[0]]['data']
        for art in j['content_elements']:
            try:
                if 'display_date' in art:
                    time = datetime.fromisoformat((d := art['display_date'])[:d.index('.') if '.' in d else -1])
                else:
                    time = datetime.fromisoformat((d := art['last_updated_date'])[:d.index('.') if '.' in d else -1])
                if (now - time).days:
                    break
                title = art['headlines']['basic'].strip()
                snippet = art['description']['basic'].strip()
                articles.append({'source': 'infobae', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from infobae.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get infobae articles.')
        return []


def scrape_venturebeat_articles():
    logging.info('Getting VentureBeat articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://venturebeat.com/category/ai/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('article'):
            try:
                url = art.select_one('a')
                r = SESSION.get(url.get('href'), headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = s.select_one('time')
                if time is None:
                    continue
                time = datetime.fromisoformat(time.get('datetime'))
                if (now - time).days:
                    if 'ArticleListing' in art.get('class'):
                        break
                    else:
                        continue
                title = art.select_one('h2').text.strip()
                snippet = s.select_one('.article-content > p').text.strip()
                articles.append({'source': 'VentureBeat', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from VentureBeat.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get VentureBeat articles.')
        return []


def scrape_mittr_articles():
    logging.info('Getting MIT Technology Review articles')
    headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://www.technologyreview.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.technologyreview.com/',
        'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://wp.technologyreview.com/wp-json/irving/v1/data/topic_feed?page=1&orderBy=date&topic=9&requestType=topic', headers=headers)
        arts = [(j := response.json()[0])['featuredPost']] + j['feedPosts']
        articles = []
        now = datetime.now()
        for art in arts:
            try:
                time = art['config']['link'][33:43]
                time = dateparser.parse(time)
                if (now - time).days > 1:
                    break
                title = art['config']['hed'].strip()
                snippet = BeautifulSoup(art['config']['dek'], 'html.parser').text.strip()
                articles.append({'source': 'MIT Technology Review', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from MIT Technology Review.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get MIT Technology Review articles.')
        return []


def scrape_aim_articles():
    logging.info('Getting Analytics India Magazine articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://analyticsindiamag.com/ai-news-updates/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('[data-elementor-type="archive"] article'):
            try:
                time = art.select_one('.elementor-post-date').text.strip()
                time = dateparser.parse(time)
                if (now - time).days > 1:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('.elementor-post__excerpt').text.strip()
                articles.append({'source': 'Analytics India Magazine', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from Analytics India Magazine.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get Analytics India Magazine articles.')
        return []


def scrape_theregister_articles():
    logging.info('Getting The Register articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.theregister.com/Tag/AI/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('article'):
            try:
                time = art.select_one('.time_stamp').get('data-epoch')
                time = datetime.fromtimestamp(int(time))
                if (now - time).days > 0:
                    break
                title = art.select_one('h4').text.strip()
                snippet = art.select_one('div.standfirst')
                label = snippet.select_one('.label')
                if label:
                    label.decompose()
                snippet = snippet.text.strip()
                articles.append({'source': 'The Register', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from The Register.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get The Register articles.')
        return []


def scrape_siliconangle_articles():
    logging.info('Getting SiliconANGLE articles')
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://siliconangle.com/category/ai/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': USER_AGENT,
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    try:
        response = SESSION.get('https://siliconangle.com/wp-admin/admin-ajax.php?action=alm_query_posts&nonce=a655aaa5f4&query_type=standard&id=exclude_cube_coverage&post_id=369&slug=ai&canonical_url=https%3A%2F%2Fsiliconangle.com%2Fcategory%2Fai%2F&posts_per_page=10&page=0&offset=0&post_type%5B%5D=post&repeater=default&seo_start_page=1&preloaded=false&order=DESC&orderby=date', headers=headers)
        soup = BeautifulSoup(response.json()['html'], 'html.parser')
        articles = []
        now = datetime.now() + timedelta(minutes=5)
        for art in soup.select('li'):
            try:
                time = art.select_one('p.post-meta')
                time = dateparser.parse(time.text.split('-')[-1])
                if (now - time).days > 0:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('p.post-excerpt').text.strip()
                articles.append({'source': 'SiliconANGLE', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from SiliconANGLE.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get SiliconANGLE articles.')
        return []


def scrape_digitaltrends_articles():
    logging.info('Getting digitaltrends articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.digitaltrends.com/computing/artificial-intelligence/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        script = soup.select_one('script[type="application/ld+json"]')
        j = json.loads(script.text)
        for art in j[0]['mainEntity']['itemListElement']:
            try:
                r = SESSION.get(art['url'], headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = datetime.fromisoformat(s.select_one('time').get('datetime'))
                if (now - time).days > 0:
                    break
                title = s.select_one('h1').text.strip()
                snippet = s.select_one('article p').text.strip()
                articles.append({'source': 'digitaltrends', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from digitaltrends.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get digitaltrends articles.')
        return []


def scrape_newscientist_articles():
    logging.info('Getting NewScientist articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.newscientist.com/subject/technology/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('a.CardLink'):
            try:
                r = SESSION.get('https://www.newscientist.com' + art.get('href'), headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                time = s.select_one('.ArticleHeader__Date').text.strip()
                time = dateparser.parse(time)
                if (now - time).days > 1:
                    break
                title = s.select_one('h1').text.strip()
                snippet = s.select_one('.ArticleHeader__Copy').text.strip()
                articles.append({'source': 'NewScientist', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from NewScientist.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get NewScientist articles.')
        return []


def scrape_zdnet_articles():
    logging.info('Getting ZDNET articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://www.zdnet.com/topic/artificial-intelligence/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now() + timedelta(minutes=5)
        for art in soup.select('.c-listingDefault_item'):
            try:
                time = art.select_one('.c-listingDefault_pubDate').text.strip()
                time = dateparser.parse(time)
                if (now - time).days > 0:
                    break
                title = art.select_one('h3').text.strip()
                snippet = art.select_one('.c-listingDefault_description').text.strip()
                articles.append({'source': 'ZDNET', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from ZDNET.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get ZDNET articles.')
        return []


def scrape_ieeespectrum_articles():
    logging.info('Getting IEEE Spectrum articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://spectrum.ieee.org/tag/artificial-intelligence', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now() + timedelta(minutes=5)
        for art in soup.select('article'):
            try:
                time = art.select_one('div.social-date').text.strip()
                time = dateparser.parse(time)
                if (now - time).days > 0:
                    break
                title = art.select_one('h2').text.strip()
                snippet = art.select_one('h3').text.strip()
                articles.append({'source': 'IEEE Spectrum', 'title': title, 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from IEEE Spectrum.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get IEEE Spectrum articles.')
        return []


def scrape_tnw_articles():
    logging.info('Getting TNW articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://thenextweb.com/deep-tech', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now() + timedelta(minutes=5)
        for art in soup.select('article'):
            try:
                time = art.select_one('li.c-meta__item:nth-child(2)').text.strip()
                time = dateparser.parse(time)
                if (now - time).days > 0:
                    break
                title = art.select_one('h2 a')
                r = SESSION.get('https://thenextweb.com' + title.get('href'), headers=headers)
                s = BeautifulSoup(r.content, 'html.parser')
                snippet = s.select_one('.c-header__intro').text.strip()
                articles.append({'source': 'TNW', 'title': title.text.strip(), 'excerpt': snippet})
            except:
                logging.exception('Error retrieving an article from TNW.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get TNW articles.')
        return []


def scrape_cleantechnica_articles(n=10):
    logging.info('Getting CleanTechnica articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://cleantechnica.com/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now(timezone.utc)
        for art in soup.select('article')[:n]:
            try:
                title = art.select_one('header').text.strip()
                snippet = art.select_one('div.cm-entry-summary').text.strip()
                snippet = snippet.replace('   … [continued]', '…')
                t = datetime.fromisoformat(art.select_one('time').get('datetime'))
                if (now - t).days:
                    break
                articles.append({'source': 'CleanTechnica', 'title': title, 'excerpt': snippet})
            except Exception:
                logging.exception('Error retrieving a CleanTechnica article.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get CleanTechnica articles.')
        return []


def scrape_renews_articles(n=10):
    logging.info('Getting reNEWS articles')
    headers = {
        'User-Agent': USER_AGENT
    }
    try:
        response = SESSION.get('https://renews.biz/', headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        now = datetime.now()
        for art in soup.select('.hidden-xs .module-timeline div.articles article, article.linkbox')[:n]:
            try:
                t = art.select_one('span[itemprop="dateCreated"], span.published').text.strip()
                t = datetime.strptime(t, '%d %B %Y %M:%S')
                if (now - t).days:
                    break
                title = art.select_one('h3')
                if title:
                    title = title.text.strip()
                    snippet = art.select_one('span.text')
                    if snippet:
                        snippet = snippet.text.strip()
                    else:
                        url = art.select_one('a').get('href')
                        r = SESSION.get('https://renews.biz' + url, headers=headers)
                        s = BeautifulSoup(r.content, 'html.parser')
                        snippet = s.select_one('div.overlay p').text.strip()
                else:
                    title = art.select_one('h2').text.strip()
                    snippet = art.select_one('div.overlay p').text.strip()
                articles.append({'source': 'reNEWS', 'title': title, 'excerpt': snippet})
            except Exception:
                logging.exception('Error retrieving a reNEWS article.')
                continue
        return articles
    except Exception:
        logging.exception('Error: Failed to get reNEWS articles.')
        return []


def scrape_offshore_articles(n=10):
    logging.info('Getting Offshore articles')
    headers = {
        'User-Agent': USER_AGENT,
        'x-tenant-key': 'ebm_os',
        'content-type': 'application/json'
    }
    payload = "{\"query\":\"query getWebsiteLayoutPage(\\n  $alias: String!\\n  $useCache: Boolean\\n  $preview: Boolean\\n  $cacheKey: String\\n) {\\n  getWebsiteLayoutPage(\\n    input: { alias: $alias, useCache: $useCache, preview: $preview, cacheKey: $cacheKey }\\n  ) {\\n    id\\n    name\\n    primaryGrid\\n    secondaryGrid\\n    pageData\\n    cache\\n    layoutType {\\n      alias\\n      contentType\\n      type\\n      propagate\\n      key\\n    }\\n    loadMoreType {\\n      type\\n    }\\n    excludeAds {\\n      welcomeAd\\n      stickyLeaderboardAd\\n      contentBodyNativeAd\\n      contentBodyEmbedAd\\n      contentListNativeAd\\n      reskinAd\\n    }\\n    created\\n    usedContentIds\\n    usedIssueIds\\n  }\\n}\",\"variables\":{\"alias\":\"/renewable-energy\",\"useCache\":true,\"preview\":false,\"cacheKey\":\"v2.4\"}}"
    try:
        response = SESSION.post('https://aerilon.graphql.aspire-ebm.com/', headers=headers, data=payload)
        articles = []
        now = datetime.now()
        rows = response.json()['data']['getWebsiteLayoutPage']['primaryGrid']['rows']
        for r in rows:
            for c in r['columns']:
                for b in c['blocks']:
                    if b['type'] == 'content_list':
                        for d in b['data']['items']:
                            t = datetime.fromtimestamp(d['published'] / 1000)
                            if (now - t).days:
                                return articles[:n]
                            title = d['name']
                            snippet = d['teaser']
                            articles.append({'source': 'Offshore', 'title': title, 'excerpt': snippet})
        return articles[:n]
    except Exception:
        logging.exception('Error: Failed to get Offshore articles.')
        return articles[:n]


def generate_stories(data):
    if not data:
        return []
    data = json.dumps(data)
    data = data.replace('\xa0', ' ')
    stories = generate_stories_openai(data)
    try:
        return json.loads(stories)['stories']
    except:
        logging.exception(f'Error: Failed to load stories from chatgpt to json.')
        return []


def get_ai_news():
    articles1 = scrape_techcrunch_articles('artificial-intelligence')
    articles2 = scrape_techcrunch_articles('social')
    articles3 = scrape_techcrunch_articles('media-entertainment')
    articles4 = scrape_arstechnica_articles('gadgets')
    articles5 = scrape_theverge_articles('tech')
    articles6 = scrape_theverge_articles('entertainment')
    articles7 = scrape_platformer_articles()
    articles8 = scrape_binsider_articles()
    articles9 = scrape_morningbrew_articles()
    articles10 = scrape_breitbart_articles()
    articles11 = scrape_deepnewz_articles()
    articles12 = scrape_softzone_articles()
    articles13 = scrape_genbeta_articles()
    articles14 = scrape_elpais_articles()
    articles15 = scrape_wired_articles()
    articles16 = scrape_ainews_articles()
    articles17 = scrape_theinformation_articles()
    articles18 = scrape_xataka_articles()
    articles19 = scrape_thedecoder_articles()
    articles20 = scrape_autogptnews_articles()
    articles21 = scrape_tomsguide_articles()
    articles22 = scrape_wsj_articles()
    articles23 = scrape_reuters_articles('technology/artificial-intelligence')
    articles24 = scrape_livescience_articles()
    articles25 = scrape_techradar_articles()
    articles26 = scrape_infobae_articles()
    articles27 = scrape_venturebeat_articles()
    articles28 = scrape_mittr_articles()
    articles29 = scrape_aim_articles()
    articles30 = scrape_theregister_articles()
    articles31 = scrape_siliconangle_articles()
    articles32 = scrape_digitaltrends_articles()
    articles33 = scrape_newscientist_articles()
    articles34 = scrape_zdnet_articles()
    articles35 = scrape_ieeespectrum_articles()
    articles36 = scrape_tnw_articles()
    articles_en = sum([
        articles1, articles2, articles3, articles4, articles5, articles6, articles7, articles8, articles9, articles10,
        articles11, articles16, articles17, articles19, articles20,
        articles21, articles22, articles23, articles24, articles25, articles27, articles28, articles29, articles30,
        articles31, articles32, articles33, articles34, articles35, articles36], []
    )
    articles_es = sum([
        articles12, articles13, articles14, articles15, articles18, articles26], []
    )
    with open(os.path.join(os.path.dirname(__file__), 'ai_articles.json'), 'w', encoding='utf-8') as f:
        json.dump(articles_en + articles_es, f, indent=4)
    logging.info('Articles saved to ai_articles.json')
    # with open(os.path.join(os.path.dirname(__file__), 'ai_articles.json'), encoding='utf-8') as f:
        # articles = json.load(f)
    # articles_en, articles_es = articles[:-12], articles[-12:]
    n = k // 50 + 1 if (k := len(articles_en)) % 50 else k // 50
    stories = []
    for i in range(n):
        logging.info(f'Generating news stories {i + 1}/{n + 1}')
        stories.extend(generate_stories(articles_en[50 * i: 50 * (i + 1)]))
    
    stories_dict = {}
    for st in stories:
        if stories_dict.get(st['source']):
            stories_dict[st['source']].append(st['story'])
        else:
            stories_dict[st['source']] = [st['story']]
    with open(os.path.join(os.path.dirname(__file__), 'ai_stories.json'), 'w', encoding='utf-8') as f:
        json.dump(stories_dict, f, indent=4)

    logging.info(f'Generating news stories {n + 1}/{n + 1}')
    stories_es = generate_stories(articles_es)

    stories_es_dict = {}
    for st in stories_es:
        if stories_es_dict.get(st['source']):
            stories_es_dict[st['source']].append(st['story'])
        else:
            stories_es_dict[st['source']] = [st['story']]
    with open(os.path.join(os.path.dirname(__file__), 'ai_stories_es.json'), 'w', encoding='utf-8') as f:
        json.dump(stories_es_dict, f, indent=4)
    logging.info('Stories saved to ai_stories.json and ai_stories_es.json')

    return stories_dict, stories_es_dict


def get_econ_news():
    articles1 = scrape_scmp_articles()
    articles2 = scrape_ft_articles()
    articles3 = scrape_reuters_articles('markets/asia')
    articles4 = scrape_cnn_articles()
    articles5 = scrape_cna_articles()
    articles6 = scrape_pvtech_articles()
    articles7 = scrape_rew_articles()
    articles8 = scrape_esn_articles()
    articles9 = scrape_logisticsmanagement_articles()
    articles10 = scrape_supplychaindive_articles()
    articles11 = scrape_maersk_articles()
    articles12 = scrape_freightwaves_articles()
    articles_en = sum([
        articles1, articles2, articles3, articles4, articles5, articles6, articles7, articles8, articles9, articles10,
        articles11, articles12,], []
    )
    with open(os.path.join(os.path.dirname(__file__), 'econ_articles.json'), 'w', encoding='utf-8') as f:
        json.dump(articles_en, f, indent=4)
    logging.info('Articles saved to econ_articles.json')
    n = k // 50 + 1 if (k := len(articles_en)) % 50 else k // 50
    stories = []
    for i in range(n):
        logging.info(f'Generating news stories {i + 1}/{n}')
        stories.extend(generate_stories(articles_en[50 * i: 50 * (i + 1)]))

    stories_dict = {}
    for st in stories:
        if stories_dict.get(st['source']):
            stories_dict[st['source']].append(st['story'])
        else:
            stories_dict[st['source']] = [st['story']]
    with open(os.path.join(os.path.dirname(__file__), 'econ_stories.json'), 'w', encoding='utf-8') as f:
        json.dump(stories_dict, f, indent=4)

    return stories_dict


def make_podcast(stories, topic, filename, intro=True, outro='es'):

    logging.info(f'Making {topic} podcast.')
    news = ''
    if intro:
        news += f'These are the {topic} news for {datetime.today().strftime("%A, %B %#d")}\n'

    headers = [
        'Here are the latest trending stories from ',
        'Discover the most recent buzzworthy stories from ',
        'Explore the current hot topics making waves on ',
        'Stay updated with the freshest trending stories from ',
        'Catch up on the newest and most talked-about stories from ',
        'Dive into the latest trending narratives featured on ',
        'Uncover the trending headlines shaping discussions on ',
        'Get the scoop on the most recent stories gaining traction on ',
        'Check out the newest updates and trends from ',
        'Stay in the loop with the latest stories making headlines on ',
    ]
    headers_es = [
        'Aquí están las últimas historias de tendencia de ',
        'Descubre las historias más recientes y populares de ',
        'Explora los temas candentes actuales que están causando sensación en ',
        'Mantente actualizado con las historias de tendencia más frescas de ',
        'Ponte al día con las historias más nuevas y comentadas de ',
        'Sumérgete en las últimas narrativas de tendencia presentadas en ',
        'Descubre los titulares de tendencia que están dando forma a las discusiones en ',
        'Entérate de las historias más recientes que están ganando tracción en ',
        'Consulta las actualizaciones y tendencias más nuevas de ',
        'Mantente al tanto de las últimas historias que están haciendo titulares en '
    ]

    for source in stories:
        head = headers_es if source in ['SoftZone', 'GENBETA', 'EL PAIS', 'WIRED', 'Xataka', 'infobae'] else headers
        news += f'\n{choice(head)}{source}:\n'
        if len(stories[source]) == 1:
            news += f'{stories[source][0].lstrip(".")}\n'
        else:
            for i, story in enumerate(stories[source]):
                news += f'{i + 1}. {story.lstrip(".")}\n'
    
    if outro:
        if outro == 'en':
            news += '\nThat was what I had for you today. I wish you a great day and you will hear from me again tomorrow.'
        elif outro == 'es':
            news += '\nEsto es lo que tenía para ti hoy. Te deseo un gran día y volverás a saber de mí mañana.'

    with open(os.path.join(os.path.dirname(__file__), filename), 'w', encoding='utf-8') as f:
        f.write(news)
    logging.info(f'Podcast text saved to {filename}')

    return news


def translate(text, topic, lang='spanish'):
    lines = text.split('\n')
    chunks = ceil(len(text) / 50000)
    chunk_size = ceil(len(lines) / chunks)
    output = ''
    for i in range(chunks):
        chunk = lines[i * chunk_size: i * chunk_size + chunk_size]
        chunk = '\n'.join(chunk)
        output += translate_openai(chunk, lang) + '\n'
    with open(os.path.join(os.path.dirname(__file__), f'{topic}_{lang}_news.txt'), 'w', encoding='utf-8') as f:
        f.write(output)
    return output


if __name__ == '__main__':

    logging.basicConfig(
        level = logging.INFO,
        format = '%(asctime)s [%(levelname)s] %(message)s',
        handlers = [
            # logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log.txt'), mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # main()
