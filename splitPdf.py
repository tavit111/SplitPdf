#!/usr/bin/env python3
import csv
from PyPDF2 import PdfWriter, PdfReader
import sys
import os
import argparse

# splitPdf [options] book.pdf table.csv
# options:
# -z number of the zero page

# CSV file (tab separated):
# file start_page end_page
# if end_page is empty than it will be start of next chapter - 1
# row starting with ( will be ignored

# app description
parser = argparse.ArgumentParser(
    prog='Pdf Splitter',
    description='Copy pages of pdf file into separate files based on page number and file name provided by svg file. Each row of svg file represent new file. Svg file should contain max 3 columns: file name, starting page, end page. The third column is optional and if omitted the end page will be the -1 of the starting page of row below or end of document if this is the last row'
)

# CLI interface
parser.add_argument('pdfFilename', help="path to input pdf file")
parser.add_argument(
    'csvFilename', help='path to csv file with information how to split pdf document.')
parser.add_argument('-z', '--offset', type=int, default=0,
                    help='offset value for pdf document. Which page of pdf file match the zero page of the document. Useful when spiting based on page number from a table of content. Default value: 0')
parser.add_argument('-o', '--output', default=os.getcwd(),
                    help='Output directory. Default current directory')

args = parser.parse_args()
bookPath = args.pdfFilename
csvPath = args.csvFilename
offset = args.offset
output = args.output

book = bookPath
table = csvPath
shift = offset - 1
chapters = []
destination = output


def isNotFolder(row):
    title = row[0]
    if title[0] == "(":
        return False

    return True


def addEnds(chapters):
    ends = [int(chapter[1]) for chapter in chapters]
    ends.pop(0)
    ends.append(-1)

    for chapter, end in zip(chapters, ends):
        if not chapter[2]:
            chapter[2] = end
        else:
            chapter[2] = int(chapter[2]) + 1

    return chapters


with open(table, encoding='utf-8', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter="\t", quotechar="|")
    for row in reader:
        chapters.append(row)

# removing ()
chapters = [chapter for chapter in chapters if isNotFolder(chapter)]
# adding end each chapter if it not specified
chapters = addEnds(chapters)


def splitPdf(chapters, book):
    with open(book, 'rb') as readFile:
        reader = PdfReader(readFile)
        for title, start, stop in chapters:
            start = int(start) + shift
            if stop == -1:
                stop = -1
            else:
                stop = int(stop) + shift
            filename = f"{title}.pdf"
            path = f"{destination}/{filename}"

            with open(path, 'wb') as writeFile:
                writer = PdfWriter(writeFile)
                for page in reader.pages[start:stop]:
                    writer.add_page(page)
                writer.write(writeFile)
                print("saved:", path)


splitPdf(chapters, book)
