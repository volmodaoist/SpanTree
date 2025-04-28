from tracespantree.collections import SpanTree
from tracespantree.utils import io, ploter


if __name__ == '__main__':
    d1 = io.open_json(fname="demo1", file_dir=".")    
    
    spans = {span['span_id']: span for span in d1['spans']}
    tree = SpanTree(spans = d1['spans'])
    
    ploter.visualize_trace(spans)

    
    