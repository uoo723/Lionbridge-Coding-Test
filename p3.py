"""
$ python p3.py

kowiki-20180401-pages-articles-multistream.xml
Sequential하게 탐색하여 최대 1000개의 축구 선수 정보를 수집한 후 랜덤으로 10 개씩 추출하고
csv포멧으로 결과값 저장.

※ 추출 정규식 및 parser가 축구선수정보 > 1000에 대해서는 예외가 발생할 수 있음.
"""

import xml.etree.ElementTree as ET
import re
import csv
import random

xml_filename = 'kowiki-20180401-pages-articles-multistream.xml'
info_title = '축구 선수 정보'


def fixtag(ns, tag, nsmap):
    return '{%s}%s' % (nsmap[ns], tag)


def process_page(page_elem, nsmap):
    page_id = page_elem.find(fixtag('', 'id', nsmap)).text
    page_title = page_elem.find(fixtag('', 'title', nsmap)).text
    text = page_elem \
        .find(fixtag('', 'revision', nsmap)) \
        .find(fixtag('', 'text', nsmap)).text or ''

    text = find_infobox_text(text)

    if text is None:
        return None

    info_dict = get_infobox_dict(text)
    info_dict = process_infobox_dict(info_dict)

    return {
        'page_id': page_id,
        'page_title': page_title,
        'template_name': info_title,
        'date_of_birth': info_dict['date_of_birth'],
        'height': info_dict['height'],
        'team': info_dict['team'],
    }


def find_infobox_text(text, info_title=info_title):
    regex = r'({{info_title\n(?:\|\s?.*\n)+}})'.replace(
        'info_title', info_title)
    match = re.match(regex, text)
    return match.group() if match is not None else None


def get_infobox_dict(text, info_title=info_title):
    info_dict = {}
    text = text[2 + len(info_title):-2]
    for line in text.split('\n'):
        if not line.startswith('|'):
            continue
        try:
            key, value, *_ = line.split('=')
        except ValueError:  # invalid format
            continue

        info_dict[key[1:].strip()] = value.strip()
    return info_dict


def process_infobox_dict(infobox_dict):
    date_of_birth = infobox_dict['출생일'] if '출생일' in infobox_dict else None
    height = infobox_dict['키'] if '키' in infobox_dict else None
    team = infobox_dict['현 소속팀'] if '현 소속팀' in infobox_dict else None

    if date_of_birth:
        match = re.search(
            r'(\d{4})[^\d]*(\d{1,2})[^\d]*(\d{1,2})',
            date_of_birth)
        assert match is not None

        year, month, day = match.groups()
        date_of_birth = '%02d-%02d-%02d' % (int(year), int(month), int(day))

    if height:
        match = re.match(r'((?:1|2)\.?\d{2})', height)
        assert match is not None

        height = match.groups()[0]
        if '.' in height:
            height = str(int(float(height) * 100))

    if team:
        match = re.search(r'\[\[((?:\w|\s|\d)+).*\]\]', team)
        if not match:
            team = re.sub(r'{{(?:\d|\w|\s|\|)+}}', '', team).strip()
        else:
            team = match.groups()[0]

    date_of_birth = date_of_birth or '정보 없음'
    height = height or '정보 없음'
    team = team or '없음'

    return {'date_of_birth': date_of_birth, 'height': height, 'team': team}


def run_parse():
    nsmap = {}
    results = []
    count = 0

    for event, elem in ET.iterparse(xml_filename, events=['end', 'start-ns']):
        if event == 'start-ns':
            ns, url = elem
            nsmap[ns] = url
        elif event == 'end':
            if elem.tag == fixtag('', 'page', nsmap):
                result = process_page(elem, nsmap)
                if result is not None:
                    count += 1
                    results.append(result)
                    if count == 1000:
                        break
                elem.clear()

    samples = []
    while True:
        if len(samples) == 10:
            break

        sample = results[random.randrange(0, count)]
        if sample not in samples:
            samples.append(sample)

    with open('results.csv', 'w', encoding='utf8', newline='') as f:
        wr = csv.writer(f)
        wr.writerow([
            'Page ID', 'Page Title', 'Template Name',
            'Date of Birth', 'Height', 'Team'])

        for sample in samples:
            wr.writerow([
                sample['page_id'], sample['page_title'], info_title,
                sample['date_of_birth'], sample['height'], sample['team']])


if __name__ == '__main__':
    run_parse()
