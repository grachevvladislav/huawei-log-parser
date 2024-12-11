import re
import tarfile
from io import BytesIO

# from exceptions import ExtractFail


# def fix_values(data: dict[dict]) -> None:
#     keys_to_remove = []
#     new_items = {}
#     for key, value in data.items():
#         if not value:
#             math = re.search(r"[:=](?!.*[:=])", key)
#             if math:
#                 delimiter_pos = math.start()
#                 new_items[key[:delimiter_pos].strip()] = key[
#                     delimiter_pos + 1 :
#                 ].strip()
#             else:
#                 new_items[key.strip()] = ""
#             keys_to_remove.append(key)
#         else:
#             fix_values(value)
#
#     if len(keys_to_remove) != len(new_items.keys()):
#         raise KeyError(
#             f"Ошибка при создании словаря. Дублируются ключи: " f"{str(keys_to_remove)}"
#         )
#     for key in keys_to_remove:
#         del data[key]
#     data.update(new_items)
#
#
# def extract_to_dict(
#     lines: list[str],
#     start_line: int = 0,
#     start_pattern: str = None,
#     end_pattern: str = None,
# ) -> tuple[dict, int]:
#     """
#
#     :param lines: Strings for parsing.
#     :param start_line: Start line number.
#     :param start_pattern: First line pattern.
#     :param end_pattern: Last line pattern.
#     :return: Result dict. Line number matching the final pattern.
#     """
#     if start_pattern and start_line:
#         raise ExtractFail(
#             "Одновременно заданы параметры start_line и start_pattern")
#     result = {}
#     stack = [(result, -1)]
#     if start_pattern:
#         for line, start_line in zip(lines, range(len(lines) + 1)):
#             if re.match(start_pattern, line):
#                 break
#
#     number = 0
#     for line, number in zip(lines[start_line:], range(start_line, len(lines) + 1)):
#         if re.match(end_pattern, line):
#             break
#         indent_level = len(line) - len(line.lstrip(" "))
#         line_content = re.sub(r"^[\-\#]+|[\-\#]{3,}$", "", line.strip()).strip()
#         if line_content == "":
#             continue
#         while stack and indent_level <= stack[-1][1]:
#             stack.pop()
#         current_dict = stack[-1][0]
#         current_dict[line_content] = {}
#         stack.append((current_dict[line_content], indent_level))
#     fix_values(result)
#     return result, number


def extract_conf(file: BytesIO) -> list[str]:
    """
    Extracting a configuration into a list of stings.
    :param file: tgz archive.
    :return: Confing by lines.
    """
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
    return conf_by_line


def add_to_dict(data, index, name, result) -> int:
    if name not in result.keys():
        result[name] = data
    else:
        result[name] += data
    return index


def two_stage_parsing(result, lines, index) -> int:
    index = add_to_dict(*get_block(
        lines, index, start_pattern="^.{0,}Control Board Info--",
        end_pattern="^.{0,}Management Ethernet port",
        step_pattern="^.{0,}Controller ID"), name="cte", result=result)
    index = add_to_dict(*get_block(
        lines, index, start_pattern="^.{0,}Management Ethernet port",
        end_pattern="^.{0,}Maintenance Ethernet port--",
        step_pattern="^.{0,}ID: "), name="manage_eth", result=result)
    index = add_to_dict(*get_block(
        lines, index, start_pattern="^.{0,}SAS Port-",
        end_pattern="^.{0,}FCoE Port--",
        step_pattern="^.{0,}ID: "), name="sas_ports", result=result)
    return index


def parse_to_dict(lines: list[str]) -> dict[str, dict]:
    result = {}

    result["summary"], index = get_block(lines, 0,
                                         end_pattern="^.{0,}License--",
                                         step_pattern='^\n')
    result["license"], index = get_block(lines, index,
                                         start_pattern="^.{0,}License--",
                                         end_pattern="^.{0,}Disk Domain Info --",
                                         step_pattern="^.{0,}Feature")
    index = two_stage_parsing(result, lines, index)
    index = two_stage_parsing(result, lines, index)
    result["bbu"], index = get_block(lines, index,
                                     start_pattern="^.{0,}BBU Info--",
                                     end_pattern="^.{0,}Power Info--",
                                     step_pattern="^.{0,}Enclosure ID:")
    result["psu"], index = get_block(lines, index,
                                     start_pattern="^.{0,}Power Info--",
                                     end_pattern="^.{0,}Fan Info--",
                                     step_pattern="^.{0,}Enclosure ID:")
    result["fan"], index = get_block(lines, index,
                                     start_pattern="^.{0,}Fan Info--",
                                     end_pattern="^.{0,}Expander Board Info--",
                                     step_pattern="^.{0,}Enclosure ID:")
    return result


def get_block(
        data: list[str], start_index: int = 0,
        start_pattern: str = '', end_pattern: str = '',
        step_pattern: str = '',
) -> dict[str, list[list[str]]]:
    """
    Parses strings into a dictionary using patterns.
    :param start_index: Starting position for parsing
    :param data: Data in rows.
    :param start_pattern: Start template.
    :param end_pattern: End template.
    :param step_pattern: Sub block start template.
    :return: Nested dictionary.
    """
    result = [[]]
    index = 0
    if start_pattern:
        for line, index in zip(data[start_index:], range(start_index, len(data) + 1)):
            if re.match(start_pattern, line):
                break
    else:
        index = start_index
    for line, index in zip(data[index:], range(index, len(data) + 1)):
        if end_pattern and re.match(end_pattern, line):
            return result, index
        if step_pattern and re.match(step_pattern, line) and result[-1] != []:
            result.append([])
        match = re.match(r"^\s*([^:\n]+)[:|=]\s?(.*)$", line)
        if match:
            result[-1].append([match.group(1), match.group(2)])
        elif line:
            print("В словарь не добавлена строка", line)
    return result, index
