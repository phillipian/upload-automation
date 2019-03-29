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
    
    print(murl_elements)
    
    cur_month = str(datetime.datetime.now().month)
    if (len(cur_month) < 2):
        cur_month = '0'+cur_month
    iurl = '/'.join(murl_elements[:-1])+'/wp-content/uploads/'+str(datetime.datetime.now().year)+'/'+str(cur_month)+'/'+filename
    return iurl