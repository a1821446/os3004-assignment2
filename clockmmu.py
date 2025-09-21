from mmu import MMU

class ClockMMU(MMU):
#clock page replacement algo using a circular hand and reference bits to approx LRU
    def __init__(self, frames):
        self.frames = frames  #how many frames do we have in physical memory
        self.frame_table = [{'page': None, 'dirty': False, 'ref': 0} for _ in range(frames)]   #info of each frame
        self.page_table = {}  #check if a page is in memory and where 
        self.hand = 0         # clock hand start at 0

        #counters for stats
        self.disk_reads = 0
        self.disk_writes = 0
        self.page_faults = 0

        self.debug = False   #for optional debug printing

    def set_debug(self):
        self.debug = True

    def reset_debug(self):
        self.debug = False

    def db(self, msg):
        if self.debug:
            print(msg)

    def _advance_hand(self):
        #move hand clockwise, wrap around when it hits end 
        self.hand = (self.hand + 1) % self.frames

    def _try_find_free(self):
        #look for empty frame we can use straight away
        for i, fr in enumerate(self.frame_table):
            if fr['page'] is None:
                return i
        return None



    def _install_in_frame(self, idx, page_number, is_write):
        # load a page into the chosen frame
        # evict old one if needed, write back to disk if dirty

        fr = self.frame_table[idx]
        old_page = fr['page']
        if old_page is not None:
            #chuck out old page
            if fr['dirty']:
                self.disk_writes += 1
                self.db(f"-- EVICT page {old_page} from frame {idx} (DIRTY)")
            else:
                self.db(f"-- EVICT page {old_page} from frame {idx} (CLEAN)")
            #remove old mapping
            if old_page in self.page_table and self.page_table[old_page] == idx:
                del self.page_table[old_page]

        # bring the new page in
        self.disk_reads += 1
        fr['page'] = page_number
        fr['dirty'] = bool(is_write)
        fr['ref'] = 1  #mark as recently used
        self.page_table[page_number] = idx
        self.db(f"-- INSTALL page {page_number} into frame {idx} (write={is_write})")

        self._advance_hand()  #move hand on after placing

    def _evict_victim(self):
        # clock algorithm - give second chances to pages with ref=1 (setting ref back to 0)
        #evict a clean page with ref=0 on the first pass
        #if none clean, evict dirty one with ref=0 on the second pass

        for pass_no in (1, 2):
            scanned = 0
            while scanned < self.frames:
                idx = self.hand
                fr = self.frame_table[idx]
                if fr['ref'] == 1:
                    #page recently used, so clear ref and skip this time
                    fr['ref'] = 0
                    self.db(f"-- SCAN frame {idx}: ref=1 → clear to 0")
                else:
                    #ref=0, so it is a candidate
                    if pass_no == 1 and not fr['dirty']:
                        self.db(f"-- VICTIM frame {idx} page {fr['page']} (clean, pass1)")
                        return idx
                    elif pass_no == 2:
                        self.db(f"-- VICTIM frame {idx} page {fr['page']} (pass2)")
                        return idx
                self._advance_hand()
                scanned += 1
        return self.hand  # fallback



    def _ensure_page(self, page_number, is_write):
        ### Check if the page is already in memory. If hit, then update ref/dirty. If miss, handle page default and load it. ###
        if page_number in self.page_table:
            # page hit
            idx = self.page_table[page_number]
            fr = self.frame_table[idx]
            fr['ref'] = 1
            if is_write:
                fr['dirty'] = True
            self.db(f"-- HIT page {page_number} in frame {idx} (write={is_write})")
            return

        #page fault
        self.page_faults += 1
        self.db(f"-- MISS page {page_number} (write={is_write})")
        free = self._try_find_free()
        if free is not None:
            self._install_in_frame(free, page_number, is_write)
        else:
            victim = self._evict_victim()
            self._install_in_frame(victim, page_number, is_write)


#public methods
    def read_memory(self, page_number):
        self._ensure_page(page_number, False)

    def write_memory(self, page_number):
        self._ensure_page(page_number, True)


#stats
    def get_total_disk_reads(self):
        return self.disk_reads

    def get_total_disk_writes(self):
        return self.disk_writes

    def get_total_page_faults(self):
        return self.page_faults

        