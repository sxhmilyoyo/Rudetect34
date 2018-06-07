from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json
from bs4 import BeautifulSoup
# from pyvirtualdisplay import Display


def tweets_crawler(query,name,max_number=10000):
    print query
    # display = Display(visible=0, size=(800, 600))
    # display.start()
    try:
        driver = webdriver.Chrome()
        driver.get("https://twitter.com/search?f=tweets&l=en&q="+query+"&src=typd")

    except:
        driver = webdriver.Chrome('./chrome_driver/chromedriver')
        driver.get("https://twitter.com/search?f=tweets&l=en&q="+query+"&src=typd")
    # driver = init_phantomjs_driver()
    print 'chrome started'
    time.sleep(2)
    # driver.get_screenshot_as_file('test.png')
    driver.find_element_by_class_name('SearchNavigation').click()
    time.sleep(2)
    item_id_set=set()
    count=5
    current=0
    error=10
    tweets_collection=[]
    while(True):
        # print 'in'
        ActionChains(driver).key_down(Keys.END).perform()
        # ActionChains(driver).key_down(Keys.SPACE).perform()
        time.sleep(2)
        count-=1
        items=driver.find_elements_by_css_selector('li[data-item-type*="tweet"]')
        if len(items)>max_number:
        # Keys.-
            break
        print len(items)-current
        if len(items)-current==0:
            error-=1;
            print 'error happened'
            print 'write html'
            with open(name+'_source_page.html', 'w') as source_file:
                source_file.write(driver.page_source.encode('utf-8'))

            html = driver.page_source
            soup = BeautifulSoup(html,'lxml')

            # driver.close()
            # display.stop()
            items=soup.find_all('li',{'data-item-type':'tweet'})
            print len(items)


            for index,i in enumerate(items):
                print 'get tweet',index
                tweet_info={}

                # print i.text
                # print i.get_attribute('innerHTML')
                # print i.get_attribute('data-item-id')
                div=i.find('div',"tweet")
                # print div.get_attribute('data-tweet-id')
                tweet_id=div['data-tweet-id']
                # print div.get_attribute('data-permalink-path')
                permalink_path=div['data-permalink-path']
                # print div.get_attribute('data-screen-name')
                user_screen_name=div['data-screen-name']

                # print div.get_attribute('data-name')
                user_name=div['data-name']
                # print div.get_attribute('data-user-id')
                user_id=div['data-user-id']

                # print i.find_element_by_class_name('stream-item-header').find_element_by_class_name('time').find_element_by_tag_name('a').text#.get_attribute('data-original-title')
                try:
                    post_time=i.find('div','stream-item-header').find('small','time').find('a')['title']
                except:
                    post_time=''
                # print i.find_element_by_class_name('stream-item-header').find_element_by_class_name('time').find_element_by_tag_name('a').find_element_by_tag_name('span').get_attribute('data-time')
                try:
                    data_time=i.find('div','stream-item-header').find('small','time').find('a').find('span')['data-time']
                except:
                    data_time=''
                # print i.find_element_by_class_name('js-tweet-text-container').text
                tweet_content=i.find('div','js-tweet-text-container').text
                # print content
                media_info=''
                media_link=''
                try:
                    # print i.find_element_by_class_name('js-media-container').find_element_by_class_name('js-macaw-cards-iframe-container').get_attribute('data-card-url')
                    media_info=i.find_element_by_class_name('js-media-container').text
                    media_link=i.find_element_by_class_name('js-media-container').find_element_by_class_name('js-macaw-cards-iframe-container').get_attribute('data-card-url')
                    # break
                except:
                    pass
                # print ''
                tweet_info['tweet_id']=tweet_id
                tweet_info['permalink_path']=permalink_path
                tweet_info['user_screen_name']=user_screen_name
                tweet_info['user_name']=user_name
                tweet_info['user_id']=user_id
                tweet_info['tweet_content']=tweet_content
                tweet_info['media_info']=media_info
                tweet_info['media_link']=media_link
                tweet_info['post_time']=post_time
                tweet_info['data_time']=data_time
                # print tweet_info
                tweets_collection.append(tweet_info)
            print 'write json'
            with open(name+'.json', 'w') as outfile:
                json.dump(tweets_collection, outfile, indent=4, sort_keys=True, separators=(',', ':'))
                # break
            print 'Total:',len(items)
        else:
            error=10;
        if error<=0:
            # driver.get_screenshot_as_file('test_end.png')
            print 'error times exceed'
            break
        current=len(items)
    print 'done'

    driver.close()

    time.sleep(1)
    # driver.close()
    return tweets_collection

if __name__ == '__main__':

    tweets_crawler("trump is fool",'trump_test')
