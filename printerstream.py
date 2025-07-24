import socket
import threading
import struct
import time
from collections import defaultdict
import queue

class UDPVideoReceiver:
    def __init__(self, port=9999):
        self.port = port
        self.running = False

        

    def start(self):
        if self.running:
            print("Receiver already running")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', self.port))
        except OSError as e:
            print(f"Failed to bind socket: {e}")
            self.stop()  # Force cleanup if previous session was half-dead
            time.sleep(0.5)  # Let OS release port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', self.port))

        self.running = True
        self.frame_chunks = defaultdict(dict)
        self.frame_queue = queue.Queue(maxsize=5)
        self.receiver_thread = threading.Thread(target=self._receive_frames, daemon=True)
        self.receiver_thread.start()
        print(f"UDP receiver started on port {self.port}")
        
    def _receive_frames(self):
        """Receive and reconstruct frames from UDP chunks"""
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65536)
                
                # Parse header
                chunk_id, total_chunks = struct.unpack('!II', data[:8])
                chunk_data = data[8:]
                
                # Create frame key (use timestamp to handle multiple concurrent frames)
                frame_key = f"{addr}_{total_chunks}"
                
                # Store chunk
                self.frame_chunks[frame_key][chunk_id] = chunk_data
                
                # Check if we have all chunks for this frame
                if len(self.frame_chunks[frame_key]) == total_chunks:
                    # Reconstruct frame
                    frame_data = b''
                    for i in range(total_chunks):
                        frame_data += self.frame_chunks[frame_key][i]
                    
                    # Add to frame queue
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame_data, block=False)
                    else:
                        # Drop old frame
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put(frame_data, block=False)
                        except queue.Empty:
                            pass
                    
                    # Clean up old chunks
                    del self.frame_chunks[frame_key]
                    
                    # Clean up very old incomplete frames (prevent memory leak)
                    current_time = time.time()
                    keys_to_remove = []
                    for key in self.frame_chunks:
                        if len(self.frame_chunks[key]) == 0:
                            keys_to_remove.append(key)
                    for key in keys_to_remove:
                        del self.frame_chunks[key]
                        
            except Exception as e:
                if self.running:
                    print(f"Receive error: {e}")
                
    def get_frame(self):
        """Get latest frame"""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
            
    def stop(self):
        if not self.running:
            return
        print("Stopping video receiver")
        self.running = False
        try:
            self.sock.close()
        except Exception:
            pass
        self.sock = None
        self.receiver_thread = None

