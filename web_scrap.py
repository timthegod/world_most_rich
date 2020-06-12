import requests
import lxml.html as lh
import pandas as pd


class PageTableHandler:
    def __init__(self):
        self.url = None

    def setURL(self, url):
        self.url = url

    def getTRElements(self):
        # Create a handle, page, to handle the contents of the website
        page = requests.get(self.url)

        # Store the contents of the website under doc
        doc = lh.fromstring(page.content)

        # Parse data that are stored between <tr>..</tr> of HTML
        return doc.xpath('//tr')

    @staticmethod
    def getTableChildValue(currentTree):
        return [c.text_content() for c in currentTree]

    @staticmethod
    def getTableColumnName(firstTree):
        return [c.text_content().split('\n')[0] for c in firstTree]

    def getTableDict(self, colName, trElements):
        columnList = []

        for i, tr in enumerate(trElements[1:]):
            if i == 0:
                for j, c in enumerate(tr):
                    value = c.text_content().split('\n')[0]
                    if j == 3:
                        value = value.replace(',', '')
                    columnList.append([value])
            else:
                for j, c in enumerate(tr):
                    value = c.text_content().split('\n')[0]
                    if j == len(tr) - 1:
                        if '臺灣' in value:
                            value = '臺灣'
                        elif '香港' in value:
                            value = '香港'
                        columnList[j].append(value)
                    else:
                        columnList[j].append(value)
        return {colName[i]: column for i, column in enumerate(columnList)}

    def getDf(self):
        tr_elements = self.getTRElements()
        colName = self.getTableColumnName(tr_elements[0])
        return pd.DataFrame(self.getTableDict(colName, tr_elements))


def getFullRichDF():
    urlHead = "https://wiki.mbalib.com/zh-tw/2020%E5%B9%B4%E3%80%8A%E7%A6%8F%E5%B8%83%E6%96%AF%E3%80%8B%E5%85%A8%E7%90%83%E4%BA%BF%E4%B8%87%E5%AF%8C%E8%B1%AA%E6%8E%92%E8%A1%8C%E6%A6%9C_%28"
    pages = [(1,100), (101,200), (200,293), (293, 401), (401, 514), (514, 616), (616, 712), (712, 804), (804, 945), (945, 1135), (1135, 1513), (1513, 1990)]
    pth = PageTableHandler()
    df = pd.DataFrame()
    for p in pages:
        print(p)
        cURL = urlHead + str(p[0]) + "-" + str(p[1]) + "%29"
        pth.setURL(cURL)
        df = df.append(pth.getDf())
    return df


if __name__ == '__main__':
    df = getFullRichDF()
    twDf = df[df['國家和地區'] == '臺灣']
    print(df['國家和地區'].value_counts()[:20])
    print(df['國家和地區'].value_counts()[:20] / len(df))
    print(twDf['財富來源'].value_counts())
    print(df['財富來源'].value_counts()[:20])
    print(df['財富來源'].value_counts()[:20]/len(df))
    worldAsset = 241000  # 241 trillion
    df['財富（億美元）'] = df['財富（億美元）'].astype(int)
    df['財富（億美元）'].sum() / worldAsset
    wp = pd.read_csv('wp.csv')
    top20Country = df['國家和地區'].value_counts()[:20]
    topRatio = {}
    for k, i in top20Country.iteritems():
        try:
            topRatio[k] = i / int(wp[wp['國家/地區'] == k]['人口'].values[0])
            print(k, i, i / int(wp[wp['國家/地區'] == k]['人口'].values[0]))
        except:
            pass
    sorted(topRatio.items(), key=lambda x: x[1], reverse=True)



