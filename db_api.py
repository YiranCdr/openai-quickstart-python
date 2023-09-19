import sqlite3
import re
import datetime


def parse_plain_text(filename, character_identifier_assistant,
                     character_identifier_user, initial_timestamp):
    """
    :param filename:
    :param character_identifier_assistant: Name of the assistant.
    :param character_identifier_assistant: Name of the assistant.
    :param character_identifier_user: Name of the user.
    :param initial_timestamp: Optional. The initial timestamp that reads the
    file.
    :return: a list of records that include role, create_timestamp and content.
    Reading each line in the file would increase the timestamp of the record by
    1 second.
    """
    records = []
    if not initial_timestamp:
        initial_timestamp = datetime.datetime.fromisoformat('2000-01-01T00'
                                                            ':00:00-07:00')
    with open(filename, "r") as f:
        _timestamp = initial_timestamp
        for _line in f:
            # For each line in the file, increase timestamp by 1 second.
            _timestamp += datetime.timedelta(seconds=1)
            # Skip empty lines and indents.
            if len(_line.strip()) < 1 or re.search(r"---", _line) or re.match(
                    r"--", _line):
                continue
            # Record assistant's response.
            elif re.search(r"%s" % character_identifier_assistant, _line):
                records.append({"role": "assistant",
                                "create_ts": _timestamp,
                                "content": re.sub(
                                    r"%s" % character_identifier_assistant, '',
                                    _line).strip()})
            # Record user's response.
            elif re.search(r"%s" % character_identifier_user, _line):
                records.append({"role": "user",
                                "create_ts": _timestamp,
                                "content": re.sub(
                                    r"%s" % character_identifier_user,
                                    '',
                                    _line).strip()})
            # For all the other response that cannot be identified as assistant
            # or user, record them as user's respond.
            else:
                records.append({"role": "user",
                                "create_ts": _timestamp,
                                "content": _line.strip()})
    return records


def get_top_n_records(db_name, table_name, order_by_field, n=-1, is_asc=True):
    """
    :param order_by_field: The name of the field we wish to order-by.
    :param n: Gets top n records under the given order. Gets all records if
    n = -1.
    :param is_asc: True to make the records order in ASC. False for DESC.
    :return: A list of record tuples.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    order = "ASC" if is_asc else "DESC"
    limit_str = ("LIMIT %d" % n) if n >= 0 else ""
    cursor.execute(
        """SELECT * FROM %s ORDER BY %s %s %s""" % (
            table_name, order_by_field, order, limit_str))
    records = cursor.fetchall()
    connection.close()
    return records


def dump_records(db_name, table_name, records, schema=None, overwrite=True):
    """
    :param records: A list of kv records.
    :param schema: A list of kv pairs, with required keys as `name`, the name
    of the field in STRING, `type`, the type of the field in STRING, and
    `not_null`, if the field can be a null or not in BOOLEAN.
    :param overwrite: If TRUE, delete the `table_name` table (if applicable),
    and create a new one.
    """
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    if overwrite:
        cursor.execute("DROP TABLE IF EXISTS %s" % table_name)
        if not schema:
            raise Exception("Must provide schema when overwrite=TRUE. ")
        schema_str = ""
        for _field in schema:
            schema_str += """%s %s %s, """ % (_field['name'],
                                              _field['type'],
                                              'NOT NULL' if _field[
                                                  'not_null'] else '')
        schema_str = schema_str[:-2]
        cursor.execute("""
        CREATE TABLE %s (%s)
        """ % (table_name, schema_str))

    for _record in records:
        _values = """("""
        for _field in schema:
            _values += """'%s', """ % _record[_field['name']]
        _values = _values[:-2] + """)"""
        cursor.execute("""
        INSERT INTO %s VALUES %s
        """ % (table_name, _values))

    connection.commit()
    connection.close()
