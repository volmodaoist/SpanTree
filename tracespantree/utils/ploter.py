
import matplotlib.pyplot as plt
import networkx as nx

from tracespantree.collections import MultiNestDict, KVTree


# 生成树并可视化
def visualize_trace(spans, title = "untitle"):
    G = nx.DiGraph()

    #  spans 之中每个节点作为图的节点
    for span_id, span in spans.items():
        G.add_node(span_id, label=span['name'])

    # spans 之中的父子关系作为图连边
    for span_id, span in spans.items():
        parent_span_id = span['parent_id']
        if parent_span_id:
            G.add_edge(parent_span_id, span_id)

    # 使用 graphviz_layout 来生成按层次排序的布局，确保父子节点关系在可视化时是上下结构
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

    # 绘制图
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'), node_size=2000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)

    # 显示图
    plt.title("Trace Mock Visualization")
    plt.savefig(f"{title}.png")