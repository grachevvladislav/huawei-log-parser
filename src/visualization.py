import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import ManualLayout
from parsing import extract_conf, make_dict_tree
from constants import ports_step, ports_delimiter
from fixture import example, data_str
from pprint import pprint


def hide_loader():
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
                    </style>
                    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def file_parsing(uploaded_file):
    try:
        with st.spinner("Loading..."):
            conf = extract_conf(uploaded_file)
        return conf
    except (FileNotFoundError, KeyError) as e:
        st.error(e)
    return {}


def make_link(name, text=None, input=None, output=None):
    if input and output:
        return StreamlitFlowNode(
            name, (1, 0), {'content': text or name},
            draggable=False, node_type='default',
            source_position='bottom', target_position='top'
        )
    if input:
        return StreamlitFlowNode(
            name, (1, 0), {'content': text or name},
            draggable=False, node_type='input', source_position='bottom'
        )
    if output:
        return StreamlitFlowNode(
            name, (1, 0), {'content': text or name},
            draggable=False, node_type='output', source_position='top'
        )


def fix_node_name(name, size):
    size = int(size)
    if size > 155:
        size = 155
    return name.center(size).replace(' ', '\u2003')


def create_block(nodes, tree, current_pos, parent_name='', name=''):
    if not tree:
        current_pos[0] += ports_step
        return 4
    size = 0
    for key, value in tree.items():
        bottom_pos = current_pos.copy()
        bottom_pos[1] += 60
        bottom_size = create_block(nodes, value, bottom_pos, '.'.join([parent_name, key]), key)
        size += bottom_size
        nodes.append(
            StreamlitFlowNode(
                '.'.join([parent_name, key]), tuple(current_pos),
                {'content': fix_node_name(key, bottom_size)},
                style={"font-size": "10px", "font-family": "monospace"},
                draggable=False, node_type='input',
            )
        )
        current_pos[0] = bottom_pos[0]
    return int(size + (len(tree.keys()) - 1) * ports_delimiter)


@st.fragment
def make_graph(data):
    nodes = []
    edges = []
    dict_data = make_dict_tree(data_str)
    y = 0
    for key, value in dict_data.items():
        create_block(nodes, {key: value}, [0, y], '')
        y += 250
    # port_block_size = 130
    # cntrlr_ports = {}
    # current_center = len(data_str) // 2 * port_block_size * -1
    # print(current_center)
    # top_name = "CTE0".center(int(len(data_str) * 8.375))
    # nodes.append(
    #     StreamlitFlowNode(
    #         top_name, (current_center, -100), {'content': top_name},
    #         draggable=False, style={"font-size": "30px"}, node_type='input'
    #     )
    # )
    # nodes.append(
    #     StreamlitFlowNode(
    #         top_name, (current_center, -100), {'content': top_name},
    #         draggable=False, style={"font-size": "30px"}, node_type='input'
    #     )
    # )
    # for channel in data_str:
    #     channel_list = channel.split('->')
    #     full_name = channel_list[0]
    #     port_name = full_name.split('.')[-1].center(4).replace(' ', '\u2003')
    #     cntrlr_ports[port_name] = (current_center, 0)
    #     current_center += port_block_size
    #     data_new.append(channel_list)
    #     nodes.append(
    #         StreamlitFlowNode(
    #             full_name, cntrlr_ports[port_name], {'content': port_name},
    #             draggable=False, style={"font-size": "30px"}, node_type='input'
    #         )
    #     )
    #
    # print(cntrlr_ports)
    # print()

    # pos_x = {}
    # pos_y = 0
    # for pair in data:
    #     for node in pair:
    #         name = node.split('.')
    #         group_name = '.'.join(name[:-1])
    #         pos_x.setdefault(group_name, 0)
    #         pos_x[group_name] += 200
    #
    #         nodes.append(
    #             StreamlitFlowNode(
    #                 node, (pos_x[group_name], pos_y), {'content': node},
    #                 draggable=False, node_type='input'
    #             )
    #         )
    #     pos_y += 100
    #     edges.append(
    #         StreamlitFlowEdge(
    #             f"{pair[0]}-{pair[1]}", str(pair[0]), str(pair[1]),
    #             #label='6666666', label_show_bg=True,
    #             animated=True)
    #     )
    st.session_state.curr_state = StreamlitFlowState(nodes, edges)
    st.session_state.curr_state = streamlit_flow(
        'example_flow', st.session_state.curr_state,
        layout=ManualLayout(),
        style={".rect_fill": "none"},
        fit_view=True,
        hide_watermark=True, allow_zoom=True,
        show_controls=False, pan_on_drag=True,
        get_node_on_click=True,
    )


def show_details():
    for node in st.session_state.curr_state.nodes:
        if node.id == st.session_state.curr_state.selected_id:
            st.write(node.id, node.position, len(node.data['content']))
            return None
    st.write('Тыкни на ноду')


def show_blocks(data):
    s = data['summary']
    st.title(f"{s['System Name']} {s['Product Model']} "
             f"sn:\u00A0{s['Product Serial Number']}")

    for name, value in data.items():
        with st.expander(name):
            st.write(value)

    make_graph(data)
    show_details()