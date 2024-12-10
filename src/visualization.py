import re
from io import BytesIO
from typing import Union

import networkx as nx
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowEdge, StreamlitFlowNode
from streamlit_flow.layouts import ManualLayout
from streamlit_flow.state import StreamlitFlowState

from constants import (
    chars_to_px_factor,
    node_x_step,
    node_y_step,
    port_y_size,
    port_y_step,
)
from exceptions import DeterminingDirectionFail, ParsingFail
from parsing import extract_conf, parse_to_dict, example


def hide_loader() -> None:
    hide_streamlit_style = """
                    <style>
                    div[data-testid="stToolbar"] {
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                    }
                    div[data-testid="stDecoration"] {
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                    }
                    div[data-testid="stStatusWidget"] {
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                    }
                    #MainMenu {
                    visibility: hidden;
                    height: 0%;
                    }
                    header {
                    visibility: hidden;
                    height: 0%;
                    }
                    footer {
                    visibility: hidden;
                    height: 0%;
                    }
                    div[data-testid="stStatusWidget"] {
                    visibility: hidden;
                    height: 0%;
                    position: fixed;
                    }
                    # [data-testid="stMetricValue"] {
                    # font-size: 10px;
                    # }
                    # [data-testid="stMetricLabel"] {
                    # font-size: 50px;
                    # }
                    [data-testid="stVerticalBlockBorderWrapper"] {
                    position: sticky;
                    top: 0;
                    #background-color: #f9f9f9;
                    padding: 10px;
                    #order-bottom: 2px solid #ddd;
                    #z-index: 1000;
                    }
                    </style>
                    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def zip_file_parsing(uploaded_file: BytesIO) -> dict[str, dict]:
    """Screen saver for unpacking archive."""
    try:
        with st.spinner("Loading..."):
            lines_conf = extract_conf(uploaded_file)
            conf = parse_to_dict(lines_conf)
        return conf
    except (FileNotFoundError, KeyError) as e:
        st.error(e)
    return {}


def fix_node_name(name: str, size: Union[int, float]) -> str:
    size = int(size)
    if size > 155:
        size = 155
    return name.center(size).replace(" ", "\u2003")


def create_block(
    nodes: list[StreamlitFlowNode],
    pos: list[int],
    ports_list: list[str],
    links: dict[str, str],
) -> int:
    """
    Creating SLF block with ports by coordinates.
    :param nodes: SLF nodes list.
    :param pos: Left center pos of node.
    :param ports_list: List of node ports.
    :param links:
    :return: Node size along Y axis.
    """
    ports_list.sort()
    max_len = 0
    for port in ports_list:
        current = len(port)
        if current > max_len:
            max_len = current
    pos[1] -= (len(ports_list) * (port_y_size + port_y_step) + port_y_step) / 2
    for port in ports_list:
        if any(port in line for line in links.keys()):
            direction = 0
        elif any(port in line for line in links.values()):
            direction = 1
        elif any(line in port for line in ["CTE", "EXP"]):
            direction = 0
        elif "PRI" in port:
            direction = 1
        else:
            raise DeterminingDirectionFail(
                f"Не удалось определить направление для {port}"
            )
        nodes.append(
            StreamlitFlowNode(
                port,
                tuple(pos),
                {"content": fix_node_name(port, max_len)},
                style={"font-size": "10px", "font-family": "monospace"},
                node_type=["input", "output"][direction],
                source_position="right",
                target_position="left",
                draggable=False,
            )
        )
        pos[1] += port_y_size + port_y_step
    return int(chars_to_px_factor * max_len)


def get_branch_name(enclosure_name) -> str:
    """
    Getting the branch name from a template.
    :param enclosure_name: Enclosure name
    :return: Branch name
    """
    match = re.match(r"([^.0-9]+\d{1,2})(.*)$", enclosure_name)
    return match.group(1)


def get_node_name(name) -> str:
    """
    Getting the node name from a template.
    :param name: Enclosure name
    :return:Node name
    """
    return name.split(".")[0]


def make_state(
    links: list[str],
    ports_list: list[str],
) -> (int, StreamlitFlowState):
    """
    Creating a list of links and SLF links.
    :param links: List of link chains.
    :param ports_list: List of all ports, including inactive ones.
    :return: (Dictionary source: destination, StreamlitFlowEdge list)
    """
    directions = {}
    slf_edges = []
    slf_nodes = []
    G = nx.DiGraph()

    for line in links:
        list_line = line.split("->")
        if len(list_line) < 2:
            G.add_node(get_node_name(list_line[0]))
            continue
        for i in range(0, len(list_line), 2):
            directions[list_line[i]] = list_line[i + 1]
            G.add_edge(get_node_name(list_line[i]), get_node_name(list_line[i + 1]))
            slf_edges.append(
                StreamlitFlowEdge(
                    f"{list_line[i]}-{list_line[i+1]}",
                    list_line[i],
                    list_line[i + 1],
                    # label='6666666', label_show_bg=True,
                    animated=True,
                    focusable=True,
                )
            )

    input_nodes = [node for node in G.nodes if G.in_degree(node) == 0]

    ports_by_nodes = {}
    for port in ports_list:
        node_name = get_node_name(port)
        branch_name = get_branch_name(port)
        if branch_name not in ports_by_nodes.keys():
            ports_by_nodes[branch_name] = {}

        if node_name not in ports_by_nodes[branch_name].keys():
            ports_by_nodes[branch_name][node_name] = [
                port,
            ]
        else:
            ports_by_nodes[branch_name][node_name].append(port)

    max_ports_in_node = 0
    for nodes in ports_by_nodes.values():
        for node, ports in nodes.items():
            if node in input_nodes:
                continue
            if len(ports) > max_ports_in_node:
                max_ports_in_node = len(ports)
    largest_node = (
        max_ports_in_node * port_y_size + (max_ports_in_node - 1) * port_y_step
    )
    input_lt_pos = [0, 0]
    for input_node in input_nodes:
        linked_branches = sorted(
            list(set(get_branch_name(x) for x in G.successors(input_node)))
        )
        branches_x_size = (
            len(linked_branches) * (largest_node + node_y_step) + node_y_step
        )
        input_node_x_size = (
            len(ports_by_nodes[input_node][input_node]) * (port_y_size + port_y_step)
            + port_y_step
        )
        cte_size = max(branches_x_size, input_node_x_size)

        input_lt_pos[1] += port_y_step
        input_size = create_block(
            slf_nodes,
            [input_lt_pos[0], input_lt_pos[1] + cte_size / 2],
            ports_by_nodes[get_branch_name(input_node)][get_node_name(input_node)],
            directions,
        )
        y_tree_counter = [
            input_lt_pos[0] + input_size + node_x_step * 2,
            input_lt_pos[1]
            + (cte_size - branches_x_size + largest_node) / 2
            + node_y_step,
        ]
        for branch in linked_branches:
            x_tree_counter = y_tree_counter.copy()
            for child_node in ports_by_nodes[branch].values():
                node_size = create_block(
                    slf_nodes, x_tree_counter.copy(), child_node, directions
                )
                x_tree_counter[0] += node_size + node_x_step
            y_tree_counter[1] += largest_node + node_y_step
        input_lt_pos[1] += cte_size - port_y_step
    return input_lt_pos[1], StreamlitFlowState(slf_nodes, slf_edges)


@st.fragment
def sas_graph(data: list[str]) -> None:
    links_seq, ports = [], []
    sas_info = {}
    for block in data:
        if block[0][0] != 'ID':
            raise ParsingFail('Не найдено поле ID для одного из SAS линков.')
        id = block[0][1]
        ports.append(id)
        sas_info[id] = []
        for pair in block:
            sas_info[id].append(pair)
            if 'Cascade Info' == pair[0]:
                links_seq.append(pair[1])
    size, state = make_state(links_seq, ports)
    col1, col2 = st.columns([3, 2])
    with col1:
        st.session_state.curr_state = streamlit_flow(
            "example_flow",
            state,
            layout=ManualLayout(),
            fit_view=True,
            hide_watermark=True,
            allow_zoom=True,
            show_controls=False,
            get_node_on_click=True,
            min_zoom=0.8,
            height=size + 100,
        )

    with col2:
        container = st.container(border=True)
        with container:
            show_details(sas_info)


def show_details(info: dict):
    selected_id = st.session_state.curr_state.selected_id
    if selected_id in info.keys():
        st.text('\n'.join(': '.join(x) for x in info[selected_id]))
        return None
    st.write("Выбери порт")


def make_page(data):
    tab1, tab2, tab3 = st.tabs(["Summary", "License", "SAS Port"])

    with tab1:
        st.write('')
    with tab2:
        st.write('fffffffffffff')
    with tab3:
        sas_graph(data["sas_ports"])
