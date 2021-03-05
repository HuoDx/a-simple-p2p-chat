import socket
import threading
import multiprocessing
import queue
from snuf_release.utils import serialization
import time

class ThreadStopSignal:
    pass
class MaintainenceThreads:
   
    
    @staticmethod
    def recv_process(server_info, output_event_queue):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((server_info[0], server_info[1]))
        print('Server ok.')
        while True:
            data, address = server_socket.recvfrom(server_info[2])
            output_event_queue.put((data, address))
               
        
    @staticmethod
    def parsing_thread(input_event_queue: queue.Queue, output_event_queue: queue.Queue):
        while True:
            if not input_event_queue.empty():
                
                event = input_event_queue.get()
            else:
                time.sleep(1/1000)
                continue
   
            if event == ThreadStopSignal:
                break
            
            message = serialization.deserialize(event[0])
            message.update({
                'from': event[1][0]
            })
            output_event_queue.put(message)
            
    @staticmethod          
    def processing_thread(input_event_queue: queue.Queue, callback_function):
        if callback_function is None:
            raise Exception('Callback function is null in processing thread.')
        while True:
            if not input_event_queue.empty():
                event = input_event_queue.get()
            else:
                time.sleep(1/1000)
                continue

            if event == ThreadStopSignal:
                break
        
            callback_function(event)
            
class SNUF:
    
    def __init__(self, host = '0.0.0.0', port = 5000, buffer_size = 1024 ** 3):
        self.server_info = (
            host,
            port,
            buffer_size
        )
        self.callback_method = None
        
    
    def on_message(self, func):
        if func is None:
            raise Exception('Callback is null.')
        
        self.callback_method = func   
    
    def run(self):
        self.parsing_queue = multiprocessing.Queue(-1)
        self.processing_queue = queue.Queue(-1)

        
        self._recv_process = multiprocessing.Process(
            target=MaintainenceThreads.recv_process, 
            args=(
                self.server_info,
                self.parsing_queue
            )
        )
        
        self.parsing_thread = threading.Thread(target=MaintainenceThreads.parsing_thread, args=(
            self.parsing_queue,
            self.processing_queue
        ))
        
        self.processing_thread = threading.Thread(target=MaintainenceThreads.processing_thread, args=(
            self.processing_queue,
            self.callback_method
        ))
        
        self.processing_thread.start()
        self.parsing_thread.start()
        self._recv_process.start()
        
    def stop(self):
        self.processing_queue.put(ThreadStopSignal)
        print('Signal injected, waiting for thread [process thread] to stop.')
        self.processing_thread.join()
        print('Thread [process thread] stopped.')
        
        self.parsing_queue.put(ThreadStopSignal)
        print('Signal injected, waiting for thread [parsing thread] to stop.')
        self.parsing_thread.join()
        print('Thread [parsing thread] stopped.')
        
        # here we have to force it.
        self._recv_process.terminate()
        print('All threads stopped.')


# snuf = SNUF()

# @snuf.on_message
# def see_message(msg):
#     print(msg)
    
# if __name__ == '__main__':
#     snuf.run()
    
    
    