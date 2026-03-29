from bs4 import BeautifulSoup


def html_to_table(html):

    soup = BeautifulSoup(html, "html.parser")

    table = []

    rows = soup.find_all("tr")

    for row in rows:

        cols = row.find_all(["td", "th"])

        row_data = [col.get_text(strip=True) for col in cols]

        if row_data:
            table.append(row_data)

    return table
