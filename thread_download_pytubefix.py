'''
Download Thread for Pytubefix
F.Garcia
11.08.2024
Streaming Handle thread.
Is alive meanwhile there are downloads.
'''
import threading
import queue
import logging
import time

from common import *

from PyQt5 import QtCore

import class_pytubefix_use


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter=logging.Formatter('[%(levelname)s] (%(threadName)-10s) %(message)s')
ahandler=logging.StreamHandler()
ahandler.setLevel(logging.INFO)
ahandler.setFormatter(formatter)
log.addHandler(ahandler)


 
class queueStream(threading.Thread):
    """
        A thread class to buffer and deliver the downloads to pytubefix
    """                  

    def __init__(self, url_list:list[str],file_properties_dict:dict,cycle_time:float,kill_event:threading.Event,progress_bar_one_download=None,progress_bar_files_downloaded=None):
        threading.Thread.__init__(self, name="File download thread")        
        self.ptf = class_pytubefix_use.use_pytubefix()

        self.ptf.to_log[str].connect(self.pytubefix_log)
        self.ptf.download_start[str, str].connect(self.pytubefix_download_start)
        self.ptf.download_end[str, str].connect(self.pytubefix_download_end)
        self.ptf.on_progress[list].connect(self.pytubefix_download_progress)

        self.cycle_time=cycle_time
        self.killer_event = kill_event        
        self.file_queue = queue.Queue()
        self.output_queue = queue.Queue()   
        self.file_queue_size=self.file_queue.qsize()
        self.out_queue_size=self.output_queue.qsize()                    
        self.progress_bar_one_download=progress_bar_one_download
        self.progress_bar_files_downloaded=progress_bar_files_downloaded
        self.progress_bar_ini=0
        self.progress_bar_end=100        
        self.progress_bar_set_status(self.progress_bar_one_download,0)        
        self.progress_bar_set_status(self.progress_bar_files_downloaded,0) 
        #event handled       
        self.event_finished_one_file_download=threading.Event()        
        self.event_finished_one_file_download.clear() 
        self.event_get_next_file_to_download=threading.Event()
        self.event_get_next_file_to_download.clear() 
        self.is_file_download_finished=False
        self.download_finished=False
        self.download_stream_size=0
        self.max_buffer_size=10        
        self.file_list= url_list
        self.number_of_files_to_download=len(url_list)
        self.number_of_files_downloaded=0
        self.set_files_to_file_queue(url_list)
        self.actual_url_info={}
    
    def pytubefix_log(self, log_msg: str):
        """
        Logs message from pytubefix
        Args:
             log_msg (str): message
        """
        if "error" in log_msg.lower():
            log.error("Error while downloading %s", self.actual_url_info)
            log.error(log_msg)
            self.quit()
        elif "warning" in log_msg.lower():
            log.warning(log_msg)
        else:
            log.info(log_msg)

    def pytubefix_download_progress(self, progress_list: list):
        """
        Shows download progress
        """
        # url = self.ongoing_download_url
        [bytes_received, filesize] = progress_list
        sstatb=self.get_progress_percentage(bytes_received, filesize,Perini=0,Perend=100)
        self.progress_bar_set_status(self.progress_bar_one_download,sstatb)
        

    def pytubefix_download_start(self, url: str, title: str):
        """Receives Signal form Pytube fix when a Download is started

        Args:
            url (str): url of download
            title (str): title of the download
        """
        log.info("Download started: %s \nURL: %s",title,url)
        log.info(self.actual_url_info)
    
    def pytubefix_download_end(self, url: str, title: str):
        """Receives Signal form Pytube fix when a Download is ended

        Args:
            url (str): url of download
            title (str): title of the download
        """
        self.event_get_next_file_to_download.set()
        self.number_of_files_downloaded = self.number_of_files_downloaded + 1
        log.info("Download finished: %s \nURL: %s",title,url)

    def download_file(self):
        if self.event_get_next_file_to_download.is_set():
            #Clear flag
            self.event_get_next_file_to_download.clear()
            # get next url
            a_url=self.add_to_output_queue()
            #----------------  here add all other download options
            self.actual_url_info=self.ptf.get_url_info(a_url)
            self.ptf.download_video(a_url)

            


    def add_one_line_to_buffer_ev(self):
        self.event_finished_one_file_download.set()

    def set_Buffer(self,Refill_value=0,Buffer_size=5):
        '''
        Sets values for filling the buffer when reaching refill value. 
        Refill_value=0 -> when empty
        Refill_value>= Buff_size-> never
        '''
        if Buffer_size<=0:
            Buffer_size=5
        if Buffer_size>int(self.max_buffer_size/2):
            Buffer_size=int(self.max_buffer_size/2)
        self.Buff_size=Buffer_size
        self.Buff_fill=Refill_value
        
    def Fill_buffer(self,whencountis=0,untilcountis=5):        
        if whencountis<0:
            whencountis=0
        if self.out_queue_size<=whencountis and self.file_queue_size>0:            
            while self.file_queue_size>0 and self.out_queue_size<untilcountis:
                self.add_to_output_queue()    
            self.event_get_next_file_to_download.set()                
        self.update_queue_sizes()    

    def progress_bar_set_status(self,Pbar,val):
        if  Pbar!=None and int(val)>=0 and int(val)<=100:      
            Pbar.SetStatus(int(val))
    
    def quit(self):
        self.killer_event.set()        

    def get_progress_percentage(self,sss,Numsss,Perini=0,Perend=100):
        if sss>Numsss:            
            return Perend
        if sss<0 or Numsss<=0:            
            return Perini
        if (Perend-Perini)<=0:
            Per=min(abs(Perini),abs(Perend))              
            return Per 
        Per=round(Perini+(sss/Numsss)*(Perend-Perini),2)        
        return Per   
       
    def refresh_progress_bar_files_downloaded(self):    
        sstat=self.get_progress_percentage(self.number_of_files_downloaded,self.number_of_files_to_download,Perini=0,Perend=100)        
        self.progress_bar_set_status(self.progress_bar_files_downloaded,sstat)
        #print('buffer per:',sstatb,'%',' stream per:',sstat,'%')

    def run(self):                 
        #print('Entered Run------------------------------------')
        #set flag to start downloading
        self.event_get_next_file_to_download.set()
        count=0
        #print('is file:',a_url)
        self.refresh_progress_bar_files_downloaded()
        while not self.killer_event.wait(self.cycle_time):   
            try:
                # Read from the file until end and close it and set Pbar     
                self.download_file()           
                self.update_queue_sizes()
                    
                # if self.event_finished_one_file_download.is_set()==True:                    
                #     self.event_get_next_file_to_download.set()                     
                #     self.event_finished_one_file_download.clear()   
                
                #delay for refreshing in class                                     
                if count>=1000:
                    self.refresh_progress_bar_files_downloaded()
                    count=0
                count=count+1
                if self.download_finished:
                    break           
            except Exception as e:
                self.killer_event.set()
                log.error(e)
                log.error("Stream Queue fatal error! exiting thread!")                                         
                raise  
        if self.download_finished:
            log.info("Successfully downloaded %s Files!",self.number_of_files_to_download)
        if self.killer_event.is_set():
            log.info("Stream Queue Killing event Detected!")    
            log.info("Successfully downloaded %s Files!",self.number_of_files_downloaded)                     
        log.info("File download thread Ended!")  
            
        # self.progress_bar_set_status(self.progress_bar_one_download,0)        
        # self.progress_bar_set_status(self.progress_bar_files_downloaded,100)     
        # self.killer_event.set()   
        # self.quit() 
    
    def add_to_file_queue_from_url_list(self,a_url:str):       
        if not self.is_file_download_finished:
            if a_url is not None:
                #video_info=self.ptf.get_url_info(a_url)
                self.file_queue.put(a_url)

    def update_queue_sizes(self):
        self.file_queue_size=self.file_queue.qsize()
        self.out_queue_size=self.output_queue.qsize()
        # Finished when 
        # self.file_queue_size is empty
        # and self.out_queue_size is self.number_of_files_to_download
        if self.number_of_files_to_download == self.number_of_files_downloaded and self.file_queue_size==0:
            self.download_finished=True
    
    def add_to_output_queue(self): 
        a_url=None       
        try:        
            a_url=self.file_queue.get_nowait()
            self.output_queue.put(a_url)
        except queue.Empty:                    
            pass     
        self.update_queue_sizes()
        sstat=self.get_progress_percentage(self.number_of_files_downloaded,self.number_of_files_to_download,Perini=0,Perend=100)
        self.progress_bar_set_status(self.progress_bar_one_download,sstat)     
        return a_url                   
    
    def Consume_buff(self,doblock=False):
        '''
        returns the text in Buffer. Returns None if buffer empty.
        '''
        txt=None
        #if self.Are_items_in_buffer==True:
        try:
            #txt=self.output_queue.get_nowait()
            txt=self.output_queue.get(block=doblock)
        except queue.Empty:                    
            pass 
        return txt

    def set_files_to_file_queue(self,files_to_download:list):
        """sets the URLs in the list to the queue

        Args:
            files_to_download (list): list of URLs
        """
        if files_to_download is None or self.number_of_files_to_download==0:
            log.error('No files to download!')
            self.quit()
        self.progress_bar_set_status(self.progress_bar_one_download,0)        
        self.progress_bar_set_status(self.progress_bar_files_downloaded,0)                 
        for a_url in files_to_download:
            self.add_to_file_queue_from_url_list(a_url)                
    
    def Get_linelist_from_file(self,filename):        
        linelist=[]
        if filename is not None:            
            log.info('Opening:'+filename)
            try:
                self.plaintextEdit_GcodeScript.clear()
                with open(filename, 'r') as yourFile:                    
                    linelist=yourFile.readlines() #makes list of lines                  
                yourFile.close()                
            except Exception as e:
                log.error(e)
                log.info("File was not read!")
        return linelist    

def main():
    
    kill_ev = threading.Event()
    kill_ev.clear()
    files_to_download=';Test1\n'
    for iii in range(25):
        files_to_download=files_to_download+'G0 X'+str(iii)+'\n'
        files_to_download=files_to_download+'G0 X'+str(-iii)+'\n'    
    cycle_time=0.1
    qstream=queueStream(files_to_download,cycle_time,kill_ev,Refill_value=15,Buffer_size=20)
    qstream.start()
    print('inbuff:',qstream.get_num_of_commands_buff(),'Executed:',qstream.get_num_of_commands_consumed(),'Total:',qstream.get_num_of_total_commands())
    #while not kill_ev.is_set():    
    try:
        while qstream.is_alive()==True:                
            txt=qstream.Consume_buff(True)
            print('inbuff:',qstream.get_num_of_commands_buff(),'Executed:',qstream.get_num_of_commands_consumed(),'Total:',qstream.get_num_of_total_commands())
            if txt != None:
                print(txt)
            time.sleep(0.1)
            if qstream.get_num_of_commands_left()==20:
                qstream.get_all_nums(True)
                kill_ev.set()
                #qstream.join()
            print(qstream.is_alive())    
    except:
        pass

    

    

if __name__ == '__main__':
    main()
