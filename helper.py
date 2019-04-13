import datetime
import re


def remove_spaces_commas(s_in):
    """Remove spaces and commas from a string"""
    s_out = ''
    for i in range(len(s_in)):
        if (s_in[i] != ',' and s_in[i] != ' '):
            s_out += s_in[i]
    return s_out
def media_url_to_img_url(murl, filename):

    murl_elements = murl.split('/')

    if ('' == murl_elements[-1] or '\n' == murl_elements[-1]):
        del murl_elements[-1]
    
    # print(murl_elements)
    
    cur_month = str(datetime.datetime.now().month)
    if (len(cur_month) < 2):
        cur_month = '0'+cur_month
    iurl = '/'.join(murl_elements[:-1])+'/wp-content/uploads/'+str(datetime.datetime.now().year)+'/'+str(cur_month)+'/'+filename
    return iurl
def replace_dash_w_colon(s):
    r = ''
    for i in range(len(s)):
        if (s[i] == '-'):
            r += s[i]
        else:
            r += ':'

def prepend(article_txt_file, image_txt):
    """prepend image_txt to the article_txt_file"""
    src=open(article_txt_file,"r")
    content=src.readlines()
    # print(content)
    # print()
    content.insert(0,image_txt+'\n') 
    src.close()
    for i in range(len(content)):
        content[i] = re.sub(u'\u2019',"'",content[i])
        content[i] = str(content[i])
    src=open(article_txt_file,"w")
    src.writelines(content)
    src.close()

def check_content(list_of_strings):
    """make sure all strings in list are non-empty"""
    for any_string in list_of_strings:
        if (any_string == '' or any_string == None):
            print('error: missing field')

def check_columns(s_df, cols):
    """verify that all columns in 'cols' are columns of s_df"""
    for col in cols:
        if (not col in s_df.columns):
            print('error: missing budget column "'+col+'", exiting program')
            exit(0)
