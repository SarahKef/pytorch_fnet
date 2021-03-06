from fnet.data.fnetdataset import FnetDataset
import numpy as np
import torch

from tqdm import tqdm

import pdb



class ChunkDatasetDummy(FnetDataset):
    """Dummy ChunkDataset"""

    def __init__(
            self,
            dataset: FnetDataset,
            dims_chunk,
            random_seed: int = 0,
    ):
        self.dims_chunk = dims_chunk
        self._rng = np.random.RandomState(random_seed)
        self._length = 1234
        self._chunks_signal = 10*self._rng.randn(self._length, *dims_chunk)
        self._chunks_target = 2*self._chunks_signal + 3*self._rng.randn(self._length, *dims_chunk)

    def __getitem__(self, index):
        return (self._chunks_signal[index], self._chunks_target[index])

    def __len__(self):
        return len(self._chunks_signal)

class BufferedPatchDataset(FnetDataset):
    """Dataset that provides chunks/patchs from another dataset."""

    def __init__(self, 
                 dataset,
                 patch_size, 
                 buffer_size = 1,
                 buffer_switch_frequency = 720, 
                 npatches = 100000,
                 verbose = False,
                 transform = None):
        
        self.counter = 0
        
        self.dataset = dataset
        self.patch_size = patch_size
        self.transform = transform
        
        self.buffer_switch_frequency = buffer_switch_frequency
        
        self.npatches = npatches
        
        self.buffer = list()
        
        self.verbose = verbose
        
        shuffed_data_order = np.arange(0, len(dataset))
        np.random.shuffle(shuffed_data_order)
        
        pbar = tqdm(range(0, buffer_size))
                                               
        for i in pbar:
            #convert from a torch.Size object to a list
            if self.verbose: pbar.set_description("buffering images")

            datum_index = shuffed_data_order[i]

            self.buffer.append(dataset[datum_index])

            
    def __len__(self):
        return self.npatches

    def __getitem__(self, index):
        self.counter +=1
        
        if self.counter % self.buffer_switch_frequency == 0:
            if self.verbose: print("Inserting new item into buffer")
                
            self.insert_new_element_into_buffer()
        
        return self.get_random_patch()
                       
    def insert_new_element_into_buffer(self):
        #sample with replacement
                       
        self.buffer.pop(0)
        
        new_datum_index = np.random.randint(len(self.dataset))
                                            
        self.buffer.append(self.dataset[new_datum_index])
        
        if self.verbose: print("Added item {0}".format(new_datum_index))


    def get_random_patch(self):
        
        buffer_index = np.random.randint(len(self.buffer))
                                   
        datum = self.buffer[buffer_index]
                                            
        starts = np.array([np.random.randint(0, d-p) for d, p in zip(datum[0].size(), self.patch_size)])
               
        ends = starts + np.array(self.patch_size)
        
        #thank you Rory for this weird trick
        index = [slice(s, e) for s,e in zip(starts,ends)]

        return [d[tuple(index)] for d in datum]
    
    
def _test():
    # dims_chunk = (2,3,4)
    dims_chunk = (4,5)
    ds_test = ChunkDatasetDummy(
        None,
        dims_chunk = dims_chunk,
    )
    print('Dataset len', len(ds_test))
    for i in range(3):
        print('***** {} *****'.format(i))
        element = ds_test[i]
        print(element[0])
        print(element[1])
    
if __name__ == '__main__':
    _test()
