from mmu import MMU

class LruMMU(MMU):
    def __init__(self, frames):
        # TODO: Constructor logic for LruMMU
        self.frames = frames
        self.frame_table = [{'page': None, 'dirty': False, 'last_used': -1} for _ in range(frames)]
        self.page_table = {}
        self.free_list = list(range(frames))
        self.used_frames = []
        self.time = 0
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0
        self.debug = False

    def set_debug(self):
        # TODO: Implement the method to set debug mode
        self.debug = True

    def reset_debug(self):
        # TODO: Implement the method to reset debug mode
        self.debug = False

    def db_message(self, msg):
        if self.debug:
            print(msg)

    def move_into_frame(self, f, page_number, is_write):
        self.frame_table[f] = {'page': page_number, 'dirty': is_write}
        self.page_table[page_number] = f
        self.disk_reads += 1
        self.frame_table[f]['last_used'] = self.time
        self.time += 1

        self.db_message(f"Loaded page [{page_number}] into frame [{f}]")

    def evict_lru_page(self):
        f = min(self.used_frames, key=lambda fi: self.frame_table[fi]['last_used'])
        victim = self.frame_table[f]
        if victim['dirty']:
            self.disk_writes += 1
            self.db_message(f"Evicting dirty page [{victim['page']}] from frame [{f}] -> disk write")
        else:
            self.db_message(f"Evicting clean page [{victim['page']}] from frame [{f}]")

        if victim['page'] in self.page_table:
            del self.page_table[victim['page']]
        self.frame_table[f] = {'page': None, 'dirty': False, 'last_used': -1}

        return f

    def read_memory(self, page_number):
        # TODO: Implement the method to read memory
        if page_number in self.page_table:
            # HIT
            f = self.page_table[page_number]
            self.frame_table[f]['last_used'] = self.time
            self.time += 1
            self.db_message(f"Page hit.\n\tPage: {page_number}\n\tFrame: {f}\n\tOperation: READ\n\tDirty: {self.frame_table[f]['dirty']}")
            return
        
        # MISS
        self.page_faults += 1
        self.db_message(f"Page miss.\n\tPage: {page_number}\n\tOperation: READ")
        if len(self.free_list) > 0:
            f = self.free_list.pop()
            self.used_frames.append(f)
            self.move_into_frame(f, page_number, is_write = False)
            
        else:
            f = self.evict_lru_page()
            self.move_into_frame(f, page_number, is_write = False)

    def write_memory(self, page_number):
        # TODO: Implement the method to write memory
        if page_number in self.page_table:
            # HIT
            f = self.page_table[page_number]
            self.frame_table[f]['dirty'] = True
            self.frame_table[f]['last_used'] = self.time
            self.time += 1
            self.db_message(f"Page hit.\n\tPage: {page_number}\n\tFrame: {f}\n\tOperation: WRITE\n\tDirty: {self.frame_table[f]['dirty']}")
            return
        
        # MISS
        self.page_faults += 1
        self.db_message(f"Page miss.\n\tPage: {page_number}\n\tOperation: WRITE")
        if len(self.free_list) > 0:
            f = self.free_list.pop()
            self.used_frames.append(f)
            self.move_into_frame(f, page_number, is_write = True)
        else:
            f = self.evict_lru_page()
            self.move_into_frame(f, page_number, is_write = True)

    def get_total_disk_reads(self):
        # TODO: Implement the method to get total disk reads
        return self.disk_reads

    def get_total_disk_writes(self):
        # TODO: Implement the method to get total disk writes
        return self.disk_writes

    def get_total_page_faults(self):
        # TODO: Implement the method to get total page faults
        return self.page_faults
