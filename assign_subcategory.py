# OTHER
arts_slugs = {'look of the week':'lotw', 'off the shelf':'off-the-shelf'} # complete names : slugs
def find_arts_subcategories(headline):
    categ_string = ''
    for key in arts_slugs.keys():
        if (key in headline.lower()):
            categ_string += arts_slugs[key]
    return categ_string

# SPORTS
# look for these keywords in the articles (error if none are found)
sports_teams_keywords = ['Boys Cross Country', 'Boys Soccer', 'Boys Water Polo', 'Field Hockey', 'Football', 'Girls Cross Country', 'Girls Soccer', 'Girls Volleyball', \
    'Girls Hockey', 'Girls Squash', 'Girls Swimming', 'Nordic', 'Indoor Track', 'Wrestling' \
    'Baseball', 'Boys Crew', 'Boys Lacrosse', 'Boys Tennis', 'Boys Volleyball', 'Cycling', 'Girls Crew', 'Girls Lacrosse', 'Girls Tennis', 'Girls Water Polo', 'Golf', 'Softball', 'Track', 'Ultimate']

# the slug is the sanitized version of the string 

# map team slugs to season slugs
sports_seasons_slugs = {'boys-soccer': 'fall-sports', 'football': 'fall-sports', 'girls-volleyball': 'fall-sports', \
    'girls-cross-country': 'fall-sports', 'boys-cross-country': 'fall-sports', 'field-hockey': 'fall-sports', \
    'girls-soccer': 'fall-sports', 'boys-water-polo': 'fall-sports', 'girls-tennis': 'spring-sports', \
    'cycling': 'spring-sports', 'spring-track-field': 'spring-sports', 'boys-lacrosse': 'spring-sports', \
    'girls-lacrosse': 'spring-sports', 'boys-tennis': 'spring-sports', 'baseball': 'spring-sports', \
    'ultimate': 'spring-sports', 'softball': 'spring-sports', 'boys-crew': 'spring-sports', 'golf': 'spring-sports', \
    'girls-water-polo': 'spring-sports', 'boys-volleyball': 'spring-sports', 'girls-crew': 'spring-sports', \
    'winter-track-field': 'winter-sports', 'girls-hockey': 'winter-sports', 'girls-swimming': 'winter-sports', \
    'wrestling': 'winter-sports', 'girls-squash': 'winter-sports', 'nordic': 'winter-sports'}
'''
def find_sports_subcategories(headline, article_text):
    categ_string = ''
    team_found = False
    for keyword in sports_teams_keywords:
        if (team_found):
            break
        # search the headline
        if (keyword in headline):
            team_found = True
            team_slug = category_sanitize(keyword)
            categ_string += team_slug +','+ sports_seasons_slugs[team_slug] # append slug
        if (team_found):
            break
        # search the article_text
        if (keyword in article_text):
            team_found = True
            team_slug = category_sanitize(keyword)
            categ_string += team_slug +','+ sports_seasons_slugs[team_slug] # append slug
    if (categ_string == ''):
        print('  error: no sports subcategory found, ASSIGN MANUALLY!')
    return categ_string
'''
def find_sports_subcategories(headline, subcategory):
    team_slug = category_sanitize(keyword)
    return team_slug +','+ sports_seasons_slugs[team_slug] # append slug

def category_sanitize(s_in):
    """categ name to slug -- make all words lowercase and replace ' ' with '-'"""
    if (s_in == 'Indoor Track'):
        return 'winter-track-field'
    if (s_in == 'Track'):
        return 'spring-track-field'

    s_in = s_in.lower()
    s_out = ''
    for i in range(len(s_in)):
        if (s_in[i] == ' '):
            s_out += '-'
        else:
            s_out += s_in[i]
    return s_out
def category_desanitize(s_in):
    """slug to categ name -- capitalize all words and replace '-' with ' '"""
    if (s_in == 'winter-track-field'):
        return 'Indoor Track'
    if (s_in == 'spring-track-field'):
        return 'Track'

    s_out = ''
    for i in range(len(s_in)):
        if (s_in[i] == '-'):
            s_out += ' '
        else:
            s_out += s_in[i]
    words = s_out.split(' ')
    for i in range(len(words)):
        words[i] = words[i][0].upper()+words[i][1:]
    return ' '.join(words)



"""
# OLD METHOD:
sports_team_keywords = ['andover','girls','boys','cross','country','soccer','water','polo','volleyball','field','hockey','football','basketball','hockey','squash','nordic','swimming','wrestling','indoor','track','and','field','baseball','softball','crew','lacrosse','tennis','cycling','golf','ultimate']

fall_sports_team_slugs = ['boys-cross-country','boys-soccer','boys-water-polo','field-hockey', \
'football','girls-cross-country','girls-soccer','girls-volleyball'] 
spring_sports_team_slugs = ['baseball','boys-crew','boys-lacrosse','boys-tennis','boys-volleyball','cycling','girls-crew','girls-lacrosse','girls-tennis','girls-water-polo','golf','softball','spring-track-field','ultimate']
winter_sports_team_slugs = ['girls-hockey','girls-squash','girls-swimming','nordic','winter-track-field','wrestling']
"""