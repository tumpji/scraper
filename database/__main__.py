from .tools import Connection


if __name__ == '__main__':
    conn = Connection(create_database=True)

    conn.make_table(clear=False)

    print(">> Items in the database:")

    for i, (title, url) in enumerate(conn.select_table()):
        print(f"{i+1:>4}: {title}\t{url}")

    print(">> End")
