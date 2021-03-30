# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 19:55:15 2021

@author: us51114
"""
import os
import cv2
import pytesseract
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd=r'C:\\Users\\us51114\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'
import pandas as pd #this to read the manually extracted data and use it for percentage value extraction
import numpy as np
import re
#'5.jpg: getting all data', 7.jpg: getting partial data, 7_rotate.jpg: getting all datae

class account_detail:
  def __init__(self):
    self.file = ""
    self.name = ""
    self.ac_no =""
    self.ifsc = ""
    
def conver_to_black_and_white(inp_img):
    x=inp_img.shape[0]
    y=inp_img.shape[1]
    req_val=0
    find_val=[255,255,255] #white
    find_sum=np.sum(find_val)
    for i in range(x):
        for j in range(y):
            check_val=inp_img[i,j]
            comparison = find_val == check_val 
            equal_arrays = comparison.all() 
            if ~equal_arrays: #for not white
                 ch_sum=np.sum(check_val)
                 if ch_sum<0.9*find_sum:
                     inp_img[i,j]=[0,0,0] #black
                     req_val=req_val+(i+1)/x+(j+1)/y
                 else:
                     inp_img[i,j]=[255,255,255] #black
    return inp_img

def OCR_cv2_read1(img):
    global inp_path,out_text_file,out_img_file
    #converting image into gray scale image
    # gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # converting it to binary image by Thresholding
    # this step is require if you have colored image because if you skip this part
    # then tesseract won't able to detect text correctly and this will give incorrect result
    # threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
    # text_fname=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + ".txt"
    # f = open(out_text_file, "w")
    #config = ("-l eng --oem 1 --psm 7") #no reqyired output
    custom_config = r'--oem 3 --psm 6'
    #below for image to data #threshold_img
    text = pytesseract.image_to_data(img, output_type=Output.DICT, config=custom_config, lang='eng')
    #below for image to string
    # text=pytesseract.image_to_string(threshold_img,config=custom_config,output_type=Output.DICT)
    # f.write(str(text.keys())) #str(text))
    # print(type(text['text']))
    # f.write(''.join(text['text']))
    # f.close()
    # ka=cv2.imwrite(out_img_file,img)
    # cv2.imshow('image',gray_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return text['text']
    # print(os.path.splitext(full_fname)[0])
    
    
def check_per_output_extracted(img_fname,inp_list):
    global df_req_output
    inp_str=''.join(inp_list).upper()
    #print(inp_str)
    row_indx=df_req_output[df_req_output['File name']==img_fname].index.values
    row_indx=row_indx[0]
    out_req=df_req_output.iloc[row_indx,1:4]
    no_req_out=0;no_out_find=0
    for each_out in out_req:
        find_str=each_out.upper()
        # print("find:",find_str)
        if each_out!="-":
            no_req_out=no_req_out+1
            if (inp_str.find(find_str.replace(' ','')) != -1):
                # print("yes find 1")
                no_out_find=no_out_find+1
            else:
                #check for all 0, because the image text can mention 0-->O or O-->0
                inp_str1=inp_str.replace("O","0")
                find_str=find_str.replace(' ','').replace("O","0")
                if (inp_str1.find(find_str) != -1):
                    # print("yes find 2")
                    no_out_find=no_out_find+1
    # if no_req_out!=0:
    #     print(img_fname,":",no_out_find,no_req_out,no_out_find/no_req_out*100,"%")
    # else:
    #     print(img_fname,":",'0%')
    #     # if not np.isnan(each_out):
    #     #     print(str(each_out))
    # # print(img_fname,':',out_req) #[row_indx:]
    return no_out_find


def extract_required_data_from_str(inp_str_list):
    output_data=account_detail()
    name_limit_str=['acco','cif','ount']
    #below to find account name
    index_i=0;data_identified=False
    for each_str in inp_str_list:
        # print(each_str)
        each_str=each_str.lower()
        if each_str.find('name')!=-1 or each_str.find('customer')!=-1: #check for account holder name
            skip_str=['+']
            if each_str.find('name')!=-1: #name format
                if inp_str_list[index_i+1]==":" or inp_str_list[index_i+1]=="+":
                    for loc_i in range(index_i+2,len(inp_str_list)):
                        new_str=inp_str_list[loc_i].lower()
                        if new_str!='' and all([new_str.find(str_y)==-1 for str_y in skip_str]):
                            if len(re.findall("[0-9]", new_str))>0:
                                break
                            limiter_found=False
                            for limit_str in name_limit_str:
                                if new_str.find(limit_str)!=-1:
                                    limiter_found=True
                                    break
                            if limiter_found: break
                            data_identified=True
                            if output_data.name=='':
                                output_data.name=inp_str_list[loc_i]
                            else:
                                output_data.name=output_data.name + " " + inp_str_list[loc_i]
            else: #for customer format
                skip_str=['+','name']
                # print("entered")
                for loc_i in range(index_i+1,len(inp_str_list)):
                        new_str=inp_str_list[loc_i].lower()
                        if new_str.find('address')!=-1: break
                        ch_out=[new_str.find(str_y)!=-1 for str_y in skip_str]
                        # print(ch_out)
                        if new_str!='' and all([new_str.find(str_y)==-1 for str_y in skip_str]):
                            # print("enter2")
                            if len(re.findall("[0-9]", new_str))>0:
                                break
                            limiter_found=False
                            for limit_str in name_limit_str:
                                if new_str.find(limit_str)!=-1:
                                    limiter_found=True
                                    break
                            if limiter_found: break
                            data_identified=True
                            if output_data.name=='':
                                output_data.name=inp_str_list[loc_i]
                            else:
                                output_data.name=output_data.name + " " + inp_str_list[loc_i]
        elif each_str.find('accou')!=-1 or each_str.find('ount')!=-1: #check for account number
            if inp_str_list[index_i+1].find(':')!=-1: #inp_str_list[index_i+1]==":" or inp_str_list[index_i+2]==":":
                output_data.ac_no=inp_str_list[index_i+2]
            elif inp_str_list[index_i+2].find(':')!=-1:
                output_data.ac_no=inp_str_list[index_i+3]
            elif inp_str_list[index_i+1].lower().find('no')!=-1:
                output_data.ac_no=inp_str_list[index_i+2]
            output_data.ac_no=output_data.ac_no.replace("O","0")
            data_identified=True
            # new_acc=""
            # for each_chr in output_data.ac_no:
            #     if each_chr.isnumeric():
            #         new_acc=new_acc + each_chr
            # if new_acc!='':
            #     output_data.ac_no=new_acc
        elif each_str.find('ifsc')!=-1: #check for account ifsc
            if inp_str_list[index_i+1].find(':')!=-1: #inp_str_list[index_i+1]==":" or inp_str_list[index_i+2]==":":
                data_identified=True
                output_data.ifsc=inp_str_list[index_i+2]
            elif inp_str_list[index_i+2].find(':')!=-1:
                data_identified=True
                output_data.ifsc=inp_str_list[index_i+3]
        index_i=index_i+1
    return output_data,data_identified

def rotate_the_skew_image(img):
    #below to check for skew and rotate
    neg = 255 - img  # get negative image
    angle_counter = 0 # number of angles
    angle = 0.0 # collects sum of angles
    
    # get all the Hough lines
    for line in cv2.HoughLinesP(neg, 1, np.pi/180, 325):
        x1, y1, x2, y2 = line[0]
    
        # calculate the angle (in radians)
        this_angle = np.arctan2(y2 - y1, x2 - x1)
        if this_angle and abs(this_angle) <= 10:
            # filtered zero degree and outliers
            angle += this_angle
            angle_counter += 1
    
    # the skew is calculated of the mean of the total angles
    skew = np.rad2deg(angle / angle_counter)
    
    #below rotate the image
    rows, cols = img.shape
    rot_mat = cv2.getRotationMatrix2D((cols/2, rows/2), skew, 1.0) #angle
    result = cv2.warpAffine(img,
                            rot_mat,
                            (cols, rows),
                            flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(255, 255, 255))
    return result

def check_threshold(img):
    #this function is to check the image for different threshold value
    # cv2.imshow('image',img)
    #below to create a kernel to use for erode and dilate
    kernel = np.ones((1, 1), np.uint8)
    # THRESHOLD =200 #127
    # cv2.imshow('image',img)
    # out_img_path=r'D:\kalathi\My_collection\Python\Task_Artivatic\WIP\Remove_Scan_noise\img_3'
    for THRESHOLD in range(170,210): #140,260
        ret, img_thr1 = cv2.threshold(img, THRESHOLD, 255, cv2.THRESH_BINARY)
        # out_fimg=out_img_path + '\\' + 'threshold_' + str(THRESHOLD) +'.png'
        # ka=cv2.imwrite(out_fimg,img_thr1)
        # cv2.imshow('image_thr1',img_thr1)
        # cv2.waitKey()
        # f.write('image_gray_threshold'+ str(THRESHOLD) + '\n')
        out_str=OCR_cv2_read1(img_thr1)
        comb_str=''.join(out_str).lower()
        if comb_str.find('name')!=-1 and comb_str.find('ount')!=-1:
            return True,out_str
    return False,out_str

if __name__ == '__main__':
    global inp_path,out_text_file,df_req_output,out_img_file
    #below to read the manually extracted reuired output
    # loc=r'D:\kalathi\My_collection\Python\Task_Artivatic\WIP\Manual_extracted_database.xlsx'
    # df_req_output=pd.read_excel(loc, dtype=str)
    # print(df_req_output)
    required_info=[]
    cur_dir = os.getcwd()
    inp_path=cur_dir + '\\Input'
    # out_path=cur_dir + '\\Output\\Image_to_data' #Image_to_String' #'
    file_nlist = os.listdir(inp_path)
    
    for each_f in file_nlist:
        if not each_f.endswith("txt"):
            print(each_f + ':in progress..')
            full_fname=inp_path + '\\' + each_f
            img=cv2.imread(full_fname) #'breakingnew.png')
            # img=conver_to_black_and_white(img)
            # out_text_file=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + ".txt"
            # out_list_file=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + "_list.txt"
            # out_img_file=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + ".png"
            img_str_list=OCR_cv2_read1(img)
            # f=open(out_list_file,"w")
            # f.write(" ".join(img_str_list))
            # f.close()
            # print(img_str)
            # no_match=check_per_output_extracted(each_f,img_str_list) #this is for cross check
            acc_info,data_identified=extract_required_data_from_str(img_str_list)
            if data_identified:
                acc_info.file=each_f
                required_info.append(acc_info)
            if not data_identified: #no_match==0:
                # by 90 degrees clockwise
                img_rotate = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
                # out_text_file=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + "_90_clock.txt"
                # out_list_file=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + "_90_clock_list.txt"
                # out_img_file=out_path + "\\" + os.path.splitext(os.path.basename(full_fname))[0] + "_90_clock.png"
                img_str_list=OCR_cv2_read1(img_rotate)
                # f=open(out_list_file,"w")
                # f.write(" ".join(img_str_list)) #str(img_str_list)
                # f.close()
                # no_match=check_per_output_extracted(each_f,img_str_list) #this is for cross check
                acc_info,data_identified=extract_required_data_from_str(img_str_list)
                if data_identified:
                    acc_info.file=each_f #+ '_90 clock'
                    required_info.append(acc_info)
            if not data_identified: #check for skewed img
                img=cv2.imread(full_fname, cv2.IMREAD_GRAYSCALE)
                skew_img=rotate_the_skew_image(img)
                out_info,img_str_list=check_threshold(skew_img)
                if out_info:
                    acc_info,data_identified=extract_required_data_from_str(img_str_list)
                    if data_identified:
                        acc_info.file=each_f #+ '_skew_threshold'
                        required_info.append(acc_info)
            if not data_identified: #check for 90deg rotated skewed img
                img_rotate = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
                skew_img=rotate_the_skew_image(img_rotate)
                out_info,img_str_list=check_threshold(skew_img)
                if out_info:
                    acc_info,data_identified=extract_required_data_from_str(img_str_list)
                    if data_identified:
                        acc_info.file=each_f #+ '_skew_threshold'
                        required_info.append(acc_info)
            if not data_identified:
                acc_info=account_detail()
                acc_info.file=each_f
                required_info.append(acc_info)
            print(each_f + ':completed')
    Overall_out=cur_dir + "\\Output_summary" + ".txt"
    f=open(Overall_out,"w")
    f.write("Filename, Name, Account Number, IFSC Code \n")
    for each_acc in required_info:
        f.write(each_acc.file + ", " + each_acc.name + ", " + each_acc.ac_no + ", " + each_acc.ifsc + "\n") #str(img_str_list)
        print(each_acc.file,",",each_acc.name,",",each_acc.ac_no,",",each_acc.ifsc)
    f.close()
    # f = open("demofile3.txt", "w")
    # f.write("Woops! I have deleted the content!")
    # f.close()

# img=cv2.imread('7_rotate.jpg') #'breakingnew.png')
# # cv2.imshow('image',img)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()
# text=pytesseract.image_to_string(img,output_type=Output.DICT) #Output.DICT #Output.STRING

# # custom_config = r'--oem 3 --psm 6'
# # text=pytesseract.image_to_string(img, config=custom_config)
# print('text',text)


