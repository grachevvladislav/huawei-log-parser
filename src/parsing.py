import re
import tarfile
from io import BytesIO

from exceptions import ExtractFail
from fixture import data_str, names_example


def fix_values(data: dict[dict]) -> None:
    keys_to_remove = []
    new_items = {}
    for key, value in data.items():
        if not value:
            math = re.search(r"[:=](?!.*[:=])", key)
            if math:
                delimiter_pos = math.start()
                new_items[key[:delimiter_pos].strip()] = key[
                    delimiter_pos + 1 :
                ].strip()
            else:
                new_items[key.strip()] = ""
            keys_to_remove.append(key)
        else:
            fix_values(value)

    if len(keys_to_remove) != len(new_items.keys()):
        raise KeyError(
            f"Ошибка при создании словаря. Дублируются ключи: " f"{str(keys_to_remove)}"
        )
    for key in keys_to_remove:
        del data[key]
    data.update(new_items)


def extract_to_dict(
    lines: list[str],
    start_line: int = 0,
    start_pattern: str = None,
    end_pattern: str = None,
) -> tuple[dict, int]:
    if start_pattern and start_line:
        raise ExtractFail("Одновременно заданы параметры start_line и start_pattern")
    result = {}
    stack = [(result, -1)]
    if start_pattern:
        for line, start_line in zip(
            lines[start_line:], range(start_line, len(lines) + 1)
        ):
            if re.match(start_pattern, line):
                break

    for line, number in zip(lines[start_line:], range(start_line, len(lines) + 1)):
        if re.match(end_pattern, line):
            break
        indent_level = len(line) - len(line.lstrip(" "))
        line_content = re.sub(r"^[\-\#]+|[\-\#]{3,}$", "", line.strip()).strip()
        if line_content == "":
            continue
        while stack and indent_level <= stack[-1][1]:
            stack.pop()
        current_dict = stack[-1][0]
        current_dict[line_content] = {}
        stack.append((current_dict[line_content], indent_level))
    fix_values(result)
    return result, number


def extract_conf(file: BytesIO) -> dict[str, dict]:
    """Extracting a configuration into a dictionary."""
    with tarfile.open(fileobj=file) as tar:
        if "Config/Config.tgz" not in tar.getnames():
            raise FileNotFoundError(
                "Не найден файл Config/Config.tgz. "
                "Убедитесь, что контроллер активен."
            )
        config_tar = tar.extractfile("Config/Config.tgz")
        with tarfile.open(fileobj=config_tar) as conf_tar:
            if "config.txt" not in conf_tar.getnames():
                raise FileNotFoundError("Не найден файл Config/Config.tgz/config.txt")
            conf_by_line = (
                conf_tar.extractfile("config.txt").read().decode("utf-8").split("\n")
            )
    summary, key = extract_to_dict(
        conf_by_line, start_pattern="^.{0,}SUMMARY--", end_pattern=r"^.{0,}License--"
    )
    result = {"summary": summary["SUMMARY"]}
    return result


def get_sas_data(data):
    """Creates a list of ports and links."""
    links, ports = data_str, names_example
    return links, ports


# def get_block(data, start_line: int, end_patterns=[], delimiters=[':', '=']):
#     result = {}
#     for index in range(start_line + 1, len(data)):
#         line = data[index]
#         for pattern in end_patterns:
#             if pattern in line:
#                 break
#
#         for delimeter in delimiters:
#             if leftPart(line, delimeter).upper() == key_search.upper():
#                 key = leftPart(line, delimeter)
#                 key_value = rightPart(line, delimeter)
#                 result[key_value] = {}
#                 break
#
#         for delimeter in delimiters:
#             for clmn in colum ns:
#                 if leftPart(line, delimeter) == columns[clmn]['search']:
#                     try:
#                         prefix_str = result[key_value][columns[clmn]['field']]
#                     except:
#                         prefix_str = ''
#                     if prefix_str != '':
#                         result[key_value][
#                             columns[clmn]['field']] = prefix_str + ', ' + chr(
#                             10) + rightPart(line, delimeter)
#                     else:
#                         result[key_value][columns[clmn]['field']] = rightPart(
#                             line, delimeter)
#
#     return index, result


# if not isinstance(tree, dict):
#     for port in tree:
#         nodes.append(
#             StreamlitFlowNode(
#                 parent_name+port, tuple(current_pos),
#                 {'content': fix_node_name(port, 4)},
#                 style={"font-size": "10px", "font-family": "monospace"},
#                 draggable=False, node_type='input',
#             )
#         )
#         current_pos[0] += ports_step
#     return int(len(tree) * 4 + (len(tree) - 1) * ports_delimiter)
