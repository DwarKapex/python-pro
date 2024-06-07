"""
Log Parser
"""

# log_format ui_short:
#   '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#   '$status $body_bytes_sent "$http_referer" '
#    '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#    '$request_time';

import argparse
import gzip
import json
import os
import pathlib
import re
import shutil
import sys
from statistics import mean, median
from typing import Dict, List

import structlog

config = {"REPORT_SIZE": 1000, "REPORT_DIR": "./reports", "LOG_DIR": "./log"}


def configure_logger(log_file: str = ""):
    """
    Configure structlog file
    :param log_file: path to log file to save
    :return: Logger
    """
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )
    if log_file:
        # pylint: disable=consider-using-with
        structlog.configure(
            logger_factory=structlog.WriteLoggerFactory(file=pathlib.Path(log_file).open("wt", encoding="UTF-8")),
        )
    return structlog.get_logger()


logger = configure_logger()


def parse_args():
    """
    Parse script arguments
    :return: dict with parsed arguments
    """
    parser = argparse.ArgumentParser(description="Parameters for log_analyzer")
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        required=False,
        default="unknown",
        help="Path to configuration file (JSON formatted)",
    )
    return parser.parse_args()


def update_config(default_config: Dict, config_path: pathlib.Path):
    """
    Update script config from file
    :param default_config: Default configuration
    :param config_path: Path to the JSON file with update for config
    :return: Updated config
    """
    if config_path is None or str(config_path) == "unknown":
        return default_config
    updated_config = default_config
    try:
        with open(config_path, encoding="UTF-8") as fconfig:
            config_update = json.load(fconfig)
            updated_config.update(config_update)
    except FileNotFoundError as e:
        logger.error(f"Failed to load config file {str(config_path)!r}, exception: {str(e)}")
    except json.decoder.JSONDecodeError as e:
        logger.error(f"Failed to decode config file {str(config_path)!r}, exception: {str(e)}")
    return updated_config


def get_log_file_and_date(log_dir: pathlib.Path):
    """
    Obtain log file path and date it was created
    :param log_dir: Path to folder with log files
    :return: Path to the latest log file and its date
    """
    log_starts_with = "nginx-access-ui.log-"
    parse_log_name = ""
    if not os.path.isdir(log_dir):
        logger.error(f"Error to get access to log directory {str(log_dir)!r}")
        sys.exit(1)
    for fname in os.listdir(log_dir):
        if fname.startswith(log_starts_with) and parse_log_name < fname:
            parse_log_name = fname
    logfile_path = log_dir / parse_log_name
    logger.info(f"Found log file {str(logfile_path)!r} for parsing")
    log_date = re.findall(r"\d+", parse_log_name)[0]
    if len(log_date) != 8:
        logger.warning("warning")
    log_date = f"{log_date[:4]}.{log_date[4:6]}.{log_date[6:8]}"

    return logfile_path, log_date


def parse_log_line(line: str = ""):
    """
    Parse logic for single line from log file
    :param line: Single line from log file
    :return: Extracted URL and corresponded request time
    """
    re_result = re.search("(?:GET|POST|HEAD|OPTIONS|PUT)(.+?)HTTP", line)
    url = None
    if re_result:
        url = re_result.group(1).strip()
    else:
        logger.error(f"Need to adjust search criteria for line {line!r}")

    request_time = float(re.findall(r"\d+\.\d+", line.split(" ")[-1].strip())[0])
    return url, request_time


def parse_logs(log_file: pathlib.Path):
    """
    Main function for log parsing
    :param log_file: Path to log file to parse
    :return: Dictionary with URL as a key, and list of requested time as value for the key
    """
    # find the latest log file in log dir
    if log_file.suffix == ".gz":
        with gzip.open(log_file, mode="rt") as f:
            logfile_content = f.readlines()
    else:
        with open(log_file, encoding="UTF-8") as f:
            logfile_content = f.readlines()

    data = {}
    lines_count = 0
    failed_line_count = 0
    for line in logfile_content:
        lines_count += 1
        url, request_time = parse_log_line(str(line))
        if url is None:
            failed_line_count += 1
        if url not in data:
            data[url] = [request_time]
        else:
            data[url].append(request_time)

    if failed_line_count > 0.5 * lines_count:
        logger.error("Parser failed with more than 50% of log entities. Consider to update parse criteria")
    return data


def create_log_stats(log_data: Dict, report_size: int = 0):
    """
    Generate lag statistics to populate the outcome report
    :param log_data: Dictionary of parsed data
    :param report_size: The max number of requests to report about
    :return: Dictionary with log statistics
    """
    url_count = []
    total_time = 0
    total_count = 0
    for url, data in log_data.items():
        url_count.append((url, sum(data)))
        total_time += sum(data)
        total_count += len(data)
    url_count = sorted(url_count, key=lambda x: x[1], reverse=True)
    log_stats = []
    for url, time_sum in url_count[:report_size]:
        url_data = sorted(log_data[url])
        report_entity = {
            "count": len(url_data),
            "time_avg": f"{mean(url_data):.3f}",
            "time_max": f"{max(url_data):.3f}",
            "time_sum": f"{time_sum:.3f}",
            "url": url,
            "time_med": f"{median(url_data):.3f}",
            "time_perc": f"{100*time_sum / total_time:.3f}",
            "count_perc": f"{100*len(url_data) / total_count:.3f}",
        }
        log_stats.append(report_entity)
    return log_stats


def generate_report(report_dir, log_date, log_stats: List[Dict]):
    """
    Generate report from log stats
    :param report_dir: Path to folder to save the report to
    :param log_date: Log date for report file name generation
    :param log_stats: Log statistics
    :return: None
    """
    if not os.path.isdir(report_dir):
        os.makedirs(report_dir, exist_ok=True)
    report_fname = report_dir / f"report-{log_date}.html.tmp"
    shutil.copyfile("report-template.html", report_fname)
    with open(report_fname, encoding="UTF-8") as file:
        data = file.read()
        data = data.replace("var table = $table_json;", f"var table = {log_stats!r};")
    with open(report_fname, "w", encoding="UTF-8") as file:
        file.write(data)

    final_report_fname = report_fname.parent / report_fname.stem
    os.rename(report_fname, final_report_fname)
    logger.info(f"Generated report: {str(final_report_fname)!r}")


def report_file_exists(report_dir: pathlib.Path, log_date=None):
    """
    Check if report file already exists
    :param report_dir: Path to folder with reports
    :param log_date: Log date
    :return: True if report already exists, Flase otherwise
    """
    maybe_report_fname = report_dir / f"report-{log_date}.html"
    return maybe_report_fname.exists()


def main(default_config: Dict):
    """
    Main function to execute
    :param default_config: Defatul config for the scrit
    :return: None
    """
    args = parse_args()
    updated_config = update_config(default_config, args.config)
    # pylint: disable=global-statement
    global logger
    logger = configure_logger(updated_config.get("LOG_FILE", None))
    log_file, log_date = get_log_file_and_date(pathlib.Path(updated_config.get("LOG_DIR", None)))
    if report_file_exists(pathlib.Path(updated_config.get("REPORT_DIR")), log_date):
        logger.info(f"Log file {str(log_file)!r} was already parsed. Nothing to do")
        return
    log_data = parse_logs(log_file)
    log_stats = create_log_stats(log_data, updated_config["REPORT_SIZE"])
    generate_report(pathlib.Path(updated_config["REPORT_DIR"]), log_date, log_stats)


if __name__ == "__main__":
    main(config)
