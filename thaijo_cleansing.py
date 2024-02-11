import pandas as pd
import regex as re
import string


def remove_spaces(string):
    if string == '':
        return ''
    elif string == ' ':
        return ''
    if string[0] == ' ':
        string = string[1:]
    if string[-1] == ' ':
        string = string[:-1]
    return string


def call_maid_to_clean_this_data_for_me(name):
    name = name.lower()

    want_to_removes = [
        ';', '"', 'และคณะ', 'ผศ.', 'ดร.', 'ร.ต.อ.', 'นพ.', 'รศ.', 'dr.', 'm.r.', 'mr.', 'ม.ร.ว.',
        'ms.', 'assist.', 'prof.', 'lect.', 'asst.', 'assoc.', '(ผู้แต่ง)', 'กองบรรณาธิการ ผู้เชี่ยวชาญ',
        'กองบรรณาธิการ กองบรรณาธิการ', 'รายละเอียดบทความ วารสารวิทยาการจัดการ', 'กองบรรณาธิการ วารสาร',
        'วารสารวิชาการและวิจัยสังคมศาสตร์', 'สารบัญ วารสารวิทยาการจัดการ', 'บรรณาธิการ วารสารวิทยาการจัดการ',
        'คณะมนุษยศาสตร์ มหาวิทยาลัยรามคำแหง', 'บัณฑิตวิทยาลัย วไลยอลงกรณ์', '(', ')', '[', ']', 'authors :',
        'cover vol', 'tsme thailand', 'สารบัญ', 'ผู้ช่วยศาสตราจารย์', 'ผู้ช่วยศาสตราจารย์ ดร.', 'รองศาสตราจารย์ ดร.',
        'รองศาสตราจารย์', 'พระครู', 'พระมหา', 'พระปลัด', 'อาจารย์', 'พันเอกหญิง', 'พันเอก', 'author', 'บทบรรณาธิการ',
        'บรรณาธิการ', 'editorial', 'วารสารวิชาการและวิจัยสังคม', 'เกี่ยวกับวารสาร', 'about the journal', 'ผู้ทรงคุณวุฒิ -',
        'แนะนำผู้เขียน -', ',', '*', 'กสทช.', 'ว่าที่ พ.ต.', 'อ.', 'ศ.', 'ว่าที่ ร.ต', 'ว่าที่ร้อยตรี', 'ร้อยเอก', 'et.al', 
        'et al', 'and other', 'ศูนย์บริการโลหิตแห่งชาติ สภากาชาดไทย', 'วารสารมหาวิทยาลัยราชภัฏสกลนคร', '-- --'
    ] 

    for word in want_to_removes:
        name = name.replace(word, '')

    for digit in '1234567890':
        name = name.replace(digit, '')

    want_to_remove_if_start_with = [
        'ปลัด', 'ครู', 'พระ', 'นาย', 'นาง',
        'phrakru', 'phrakhru', 'phrakhru', 'phramaha', 'phra',
    ]

    for prefix in want_to_remove_if_start_with:
        name = name.replace(prefix, '', 1) if name.startswith(prefix) else name 
    
    tmp = name.split(' ')

    if '-' in tmp:
        tmp.remove('-')

    for t in tmp:
        if '@' in t:
            tmp.remove(t) # remove email

    name = ' '.join(tmp)

    name = re.sub('\s\s+', ' ', name) # remove double(or more) white space

    if isthai(name):
        name = name.strip('.@ ') # ภูรี เพ็ญหิรัญ. is not valid
    else:
        name = name.lstrip('.@ ') # but Phuree P. is valid

    # merge last 2 word if they are the same word
    tmp = name.split(' ')
    if len(tmp) > 2 and tmp[-1] == tmp[-2]:
        name = ' '.join(tmp[:-1])

    # merge first 2 word if they are the same word
    tmp = name.split(' ')
    if len(tmp) > 2 and tmp[0] == tmp[1]:
        name = ' '.join(tmp[1:])

    ignore_names = ['-', 'jphd', 'ph.d', 'm.d.', 'cfa', 'jr.', 'ma', 'team']

    for ignore in ignore_names:
        if name.lower() == ignore:
            name = ''

    name = string.capwords(name) # Capitalize

    name = name.replace('', '์') # fix wrong vowel 

    return name


def check_en_th_mix(name):
    en_flag = False
    th_flag = False

    for c in name:
        if iseng(c):
            en_flag = True
        if isthai(c):
            th_flag = True

    return th_flag and en_flag


def hope(name):
    if (isthai(name) or iseng(name)) and (len(name) > 37):
        name = '' 
    return name


def isthai(name):
    for c in name:
        if c in 'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ' + '์เๅะุ่้ัีึแๆำ๊ํู็๋์,ฦ๐':
            return True
    return False


def iseng(name):
    for c in name:
        if c in 'abcdefghijklmnopqrstuvwxyz' + 'abcdefghijklmnopqrstuvwxyz'.upper():
            return True
    return False


def count_en_th_char(name):
    n_en = 0

    for c in name:
        if iseng(c):
            n_en += 1

    n_th = abs(len(name) - n_en)
    
    return n_en, n_th


def detect_noise(name):
    n_en, n_th = count_en_th_char(name)

    yy = sorted([n_th, n_en])

    if yy[0] / yy[1] < 0.2: # found noise (eg. Phuงงree Phenhiran)
        return True
    

def denoise(name):
    n_en, n_th = count_en_th_char(name)

    newstr = ''

    if n_en > n_th:
        for c in name:
            if iseng(c):
                newstr += c
        return 'en', newstr
    
    else:
        for c in name:
            if not iseng(c):
                newstr += c
        return 'th', newstr

    
if __name__ == '__main__':

    char = {'id': [], 'name': []}
    df = pd.read_csv('test.csv')
    df = df.fillna('')

    for idx, row in df.iterrows():
        names = []
        char['id'].extend([f"{row['_id']}_{i+1}" for i in range(10)])
        author = row['_source.author']
        co_author = row['_source.co-author']


        if author != '':

            if author == 'มาริยา เถาอินปาก   ธีรชัย เนตรถนอมศักดิ์  เพ็ญณี  แนรอท': # special case
                lst = ['มาริยา เถาอินปาก', 'ธีรชัย เนตรถนอมศักดิ์', 'เพ็ญณี  แนรอท']

            elif ';' in author:
                lst = author.split(';')

            else:
                lst = author.split(',')

            for a in lst:
                if a not in names:
                    names.append(a)


        if co_author != '':
            lst = co_author.split(',')
            for c in lst:
                if c not in names:
                    names.append(c)


        if len(names) == 0:
            char['name'].extend([None]*10)
            continue


        names = [remove_spaces(name) for name in names]
        names = [call_maid_to_clean_this_data_for_me(name) for name in names]

        # remove duplicate and blank name
        tmpname = []
        for n in names:
            if n not in tmpname and n!='': 
                tmpname.append(n)
        names = tmpname

        # HANDLE MIXED LANGUAGE NAME
        tmpname = []
        for n in names:
            if check_en_th_mix(n):
                th = []
                en = []

                lst = n.split(' ')

                for word in lst:
                    ## if NAME CONTAINS EN & TH
                    if check_en_th_mix(word):

                        # [CASE 1 NOISE]: detect and remove noise (eg. eg. Phuงงree Phenhiran)
                        if detect_noise(word):
                            denoised = denoise(word)
                            if denoised[0] == 'en':
                                en.append(denoised[1])
                            else:
                                th.append(denoised[1])

                        # [CASE 2 NO WHITESPACE]: detect no whitespace between en & th name (eg. ภูรีPhuree)
                        else:
                            firstchr = word[0]
                            is_firstchr_eng = iseng(firstchr)

                            cnt = 0
                            for ec in word:
                                if iseng(ec) != is_firstchr_eng: # trigger when language change
                                    break
                                cnt += 1

                            # split en/th
                            if is_firstchr_eng:
                                en.append(word[:cnt])
                                th.append(word[cnt:])
                            else:
                                th.append(word[:cnt])
                                en.append(word[cnt:])

                    ## if NAME CONTAINS ONLY TH
                    elif isthai(word):
                        th.append(word)
                    
                    ## if NAME CONTAIN EN (OR OTHERS)
                    else:
                        en.append(word)

                # join name
                th = ' '.join(th)
                en = ' '.join(en)


                if not isthai(lst[0]):
                    name_pair = [en, th]
                else:
                    name_pair = [th, en]


                name_pair = [remove_spaces(n) for n in name_pair]
                name_pair = [call_maid_to_clean_this_data_for_me(n) for n in name_pair]


                name_pair = [n for n in name_pair if n!='']

                tmpname.extend(name_pair)

            ## if name contains only one language
            else:
                tmpname.append(n)



        names = tmpname
        names = [hope(name) for name in names]


        # reverse order if name is Arabic
        if len(names) > 0:
            if re.search('[\u0621-\u064A0-9]', names[0]) != None: # found Arabic letter
                names = names[::-1] # reverse name order


        if len(names) > 10:
            names = names[:10]
        elif len(names) < 10:
            names.extend(['']*(10-len(names)))
        char['name'].extend(names)


    # handle Phra codename
    phra_codenames = []
    tmp_df = pd.read_csv('starting_point.csv')
    tmp_df = tmp_df.fillna('')

    for idx, row in tmp_df.iterrows():
        name = row['name']
        
        if name.startswith(('พระ', 'Phra', 'phra')):
            try:
                sb = name.index('(')
                cb = name.index(')')
                codename_include_bracket = name[sb: cb+1]

                if iseng(codename_include_bracket[1]) == iseng(name[0]):
                    phra_codenames.append((codename_include_bracket, name))
            except:
                ...


    char = pd.DataFrame(char)


    for idx, row in char.iterrows():
        name = row['name']
        for (codename_w_bracket, phra_name) in phra_codenames:
            # if detect Phra, fill codename with bracket at the end
            if codename_w_bracket[1:-1] in name and name.split(' ')[0] in phra_name:
                n = len(codename_w_bracket[1:-1].split(' '))
                only_phra_name = name.split(' ')[:-n]
                row['name'] = ' '.join(only_phra_name) + ' ' + codename_w_bracket


    char.to_csv('latest.csv', index=False) # export csv
