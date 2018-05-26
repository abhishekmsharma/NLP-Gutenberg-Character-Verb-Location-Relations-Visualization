'''
Developer: Abhishek Manoj Sharma
Course: CS 256 Section 2
Date: November 18, 2017
'''
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.sem import relextract
import urllib2
import matplotlib.pyplot as plt
import sys
import os

#this method extracts the name and location from a relation string
def get_person_location(s):
    first_close = s.find("]")
    person = s[0:first_close + 1]
    person = person.replace("/NNP", "").replace("[PER: '", "").replace("']", "").replace("/NN","").replace("/JJ","")
    s = s[first_close + 1:]
    second_open = s.find("[GPE:")
    location = s[second_open:].replace("/NNP", "").replace("[GPE: '", "").replace("']", "").replace("/NN","").replace("/JJ","")
    return (person,location)

#this method plots a heatmap for relations between people and location
def generate_pair_graph(interaction_pairs):

    length_pairs = len(interaction_pairs)
    count = 0
    #taking top 10% of interactions
    length_pairs = int(length_pairs * 0.1)
    if length_pairs<5:
        length_pairs = min(len(interaction_pairs),10)
    new_dict = {}
    for k,v in interaction_pairs.iteritems():
        new_dict[k] = v
        count+=1
        if count==length_pairs:
            break
    interaction_pairs = new_dict
    name_pairs = interaction_pairs.keys()
    people = []
    location = []
    for i in name_pairs:
        people.append(i[0])
        location.append(i[1])
    people = list(set(people))
    location = list(set(location))
    min_length = min(len(people),len(location))
    people = people[:min_length]
    location = location[:min_length]
    counts = []
    for item in people:
        current_count = []
        for new_item in location:
            if (item, new_item) in name_pairs:
                current_count.append(interaction_pairs[(item, new_item)])
            else:
                current_count.append(0)
        counts.append(current_count)

    data = counts
    row_labels = people
    column_labels = range(0, len(people))
    fig, axis = plt.subplots()
    heatmap = axis.pcolor(data, cmap=plt.cm.Reds, edgecolors='black',)
    axis.set_yticks(column_labels, location)
    axis.set_xticks(column_labels, people)
    axis.set_yticklabels(location)
    axis.set_xticklabels(column_labels)

    colorbar_values = list(set(interaction_pairs.values()))
    colorbar_values.insert(0, 0)

    fig.set_size_inches(12,8)
    fig.subplots_adjust(bottom=0.2)
    plt.xticks(column_labels, people, rotation='vertical')
    plt.yticks(column_labels, location)
    cbar = plt.colorbar(heatmap, ticks=colorbar_values)
    cbar.ax.set_ylabel('counts', rotation='270')
    plt.tick_params(axis='x', labelsize=6)
    plt.tick_params(axis='y', labelsize=6)
    plt.xlabel("People")
    plt.ylabel("Locations")
    plt.title("Interactions: People vs Locations")
    plt.show()

if __name__ == "__main__":

    sys.stdout = open(os.devnull, 'w')
    nltk.download('punkt')
    nltk.download('cmudict')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    sys.stdout = sys.__stdout__

    book_num = raw_input("Enter Gutenberg book number (1 to 55000) \nOr enter 0 for default (book_num = 22776) book: ")
    try:
        book_num = int(book_num)
    except ValueError:
        print "Entered value is not a number. Exiting program.\n"
        exit()
    if book_num < 0 or book_num > 55000:
        print "Book number should be in range 0 to 55000. Exiting program.\n"
        exit()
    if book_num == 0:
        book_num = 22776
    URL = "http://www.gutenberg.org/cache/epub/" + str(book_num) + "/pg" + str(book_num) + ".txt"
    print "Retrieving book data"
    try:
        book_data = urllib2.urlopen(URL).read().decode("UTF-8").encode("ascii", "ignore")
    except urllib2.HTTPError:
        URL = "https://www.gutenberg.org/files/" + str(book_num) + "/" + str(book_num) + "-0.txt"
        try:
            book_data = urllib2.urlopen(URL).read().decode("UTF-8").encode("ascii", "ignore")
        except urllib2.HTTPError:
            print "https://www.gutenberg.org/ebooks/" + str(book_num) + " is not a text book.\nExiting program."
            exit()
    except UnicodeDecodeError:
        print "Retrieved book not in proper encoding. Exiting program.\n"
        exit()
    print "Book retrieved - URL: https://www.gutenberg.org/ebooks/" + str(book_num)
    reg_ex = re.compile(r'.*')
    s = book_data
    print "\nTokenizing book data"
    s = word_tokenize(s)
    text_with_tags = nltk.pos_tag(s)
    text_chunk = nltk.ne_chunk(text_with_tags)
    person_location_pairs = {}
    print "Searching Name - Location interections"
    for rel in relextract.extract_rels('PER', 'GPE', text_chunk, pattern=reg_ex):
        relation = nltk.sem.rtuple(rel)
        person_location = get_person_location(relation)
        if person_location in person_location_pairs:
            current_pair = person_location_pairs[person_location]
            person_location_pairs[person_location] = current_pair + 1
        else:
            person_location_pairs[person_location] = 1
    if len(person_location_pairs)==0:
        print "No interaction found in this book."
        exit()
    print "\n----------------------------------------------------"
    print "Interaction frequencies (Descending order)"
    print "(Person - Location : Count)"
    print "----------------------------------------------------"
    d_view = [(v, k) for k, v in person_location_pairs.iteritems()]
    d_view.sort(reverse=True)
    for v, k in d_view:
        print k[0], "-", k[1], ":", v
    print "--------------------------------"
    print "\nHeatmap plotted in a matplotlib window."
    print "Heatmap can be resized as per your needs."
    print "\nClose the heatmap to terminate program"
    generate_pair_graph(person_location_pairs)