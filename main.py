import heapq
import argparse
from typing import Tuple

class HuffmanNode:
    def __init__(self, freq: int, l_child=None, r_child=None, content=None):
        self._children = {'l': l_child, 'r': r_child}
        self._content= content
        self._freq = freq

    def __eq__(self, other):
        if isinstance(other, HuffmanNode):
            return self._freq == other._freq
        raise ValueError (f"Cannot compare HuffmanNode and {type(other)}")
    
    def __lt__(self, other):
        if isinstance(other, HuffmanNode):
            return self._freq < other._freq
        raise ValueError (f"Cannot compare HuffmanNode and {type(other)}")
    
    def __repr__(self):
        return f"HNode: freq {self._freq} {'*' if self._content is None else self._content}" \
               f"| l: {self.get_child('l').__repr__()}, r: {self.get_child('r').__repr__()}"
        
    def get_child(self, side: str):
        if not side in ['l', 'r']:
            raise ValueError ("You must pick either child 'l' or child 'r'.")
        
        return self._children[side]
    
    def is_leaf(self) -> bool:
        return self._children['l'] is None and self._children['r'] is None


def gen_huffman_tree(heap: heapq) -> HuffmanNode:
    while len(heap) >= 2:
        # popping smallest two items
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)

        # combining smallest trees into a node and adding it to the heap
        heapq.heappush(heap, HuffmanNode(freq = node1._freq + node2._freq, l_child=node1, r_child=node2))
    
    return heapq.heappop(heap)


def get_huffman_code(val, huffman_tree: HuffmanNode) -> Tuple[bool, bytes]:
    # this function assumes no duplicate content in the huffman tree

    if huffman_tree.is_leaf():
        return (val == huffman_tree._content, b'')
    
    if huffman_tree.get_child('l') is not None: 
        contain, code = get_huffman_code(val, huffman_tree.get_child('l'))
        if contain:
            return True, b'0' + code
        
    if huffman_tree.get_child('r') is not None:
        contain, code = get_huffman_code(val, huffman_tree.get_child('r'))
        if contain:
            return True, b'1' + code
    
    return False, b''


def compress_file(file, huffman_tree: HuffmanNode) -> bytes:
    file_cmprssd = b''
    for line in file:
        for char in line:
            contained, code = get_huffman_code(char, huffman_tree)

            if not contained:
                raise Exception(f"{char} not in Tree something went horribly wrong.")
            
            file_cmprssd += code

    return file_cmprssd


def get_quantitative_heap(file) -> list:
    # get a count of all characters in the file
    character_counts = {}
    for line in file:
        for char in line:
            if char in character_counts.keys():
                character_counts[char] += 1
            else:
                character_counts[char] = 1

    # construct min-heap 
    counts_heap = []
    for char in character_counts.keys():
        heapq.heappush(counts_heap, HuffmanNode(freq=character_counts[char], content=char))
    
    return counts_heap


def get_next_val(file: list[bytes], huffman_tree: HuffmanNode):
    if len(file) == 0:              # no more bits to read
        return [], None
    if huffman_tree.is_leaf():      # leaf so search has ended
        return file, huffman_tree._content
    if len(bytes(file[0])) == 0:    # this line is empty moving to next line
        return get_next_val(file[1:], huffman_tree)
    
    bit = bytes(file[0])[0] - 48    # it implicitely interprets the bit as a char and converts to an int

    if bit == 0:
        # go into left branch
        return get_next_val([bytes(f)[1:] for f in file], huffman_tree.get_child('l'))
    elif bit == 1:
        # go into right branch
        return get_next_val([bytes(f)[1:] for f in file], huffman_tree.get_child('r'))
    else:
        raise ValueError ("Something went very wrong")
    

def files_equal(file1, file2):
    with open(file1, 'r') as f1:
        with open(file2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()
            i = 0
            while i < min(len(lines1), len(lines2)):
                if lines1[i] != lines2[i]:
                    print(f"original:\n{lines1[i]}\npost-compression:\n{lines2[i]}")
                    raise Exception ("inequality detected")
                i += 1

def main():
    # get name of file to compress
    parser = argparse.ArgumentParser(description='Huffman compressor')

    parser.add_argument('-f', '--file', type=str, help='file to compress')

    args = parser.parse_args()

    HuffmanTree = None
    file_cmprssd = b''
    file_de_cmprssd = ""

    # reading the file and generating the HuffmanTree and compress the file
    with open(args.file, 'rb') as file:
        lines = file.readlines()
        print(f"file is {sum([len(line) for line in lines]) * 8} bits long")

        # creating the huffman tree
        counts_heap = get_quantitative_heap(lines)
        HuffmanTree = gen_huffman_tree(counts_heap)

        # compressing the file
        file_cmprssd = compress_file(lines, HuffmanTree)

        # TODO encoding the huffman tree
        

    print(f"file compressed is {len(file_cmprssd)} bits long")

    # writing compressed version to a file
    name, affix = args.file.split('.')
    with open(f"{name}_compressed.{affix}", 'wb') as file:
        file.write(file_cmprssd)

    # reading the dompressed file and decompressing it
    with open(f"{name}_compressed.{affix}", 'rb') as file:
        lines = file.readlines()

        # TODO decoding huffman tree
        
        # decompressing file
        lines, val = get_next_val(lines, HuffmanTree)
        while val is not None:
            file_de_cmprssd += chr(val)
            lines, val = get_next_val(lines, HuffmanTree)
        file_de_cmprssd = file_de_cmprssd.replace("\r\n", "\n")

    print(f"file decompressed is {len(file_de_cmprssd) * 8} bits long")

    
    # writing decompressed version to a file
    name, affix = args.file.split('.')
    with open(f"{name}_de_compressed.{affix}", 'w') as file:
        file.write(file_de_cmprssd)

    # check for equality
    files_equal(args.file, f"{name}_de_compressed.{affix}")
    print("compression succesfull and verified")
    


if __name__ == '__main__':
    main()
