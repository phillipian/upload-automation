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
    # if there are many dashes in a row, remove all but 1
    new_filename = ''
    for i in range(len(filename)):
        if filename[i] != '-':
            new_filename += filename[i]
        else:
            if filename[i+1] == '-': # if the next char is also -, don't add it
                continue
            else:
                new_filename += filename[i]

    filename = new_filename

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
def deprepend(article_txt_file):
    """remove and return first line from article_txt_file"""
    src=open(article_txt_file,"r")
    content=src.readlines()
    src.close()
    first_line = content[0]
    del content[0]
    src=open(article_txt_file,"w")
    src.writelines(content)
    src.close()
    return first_line
    
def prepend(article_txt_file, image_txt):
    """prepend image_txt to the article_txt_file"""
    src=open(article_txt_file,"r")
    content=src.readlines()
    # print(content)
    # print()
    content.insert(0,image_txt+'\n') 
    src.close()
    for i in range(len(content)):
        content[i] = re.sub(u'\u2018',"'",content[i])
        content[i] = re.sub(u'\u2019',"'",content[i])
        content[i] = re.sub(u'\u201c','"',content[i])
        content[i] = re.sub(u'\u201d','"',content[i])
        content[i] = re.sub(u'\u2013','-',content[i])
        content[i] = str(content[i])
    src=open(article_txt_file,"w")
    src.writelines(content)
    src.close()
def add_line_breaks(article_txt_file):
    """add extra \n after every line for better readability"""
    content = ''
    with open(article_txt_file,"r") as artic:
        for line in artic:
            content += line+'\n'
    with open(article_txt_file,"w") as artic:
        artic.write(content)
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
            
def fix_characters(input_string):
    #Fixes the weird characters with dashes and quotes
    input_string = re.sub(u'\u2018',"'", input_string)
    input_string = re.sub(u'\u2019',"'",input_string)
    input_string = re.sub(u'\u201c','"',input_string)
    input_string = re.sub(u'\u201d','"',input_string)
    input_string = re.sub(u'\u2013','-',input_string)
    input_string = re.sub(u'\u2026', '...', input_string) 
    return input_string