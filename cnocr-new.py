#-*- coding:utf-8 -*-
import re
import ocr
import time
import sys
import json
import numpy as np
from PIL import Image
reload(sys)
sys.setdefaultencoding('utf-8')
def str2date(s):
    try:
        year = s.split('年')[0]
        month = s.split('年')[1].split('月')[0]
        day = s.split('年')[1].split('月')[1].split('日')[0]
        #去掉中间十
        if(len(day))>2:
            day=day[0]+day[2];
        nm = {u'十':'10',u'一':'1',u'二':'2',u'三':'3',u'四':'4',u'五':'5',u'六':'6',u'七':'7',u'八':'8',u'九':'9',u'〇':'0',u'○':'0',u'0':'0',u'o':'0'}
        year = ''.join(nm[i] for i in year)
        month = ''.join(nm[i] for i in month)
        day = ''.join(nm[i] for i in day)
        if(len(month))==3:#去掉因为十二变成的102的类似情况。
            month=month[0]+month[2];
        elif(len(month)==1):
            month='0'+month[0];
        if(len(day)==3):#与month类似
            day=day[0]+day[2];
        elif len(day)==1:
            day='0'+day[0]
        ndate = year+'-'+month+'-'+day;
    except:
        nadate=''
    return ndate
def remove_alphabet(string,except_alphabet=None):
    alphabet=u'[qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM]'
    if except_alphabet==None:
        return re.sub(alphabet,'',string)
    else:
        alphabet=re.sub(except_alphabet,'',alphabet)
        return re.sub(alphabet,'',string)
def remove_punctuation(string,except_punctuation=None):
    punctuation=u"[`:\\\：﹒\s~!@#$%^&*()+=|{}\';\',\\[\\].<>/?~！@#￥%……& amp;*（）,，。·（）——+|{}【】《》\"\"‘；”“’。，、？|-]"
    if except_punctuation==None:
        return re.sub(punctuation, '',string)
    else:
        punctuation=re.sub(except_punctuation,'',punctuation)
        return re.sub(punctuation,'',string)
def deal_date(string):
    try:
        date_list=re.findall(u'\d+',string)
        if len(date_list[1])==1:
            date_list[1]='0'+date_list[1]
        if len(date_list[2])==1:
            date_list[2]='0'+date_list[2]

        return date_list[0]+'-'+date_list[1]+'-'+date_list[2]
    except:
        return ''
def deal_data(data,count,item):
    file_dict={}
    file_dict['data'] = data
    #filename=filename+'.json'
    if count>=item-1:
        file_dict['state']=True
    else:
        file_dict['state']=False
    return file_dict

def deal_certificate_of_degree(string):
    string=remove_punctuation(string)
    # string.replaceAll(
    #     "[`:：qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM~!@#$%^&*()+=|{}';',\\[\\].<>/?~！@#￥%……& amp;*（）——+|{}【】《》‘；”“’。，、？|-]",
    #     "")
    print(string)
    data={}
    count=0
    item=7
    """
    1.
    学士学位证书1988年11月29日生在湖南工业大学蒋斌男专业完成了本科学习计划业已印刷工程毕业
    经审核符合中华人民共和国学泣条例的规定授予工学学士学位校长2汉奇湖南工业大学学位评定委员
    会主席证书编号153542012003867二0一二年六月十五普通高等教育本科毕业生
    2.
    学士学位证书余露男1991年09月10日生在湖南科技大学潇湘学院专业完成了本科学习计划业已
    电气工程及其自动化毕业经审核符合中华人民共和国学位条例的规定授予工学学士学位长校
    湖南科技大学潇湘学院学位评定委员会主席证书编号1264942013001845二○一三年六月二十五日成人高等教莴本料毕业生
    """
    if string.find(u'男')>string.find(u'19')or string.find(u'女')>string.find(u'19') :
        try:
            name_pos=string.find(u'大学')+2
            sex_pos=string.find(u'专业')
            name=string[name_pos:sex_pos-1]
            sex=string[sex_pos-1:sex_pos]
            year_pos=string.find(u'19')
            day_pos=string.find(u'日生')
            birthday=string[year_pos:day_pos]
            birthday=deal_date(birthday)
        except:
            name=''
            sex=''
            birthday=''
    else:
        try:
            name_pos=string.index(u'书')+1
        except:
            name_pos=-1

        try:
            year_pos=string.index(u'19')
        except:
            year_pos=-1
        try:
            day_pos=string.index(u'日',year_pos)+1
        except:
            day_pos=-1
        if (name_pos>=0&year_pos>=0):
            name=string[name_pos:year_pos-1]
            sex=string[year_pos-1:year_pos]
            count=count+2
        else:
            name=''
            sex=''

        if(year_pos>=0&day_pos>=0):
            birthday=string[year_pos:day_pos]
            birthday=deal_date(birthday)
            count+=1
        else:
            birthday=''
    data["name"] = name
    data['sex'] = sex
    data['birthday']=birthday
    try:
        university_start_pos=string.index(u'在',day_pos)+1
        university_end_pos=string.index(u'学',university_start_pos)+1
        university=string[university_start_pos:university_end_pos]
        count+=1
    except:
        university=''
    data['university']=university
    try:
        major_pos_start=string.index(u'业已',university_end_pos)+2
        major_pos_end=string.index(u'毕业',major_pos_start)
        major=string[major_pos_start:major_pos_end]
        count += 1
    except:
        major=''
    data['major']=major
    try:
        for i in re.findall(u'\w+',string):#取出字符串中的所有数字和字母组合
            if len(i)>=15:#找到编号
                number=i
        # number_start_pos=string.index(u'编号')+2
        # number_end_pos=string.index(u'编号')+18
        # number=string[number_start_pos:number_end_pos]
        string=string[string.find(number):]
        count += 1
    except:
        number=''
        #time=
    data['number']=number
    try:
        time_start_pos=string.index(u'二')
        time_end_pos=string.index(u'日',time_start_pos)+1
        time=string[time_start_pos:time_end_pos]
        time=str2date(time)
        count += 1
    except:
        time=''
    data['time']=time
    print(name)
    print(sex)
    print(birthday)
    print(university)
    print(major)
    print(number)
    print(time)
    return deal_data(data,count,item)



def deal_patent(string):
    original_string=string
    print(original_string)
    string=remove_punctuation(original_string)
    print(string)
    data = {}
    count = 0
    item = 7
    #string = re.sub(u"[`:：\s~!@#$%^&*()+=|{}\';\',\\[\\].<>/?~！@#￥%……& amp;*（）,，。·（）——+|{}【】《》\"\"‘；”“’。，、？|-]", '',string)
    #证书编号：
    try:
        certificate_number_start_pos=string.index(u'第')+1
        certificate_number_end_pos=string.index(u'号',certificate_number_start_pos)
        certificate_number=string[certificate_number_start_pos:certificate_number_end_pos]
        # certificate_number=remove_punctuation(certificate_number)
        count+=1
    except:
        certificate_number=''
    data["certificate_number"]=certificate_number
    #发明名称
    try:
        name_start_pos=string.index(u'名称')+2
        try:
            name_end_pos=string.index(u'发明人')
        except:
            try:
                name_end_pos = string.index(u"发则人")
            except:
                try:
                    name_end_pos = string.index(u"设计人")
                except:
                    try:
                        name_end_pos=string.index(u'设让人')
                    except:
                        name=''
        name = string[name_start_pos:name_end_pos]
        count+=1
    except:
        name=''
    data['name']=name
    #发明人
    try:
        author_start_pos=original_string.index(u'人',name_end_pos)+2
        author_end_pos=original_string.index('专',author_start_pos)
        author=original_string[author_start_pos:author_end_pos]
        author=re.sub('[:：]',';',author)
        author=remove_punctuation(author,u';')
        count+=1
    except:
        author=''
    data['author']=author
    #专利号
    try:
        patent_number_start_pos=string.index(u'专利号')+3
        patent_number_end_pos=string.index(u'专利',patent_number_start_pos)
        patent_number=string[patent_number_start_pos:patent_number_end_pos]
        string=string[patent_number_end_pos:]
        count+=1
    except:
        patent_number=''
    data['patent_number']=patent_number
    # 专利申请日
    try:
        try:
            # 限定范围内查询，避免查询后面的内容而出错，为啥在“公”字位置截止，是因为后面有“授权公告日”，‘公司’等，
            # 而且位置离专利申请日不远，范围适当，而且肯定有“公”字，因为两次出现公字识别错误的可能性太小
            patent_of_the_application_date_start_pos=string.index(u'请日',0,string.find('公'))+2
        except:
            try:
                patent_of_the_application_date_start_pos = string.index(u'请H') + 2
            except:
                try:
                    patent_of_the_application_date_start_pos=string.index(u'请旧')+2
                except:
                    try:
                        patent_of_the_application_date_start_pos=string.index(u'请曰')+2
                    except:
                        try:
                            patent_of_the_application_date_start_pos=string.index(u'请口')+2
                        except:
                            try:
                                patent_of_the_application_date_start_pos=string.index(u'请l')+2
                            except:
                                try:
                                    patent_of_the_application_date_start_pos=string.index(u'清H')+2
                                except:
                                    try:
                                        patent_of_the_application_date_start_pos=string.index(u'清曰')+2
                                    except:
                                        patent_of_the_application_date=''

        
        try:
            patent_of_the_application_date_end_pos=string.index(u'日专')
        except:
            try:
                patent_of_the_application_date_end_pos = string.index(u'H专')
            except:
                try:
                    patent_of_the_application_date_end_pos=string.index(u'口专')
                except:
                    try:
                        patent_of_the_application_date_end_pos=string.index(u'门专')
                    except:
                        try:
                            patent_of_the_application_date_end_pos=string.index(u'曰专')
                        except:
                            try:
                                patent_of_the_application_date_end_pos = string.index(u'专')
                            except:
                                patent_of_the_application_date=''
        patent_of_the_application_date=string[patent_of_the_application_date_start_pos:patent_of_the_application_date_end_pos]
        patent_of_the_application_date=remove_alphabet(patent_of_the_application_date)
        patent_of_the_application_date=deal_date(patent_of_the_application_date)
        string=string[patent_of_the_application_date_end_pos:]
        count+=1
    except:
        patent_of_the_application_date=''
    data['patent_of_the_application_date']=patent_of_the_application_date
   #专利权人
    try:
        patentee_start_pos=string.index(u'权人')+2
        try:
            patentee_end_pos=string.index(u'授权')
            patentee=string[patentee_start_pos:patentee_end_pos]
            string=string[patentee_end_pos:]
            count+=1
        except:
            try:
                patentee_end_pos=string.index(u'公d')
                patentee=string[patentee_start_pos:patentee_end_pos]
                patentee=patentee+'公司'
                string=string[patentee_end_pos:]
                count+=1
            except:
                patentee=''
    except:
        patentee=''
    data['patentee']=patentee
    #授权公告日
    try:
        try:
            the_date_of_authorization_proclamation_start_pos=string.index(u'告日')+2
        except:
            try:
                the_date_of_authorization_proclamation_start_pos=string.index(u'告曰')+2
            except:
                try:
                    the_date_of_authorization_proclamation_start_pos=string.index(u'告H')+2
                except:
                    try:
                        the_date_of_authorization_proclamation_start_pos=string.index(u'告口')+2
                    except:
                        try:
                            the_date_of_authorization_proclamation_start_pos = string.index(u'告l') + 2
                        except:
                            the_date_of_authorization_proclamation=''
        try:
            the_date_of_authorization_proclamation_end_pos=string.index(u'日本')
        except:
                try:
                    the_date_of_authorization_proclamation_end_pos=string.index(u'口未')
                except:
                    try:
                        the_date_of_authorization_proclamation_end_pos=string.index(u'口本')
                    except:
                        try:
                            the_date_of_authorization_proclamation_end_pos=string.index(u'口不')
                        except:
                            try:
                                the_date_of_authorization_proclamation_end_pos=string.index(u'H本')
                            except:
                                try:
                                    the_date_of_authorization_proclamation_end_pos = string.index(u'l本')
                                except:
                                    the_date_of_authorization_proclamation=''
        the_date_of_authorization_proclamation=deal_date(string[the_date_of_authorization_proclamation_start_pos:the_date_of_authorization_proclamation_end_pos])
        count+=1
    except:
        the_date_of_authorization_proclamation=''
    data['the_date_of_authorization_proclamation']=the_date_of_authorization_proclamation


    print(certificate_number)
    print(name)
    print(author)
    print(patent_number)
    print(patent_of_the_application_date)
    print(patentee)
    print(the_date_of_authorization_proclamation)
    return deal_data(data,count,item)
def deal_IDcard(string):
    original_string = string
    print(original_string)
    string = remove_punctuation(original_string)
    print(string)
    data = {}
    count = 0
    item = 6
    #姓名
    try:
        name_start_pos=string.index(u"姓名")+2
        name_end_pos = string.index(u"性别")
        name=string[name_start_pos:name_end_pos]
        string=string[name_end_pos:]
        if (len(name)>=5)&((u"民族"in name )or (u"民旅" in name)):
            try:
                new_name=name[0:name.find(u'民族')]
                nation=name[name.find(u"民族")+2:]
                count+=1
            except:
                try:
                    new_name = name[0:name.find(u'民旅')]
                    nation = name[name.find(u"民旅") + 2:]
                    count+=1
                except:
                    new_name=''
            name=new_name
        else:
            count+1
    except:
        name=''
    data['name']=name
    # 性别
    try:
        sex_start_pos = string.index(u"性别") + 2
        sex=string[sex_start_pos:sex_start_pos+1]
        string=string[sex_start_pos+1:]
        count+=1
    except:
        sex = ''
    data['sex']=sex
    #民族
    try:
        try:
            nation_start_pos = string.index(u"民族") + 2
        except:
            try:
                nation_start_pos=string.index(u"民旅")+2
            except:
                try:
                    if nation is not None:
                        pass
                except:
                    nation=''
        try:
            nation_end_pos=string.index(u"出生")
        except:
            try:
                nation_end_pos=string.index(u"慈生")
            except:
                try:
                    if nation is not None:
                        pass
                except:
                    nation=''
        nation = string[nation_start_pos:nation_end_pos]
        string = string[nation_end_pos:]
        count+=1
    except:
        try:
            if nation is not None:
                count+=1
        except:
            nation = ''
    data['nation']=nation
    #出生日期
    try:
        birthday_start_pos = string.index(u"生")+1
        try:
            birthday_end_pos=string.index(u'日')
        except:
            try:
                birthday_end_pos=string.index(u'曰')
            except:
                try:
                    birthday_end_pos=string.index(u'往')
                except:
                    try:
                        birthday_end_pos=string.index(u'住')
                    except:
                        birthday=''
        birthday = deal_date(remove_alphabet(string[birthday_start_pos:birthday_end_pos]))
        string = string[birthday_end_pos:]
        count+=1
    except:
        birthday=''
    data['birthday']=birthday
    #身份证号码
    try:
        for i in re.findall(u'\w+',string):#取出字符串中的所有数字和字母组合
            if len(i)>16:#找到身份证号码，身份证号码是大于16位的
                number=i
        string=re.sub(i,'',string)
        count+=1
    except:
        number=''
    data['number']=number
    #住址
    try:
        address_start_pos=string.index(u'址')+1
        address_end_pos=string.index(u'公民')
        address=string[address_start_pos:address_end_pos]
        count+=1
    except:
        address=''
    data['address']=address
    print(name)
    print(sex)
    print(nation)
    print(birthday)
    print(address)
    print(number)
    return deal_data(data, count, item)

def deal_business_license(string):
    string = remove_punctuation(string)
    print(string)
    data = {}
    count = 0
    item = 6
    #统一社会信用代码
    try:
        credit_code_start_pos=string.find(u'代码')+2
        if credit_code_start_pos<0:
            credit_code_start_pos=string.find(u'册号')+2
        credit_code_end_pos=string.find(u'名称',credit_code_start_pos)
        if credit_code_end_pos<0:
            credit_code_end_pos=string.find(u'称',credit_code_start_pos)
        credit_code=string[credit_code_start_pos:credit_code_end_pos]
        string=string[credit_code_end_pos:]
        count+=1
    except:
        credit_code=''
    data['credit_code']=credit_code
    #企业名称
    try:
        name_start_pos=string.find(u'称')+1
        name_end_pos=string.find(u'型')
        name=string[name_start_pos:name_end_pos]
        string=string[name_end_pos:]
        count+=1
    except:
        name=''
    data['name']=name
    #企业地址
    try:
        address_start_pos=string.find(u'所')+1
        address_end_pos=string.find(u'住法定')
        if address_end_pos<0:
            address_end_pos=string.find(u'法定')
        if address_end_pos<0:
            address_end_pos=string.find(u'负责人')
        address=string[address_start_pos:address_end_pos]
        address=remove_alphabet(address,u'[A-Z]')#去除地址中的小写字母，因为地址里一般都是大写字母
        string=string[address_end_pos:]
        count+=1
    except:
        address=''
    data['address']=address
    #法人
    try:
        legal_representative_start_pos=string.find(u'人')+1
        legal_representative_end_pos=string.find(u'注册')
        if legal_representative_end_pos<0:
            legal_representative_end_pos=string.find(u'成立')
        legal_representative=string[legal_representative_start_pos:legal_representative_end_pos]
        string=string[legal_representative_end_pos:]
        count+=1
    except:
        legal_representative=''
    data['legal_representative']=legal_representative
    #开始营业时间
    try:
        start_time_start_pos=string.find(u'日期')+2
        start_time_end_pos=string.find(u'营业')
        start_time=string[start_time_start_pos:start_time_end_pos]
        string=string[start_time_end_pos:]
        #有营业执照的成立日期是中文的数字，所以这里处理特殊处理
        if deal_date(start_time)=='':
            start_time=str2date(start_time)
        else:
            start_time=deal_date(start_time)
        count+=1

    except:
        start_time=''
    data['start_time']=start_time
    #结束营业时间
    try:
        if string.find(u'长期经')>=0:
            end_time=u"长期经营"
        else:
            end_time_start_pos=string.find(u'至')+1
            end_time_end_pos=string.find(u'经营')
            end_time=string[end_time_start_pos:end_time_end_pos]
            end_time=deal_date(end_time)
        count+=1
    except:
        end_time=''
    data['end_time']=end_time
    print(credit_code)
    print(name)
    print(address)
    print(legal_representative)
    print(start_time)
    print(end_time)
    return deal_data(data,count,item)

def run(image_file,type):
    # if len(sys.argv)==3:
    #     image_file=sys.argv[1]
    #     type=sys.argv[2]
    # else:
    #     print('wrong!!!')
    image = np.array(Image.open(image_file).convert('RGB'))
    t = time.time()

    result, image_framed = ocr.model(image)
    print(t)
    print("Mission complete, it took {:.3f}s".format(time.time() - t))
    print("\nRecognition Result:\n")
    result_string=''
    for key in result:
        result_string+=result[key][1]
    dict={'certificate_of_degree':deal_certificate_of_degree,'patent':deal_patent,'IDcard':deal_IDcard,'business_license':deal_business_license}
    result_data=dict[type](result_string)
    return result_data

# if __name__=="__main__":
#     data=run("/root/桌面/最终数据/身份证/刘兵500223199307191433.jpg","IDcard")
#     print(data)
# import SocketServer
#
# class Myserver(SocketServer.BaseRequestHandler):
#     def handle(self):
#         print('服务端启动')
#         while True:
#             conn=self.request
#             print(self.client_address)
#             while True:
#                 try:
#                     # try:
#                     #     data=conn.recv(1024)
#                     # except Exception:
#                     #     break
#                     data = conn.recv(1024)
#                     if data=='exit': break
#                     data=str(data)
#                     # data.encode('utf-8')
#                     print(data)
#                     print('waiting....')
#                     image_file=data.split('#')[-2]
#                     type=data.split('#')[-1]
#                     print(image_file)
#                     print(type)
#                     result_data=run(image_file,type)
#                     result_data=json.dumps(result_data,ensure_ascii=False)
#                     conn.sendall(bytes(result_data))
#                 except Exception:
#                     conn.sendall(bytes(Exception))
#
#             conn.close()
#
# if __name__=='__main__':
#     sever=SocketServer.ThreadingTCPServer(('127.0.0.1',8091),Myserver)
#     sever.serve_forever()

# import socket
# import subprocess
# sk=socket.socket()
# address=('127.0.0.1',8000)
# sk.bind(address) #绑定IP地址及端口号
# sk.listen(3)#开始监听传入连接。backlog指定在拒绝连接之前，可以挂起的最大连接数量。
#       #backlog等于5，表示内核已经接到了连接请求，但服务器还没有调用accept进行处理的连接个数最大为5
#       #这个值不能无限大，因为要在内核中维护连接队列
#
# print('waiting.......')
#
# while True:
#     conn, addr = sk.accept()
#     while True:
#         try:
#             data = conn.recv(1024)
#             #print("----",str(data,'utf-8'))
#             data=str(data)
#             # data.encode('utf-8')
#             print(data)
#             print('waiting....')
#             image_file=data.split('#')[-2]
#             type=data.split('#')[-1]
#             print(image_file)
#             print(type)
#             result_data=run(image_file,type)
#             result_data=json.dumps(result_data,ensure_ascii=False)
#             conn.sendall(bytes(result_data))
#         except Exception:
#             conn.sendall(bytes(Exception))
#        # subprocess.Popen(data,10,stdout=subprocess.PIPE)
#
#         #answer=input(">>>")
#         #conn.send(bytes(answer,'utf-8'))
# sk.close()

# from SocketServer import BaseRequestHandler,ThreadingTCPServer
# import threading
#
# BUF_SIZE=1024
#
# class Handler(BaseRequestHandler):
#     def handle(self):
#         address,pid = self.client_address
#         print('%s %s connected!'%(address,pid))
#         while True:
#             data = self.request.recv(BUF_SIZE)
#             if len(data)>0:
#                 #print('receive=',data.decode('utf-8'))
#                 cur_thread = threading.current_thread()
#                 #response = '{}:{}'.format(cur_thread.ident,data)
#                 data = str(data)
#                 # data.encode('utf-8')
#                 print(data)
#                 print('waiting....')
#                 image_file = data.split('#')[-2]
#                 type = data.split('#')[-1]
#                 print(image_file)
#                 print(type)
#                 result_data = run(image_file, type)
#                 result_data = json.dumps(result_data, ensure_ascii=False)
#                 self.request.sendall(result_data.encode('utf-8'))
#                 print('send')
#             else:
#                 print('close')
#                 break
#
# if __name__ == '__main__':
#     HOST = '127.0.0.1'
#     PORT = 8998
#     ADDR = (HOST,PORT)
#     server = ThreadingTCPServer(ADDR,Handler)  #参数为监听地址和已建立连接的处理类
#     print('listening')
#     server.serve_forever()  #监听，建立好TCP连接后，为该连接创建新的socket和线程，并由处理类中的handle方法处理
#     print(server)

from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    filePath = request.args.get("path")
    type = request.args.get("type")
    result_data=run(filePath,type)

    return result_data


if __name__ == '__main__':
    app.run()

