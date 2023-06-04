from flask import Flask, render_template, url_for, request, redirect, json
from flask_sqlalchemy import SQLAlchemy
# from flask.json import jsonify
import random
import json
import shutil


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///championMaster.db'
db = SQLAlchemy(app)

class Champion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(500), nullable=True)

    #returns the champions name after it is created
    def __repr__(self):
        return '<Name %r>' % self.name

#has all champions objects corresponding their id to the index of list
all_champions = []
selected_pool = []

tag_dict = {}

class Node:

    # Constructor 
    def __init__(self, val):
        
        self.key = val
        
        # Since n children are possible for a root.
        # A list created to store all the children.
        self.child = []



#There always will be a root
root_list = []

root_list.append(Node(0))
root_list.append(Node(1))
root_list.append(Node(2))
root_list.append(Node(3))
root_list.append(Node(4))
root_list.append(Node(5))
root_list.append(Node(6))


@app.route('/')
def index():
    
    if len(all_champions) > 0:
        return render_template('index.html')


    champions = Champion.query.order_by(Champion.id).all()

    for champion in champions:
        all_champions.append(champion)

        encode_type = 1
        soundex_code = soundex(champion.name, encode_type)
        # print("encoding", soundex_code)

        insert(root_list[soundex_code[0]], soundex_code, champion)

    
    for champion in all_champions:
        champion.tags = []

    tag_file()
    read_file()

    return render_template('index.html')


@app.route('/admin/', methods=['GET'])
def admin():
    champions = Champion.query.order_by(Champion.id).all()

    # for champion in all_champions:
    #     champion.tags = []

    # tag_dict.clear()

    # tag_file()
    # read_file()
    return render_template('admin.html', champions=champions)


@app.route('/add_champion/', methods=['POST'])
def add_champion():
    new_name = request.form['champion_name']
    new_icon = request.form['champion_icon']

    new_champion = Champion(name=new_name, icon=new_icon)

    try:
        db.session.add(new_champion)
        db.session.commit()

        return redirect('/admin/')
    
    except:
        "There was an issue adding new champion to database."


@app.route('/delete/<int:id>')
def delete(id):
    champion_to_delete = Champion.query.get_or_404(id)

    try:
        db.session.delete(champion_to_delete)
        db.session.commit()

        return redirect('/admin/')

    except:
        return "There was an issue deleting the champion from the database."

#HOW TO GET ID
@app.route('/update/', methods=['POST'])
def update():
    # champion = Champion.query.get_or_404(id)

    new_name = request.form['update_champion_name']
    new_icon = request.form['update_champion_icon']

    # if request.method == 'POST':
    #     champion.name = request.form['champion_name']
    #     champion.icon = request.form['champion_icon']

        #<--------TAGS WILL WON'T BE SAVED IN DB-------->
        # tags = request.form['champion_tags']

        # for tag in tags:
        #     edit_tag(tag)

    try:
        db.session.commit()
        return redirect('/')

    except:
        return "There was an issue updating champion."

    # else:
    #     return render_template('admin.html', champion=champion)


@app.route('/select_champion/<int:id>', methods=['POST'])
def select_champion(id):

    champion_exists = 0
    for champion in selected_pool:
        if champion.id == id:
            champion_exists = 1
            break

    if champion_exists == 0:
        selected_pool.append(all_champions[id-1])
    
    else:
        return "None"

    
    
    champion = all_champions[id-1]
    json_data = {"id": champion.id, "name" : champion.name, "icon" : champion.icon}

    return json_data


@app.route('/deselect_champion/<int:id>', methods=['POST'])
def deselect_champion(id):
    
    i = 0
    while i < len(selected_pool):
        champion = selected_pool[i]

        if champion.id == id:
            selected_pool.pop(i)

        i += 1

    print(selected_pool)
    return "success"



@app.route('/roll_champion/', methods=['GET'])
def roll_champion():

    if len(selected_pool) > 0:
        random_int = random.randint(1, len(selected_pool)) - 1

        random_icon = selected_pool[random_int].icon

        return random_icon

    else:
        return "None"


@app.route('/get_all_champions/', methods=['GET'])
def get_all_champions():
    # need to get all champions in json form to send

    champions = Champion.query.order_by(Champion.id).all()
    # print('test')
    # print(champions[0].name)

    json_champions = json.dumps([[ob.id, ob.name, ob.icon] for ob in champions])
    # print(a)

    return json_champions


#update index all champions column
@app.route('/refine_pool/<string:query>', methods=['GET'])
def refine_pool(query):
    db_type = int(query[0])
    search_key = query[1:]

    refined_list = []

    if db_type == 0:
        encode_type = 0
        soundex_code = soundex(search_key, encode_type)

        refined_list = get_search(root_list[soundex_code[0]], soundex_code)

    else:
        try:
            print("test1")
            refined_list = tag_dict[search_key]
            
        except:

            #DON'T WANT TO SEND ALL CHAMPS SINCE ALL CHAMPS ARE ALREADY ON THE CLIENT

            print("test2")
            
            i = 1
            for champion in all_champions:
                refined_list.append(i)

                i += 1


    return json.dumps(refined_list)


@app.route('/get_tags/<int:id>', methods=['GET'])
def get_tags(id):
    # print(tag_dict)
    
    print("get tags", id)
    print(all_champions[id-1].name)
    print(all_champions[id-1].tags)

    return json.dumps(all_champions[id-1].tags)


@app.route('/delete_tag_route/<string:query>', methods=['POST'])
def delete_tag_route(query):

    i = 0
    for letter in query:
        if letter == ",":
            break

        i += 1

    champion_id = query[:i]
    tag_name = query[i+1:]


    print("delete tag function", champion_id, tag_name)

    delete_tag(champion_id, tag_name)

    return "tag deleted"


@app.route('/add_tag_route/<string:query>', methods=['POST'])
def add_tag_route(query):
    champion_id = query[0]
    tag_name = query[1:]

    add_tag(champion_id, tag_name)

    return "Done"

look_up_soundex = {'A' : 0,
                   'B' : 1,
                   'C' : 2,
                   'D' : 3,
                   'E' : 0,
                   'F' : 1,
                   'G' : 2,
                   'H' : 0,
                   'I' : 0,
                   'J' : 2,
                   'K' : 2,
                   'L' : 4,
                   'M' : 5,
                   'N' : 5,
                   'O' : 0,
                   'P' : 1,
                   'Q' : 2,
                   'R' : 6,
                   'S' : 2,
                   'T' : 3,
                   'U' : 0,
                   'V' : 1,
                   'W' : 0,
                   'X' : 2,
                   'Y' : 0,
                   'Z' : 2}

#add a code length limit
def soundex(search_text, encode_type):

    valids = []
    soundex_valids = []
        
    i = 0
        
    while i < len(search_text):
        character = search_text[i]
        
        if character.isalpha():
            character = character.capitalize()
            
            valids.append(character)
        
        i += 1
            
    
    previous_soundex_val = 0
    character_count = 1
    j = 1
    
    character = valids[0]
    soundex_character = look_up_soundex[character]
    soundex_valids.append(soundex_character)
    
    while j < len(valids) and character_count < 4:
        character = valids[j]
        soundex_character = look_up_soundex[character]
        
        if soundex_character != 0 and soundex_character != previous_soundex_val:
            
            #print(valids[j], soundex_character)
            
            previous_soundex_val = soundex_character
            # soundex_valids.append(str(soundex_character))
            soundex_valids.append(soundex_character)
            
            character_count += 1
            
        j += 1
        
    if encode_type == 0:
        return soundex_valids


    while len(soundex_valids) < 4:
        # soundex_valids.append(str(0))
        soundex_valids.append(0)
        
    # print(len(soundex_valids))
    # return int(''.join(soundex_valids))
    return soundex_valids



def insert(root, code, champion):
    current_path = find_path(root, code)
    
    current_path.append(champion)
    # print(current_path[0])


def find_path(root, code):
    path_index = []     #index of each node at each level/ branch
    path_index.append(root.key)     #append root key since root is stored in sequential order 0,1,..,6
    
    current_path = root.child
    
    i = 1    
    found_path = 0
    
    #Traverses until it gets to the leaf node
    while len(path_index) < 4:
        code_index = code[i]
        
        j = 0
        #Traverses until it finds the path or loops through the entire child list
        while j < len(current_path) and not found_path:
            node = current_path[j].key
            #print(j, node)
            
            if node == code_index:
                #print(j, node)
                current_path = current_path[j].child
                path_index.append(j)
                
                found_path = 1
                
                
            
            j += 1
        

        #after while loop search for path check
        if found_path == 1:
            found_path = 0
            
        else:
            current_path, path_index = create_path(root, code, path_index, current_path)
        

        i += 1
        
        
    return current_path


def create_path(root, code, path_index, current_path):
    #print(code, path_index)
        
    #'i' is to index code to get key value
    i = len(path_index)
    
    #print('path length', len(path_index), path_index)
    
    while len(path_index) < 4:
        key_to_add = code[i]
        #print(key_to_add)
        current_path.append(Node(key_to_add))
        
        j = 0   #'j' is the node's child index
        
        #once the node is added there is no garentee that it is the only node in the list
        #travereses correctly
        while j < len(current_path):
            if current_path[j].key == key_to_add:
                current_path = current_path[j].child
                path_index.append(j)
                
                break   #exit while loop when node is found since there won't be any duplicate nodes
            
            j += 1
        
        i += 1
                
    
    return current_path, path_index



#name search
def get_search(root, code):
        
    #from what node to get data from
    search_depth = len(code)
    node_count = 1
    
    current_path = root
    
    i = 1
    while i < len(code):
        
        j = 0
        while j < len(current_path.child):
            
            if code[i] == current_path.child[j].key:
                current_path = current_path.child[j]
                break
            
            j += 1
        node_count += 1
    
        i += 1
        
    return traverse_main(current_path, search_depth)
        
    
def traverse_main(current_path, search_depth):
    
    champions = []
    
    
    #might not need to have root node in stack since current_path can never be reversed
    def traverse(current_path, search_depth):

        if is_leaf(current_path):
            #print(champions)

            return abstract_champion(current_path)
        
        
        else:
            # print(len(current_path.child))
            for path in current_path.child:
                traverse_return = traverse(path, search_depth)
                
                if is_leaf(traverse_return):
                    # print("test")
                    champions.append(traverse_return.id)

                    
            return []
    
    #call traverse()
    traverse(current_path, search_depth)
    
    # print(champions)
    return champions


#check if it is a champion class
def is_leaf(node):
    
    # print(type(node))
    #change to type() == Champion
    if type(node) == Champion:
        return 1
    
    return 0


def abstract_champion(champion):
    # print(champion.name)
    return champion


#tag search




#tag db
def read_file():
    try:
        file = open("tag_file.txt", "r")
        
    except:
        print("Tag file could not be opened")
        return "Tag file could not be opened"
    
    print("read file")
    # tag_dict.clear()
    for line in file.readlines():
        print("test", line)


    current_tag = None
    end_tag = None

    while 1:
        line = file.readline()
        
        #break loop at end of file
        if line == "":
            # print("Found end")
            break
        
        
        #get opening tag name
        if line[0] == "<" and line[-2] == ">" and current_tag == None:
            current_tag = line[1:-2]
            end_tag = "</" + current_tag + ">"
            
            tag_dict[current_tag] = []
            
            # print("current tag:", current_tag, end_tag)
        
        
                
        while current_tag != None:
            line = file.readline()
            
            #breaks the loop at closing tag
            if line[:-1] == end_tag:
                current_tag = None
                # print("break")
                break
            
            champion_id = int(line[:-1])
            tag_dict[current_tag].append(champion_id)

            # print("testing tags:", all_champions[champion_id-1])
            # all_champions[champion_id-1].tags.append(current_tag)
            # print("here is Champ ID", champion_id)

            # print(all_champions[champion_id])
            # all_champions[champion_id].tags = [current_tag]
            all_champions[champion_id-1].tags.append(current_tag)
        
        
    print(tag_dict)


def add_tag(champion_id, tag_name):
    
    
    shutil.copy("tag_file.txt", "tag_file_temp.txt")
    
    main_file = open("tag_file.txt", "a")
    temp_file = open("tag_file_temp.txt", "r")
    
    main_file.truncate(0)
    
    start_tag = "<" + tag_name + ">\n"
    end_tag = "</" + tag_name + ">\n"
    
    # print("end tag:", end_tag)
    #if added_champion is false then create a new tag
    added_champion = 0
    
    #here edit the main file with new data
    # make a rule inside the loop for when to add the the new data 
    #need something that can twraverse through file and know where it is
    for line in temp_file.readlines():
        # print(line)
        
        if line == end_tag:
            main_file.write(str(champion_id)+"\n")

            tag_dict[tag_name].append(champion_id)
            print("adding tag", tag_dict)
            all_champions[int(champion_id)-1].tags.append(tag_name)
            print("adding tag", all_champions[int(champion_id)-1].tags)

            added_champion = 1
            
        main_file.write(line)
    
    #create new tag if 'champion_id' was not added
    if not added_champion:
        main_file.write(start_tag)
        
        main_file.write(str(champion_id)+"\n")
        
        main_file.write(end_tag)
        
    
    
    #new line at end of txt file
    #main_file.write("")
    
    
    main_file.close()
    
    #temp_file.truncate(0)
    temp_file.close()

def delete_tag(champion_id, tag_name):

    i = 0
    # print("before", all_champions[int(champion_id)-1].tags)

    # for tag in all_champions[int(champion_id)-1].tags:
    #     if tag == tag_name:
    #         print("delete test", tag, tag_name)
    #         all_champions[int(champion_id)-1].tags.pop(i)
            
    #     i += 1

    champion_tags = all_champions[int(champion_id)-1].tags

    while i < len(champion_tags):
        # print("delete test", champion_tags[i], tag_name)
        if champion_tags[i] == tag_name:
            # print("delete test", champion_tags[i], tag_name)
            champion_tags.pop(i)

        i += 1
    # print("after", all_champions[int(champion_id)-1].tags)

    # print("tag_dict before:", tag_dict)

    i = 0
    for tag_id in tag_dict[tag_name]:
        if tag_id == champion_id:
            tag_dict[tag_name].pop(i)

        i += 1

    # tag_dict[tag_name].pop(i)


    # print("tag_dict after:", tag_dict)
    shutil.copy("tag_file.txt", "tag_file_temp.txt")
    
    main_file = open("tag_file.txt", "a")
    temp_file = open("tag_file_temp.txt", "r")    
    
    main_file.truncate(0)
    
    start_tag = "<" + tag_name + ">\n"
    end_tag = "</" + tag_name + ">\n"   
    
    delete_line = str(champion_id) + "\n"
    
    found_tag = 0
    
    for line in temp_file.readlines():
        # print(line)
        
        
        if line == start_tag:
            found_tag = 1
        
        
        if line == end_tag:
            found_tag = 0
        
        
        if found_tag == 0:
            main_file.write(line)
        
        else:
            if line != delete_line:
                main_file.write(line)
                
        
    
    main_file.close()
    
    #temp_file.truncate(0)
    temp_file.close()

    # read_file()

def tag_file():
    
    #create file. else return error
    try:
        open("tag_file.txt", "x")

    except:
        print("file exists")




if __name__ == '__main__':
    app.run(debug=True)
    