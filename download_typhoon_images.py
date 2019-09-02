'''
@Description: 
@Version: 1.0
@Author: Taoye Yin
@Date: 2019-08-23 11:35:45
@LastEditors: Taoye Yin
@LastEditTime: 2019-08-23 19:45:20
'''
import urllib.request
import re
import os
from bs4 import BeautifulSoup
def get_ty_links():
    
    years = []
    year_links = []
    for i in range(1979,2020):
        years.append(str(i))
        year_links.append('http://agora.ex.nii.ac.jp/digital-typhoon/year/wnp/'+str(i)+'.html.en')

    tys = []
    ty_links = []
    for i in range(0,len(years)):
        try:
            with urllib.request.urlopen(year_links[i],timeout= 1) as h:
                html = h.read()
                soup = BeautifulSoup(html,"html.parser")
                row1 = soup.find_all(attrs={"class":"ROW1"})
                row0 = soup.find_all(attrs={"class":"ROW0"})
                number = len(row1)+len(row0)
                for j in range(1,10):
                    tys.append(years[i]+'0'+str(j))
                    ty_links.append('http://agora.ex.nii.ac.jp/digital-typhoon/summary/wnp/k/'+years[i]+'0'+str(j)+'.html.en')
                for j in range(10,number+1):
                    tys.append(years[i]+str(j))
                    ty_links.append('http://agora.ex.nii.ac.jp/digital-typhoon/summary/wnp/k/'+years[i]+str(j)+'.html.en')
        except Exception as e:
            print ("出现异常:"+str(e))
            
        # get all typhoon-page links
        

    return tys,ty_links

def download_imgs(tys,ty_links):
    import os,sys
    os.chdir(sys.path[0])
    path_ = os.path.abspath('.')
    root = 'e:/Desktop/台风图像处理/tys_raw/'
    if not os.path.exists(root):
        os.mkdir(root)
    
    for i in range(0,len(ty_links)):
        try:
            with urllib.request.urlopen(ty_links[i],timeout=1) as h1:
                html = h1.read()
                soup = BeautifulSoup(html,"html.parser")
                a_list = soup.find_all('a')
                # all satellite images for every 6 hour
                for a in a_list:
                    if a.string.strip() != 'Image':
                        continue
                    
                    image_link = 'http://agora.ex.nii.ac.jp/'+ a['href']
                    try:
                        with urllib.request.urlopen(image_link,timeout=1) as h2:
                            html_new = h2.read()
                            soup_new = BeautifulSoup(html_new,"html.parser")
                            tr_list = soup_new.find_all('tr')

                            # boo = False
                            wind = '0'
                            for tr in tr_list:
                                if tr.string != None:
                                    if tr.string.strip() == 'Maximum Wind':
                                        tr_next = tr.next_sibling.next_sibling
                                        if tr_next.string[0] == '0': # 0kt should be excluded
                                            continue
                                        wind = str(re.findall(r'\d+',tr_next.string))
                                    # if boo: # 0kt should be excluded
                                    #     continue

                            pressure = '1000'
                            for tr in tr_list:
                                if tr.string != None:
                                    if tr.string.strip() == 'Central Pressure':
                                        tr_next = tr.next_sibling.next_sibling
                                        pressure = str(re.findall(r'\d+',tr_next.string))
                                
                            pict_list = []
                            anew_list = soup_new.find_all('a')
                            for anew in anew_list: # find ir images
                                if anew.string != None:
                                    if anew.string.strip() == 'Magnify this':
                                        st = anew['href'].replace('/0/','/1/') # replace vis to ir
                                        pict_list.append('http://agora.ex.nii.ac.jp'+ st)
                    except Exception as e:
                        print ("出现异常:"+str(e))
                    if len(pict_list) > 2 :
                        s = pict_list[2] #这是台风图像，前面的[1]是track,[0]区域图片，顺序网页上的来
                        filename = tys[i]+'_'+s[len(s)-19:len(s)-11]+'_'+wind+'_'+pressure# filename : typhoon-number_time(YYMMDDHH)_wind_pressure.jpg
                        filename = rename(filename)
                        attempts5 = 0
                        success5 = False
                        while attempts5 < 5 and not success5:
                            try: # save images
                                urllib.request.urlretrieve(s, root+filename+'.jpg')
                                # f = open(root+filename+'.jpg','wb')
                                # req = urllib.request.urlopen(s)
                                # buf = req.read()
                                # f.write(buf)
                                # f.close()
                                success5 = True
                            except Exception as e:
                                attempts5 += 1
                                if attempts5 == 5:
                                    print ("出现异常:"+str(e))
                            finally:
                                urllib.request.urlcleanup()
            print (tys[i],'has been downloaded.')
        except Exception as e:
            print ("出现异常:"+str(e))
def rename(fname): # there maybe some unexcepted char in fname, drop them

    new_fname = fname.replace('[','')
    new_fname = new_fname.replace(']','')
    new_fname = new_fname.replace('u','')
    new_fname = new_fname.replace('\'','')
    return new_fname
	    
if __name__ == '__main__':

    ts,links = get_ty_links()
    download_imgs(ts,links)
