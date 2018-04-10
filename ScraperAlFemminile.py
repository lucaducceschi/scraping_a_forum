
# coding: utf-8

# In[146]:


import requests
from bs4 import BeautifulSoup
import re
import sched, time
url_prova = "https://gravidanza.alfemminile.com/forum/dosaggi-ormonali-fd5712881"
html_prova = requests.get(url_prova).text


# In[52]:


# this returns the html of a page in a string format. 
def get_raw_html(url_):
    return requests.get(url_).text

some_raw_html = get_raw_html(url_prova)


# In[138]:


# this takes an html from the forum and parses it to extract data:
# title, main post, autohr, timestamp. The output is a dictionary

def get_first_post_and_replies(some_html):
    soup = BeautifulSoup(some_html,"lxml")
    all_replies = soup.find_all("div", class_="af-post")
    out_ = {}
    first_post = {}
    first_post["post_title"] = soup.find("h1").get_text().strip()
    first_post["post_author"] = soup.find("span", class_="user-name-value").get_text().strip()
    first_post["post_date"] = soup.find("span", class_="date")['title']
    first_post["post_message"] = soup.find("div", class_="af-post-message").find("p", class_="af-message").get_text().strip()
    out_["main_post"] = first_post
    replies = get_replies(all_replies)
    for i in replies.keys():
        out_[i] = replies[i]
    
    return out_
    



# In[133]:


# This takes care of the replies in the forum

def get_replies(replies_result_set):
    all_reps_dict = {}
    for i in replies_result_set[1:]:
        data_ = {}
        data_["user_info"] = i.find("span", class_="user-name-value").get_text().strip()
        data_["date"] = i.find("span", class_="date")["title"]
        data_["reply_post"] = i.find("div", class_="af-post-message").find("p", class_="af-message").get_text().strip()
        if i.find("div", class_="af-forum-quote") is not None:
            data_["quote"] = (i.find("span", class_="username").get_text().strip(),
                              i.find("p", class_="af-forum-quote-content").get_text().strip())
        all_reps_dict[i.attrs["id"]] = data_
    return all_reps_dict


# In[2]:


# in case you want to write the text and just the text (no user, time, etc.)

def just_write_text(dictionary_of_results, filename="out.txt"):
    # if you don't specify a name for the file, the only file generated will be
    # "out.txt"; you can pass to the function something dinamically
    # generated; I used the title of the post, for example, but an ID of any kind
    # would do;
    
    out_file = open(filename, "w", encoding="utf8")
    out_file.write(dictionary_of_results["main_post"]["post_title"]+"\n\n")
    out_file.write(dictionary_of_results["main_post"]["post_message"]+"\n\n")
    for i in dictionary_of_results.keys():
        if re.search("af-post-[0-9]+", i):
            out_file.write(dictionary_of_results[i]['reply_post']+"\n\n")
    print("writing file ...")
    out_file.close()


# In[175]:


# this generates some "topic" urls

def generate_urls_al_femminile():
    list_of_all_urls = []
    base_url = ".alfemminile.com/forum/all/p"
    list_of_subjects = ["societa", "gravidanza", "neonato", "amore", "sessualita", "dieta", "bellezza"]
    for i in list_of_subjects:
        for j in range(1,31):
            list_of_all_urls.append(r"https://"+i+base_url+str(j))
    return list_of_all_urls
    


# In[1]:


# this collects the links in alle the urls generated above
# when you use this, be gentle with the server and don't be so greedy
# consider using a scheduler to end requests without flooding the forum

def scrape_links(list_of_base_links):
    links_to_posts= []
    for i in list_of_base_links:
        res_set_bs = BeautifulSoup(requests.get(i).text,"lxml").find_all("div","af-thread-item")
        links_in_page = [j.find("a")["href"] for j in res_set_bs]
        links_to_posts.extend(links_in_page)
    return links_to_posts    


# ## Just an example on how to use the link scraper

# In[212]:


some_urls = generate_urls_al_femminile()
all_the_links_i_can = scrape_links(some_urls)


with open("af-posts-urls.txt", "w") as out_file:
    for i in all_the_links_i_can:
        out_file.write(i+"\n")
    out_file.close()


# In[234]:


# another example on how to "schedule" some operations. I'm just using 
# a time.sleep() to control how frequently I'm sending a request. 
# If you are serious abount scraping, keep in mind that it's a good idea
# to add an IP rotation to your routine and to check if you are compliant 
# with the robot.txt file of the forum

sample_links = all_the_links_i_can[25:30]
count_urls =[]
pages = []
while len(sample_links)!= len(count_urls):
    for i in sample_links:
        count_urls.append(i)
        print("dealing with url nr: ", len(count_urls))
        pages.append(get_first_post_and_replies(get_raw_html(i)))
        #### Delay for 20 seconds ####
        time.sleep(10)
 
  
    


# In[244]:


import os
os.chdir("Alcuni_post_da_AF/")


# In[247]:


for i in pages:
    just_write_text(i, i["main_post"]["post_title"])

