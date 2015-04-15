from bs4 import BeautifulSoup
import urllib2
import json
import codecs
import argparse

parser = argparse.ArgumentParser(description='This is will scrape information from your Canvas account')
parser.add_argument('-t','--todo',help='Generate To-Do List',action='store_true')
parser.add_argument('-m','--modules',help='Generate Module List',action='store_true')
parser.add_argument('week',help='Number of the Week to Scrape')
args = parser.parse_args()

week = args.week
filename = 'Week' + str(args.week) + 'Info.html'
testfile = codecs.open(filename, 'w','utf-8')
tokenfile = open('token','r')

url = 'https://canvas.instructure.com/api/v1/courses'

token = tokenfile.read()
token_url = '?access_token=' + token

tokenfile.close()

courses = urllib2.urlopen(url + token_url)
parsed_courses = json.load(courses)

def get_current_term(parsed_courses):
    most_recent = 0
    for each in parsed_courses:
        if each['enrollment_term_id'] > most_recent:
            most_recent = each['enrollment_term_id']
    return most_recent

def modules_fun(course_id):
    output = False
    module_url = url + '/' + str(course_id) + '/modules' + token_url
    modules = urllib2.urlopen(module_url)
    modules_parsed = json.load(modules)
    for each in modules_parsed:
        module_name = each['name']
        if 'week' and str(args.week) in (module_name).lower():
            module_id = each['id']
            module_items_fun(course_id, module_id)
            output = True
    if not output:
        testfile.write('No modules for this week')        

def module_items_fun(course_id, module_id):
    items_url = url + '/' + str(course_id) + '/modules/' + str(module_id) + '/items'+ token_url
    items = urllib2.urlopen(items_url)
    items_parsed = json.load(items)
    for each in items_parsed:
        if each.has_key('page_url'):
            page_url = each['page_url']
            page_title = each['title']
            print page_title
            print page_url
            testfile.write('<h3>' + page_title + '</h3>')
            item_page_fun(course_id, page_url)
    
def item_page_fun(course_id, page_url):
    page_url = url + '/' + str(course_id) + '/pages/' + str(page_url)
    page = urllib2.urlopen(page_url + token_url)
    parsed_page = json.load(page)
    page_html = BeautifulSoup(parsed_page['body'])
    testfile.write('<div class="module">')
    testfile.write(page_html.prettify())
    testfile.write('</div>')

def get_todo():
    testfile.write('<H1>Current Week\'s To-Do List</H1>')
    enrollment_term = get_current_term(parsed_courses)
    for each in parsed_courses:
        if enrollment_term  == each['enrollment_term_id']:
            if each['enrollments'][0]['type'] == 'student':
                course_id = each['id']
                print each['course_code']
                testfile.write('<div class="course"><h2>' + str(each['course_code'] + '</h2>'))
                testfile.write('<div class="todo">')
                testfile.write('<h3>To-Do:</h3><ul>')
                url_todo = url + '/' + str(course_id) + '/todo' + token_url
                todo = urllib2.urlopen(url_todo)
                todo_parsed = json.load(todo)
                if len(todo_parsed) > 0:
                    for task in todo_parsed:
                        testfile.write('<li>' + task['assignment']['name'] + '</li>')
                else:
                    testfile.write('<li>No Canvas Assignments Due</li>')
                testfile.write('</ul>')
                testfile.write('</div>')                
                testfile.write('</div>')
    testfile.write('<hr>')

def get_modules():
    enrollment_term = get_current_term(parsed_courses)
    for each in parsed_courses:
        if enrollment_term  == each['enrollment_term_id']:
            if each['enrollments'][0]['type'] == 'student':
                course_id = each['id']
                print each['course_code']
                testfile.write('<div class="course"><h2>' + str(each['course_code']) + '</h2>')
                
                modules_fun(course_id)
                
                testfile.write('<H3>To-Do:</H3><ul>')
                url_todo = url + '/' + str(course_id) + '/todo' + token_url
                todo = urllib2.urlopen(url_todo)
                todo_parsed = json.load(todo)
                if len(todo_parsed) > 0:
                    for task in todo_parsed:
                        testfile.write('<li>' + task['assignment']['name'] + '</li>')
                else:
                    testfile.write('<li>No Canvas Assignments Due</li>')
                testfile.write('</ul>')
                testfile.write('</div>')

def main():
    testfile.write('<!doctype html>')
    testfile.write('<head><meta charset="UTF-8">')
    testfile.write('<title>ToDo</title>')
    testfile.write('<link rel="stylesheet" type="text/css" href="scraper.css">')
    testfile.write('</head><body>')
    if args.todo:
        get_todo()
    if args.modules:
        get_modules()
    testfile.write('</body>')
    testfile.close()

if __name__ == '__main__':
    main()
