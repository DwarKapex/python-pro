"""
Tests for log_analyzer.py
"""

from homework_01.src.log_analyzer import parse_log_line, update_config


def test_update_config():
    """
    Test config update
    :return:
    """
    # default config if no --config provided
    expected_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "LOG_DIR": "./log",
    }

    assert expected_config == update_config(expected_config, None)


def test_parse_log_line():
    """
    Test log line parsing
    :return:
    """
    log_line = (
        "1.199.4.96 -  - [30/Jun/2017:03:28:21 +0300] "
        '"GET /api/v2/banner/22910512/statistic/?date_from=2017-06-30&date_to=2017-06-30 HTTP/1.1" 200 115 '
        '"-" "Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" "1498782501-3800516057-4707-10488715"'
        ' ьфл"c5d7e306f36c" 0.116'
    )

    url, request_time = parse_log_line(log_line)
    expected_url = "/api/v2/banner/22910512/statistic/?date_from=2017-06-30&date_to=2017-06-30"
    expected_request_time = 0.116
    assert expected_url == url
    assert expected_request_time == request_time
