"""Parsing module."""

import re
import tarfile
from io import BytesIO

from settings import DEBUG


def extract_conf(file: BytesIO) -> list[str]:
    """
    Extract a configuration into a list of stings.

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
                raise FileNotFoundError(
                    "Не найден файл Config/Config.tgz/config.txt"
                )
            conf_by_line = (
                conf_tar.extractfile("config.txt")
                .read()
                .decode("utf-8")
                .split("\n")
            )
    return conf_by_line


def add_to_dict(data, index, name, result) -> int:
    """
    Add the list to the dictionary or supplement it if there is a key.

    The index is transmitted end-to-end.

    :param data: List with data.
    :param index: Index.
    :param name: Key name.
    :param result: Dictionary to add.
    :return: Index.
    """
    if name not in result.keys():
        result[name] = data
    else:
        result[name] += data
    return index


def two_stage_parsing(result, lines, index) -> int:
    """
    Group parsers for two-stage launch.

    :param result: Dictionary to add.
    :param lines: List of source strings.
    :param index: Index.
    :return: Index.
    """
    index = add_to_dict(
        *get_block(
            lines,
            index,
            start_pattern="^.{0,}Control Board Info--",
            end_pattern="^.{0,}Management Ethernet port",
            step_pattern="^.{0,}Controller ID",
        ),
        name="cte",
        result=result
    )
    index = add_to_dict(
        *get_block(
            lines,
            index,
            start_pattern="^.{0,}Management Ethernet port",
            end_pattern="^.{0,}Maintenance Ethernet port--",
            step_pattern="^.{0,}ID: ",
        ),
        name="manage_eth",
        result=result
    )
    index = add_to_dict(
        *get_block(
            lines,
            index,
            start_pattern="^.{0,}SAS Port-",
            end_pattern="^.{0,}FCoE Port--",
            step_pattern="^.{0,}ID: ",
        ),
        name="sas_ports",
        result=result
    )
    return index


def parse_to_dict(lines: list[str]) -> dict[str, dict]:
    """
    Parse. Main func.

    :param lines: List of source strings.
    :return: Dictionary with data.
    """
    result = {}

    result["summary"], index = get_block(
        lines, 0, end_pattern="^.{0,}License--", step_pattern="^\n"
    )
    result["license"], index = get_block(
        lines,
        index,
        start_pattern="^.{0,}License--",
        end_pattern="^.{0,}Disk Domain Info --",
        step_pattern="^.{0,}Feature",
    )
    index = two_stage_parsing(result, lines, index)
    index = two_stage_parsing(result, lines, index)
    result["bbu"], index = get_block(
        lines,
        index,
        start_pattern="^.{0,}BBU Info--",
        end_pattern="^.{0,}Power Info--",
        step_pattern="^.{0,}Enclosure ID:",
    )
    result["psu"], index = get_block(
        lines,
        index,
        start_pattern="^.{0,}Power Info--",
        end_pattern="^.{0,}Fan Info--",
        step_pattern="^.{0,}Enclosure ID:",
    )
    result["fan"], index = get_block(
        lines,
        index,
        start_pattern="^.{0,}Fan Info--",
        end_pattern="^.{0,}Expander Board Info--",
        step_pattern="^.{0,}Enclosure ID:",
    )
    return result


def get_block(
    data: list[str],
    start_index: int = 0,
    start_pattern: str = "",
    end_pattern: str = "",
    step_pattern: str = "",
) -> dict[str, list[list[str]]]:
    """
    Pars strings into a dictionary using patterns.

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
        for line, index in zip(
            data[start_index:], range(start_index, len(data) + 1)
        ):
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
        elif line and DEBUG:
            print("В словарь не добавлена строка", line)
    return result, index
