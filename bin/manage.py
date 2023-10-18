import argparse
import psycopg2
from config import get_config

#  python ./bin/manage.py add domain_override domain type value
#    or
#  python ./bin/manage.py remove domain_override domain type

def manage_domain_overrides(operation, domain, type, value):
    assert(operation in ['add', 'remove'])
    assert(type in ['background_color', 'cover_url'])

    # if the type is background_color, the value must be a valid hex color code
    if type == 'background_color':
        assert(value[0] == '#')
        assert(len(value) == 7)
        assert(all(c in '0123456789abcdef' for c in value[1:]))

    # if the type is cover_url, the value must be a url
    if type == 'cover_url':
        assert(value[:4] == 'http')

    config = get_config()
    conn = psycopg2.connect(dbname=config.db_name, host=config.db_host)
    cur = conn.cursor()

    if operation == 'add':
        cur.execute("INSERT INTO domain_overrides (domain, type, value) VALUES (%s, %s, %s) on conflict (domain, type) do update set value = %s, updated_at = current_timestamp", (domain, type, value, value))
    elif operation == 'remove':
        cur.execute("DELETE FROM domain_overrides WHERE domain = %s AND type = %s", (domain, type))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Manage domain overrides.')
    parser.add_argument('operation', choices=['add', 'remove'], help='The operation to perform.')
    parser.add_argument('parameter', choices=['domain_override'], help='The parameter to which the operation applies.')
    parser.add_argument('domain', help='The domain to which the operation applies.')
    parser.add_argument('type', help='The type to which the operation applies.')
    parser.add_argument('value', nargs='?', help='The value to set for the type. Only required for "add" operation.')

    args = parser.parse_args()

    if args.parameter == 'domain_override':
      manage_domain_overrides(args.operation, args.domain, args.type, args.value)
    else:
      print("Invalid parameter. Only 'domain_override' is supported.")