import numpy as np
import os
from matplotlib import pyplot as mat_plot

def find_red_pixels(map_filename: str, upper_threshold = 100, lower_threshold = 50) -> np.ndarray:
    """
    Finds all red pixels in an rgb image, and outputs a greyscale jpg image (map_red_pixels.jpg)
    where only red pixels are white to CWD

    @param map_file: Name of rgb image file in data directory of CWD
    @param upper_threshold: Upper rgb threshold (0-255) for evaluating if a pixel is red
    @param lower_threshold: Lower rgb threshold (0-255) for evaluating if a pixel is red

    @returns: A binary array representation of the greyscale image outputed. White pixels are 1 and black pixels are 0.
    """

    rgb_img = mat_plot.imread(os.path.join(os.path.dirname(__file__), 'data', map_filename))
    rgb_img = rgb_img * 255
    gs_img = []

    for row in rgb_img:
        for pixel in row:
            #if RGB values make pixel red according to thresholds
            if all((pixel[0] > upper_threshold, pixel[1] < lower_threshold, pixel[2] < lower_threshold)):
                gs_img.append(True)
            else:
                gs_img.append(False)
    
    gs_img = np.reshape(gs_img, rgb_img.shape[0:2])
    mat_plot.imsave(os.path.join(os.path.dirname(__file__), 'map_red_pixels.jpg'), gs_img, cmap = mat_plot.cm.gray)
    return(gs_img)


def find_cyan_pixels(map_filename: str, upper_threshold = 100, lower_threshold = 50) -> np.ndarray:
    """
    Finds all cyan pixels in an rgb image, and outputs a greyscale jpg image (map_cyan_pixels.jpg) 
    where only cyan pixels are white to CWD

    @param map_file: Name of rgb image file in data directory of CWD
    @param upper_threshold: Upper rgb threshold (0-255) for evaluating if a pixel is cyan
    @param lower_threshold: Lower rgb threshold (0-255) for evaluating if a pixel is cyan

    @returns: A binary array representation of the greyscale image outputed. White pixels are 1 and black pixels are 0.
    """
    
    rgb_img = mat_plot.imread(os.path.join(os.path.dirname(__file__), 'data', map_filename))
    rgb_img = rgb_img * 255
    gs_img = []

    for row in rgb_img:
        for pixel in row:
            #if RGB values make pixel cyan according to thresholds
            if all((pixel[0] < lower_threshold, pixel[1] > upper_threshold, pixel[2] > upper_threshold)):
                gs_img.append(True)
            else:
                gs_img.append(False)
    
    gs_img = np.reshape(gs_img, rgb_img.shape[0:2])
    mat_plot.imsave(os.path.join(os.path.dirname(__file__), 'map_cyan_pixels.jpg'), gs_img, cmap = mat_plot.cm.gray)
    return(gs_img)


def detect_connected_components(gs_img: np.ndarray) -> np.ndarray:
    """
    Detects connected components in binary array representation of a greyscale image (continuous areas of white)
    Records size and number of connected components in text file (cc-output-2a.txt) outputted to CWD

    @param gs_img: A binary array representation of the greyscale image. White pixels are 1 and black pixels are 0.

    @return mark: An array representation of connected component locations in greyscale image

    @algorithm_improvements: At start of new queue, segment_no is increased by 1 and initial index of queue 
    head is stored. Instead of marking all connected pixels as 1 in MARK, connected pixels are marked with 
    segment_no. When queue is emptied, subtracting initial queue head indexe from final queue head indexes gives 
    segment size. Each pixel in mark is a list of length 2. Size of each segment stored at pixel list index 0, at 
    pixel [segment_no - 1] in MARK (if mark was a flat list). E.g., pixel 233 = [own segment number or 0, the 
    size of segment 233]. Thus, the segment every connected pixel belongs to, and size of every segment is 
    contained in MARK. No summation functions are needed.
    """

    mark = np.zeros(list(gs_img.shape) + [2], dtype = int)
    queue = np.zeros((gs_img.size,2), dtype = int)
    current_head = 0
    tail = 0
    MAX_X = gs_img.shape[1] - 1
    MAX_Y = gs_img.shape[0] - 1
    segment_no = 1
    segment_lengths = {}

    for index, pixel in np.ndenumerate(gs_img):
            if pixel and mark[index][0] == 0:
                mark[list(index) + [0]] == segment_no
                queue[tail] =  index
                tail = tail + 1
                initial_head = current_head

                while current_head < tail:
                    x = queue[current_head][1]
                    y = queue[current_head][0]
                    current_head = current_head + 1

                    #find indexes of all neighbours of a pixel
                    neighbours = [(x2, y2) for x2 in range(x-1, x+2)
                               for y2 in range(y-1, y+2)
                               if ((x != x2 or y != y2) and
                                   (0 <= x2 <= MAX_X) and
                                   (0 <= y2 <= MAX_Y))]
                    
                    #check if neighbours are red and unmarked
                    for n in neighbours:
                        if gs_img[n[1], n[0]] and mark[n[1], n[0], 0] == 0:
                            mark[n[1], n[0], 0] = segment_no
                            queue[tail] = n[1::-1]
                            tail = tail + 1

                segment_lengths[segment_no] = current_head - initial_head - 1
                mark.flat[segment_no - 1] = current_head - initial_head - 1
                segment_no = segment_no + 1
    
    output = open(os.path.join(os.path.dirname(__file__), 'cc-output-2a.txt'), 'w+')
    output.writelines(['Connected Component ' + str(key) + ', number of pixels = ' + str(value) +'\n' for key, value in segment_lengths.items()])
    output.write('Total number of connected components = ' + str(segment_no - 1))
    output.close()    
    return mark

def detect_connected_components_sorted(mark: np.ndarray) -> None:
    """
    Gets segments numbers and sizes from MARK. Sorts segments numbers by size. Outputs ordered text file (cc_top_2.jpg) to CWD.

    @param mark: An array representation of connected component locations and sizes in greyscale image
    """
    
    segment_lengths = []

    #iterate through all segment sizes
    for n in range(mark.size):
        if mark.flat[n] == 0:
            break
        else:
            segment_lengths.append([n + 1, mark.flat[n]])
    
    def partition(unsorted_list: list, lower: int, upper: int) -> int:
        '''
        Compare and sort the items in a list compared to a pivot, biggest to smallest.

        @param unsorted_list: List to be sorted
        @param lower: Index marking the lower boundary of the segment to be sorted
        @param upper: Index marking the upper boundary of the segment to be sorted

        @return: The middle index of the segment
        '''
        
        pivot = unsorted_list[upper][1]
        i = lower - 1

        for j in range(lower, upper):
            if unsorted_list[j][1] >= pivot:
                i = i + 1
                (unsorted_list[i], unsorted_list[j]) = (unsorted_list[j], unsorted_list[i])
        (unsorted_list[i + 1], unsorted_list[upper]) = (unsorted_list[upper], unsorted_list[i + 1])
        return i + 1

    def quicksort(unsorted_list: list, lower: int, upper: int) -> None:
        '''
        (Implements QuickSort) Iteratively calls itself and partitions unsorted list into smaller segments to 
        be sorted untill list is ordered.
        
        @param unsorted_list: List to be sorted
        @param lower: Index marking the lower boundary of the segment to be sorted
        @param upper: Index marking the upper boundary of the segment to be sorted
        '''

        if lower < upper:
            p = partition(unsorted_list, lower, upper)
            quicksort(unsorted_list, lower, p - 1)
            quicksort(unsorted_list, p + 1, upper)
       
    quicksort(segment_lengths, 0, len(segment_lengths) - 1)
    output = open(os.path.join(os.path.dirname(__file__), 'cc-output-2b.txt'), 'w+')
    output.writelines(['Connected Component ' + str(segment_lengths[i][0]) + ', number of pixels = ' + str(segment_lengths[i][1]) +'\n' for i in range(len(segment_lengths))])
    output.write('Total number of connected components = ' + str(len(segment_lengths)))
    output.close()
    
    top_two = np.logical_or(mark[:,:,0:1] == segment_lengths[0][0], mark[:,:,0:1] == segment_lengths[1][0])
    top_two = np.reshape(top_two, top_two.shape[0:2])
    mat_plot.imsave(os.path.join(os.path.dirname(__file__), 'cc_top_2.jpg'), top_two, cmap = mat_plot.cm.gray)