try:
	from bs4 import BeautifulSoup
except ImportError as err:
	print("BeautifulSoup is not installed. To install it use apt-get install python-bs4 or visit https://www.crummy.com/software/BeautifulSoup/ for more information. \n OS error: {0}".format(err))
	raise
import sys
import string
import os
import re

def numbers( str ):
	numbers_list=[]
	numbers_list=re.findall(r'\d+', str)
	if not numbers_list:
		return
	else:
		for i in range(0,len(numbers_list)):
			numbers_list[i] = int(numbers_list[i])

	return numbers_list ;

def toc_maker(list_of_items, ul_item):
	i =0
	miao = []
	previous = []
	previous_text = ""
	while (len(list_of_items) > 0):
		if i is 0 or len(list_of_items[0][0]) is (len(previous)):
			i = 1
			first_item = soup.new_tag('li')
			# print list_of_items[0][1]
			temp_soup = BeautifulSoup(list_of_items[0][1][0], 'html.parser')
			temp_item = temp_soup.h1
			string = unicode(temp_item.contents[0])
			a = soup.new_tag('a', href=unicode(temp_item.a.attrs["href"]))
			a.string = temp_item.contents[0]
			first_item.append(a)
			ul_item.append(first_item)
			previous = list_of_items[0][0]
			previous_text = temp_item.contents[0]
			del list_of_items[0]
		elif len(list_of_items[0][0]) > (len(previous)):
			new_ul_item = soup.new_tag('ul')
			list_of_items, m = toc_maker(list_of_items, new_ul_item)
			tag = ul_item.findAll('li')[-1]
			tag.append(m)
		else:

			return list_of_items, ul_item
	return list_of_items, ul_item



script_dir = os.path.dirname(__file__)
rel_path = "../notebooks/ROOT-Primer.html"
abs_file_path = os.path.join(script_dir, rel_path)

final = open(abs_file_path, 'w')
# Find the code markdown comands in the notebooks
regex1=re.compile( "\s+<code>\s+")
regex2=re.compile( "\s+</code>\s+")
# Find the notebook body elements for concatenation
finregex=re.compile("<body>(?P<bodyText>[\s\S]*)</body>")
last_text=re.compile("</body>[\s\S]*</html>[\s\S]*")
# remove_tag=re.sub(ur'\xc2', re.UNICODE)
# files we will work with

chapter = 1
for i in range(1,len(sys.argv)):
    filename = sys.argv[i]
    infilename = filename+".html"
    # outfilename = filename+".prep1.html"

    script_dir = os.path.dirname(__file__)
    rel_path = "../notebooks"
    abs_path = os.path.join(script_dir, rel_path)
    abs_in_path = os.path.join(abs_path, infilename)

    ############ OPEN FILES ############
    f = open(abs_in_path, 'r')

    ############ PARSE TEXT ############
    soup = BeautifulSoup(f.read().decode('utf-8'),"html.parser")
    toc_soup = BeautifulSoup("","html.parser")


    ############ SELECT ALL DIVS ############
    divtags = soup.findAll('div')

    ROOT_Primer_nav = soup.find_all(text=re.compile('ROOT-Primer Navigator'))
    paragraphs = [nav.parent for nav in ROOT_Primer_nav]
    divs = [paragraph.parent for paragraph in paragraphs]

    ############ EDIT BASED ON METADATA ############
    for tag in soup.findAll('div'):
    	if 'id' in tag.attrs:
    		if 'root_plot' in tag.attrs['id']:
    			tag.attrs['id'] = tag.attrs['id'].replace('root_plot','root_plot'+'_'+str(chapter))
    	if 'class' in tag.attrs:
    		if 'output_html' in tag.attrs['class']:
    			for child in tag.children:
    				if child.name=='script':
    					child.contents[0].replace_with(str(child.contents[0]).replace('root_plot','root_plot'+'_'+str(chapter)))
    	if tag in divs:
    		tag.decompose()

    filecontents=soup.prettify().encode('utf-8')

    files_no = len(sys.argv)
    infilenames=[]
    if chapter is 1:
        firstimport = last_text.sub('',filecontents)
        finaltext =  firstimport
    else:
        	nextimportcontents=finregex.search(filecontents)
        	finaltext+=nextimportcontents.group("bodyText")

    chapter=chapter+1

finaltext +='</body>\n?</html>'
    ############ Create a TOC ############

toc_soup = BeautifulSoup(finaltext,"html.parser")


first_level = 1
# output = []
headers = toc_soup.findAll(re.compile('^h[%d-6]' % first_level))

toc_rendered=soup.new_tag('div')
toc_rendered.attrs['class'] = ["cell", "border-box-sizing", "text_cell", "rendered"]

toc_prompt=soup.new_tag('div')
toc_prompt['class'] = ["prompt", "input_prompt"]

toc_inner_cell = soup.new_tag('div')
toc_inner_cell['class'] = ["inner_cell"]

toc_rendered_html = soup.new_tag('div')
toc_rendered_html['class'] = ["text_cell_render", "border-box-sizing", "rendered_html"]

# toc.string = fin
tag = soup.new_tag('ul')
# find correct place on the <ul> tree to add them

# list of the possitions and items
possitions = []
for header in headers:
	# header.name = 'h1'
	if 'Navigator' in header.text:
		continue
	else:
		position = numbers(unicode(header.contents[0]))
		if position is None:
			position = [0]
		header.contents[0].replace_with(header.contents[0].replace('\n      ',''))
		header.a.contents[0].replace_with(header.a.contents[0].replace('\n      ',''))
		header.contents.remove(unicode('\n'))
		header_dup = soup.h1
		header_dup.contents = header.contents
		header_dup.a.contents = header.a.contents
		possitions.append([position,[str(header_dup)]])
current_level = 0
buff = []
i = len(possitions)

miao, tag = toc_maker(possitions, tag)


toc_rendered_html.insert(0, tag)
toc_inner_cell.insert(0,toc_rendered_html)
toc_rendered.insert(0,toc_prompt)
toc_rendered.insert(1,toc_inner_cell)
toc_soup.find(id="notebook-container").insert(1,toc_rendered)

finaltext=toc_soup.prettify().encode('utf-8')

########### fix all the <code> brakets ############

iteration1 = regex1.sub(' <code>',finaltext)
iteration2 = regex2.sub('</code> ',iteration1)

final.write(iteration2)

# final.write(fin.encode('utf8'))
