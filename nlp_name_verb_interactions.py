'''
Developer: Abhishek Manoj Sharma
Course: CS 256 Section 2
Date: November 18, 2017
'''
from nltk.tokenize import word_tokenize
import nltk
import urllib2
import matplotlib.pyplot as plt
import sys
import os

#this method gets all the pairs of the type <name> <verb> <name>
def get_interaction_pairs(text_with_tags):
    text_chunk = nltk.ne_chunk(text_with_tags, binary=True)
    count = 0
    pairs = {}
    length_of_tags = len(text_chunk)
    print "----------------------------------------------------"
    print "List of interactions"
    print "(Name 1 - Verb - Name 2)"
    print "----------------------------------------------------"
    while count<length_of_tags-3:
        b = False
        person_1 = ""
        person_2 = ""
        if isinstance(text_chunk[count], nltk.tree.Tree):
            l = len(text_chunk[count])
            for i in range(0,l):
                if text_chunk[count][i][1].startswith("NNP"):
                    person_1 = person_1 + text_chunk[count][i][0] + " "
            try:
                if text_chunk[count+1][1].startswith("VB") and isinstance(text_chunk[count+2], nltk.tree.Tree):
                    l = len(text_chunk[count+2])
                    for i in range(0,l):
                        if text_chunk[count+2][i][1].startswith("NNP"):
                            b = True
                            person_2 = person_2 + text_chunk[count+2][i][0] + " "
                    if b:
                        person_1 = person_1.strip()
                        person_2 = person_2.strip()
                        if not person_1.isupper() and not person_2.isupper():
                            s = [person_1, person_2]
                            print s[0], "-", text_chunk[count + 1][0], "-", s[1]
                            s = tuple(sorted(s, key=str.lower))
                            if s in pairs:
                                current_pair_count = pairs[s]
                                pairs[s] = current_pair_count + 1
                            else:
                                pairs[s] = 1
            except AttributeError:
                count+=1
                continue
            except IndexError:
                count+=1
                continue
        count+=1
    return pairs

#this method plots the heatmap for interactions between people
def generate_pair_graph(interaction_pairs):
    name_pairs = interaction_pairs.keys()
    people = []
    for i in name_pairs:
        for j in i:
            people.append(j)

    people = list(set(people))
    counts = []
    for item in people:
        current_count = []
        for new_item in people:
            if (item, new_item) in name_pairs:
                current_count.append(interaction_pairs[(item, new_item)])
            elif (new_item, item) in name_pairs:
                current_count.append(interaction_pairs[(new_item, item)])
            else:
                current_count.append(0)
        counts.append(current_count)

    data = counts
    row_labels = people

    column_labels = range(0, len(people))
    fig, axis = plt.subplots()
    heatmap = axis.pcolor(data, cmap=plt.cm.Reds, edgecolors='black',)

    axis.set_yticks(column_labels, people)
    axis.set_xticks(column_labels, people)
    axis.set_yticklabels(row_labels,minor=False)
    axis.set_xticklabels(column_labels)

    colorbar_values = list(set(interaction_pairs.values()))
    colorbar_values.insert(0, 0)

    fig.set_size_inches(12, 8)
    fig.subplots_adjust(bottom=0.2)
    plt.xticks(column_labels, people, rotation='vertical')
    plt.yticks(column_labels, people)
    cbar = plt.colorbar(heatmap, ticks=colorbar_values)
    cbar.ax.set_ylabel('counts',rotation='270')
    plt.tick_params(axis='x', labelsize=7)
    plt.tick_params(axis='y', labelsize=7)
    plt.xlabel("Names of people")
    plt.ylabel("Names of people")
    plt.title("Number of interactions between people")
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
    if book_num<0 or book_num>55000:
        print "Book number should be in range 0 to 55000. Exiting program.\n"
        exit()
    if book_num==0:
        book_num=22776
    URL = "http://www.gutenberg.org/cache/epub/" + str(book_num) + "/pg" + str(book_num) + ".txt"
    print "Retrieving book data"
    try:
        book_data = urllib2.urlopen(URL).read().decode("UTF-8").encode("ascii","ignore")
    except urllib2.HTTPError:
        URL = "https://www.gutenberg.org/files/" + str(book_num) + "/" + str(book_num) +"-0.txt"
        try:
            book_data = urllib2.urlopen(URL).read().decode("UTF-8").encode("ascii", "ignore")
        except urllib2.HTTPError:
            print "https://www.gutenberg.org/ebooks/" + str(book_num) + " is not a text book.\nExiting program."
            exit()
    except UnicodeDecodeError:
        print "Retrieved book not in proper encoding. Exiting program.\n"
        exit()
    print "Book retrieved - URL: https://www.gutenberg.org/ebooks/" + str(book_num)
    print "\nTokenizing book data"
    text = word_tokenize(book_data)
    text_with_tags = nltk.pos_tag(text)
    length_of_tags = len(text_with_tags)
    print "Searching <name> <verb> <name> interections"
    interaction_pairs = get_interaction_pairs(text_with_tags)
    if len(interaction_pairs)==0:
        print "No <name> <verb> <name> interactions found in this book."
        exit()
    print "\n----------------------------------------------------"
    print "Interaction frequencies (Descending order)"
    print "(Person 1 - Person 2 : Count)"
    print "----------------------------------------------------"
    d_view = [(v, k) for k, v in interaction_pairs.iteritems()]
    d_view.sort(reverse=True)
    for v, k in d_view:
        print k[0],"-",k[1],":",v
    print "--------------------------------"
    print "\nHeatmap plotted in a matplotlib window."
    print "Heatmap can be resized as per your needs."
    print "\nClose the heatmap to terminate program"
    generate_pair_graph(interaction_pairs)